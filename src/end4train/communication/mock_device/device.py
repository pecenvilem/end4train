import asyncio
import logging
import logging.config
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
import datetime
from pathlib import Path
from typing import Callable, Any, Coroutine

import anyio
import pandas as pd
from anyio import create_udp_socket, sleep, create_task_group
from anyio.abc import UDPSocket, SocketAttribute

from end4train.config.communication import PORT, SERVE_DELAY
from end4train.config.logging import LOGGING_CONFIG_DICT
from end4train.config.paths import RECORD_OBJECT_KSY_PATH
from end4train.communication.decode import merge_type_specific_dataframes
from end4train.communication.ksy import Device, KSYInfoStore
from end4train.communication.parsers.packets import Packets
from end4train.communication.parsers.r_packet import RPacket
from end4train.communication.parsers.s_packet import SPacket
from end4train.communication.serializers.basic_packets import serialize_j_packet, serialize_i_packet, DataRequest, \
    serialize_r_packet, serialize_s_packet, serialize_g_packet
from end4train.communication.serializers.p_packet import serialize_p_packet

TEST_HOT_HOST = "127.0.0.10"
TEST_EOT_HOST = "127.0.0.20"
TEST_MASTER_HOST = "127.0.0.30"

SAMPLE_DATA_PARQUET_FOLDER = Path(__file__).parent / "sample_data"
HOT_SAMPLE_PARQUET_FOLDER = SAMPLE_DATA_PARQUET_FOLDER / "hot"
EOT_SAMPLE_PARQUET_FOLDER = SAMPLE_DATA_PARQUET_FOLDER / "eot"

module_logger = logging.getLogger(__name__)
logging.config.dictConfig(LOGGING_CONFIG_DICT)

@dataclass(frozen=True)
class KnownHost:
    remote_host: str
    remote_port: int


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

        self.local_host = local_host
        self.local_port = local_port
        self.known_hosts: dict[Device: set[KnownHost]] = {
            device.value.identifier: set() for device in Device
        }
        self.handlers: dict[str, Callable[[Packets, str, int], bytes]] = {
            "I": self.handle_i_packet,
            "J": self.handle_j_packet,
            "T": self.handle_t_packet,
        }
        self.task_group = create_task_group()
        self._tasks_to_start: list[Coroutine[Any, Any, Any]] = []
        self._requested_data: dict[KnownHost, dict[int, DataRequest]] = {}
        self._recent_transmission: dict[KnownHost, dict[int, int]] = {}
        self.socket: UDPSocket | None = None

        # noinspection PyTypeChecker
        self.add_startup_task(self.handle_incoming_packets)

    def _set_device_type(self, device: Device) -> None:
        self.device_type = device

    def add_startup_task(self, task: Coroutine[Any, Any, Any]) -> None:
        self._tasks_to_start.append(task)

    def get_log_header(self) -> str:
        return f"{self.device_type.name} at '{self.local_host}:{self.local_port}'"

    def add_known_host(self, remote_host: str, remote_port: int, remote_device_type: str) -> None:
        # TODO: represent remote device using Device
        self.known_hosts[remote_device_type].add(KnownHost(remote_host, remote_port))

    def get_identification_response(self) -> bytes:
        return serialize_j_packet(self.device_type)

    def get_identification_request(self) -> bytes:
        return serialize_i_packet(self.device_type)

    async def start_listening(self, local_host: str, local_port: int = PORT) -> None:
        self.socket = await create_udp_socket(local_host=local_host, local_port=local_port)

    async def handle_incoming_packets(self) -> None:
        async with self.socket:
            async for packet, (host, port) in self.socket:
                # TODO: catch errors from packet parsing
                decoded_packet = Packets.from_bytes(packet)
                # noinspection PyProtectedMember
                decoded_packet._read()
                handler = self.handlers.get(decoded_packet.packet_type)
                if handler is None:
                    module_logger.info(
                        f"{self.get_log_header()}: Packet type: {decoded_packet.packet_type}: No handler"
                    )
                    continue
                response = handler(decoded_packet, host, port)
                if response is not None:
                    await anyio.wait_writable(self.socket.extra(SocketAttribute.raw_socket))
                    await self.socket.sendto(response, host, port)

    async def run(self) -> None:
        if self.socket is None:
            await self.start_listening(self.local_host, self.local_port)
        async with self.task_group:
            for task in self._tasks_to_start:
                # noinspection PyTypeChecker
                self.task_group.start_soon(task)

    def stop(self) -> None:
        self.task_group.cancel_scope.cancel()

    def handle_i_packet(self, packet: Packets, source_host: str, source_port: int) -> bytes | None:
        self.add_known_host(source_host, source_port, packet.body.i_am)
        return self.get_identification_response()

    def handle_j_packet(self, packet: Packets, source_host: str, source_port: int) -> bytes | None:
        self.add_known_host(source_host, source_port, packet.body.i_am)
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
            await sleep(SERVE_DELAY)  # wait until the nearest whole second
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

    async def send_data(self, data_to_send: pd.DataFrame, ksy_info_store: KSYInfoStore, remote_host: KnownHost) -> None:
        response = serialize_p_packet(
            int(time.time()), data_to_send, ksy_info_store.get_enum_value_to_kaitai_type_name_map(),
            False, False
        )
        module_logger.debug(
            f"{self.get_log_header()}: Sending to '{remote_host.remote_host}:{remote_host.remote_port}': Packet: {"P"}"
        )
        await self.socket.sendto(response, remote_host.remote_host, remote_host.remote_port)

    def handle_r_packet(self, packet: Packets, source_host: str, source_port: int) -> bytes | None:
        r_packet: RPacket = packet.body
        remote_host = KnownHost(source_host, source_port)
        remote_hosts_requests = self._requested_data.get(remote_host, {})
        for requested_type in r_packet.requested_types:
            if requested_type.period == RPacket.RequestPeriodEnum.stop:
                remote_hosts_requests.pop(requested_type.object_type, None)
                continue
            remote_hosts_requests[requested_type.object_type] = DataRequest(
                requested_type.object_type, requested_type.period
            )
        self._requested_data[remote_host] = remote_hosts_requests
        module_logger.info(
            f"{self.get_log_header()}: R-Packet from: '{remote_host.remote_host}:{remote_host.remote_port}': "
            f"Added requests: "
            f"{", ".join(f"{request.object_type}@{request.period}" for request in r_packet.requested_types)}"
        )
        return serialize_s_packet(r_packet.request_id, SPacket.StatusEnum.available_locally)

class HoT(DataAcquisitionDevice):
    def __init__(self, ksy_info_store: KSYInfoStore, sample_data_folder: Path, local_host: str, local_port: int = PORT):
        super().__init__(ksy_info_store, sample_data_folder, local_host, local_port)
        self._set_device_type(Device.HOT)


class EoT(DataAcquisitionDevice):
    def __init__(self, ksy_info_store: KSYInfoStore, sample_data_folder: Path, local_host: str, local_port: int = PORT):
        super().__init__(ksy_info_store, sample_data_folder, local_host, local_port)
        self._set_device_type(Device.EOT)


class Master(TimsDevice):

    def __init__(self, local_host: str, local_port: int = PORT):
        super().__init__(local_host, local_port)
        self._set_device_type(Device.MASTER)
        self.handlers["S"] = self.handle_s_packet
        self.handlers["P"] = self.handle_p_packet
        self.handlers["G"] = self.handle_g_packet

        self._scanning_period: float = 10
        # noinspection PyTypeChecker
        self.add_startup_task(self.scan_for_devices)
        # noinspection PyTypeChecker
        self.add_startup_task(self.read_remote_data_object)

    def set_scanning_period(self, period: float):
        self._scanning_period = period

    async def read_remote_data_object(self) -> None:
        await anyio.wait_writable(self.socket.extra(SocketAttribute.raw_socket))
        await self.socket.sendto(
            serialize_r_packet(
                0,
                [
                    DataRequest(RPacket.ObjectTypeEnum.pressure_current_hot, 1),
                    DataRequest(RPacket.ObjectTypeEnum.dict_version, 10),
                ]
            ),
            TEST_HOT_HOST, PORT
        )

    async def scan_for_devices(self) -> None:
        while True:
            await self.socket.sendto(self.get_identification_request(), "127.255.255.255", PORT)
            await sleep(self._scanning_period)

    def handle_p_packet(self, packet: Packets, source_host: str, source_port: int) -> bytes | None:
        module_logger.info(
            f"{self.get_log_header()}: P-packet from: '{source_host}:{source_port}': "
            f"Record types: {", ".join(str(record.object_type) for record in packet.body.body.records)}."
        )
        return None

    def handle_s_packet(self, packet: Packets, source_host: str, source_port: int) -> bytes | None:
        # TODO: add logic to retry an r-packet request if no acknowledge is received by some time
        s_packet: SPacket = packet.body
        module_logger.info(
            f"{self.get_log_header()}': S-Packet from: {source_host}:{source_port}: Acknowledged id: "
            f"{s_packet.request_id}: Status: {s_packet.request_status.name}"
        )
        return None

    def handle_g_packet(self, packet: Packets, source_host: str, source_port: int) -> bytes | None:
        return None



async def main() -> None:
    store = KSYInfoStore(RECORD_OBJECT_KSY_PATH)
    hot = HoT(ksy_info_store=store, sample_data_folder=HOT_SAMPLE_PARQUET_FOLDER, local_host=TEST_HOT_HOST)
    # eot = EoT(ksy_info_store=store, sample_data_folder=EOT_SAMPLE_PARQUET_FOLDER, local_host=TEST_EOT_HOST)
    # master = Master(local_host=TEST_MASTER_HOST)

    async with create_task_group() as tg:
        # noinspection PyTypeChecker
        # tg.start_soon(master.run)
        # noinspection PyTypeChecker
        tg.start_soon(hot.run)
        # noinspection PyTypeChecker
        # tg.start_soon(eot.run)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    # TODO: add KeyboardInterrupt handlers into e.g. serve() to enable graceful shutdown
    #   possibly already handled by AnyIO? Add print statement that catches e.g. serve function teardown
    except KeyboardInterrupt:
        module_logger.info("App: Stopped by user")
