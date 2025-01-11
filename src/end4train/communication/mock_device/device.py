import asyncio


class EchoServerProtocol(asyncio.DatagramProtocol):
    def __init__(self):
        super().__init__()
        self.transport: asyncio.DatagramTransport | None = None

    def connection_made(self, transport):
        print("Incoming connection")
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        print('Received %r from %s' % (message, addr))
        print('Send %r to %s' % (message, addr))
        self.transport.sendto(data, addr)


async def main() -> None:
    print("Starting UDP server")

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
