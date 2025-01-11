import socket

import anyio


async def udp_server():
    print('starting udp server')
    async with await anyio.create_udp_socket(
            local_host='localhost', local_port=3635) as udp:
        async for packet, (host, port) in udp:
            print('received: ', packet)
            message = b'Hello, ' + packet
            print('will send:', message)
            await udp.sendto(message, "localhost", port)
            print("Message sent")


async def main():
    async with await anyio.create_udp_socket(
        family=socket.AF_INET6, local_port=3635
    ) as udp:
        async for packet, (host, port) in udp:
            await udp.sendto(b'Hello, ' + packet, host, port)


if __name__ == '__main__':
    anyio.run(udp_server)
