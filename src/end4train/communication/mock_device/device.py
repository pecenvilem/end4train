import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Any, Coroutine

from anyio import create_connected_udp_socket, create_udp_socket, sleep, create_task_group
from anyio.abc import UDPSocket

from end4train.communication.constants import PORT
from end4train.communication.ksy import Device
from end4train.communication.parsers.packets import Packets
from end4train.communication.parsers.r_packet import RPacket
from end4train.communication.serializers.basic_packets import serialize_j_packet, serialize_i_packet


@dataclass(frozen=True)
class KnownHost:
    remote_host: str
    remote_port: int


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
            "R": self.handle_r_packet,
        }
        self.task_group = create_task_group()
        self._tasks_to_start: list[Coroutine[Any, Any, Any]] = []
        self.socket: UDPSocket | None = None

        self.add_task(self.handle_incoming_packets)

    def _set_device_type(self, device: Device) -> None:
        self.device_type = device

    def add_task(self, task: Coroutine[Any, Any, Any]) -> None:
        self._tasks_to_start.append(task)

    def add_known_host(self, remote_host: str, remote_port: int, remote_device_type: str) -> None:
        self.known_hosts[remote_device_type].add(KnownHost(remote_host, remote_port))

    def identify(self) -> bytes:
        return serialize_j_packet(self.device_type)

    def request_identification(self) -> bytes:
        return serialize_i_packet(self.device_type)

    async def start_listening(self, local_host: str, local_port: int = PORT) -> None:
        self.socket = await create_udp_socket(local_host=local_host, local_port=local_port)

    async def handle_incoming_packets(self) -> None:
        async with self.socket:
            async for packet, (host, port) in self.socket:
                decoded_packet = Packets.from_bytes(packet)
                decoded_packet._read()
                handler = self.handlers.get(decoded_packet.packet_type)
                if handler is None:
                    print(f"No handler for packet type: {decoded_packet.packet_type}")
                    continue
                response = handler(decoded_packet, host, port)
                if response is not None:
                    await self.socket.sendto(response, host, port)
            # TODO: add RPacket handling

    async def run(self) -> None:
        if self.socket is None:
            await self.start_listening(self.local_host, self.local_port)
        async with self.task_group:
            for task in self._tasks_to_start:
                self.task_group.start_soon(task)

    def stop(self) -> None:
        self.task_group.cancel_scope.cancel()

    def handle_i_packet(self, packet: Packets, source_host: str, source_port: int) -> bytes | None:
        self.add_known_host(source_host, source_port, packet.body.i_am)
        return self.identify()

    def handle_j_packet(self, packet: Packets, source_host: str, source_port: int) -> bytes | None:
        self.add_known_host(source_host, source_port, packet.body.i_am)
        return None

    def handle_r_packet(self, packet: Packets, source_host: str, source_port: int) -> bytes | None:
        r_packet: RPacket = packet.body
        for requested_type in r_packet.requested_types:
            # TODO: design a way
            requested_type.object_type


class HoT(TimsDevice):
    def __init__(self, local_host: str, local_port: int = PORT):
        super().__init__(local_host, local_port)
        self._set_device_type(Device.HOT)


class EoT(TimsDevice):
    def __init__(self, local_host: str, local_port: int = PORT):
        super().__init__(local_host, local_port)
        self._set_device_type(Device.EOT)


class Master(TimsDevice):

    def __init__(self, local_host: str, local_port: int = PORT):
        super().__init__(local_host, local_port)
        self._set_device_type(Device.MASTER)

        self._scanning_period: float = 10
        self.add_task(self.scan_for_devices)

    def set_scanning_period(self, period: float):
        self._scanning_period = period

    async def scan_for_devices(self):
        while True:
            await self.socket.sendto(self.request_identification(), "127.255.255.255", PORT)
            await sleep(self._scanning_period)


async def main() -> None:
    hot = HoT(local_host="127.0.0.3")
    eot = EoT(local_host="127.0.0.2")
    master = Master(local_host="127.0.0.1")

    async with create_task_group() as tg:
        tg.start_soon(master.run)
        tg.start_soon(hot.run)
        tg.start_soon(eot.run)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    # TODO: add KeyboardInterrupt handlers into e.g. serve() to enable graceful shutdown
    #   possibly already handled by AnyIO? Add print statement that catches e.g. serve function teardown
    except KeyboardInterrupt:
        print("Stopped by user")