import asyncio
import socket
import threading
from asyncio import AbstractEventLoop
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
        self._device: Master | None = None
        self._loop: AbstractEventLoop | None = None
        self.receive_data_handler = receive_data_handler
        self._thread: threading.Thread | None = None
        self.listening = False

    def listen(self, host: str):
        if self.listening:
            return
        self.listening = True
        # TODO: move request list to some config...
        requests = [
            DataRequest(RPacket.ObjectTypeEnum.pressure_current_hot, 1),
            DataRequest(RPacket.ObjectTypeEnum.pressure_current_eot, 1),
            DataRequest(RPacket.ObjectTypeEnum.gps_hot, 1),
            DataRequest(RPacket.ObjectTypeEnum.gps_eot, 1),
            DataRequest(RPacket.ObjectTypeEnum.brake, 1),
        ]
        self._device = Master(self.host, self.port, requests)
        self._device.register_data_handler(self.receive_data_handler)
        self._thread = threading.Thread(target=self.run_device_loop)
        self._thread.start()

    def run_device_loop(self) -> None:
        if self._device is None:
            return
        self._loop = asyncio.new_event_loop()
        self._loop.run_until_complete(self._device.run())

    def shutdown(self, host: str) -> None:
        if self._device is None:
            return
        asyncio.run_coroutine_threadsafe(self._device.stop(), self._loop)
        self._thread.join()

    def stop(self, host: str):
        if not self.listening:
            return
        self.shutdown(host)
        self.listening = False


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
