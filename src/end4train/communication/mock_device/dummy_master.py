import asyncio

from anyio import create_connected_udp_socket, fail_after


async def main():
    async with await create_connected_udp_socket(remote_host='localhost', remote_port=3635) as udp:
        await udp.send(b'Test')

        expecting_data = True
        while expecting_data:
            try:
                with fail_after(1):
                    print(await udp.receive())
            except TimeoutError:
                expecting_data = False

if __name__ == '__main__':
    asyncio.run(main())
