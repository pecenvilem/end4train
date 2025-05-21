import asyncio
import logging.config
import time
import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Any, Coroutine

import anyio
import pandas as pd
from anyio import create_udp_socket, sleep, create_task_group, Lock
from anyio.abc import UDPSocket

from end4train.communication.parsers.p_packet import PPacket
from end4train.config.communication import PORT, SERVE_DELAY, BROADCAST_ADDRESS
from end4train.config.dummy_device import TEST_HOT_HOST, TEST_MASTER_HOST, TEST_EOT_HOST
from end4train.config.logging import LOGGING_CONFIG
from end4train.config.paths import RECORD_OBJECT_KSY_PATH, HOT_SAMPLE_PARQUET_FOLDER, EOT_SAMPLE_PARQUET_FOLDER
from end4train.communication.decode import merge_type_specific_dataframes
from end4train.communication.ksy import Device, KSYInfoStore, get_device_for_identifier
from end4train.communication.parsers.packets import Packets
from end4train.communication.parsers.r_packet import RPacket
from end4train.communication.parsers.s_packet import SPacket
from end4train.communication.serializers.basic_packets import serialize_j_packet, serialize_i_packet, DataRequest, \
    serialize_r_packet, serialize_s_packet, serialize_g_packet
from end4train.communication.serializers.p_packet import serialize_p_packet, assemble_p_packet

module_logger = logging.getLogger(__name__)
logging.config.dictConfig(LOGGING_CONFIG)

@dataclass(frozen=True)
class HostInfo:
    host: str
    port: int

    def __str__(self) -> str:
        return f"{self.host}:{self.port}"


def shift_data(data: pd.DataFrame, start_time: datetime.datetime) -> pd.DataFrame:
    data = data.copy()
    new_start_second = int(start_time.timestamp())
    original_start_second = data["second"].min()
    offset = new_start_second - original_start_second
    data["second"] += offset
    return data


class TimsDevice(ABC):
    @abstractmethod
    def __init__(self, local_host: str, local_port: int = PORT):
        self.device_type: Device | None = None

        self._host = HostInfo(local_host, local_port)
        self.known_hosts: dict[Device: set[HostInfo]] = {
            device: set() for device in Device
        }
        self.handlers: dict[str, Callable[[Packets, str, int], bytes]] = {
            "I": self.handle_i_packet,
            "J": self.handle_j_packet,
            "T": self.handle_t_packet,
        }
        self._task_group: anyio.abc.TaskGroup | None = None
        self._startup_tasks: list[Coroutine[Any, Any, Any]] = []
        self._requested_data: dict[HostInfo, dict[int, DataRequest]] = {}
        self._recent_transmission: dict[HostInfo, dict[int, int]] = {}
        self._socket_lock = Lock()
        self._socket: UDPSocket | None = None

        # noinspection PyTypeChecker
        self.add_startup_task(self.handle_incoming_packets)

    def _set_device_type(self, device: Device) -> None:
        self.device_type = device

    async def _send_data_with_lock(self, data: bytes | bytearray, remote_host: str, remote_port: int) -> None:
        async with self._socket_lock:
            await self._socket.sendto(data, remote_host, remote_port)

    def add_startup_task(self, task: Coroutine[Any, Any, Any]) -> None:
        self._startup_tasks.append(task)

    def get_log_header(self) -> str:
        return f"{self.device_type.name} at '{self._host}'"

    def add_known_host(self, remote_host: HostInfo, remote_device_type: str) -> None:
        # TODO: handle possible UnknownDeviceIdentifierError (if remote_device_type is not known)
        device = get_device_for_identifier(remote_device_type)
        self.known_hosts[device].add(remote_host)
        module_logger.debug(f"{self.get_log_header()}: added known host: {device.name} @ {remote_host}")

    def get_identification_response(self) -> bytes:
        return serialize_j_packet(self.device_type)

    def get_identification_request(self) -> bytes:
        return serialize_i_packet(self.device_type)

    async def start_listening(self, local_host: str, local_port: int = PORT) -> None:
        self._socket = await create_udp_socket(local_host=local_host, local_port=local_port)

    async def handle_incoming_packets(self) -> None:
        async with self._socket:
            async for packet, (host, port) in self._socket:
                # TODO: catch errors from packet parsing
                decoded_packet = Packets.from_bytes(packet)
                # noinspection PyProtectedMember
                decoded_packet._read()
                module_logger.debug(
                    f"{self.get_log_header()}: packet: {decoded_packet.packet_type} from {HostInfo(host, port)}"
                )
                handler = self.handlers.get(decoded_packet.packet_type)
                if handler is None:
                    module_logger.warning(
                        f"{self.get_log_header()}: packet type: {decoded_packet.packet_type}: no handler"
                    )
                    continue
                response = handler(decoded_packet, host, port)
                if response is not None:
                    await self._send_data_with_lock(response, host, port)

    async def run(self) -> None:
        if self._socket is None:
            await self.start_listening(self._host.host, self._host.port)
            module_logger.info(f"{self.get_log_header()}: started listening")
        self._task_group = create_task_group()
        async with self._task_group:
            for task in self._startup_tasks:
                # noinspection PyTypeChecker
                self._task_group.start_soon(task)
        module_logger.debug(f"{self.get_log_header()}: exited task group")

    async def stop(self) -> None:
        if self._task_group is not None:
            self._task_group.cancel_scope.cancel()
            self._task_group = None

    def handle_i_packet(self, packet: Packets, source_host: str, source_port: int) -> bytes | None:
        self.add_known_host(HostInfo(source_host, source_port), packet.body.i_am)
        return self.get_identification_response()

    def handle_j_packet(self, packet: Packets, source_host: str, source_port: int) -> bytes | None:
        self.add_known_host(HostInfo(source_host, source_port), packet.body.i_am)
        return None

    @staticmethod
    def handle_t_packet(packet: Packets, source_host: str, source_port: int) -> bytes | None:
        unix_nanosecond = time.time_ns()
        second = int(unix_nanosecond // 1e9)
        millisecond = int(unix_nanosecond // 1e6 - second * 1e3)
        return serialize_g_packet(second, millisecond, False)

class DataAcquisitionDevice(TimsDevice):

    def __init__(self, ksy_info_store: KSYInfoStore, sample_data_folder: Path, local_host: str, local_port: int = PORT):
        super().__init__(local_host, local_port)
        self.ksy_info_store = ksy_info_store
        self.sample_data = DataAcquisitionDevice.load_sample_data_folder(sample_data_folder)
        self.handlers["R"] = self.handle_r_packet
        # noinspection PyTypeChecker
        self.add_startup_task(self.serve_data)

    @staticmethod
    def load_sample_data_folder(folder: Path) -> pd.DataFrame:
        dataframes = [pd.read_parquet(file) for file in folder.iterdir()]
        return merge_type_specific_dataframes(dataframes)

    async def serve_data(self) -> None:
        current_time = datetime.datetime.now(datetime.UTC)
        start_time = current_time - datetime.timedelta(hours=1)
        data = shift_data(self.sample_data, start_time)
        ksy_store = KSYInfoStore(RECORD_OBJECT_KSY_PATH)
        while True:
            await sleep(SERVE_DELAY)
            current_time = int(time.time())
            for remote_host, requests in self._requested_data.items():
                hosts_recent_transmissions = self._recent_transmission.get(remote_host, {})
                objects_to_send = []
                for request in requests.values():
                    last_transmission = hosts_recent_transmissions.get(request.data_type, 0)
                    if current_time >= last_transmission + request.period:
                        objects_to_send.append(request.data_type)
                if not objects_to_send:
                    continue
                data_to_send = data[(data["second"] == current_time) & (data["data_object_type"].isin(objects_to_send))]
                await self.send_data(data_to_send, ksy_store, remote_host)
                for sent_object in objects_to_send:
                    hosts_recent_transmissions[sent_object] = current_time
                self._recent_transmission[remote_host] = hosts_recent_transmissions

    async def send_data(self, data_to_send: pd.DataFrame, ksy_info_store: KSYInfoStore, remote_host: HostInfo) -> None:
        packet = assemble_p_packet(
            int(time.time()), data_to_send, ksy_info_store.get_enum_value_to_kaitai_type_name_map(),
            False, False
        )
        response = serialize_p_packet(packet)
        module_logger.debug(
            f"{self.get_log_header()}: sending data to '{remote_host.host}:{remote_host.port}': "
            f"record types: {", ".join([str(record.object_type) for record in packet.body.records])}"
        )
        await self._send_data_with_lock(response, remote_host.host, remote_host.port)

    def handle_r_packet(self, packet: Packets, source_host: str, source_port: int) -> bytes | None:
        r_packet: RPacket = packet.body
        remote_host = HostInfo(source_host, source_port)
        added, removed = [], []
        existing_hosts_requests = self._requested_data.get(remote_host, {})
        for requested_type in r_packet.requested_types:
            if requested_type.period == RPacket.RequestPeriodEnum.stop:
                existing_hosts_requests.pop(requested_type.object_type, None)
                removed.append(requested_type)
                continue
            existing_hosts_requests[requested_type.object_type] = DataRequest(
                requested_type.object_type, requested_type.period
            )
            added.append(requested_type)
        self._requested_data[remote_host] = existing_hosts_requests
        module_logger.info(
            f"{self.get_log_header()}: {HostInfo(source_host, source_port)}: requested types: "
            f"{self.get_r_packet_reception_log(added, removed)}"
        )
        return serialize_s_packet(r_packet.request_id, SPacket.StatusEnum.available_locally)

    @staticmethod
    def get_r_packet_reception_log(
            added_types: list[RPacket.TypeRequest],
            removed_types: list[RPacket.TypeRequest]
    ) -> str:
        if not (added_types or removed_types):
            return "no change"
        if added_types:
            added = f"added: {", ".join(f"{request.object_type}@{request.period}" for request in added_types)} "
        else:
            added =  ""
        if removed_types:
            removed = f"removed: {", ".join(f"{request.object_type}" for request in removed_types)} "
        else:
            removed = ""
        return f"{added}{removed}"


class HoT(DataAcquisitionDevice):
    def __init__(self, ksy_info_store: KSYInfoStore, sample_data_folder: Path, local_host: str, local_port: int = PORT):
        super().__init__(ksy_info_store, sample_data_folder, local_host, local_port)
        self._set_device_type(Device.HOT)


class EoT(DataAcquisitionDevice):
    def __init__(self, ksy_info_store: KSYInfoStore, sample_data_folder: Path, local_host: str, local_port: int = PORT):
        super().__init__(ksy_info_store, sample_data_folder, local_host, local_port)
        self._set_device_type(Device.EOT)


class Master(TimsDevice):

    def __init__(self, local_host: str, local_port: int = PORT, default_requests: list[DataRequest] | None = None):
        super().__init__(local_host, local_port)
        self._set_device_type(Device.MASTER)
        self.handlers["S"] = self.handle_s_packet
        self.handlers["P"] = self.handle_p_packet
        self.handlers["G"] = self.handle_g_packet

        self._scanning_period: float = 10
        self._data_handlers: dict[int, Callable[[PPacket], None]] = {}
        self._next_data_handler_id = 0
        # noinspection PyTypeChecker
        self.add_startup_task(self.scan_for_devices)
        # noinspection PyTypeChecker
        self.add_startup_task(self.read_remote_data_object)

        if default_requests is not None:
            self.requests = default_requests
        else:
            self.requests = []

    async def stop(self) -> None:
        await self.cancel_requests()
        await super().stop()

    def set_scanning_period(self, period: float):
        self._scanning_period = period

    def register_data_handler(self, handler: Callable[[PPacket], None]) -> int:
        handler_id = self._next_data_handler_id
        self._data_handlers[handler_id] = handler
        self._next_data_handler_id += 1
        return handler_id

    def deregister_data_handler(self, handler_id: int) -> None:
        del self._data_handlers[handler_id]

    async def cancel_requests(self) -> None:
        stop_requests = [
            DataRequest(request.data_type, RPacket.RequestPeriodEnum.stop) for request in self.requests
        ]
        await self._send_data_with_lock(
            serialize_r_packet(0, stop_requests),
            TEST_HOT_HOST, PORT
        )
        module_logger.info(
            f"{self.get_log_header()}: cancelled requests from: {HostInfo(TEST_HOT_HOST, PORT)}: "
            f"objects: {", ".join(f"{request.data_type}" for request in stop_requests)}"
        )

    async def read_remote_data_object(self) -> None:
        await self._send_data_with_lock(
            serialize_r_packet(0, self.requests),
            TEST_HOT_HOST, PORT
        )
        module_logger.info(
            f"{self.get_log_header()}: requesting data from: {HostInfo(TEST_HOT_HOST, PORT)}: "
            f"objects: {", ".join(f"{request.data_type}@{request.period}" for request in self.requests)}"
        )

    async def scan_for_devices(self) -> None:
        broadcast = HostInfo(BROADCAST_ADDRESS, PORT)
        while True:
            module_logger.info(f"{self.get_log_header()}: scanning for devices on {broadcast}")
            await self._send_data_with_lock(self.get_identification_request(), BROADCAST_ADDRESS, PORT)
            await sleep(self._scanning_period)

    def handle_p_packet(self, packet: Packets, source_host: str, source_port: int) -> bytes | None:
        module_logger.info(
            f"{self.get_log_header()}: data from: '{source_host}:{source_port}': "
            f"record types: {", ".join(str(record.object_type) for record in packet.body.body.records)}."
        )
        for handler in self._data_handlers.values():
            handler(packet.body)
        return None

    def handle_s_packet(self, packet: Packets, source_host: str, source_port: int) -> bytes | None:
        # TODO: add logic to retry an r-packet request if no acknowledge is received by some time
        s_packet: SPacket = packet.body
        module_logger.info(
            f"{self.get_log_header()}': request ID: {s_packet.request_id} acknowledged by: {source_host}:{source_port}: "
            f"status: {s_packet.request_status.name}"
        )
        return None

    def handle_g_packet(self, packet: Packets, source_host: str, source_port: int) -> bytes | None:
        # TODO: implement
        return None


async def main() -> None:
    store = KSYInfoStore(RECORD_OBJECT_KSY_PATH)
    hot = HoT(ksy_info_store=store, sample_data_folder=HOT_SAMPLE_PARQUET_FOLDER, local_host=TEST_HOT_HOST)
    eot = EoT(ksy_info_store=store, sample_data_folder=EOT_SAMPLE_PARQUET_FOLDER, local_host=TEST_EOT_HOST)
    master = Master(local_host="0.0.0.0")

    async with create_task_group() as tg:
        # noinspection PyTypeChecker
        tg.start_soon(master.run)

        # noinspection PyTypeChecker
        # tg.start_soon(hot.run)

        # noinspection PyTypeChecker
        # tg.start_soon(eot.run)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    # TODO: add KeyboardInterrupt handlers into e.g. serve() to enable graceful shutdown
    #   possibly already handled by AnyIO? Add print statement that catches e.g. serve function teardown
    except KeyboardInterrupt:
        module_logger.info("APP: stopped by user")
