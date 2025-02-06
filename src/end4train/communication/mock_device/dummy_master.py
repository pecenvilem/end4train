import asyncio

from anyio import fail_after, create_udp_socket

from end4train.config.communication import PORT
from end4train.communication.ksy import Device
from end4train.communication.serializers.basic_packets import serialize_i_packet


async def main():
    async with await create_udp_socket(local_host="127.0.0.1") as udp:
        packet = serialize_i_packet(Device.MASTER)
        await udp.sendto(packet, "127.255.255.255", PORT)

        expecting_data = True
        while expecting_data:
            try:
                with fail_after(1):
                    print(await udp.receive())
            except TimeoutError:
                expecting_data = False

if __name__ == '__main__':
    asyncio.run(main())
