import asyncio
import socket
import threading
from enum import Enum, auto
from typing import Callable

from end4train.communication.mock_device.device import Master
from end4train.communication.parsers.r_packet import RPacket
from end4train.communication.serializers.basic_packets import serialize_r_packet, DataRequest
from end4train.config.communication import PORT
from end4train.communication.parsers.record_object import RecordObject

REQUEST_ONE_TRANSMISSION = 65535


def request_object(host: str, object_type: RecordObject.ObjectTypeEnum, period: int = 0):
    request_objects(host, [object_type], period)
    # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, )
    # sock.bind(("0.0.0.0", PORT))
    # packet = serialize_r_packet(
    #             0,
    #             [DataRequest(object_type, period),]
    # )
    # sock.sendto(packet, (host, PORT))

def request_objects(host: str, objects: list[RecordObject.ObjectTypeEnum], period: int = 0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, )
    sock.bind(("127.0.0.1", PORT))
    packet = serialize_r_packet(
        0,
        [DataRequest(object_type, period) for object_type in objects]
    )
    sock.sendto(packet, (host, PORT))


class OnLineListener:
    def __init__(self, receive_data_handler, host='0.0.0.0', port=PORT):
        self.host = host
        self.port = port
        self.device = asyncio.run(self.init_device())
        self.receive_data_handler = receive_data_handler
        self.listener_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._thread = threading.Thread(target=self.run_device_loop)
        # self._thread = threading.Thread(target=self._listen_loop)
        self.listening = False

    async def init_device(self) -> Master:
        return Master(self.host, self.port)

    def listen(self, host: str):
        if self.listening:
            return
        self.listening = True
        self.listener_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self._thread = threading.Thread(target=self._listen_loop)
        self._thread = threading.Thread(target=self.run_device_loop)
        self._thread.start()

        request_objects(host, [object_type for object_type in RecordObject.ObjectTypeEnum], 1)

    def run_device_loop(self) -> None:
        asyncio.run(self.device.run())

    def shutdown(self, host: str) -> None:
        request_objects(host, [object_type for object_type in RecordObject.ObjectTypeEnum], 0)
        # for object_type in RecordObject.ObjectTypeEnum:
        #     request_object(host, object_type, 0)
        self.listener_socket.shutdown(socket.SHUT_RDWR)
        self.listener_socket.close()
        # make a dummy connection to the listening socket - this causes the .recv to return and throw exception
        socket.socket(socket.AF_INET, socket.SOCK_DGRAM).connect(("localhost", self.port))

    def stop(self, host: str):
        if not self.listening:
            return
        # self.shutdown(host)
        asyncio.run(self.device.stop())

    def _listen_loop(self):
        self.listener_socket.bind((self.host, self.port))
        while True:
            try:
                data = self.listener_socket.recv(1024)
                if data[0] != ord("P"):
                    continue
                self.receive_data_handler(data, DataSource.P_PACKET)
            except (OSError, BrokenPipeError):
                # connection was closed
                self.listening = False
                return


class LogDownloader:
    def __init__(self, receive_data_handler: Callable, host: str, port=PORT):
        self.host = host
        self.port = port
        self.receive_data_handler = receive_data_handler
        self.downloader_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._thread = threading.Thread(target=self._download)
        self.downloading = False

    def download(self):
        if self.downloading:
            return
        self.downloading = True
        self._thread = threading.Thread(target=self._download)
        self._thread.start()

    def _download(self):
        self.downloader_socket.connect((self.host, self.port))
        received = []
        while True:
            try:
                data = self.downloader_socket.recv(1024)
            except (OSError, BrokenPipeError):
                # connection was closed
                self.downloading = False
                return
            if len(data) == 0:
                break
            received.append(data)
        self.downloading = False
        self.receive_data_handler(b"".join(received), DataSource.LOG_FILE)

    def stop(self):
        if not self.downloading:
            return
        self.downloader_socket.shutdown(socket.SHUT_RDWR)
        self.downloader_socket.close()


class DataSource(Enum):
    LOG_FILE = auto()
    P_PACKET = auto()
