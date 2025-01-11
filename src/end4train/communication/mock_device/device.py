import asyncio


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


async def main() -> None:

    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        EchoServerProtocol,
        local_addr=("localhost", 3635)
    )

    try:
        await asyncio.sleep(3600)  # Serve for 1 hour.
    finally:
        transport.close()


if __name__ == '__main__':
    asyncio.run(main())
