import asyncio
import signal
import socket

from anyio import create_connected_udp_socket, create_udp_socket, sleep, create_task_group, CancelScope, \
    open_signal_receiver, get_cancelled_exc_class

from end4train.communication.constants import PORT
from end4train.communication.ksy import Device
from end4train.communication.parsers.packets import Packets
from end4train.communication.serializers.basic_packets import serialize_i_packet


# TODO: rework using AnyIO

class EchoServerProtocol(asyncio.DatagramProtocol):
    def __init__(self):
        super().__init__()
        self.transport: asyncio.DatagramTransport | None = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = "Hello " + data.decode()
        self.transport.sendto(message.encode(), addr)


async def serve(local_host: str, as_device: Device) -> None:
    async with await create_udp_socket(local_host=local_host, local_port=PORT) as udp:
        print("Serving...")
        async for packet, (host, port) in udp:
            print(f"Received from: {(host, port)}")
            print(f"Incoming data: {packet}")
            decoded_packet = Packets.from_bytes(packet)
            decoded_packet._read()
            print(f"Decoded packet type: {decoded_packet.packet_type}")
            if decoded_packet.packet_type == "I":
                response = serialize_i_packet(as_device)
                print(f"Sending response: {response}")
                await udp.sendto(response, host, port)


async def main() -> None:
    async with create_task_group() as tg:
        tg.start_soon(serve, "127.0.0.2", Device.EOT)
        tg.start_soon(serve, "127.0.0.3", Device.HOT)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    # TODO: add KeyboardInterrupt handlers into e.g. serve() to enable graceful shutdown
    except KeyboardInterrupt:
        print("Stopped by user")