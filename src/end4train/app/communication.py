import socket
import threading
from typing import Callable

from end4train.binary_parser import DataSource
from end4train.parsers.record_object import RecordObject

REQUEST_ONE_TRANSMISSION = 65535


def request_object(host: str, object_type: RecordObject.ObjectTypeEnum, period: int = 0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(
        b"".join([
            b"R",
            (0).to_bytes(length=4, byteorder="little"),
            object_type.value.to_bytes(length=1, byteorder="little"),
            period.to_bytes(length=2, byteorder="little"),
        ]), (host, 3635)
    )


class OnLineListener:
    def __init__(self, receive_data_handler, host='0.0.0.0', port=3635):
        self.host = host
        self.port = port
        self.receive_data_handler = receive_data_handler
        self.listener_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._thread = threading.Thread(target=self._listen_loop)
        self.listening = False

    def listen(self, host: str):
        if self.listening:
            return
        self.listening = True
        self.listener_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._thread = threading.Thread(target=self._listen_loop)
        self._thread.start()

        for object_type in RecordObject.ObjectTypeEnum:
            request_object(host, object_type, 1)

    def stop(self, host: str):
        if not self.listening:
            return
        for object_type in RecordObject.ObjectTypeEnum:
            request_object(host, object_type, 0)
        self.listener_socket.shutdown(socket.SHUT_RDWR)
        self.listener_socket.close()
        # make a dummy connection to the listening socket - this causes the .recv to return and throw exception
        socket.socket(socket.AF_INET, socket.SOCK_DGRAM).connect(("localhost", self.port))

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
    def __init__(self, receive_data_handler: Callable, host: str, port=3635):
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
