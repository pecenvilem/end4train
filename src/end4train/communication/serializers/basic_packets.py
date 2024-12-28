from dataclasses import dataclass
from io import BytesIO
from typing import Callable, Iterable

from kaitaistruct import KaitaiStream

from end4train.communication.constants import MINIMUM_INTENSITY, MAXIMUM_INTENSITY
from end4train.communication.ksy import Device
from end4train.communication.errors import InvalidDisplayIntensityError
from end4train.communication.parsers.c_packet import CPacket
from end4train.communication.parsers.d_packet import DPacket
from end4train.communication.parsers.e_packet import EPacket
from end4train.communication.parsers.ffff_packet import FfffPacket
from end4train.communication.parsers.g_packet import GPacket
from end4train.communication.parsers.i_packet import IPacket
from end4train.communication.parsers.j_packet import JPacket
from end4train.communication.parsers.r_packet import RPacket
from end4train.communication.parsers.s_packet import SPacket
from end4train.communication.parsers.t_packet import TPacket


@dataclass
class DataRequest:
    data_type: RPacket.ObjectTypeEnum
    period: int | RPacket.RequestPeriodEnum


# noinspection PyProtectedMember
def create_bytes(packet, buffer_length: int) -> bytes:
    _io = KaitaiStream(BytesIO(bytes(buffer_length)))
    packet._write(_io)
    return _io.to_byte_array()


def get_constant_packet_serializer(packet_class, length: int, **kwargs) -> Callable:
    # noinspection PyProtectedMember
    def serialize():
        packet = packet_class()
        for key, value in kwargs.items():
            setattr(packet, key, value)
        packet._check()
        return create_bytes(packet, buffer_length=length)
    return serialize


serialize_c_packet = get_constant_packet_serializer(CPacket, 1, packet_type=b"C")
serialize_d_packet = get_constant_packet_serializer(DPacket, 1, packet_type=b"D")
serialize_t_packet = get_constant_packet_serializer(TPacket, 1, packet_type=b"T")
serialize_ffff_packet = get_constant_packet_serializer(FfffPacket, 4, packet_type=b"FFFF")


# noinspection PyProtectedMember
def serialize_e_packet(intensity: int) -> bytes:
    if not MINIMUM_INTENSITY <= intensity <= MAXIMUM_INTENSITY:
        raise InvalidDisplayIntensityError(intensity)
    packet = EPacket()
    packet.packet_type = b"E"
    packet.intensity = intensity
    packet._check()

    return create_bytes(packet, buffer_length=2)


# noinspection PyProtectedMember
def serialize_g_packet(timestamp: int, millisecond: int, is_gps: bool) -> bytes:
    if timestamp < 0:
        raise ValueError(f"UNIX Timestamp can't be negative! {timestamp} given.")
    if millisecond < 0:
        raise ValueError(f"Millisecond count can't be negative! {millisecond} given.")
    if millisecond >= 1000:
        raise ValueError(f"Number above 1000 can't be used to express number of milliseconds. {millisecond} given.")
    packet = GPacket()
    packet.packet_type = b"G"
    packet.timestamp = timestamp
    if not is_gps:
        millisecond |= 0x8000
    packet.millisecond = millisecond
    packet._check()

    return create_bytes(packet, buffer_length=7)


# noinspection PyProtectedMember
def serialize_i_packet(sender_id: Device) -> bytes:
    packet = IPacket()
    packet.packet_type = b"I"
    packet.i_am = sender_id.value.identifier
    packet._check()

    return create_bytes(packet, buffer_length=2)


# noinspection PyProtectedMember
def serialize_j_packet(sender_id: Device) -> bytes:
    packet = JPacket()
    packet.packet_type = b"J"
    packet.i_am = sender_id.value.identifier
    packet._check()

    return create_bytes(packet, buffer_length=2)


# noinspection PyProtectedMember
def serialize_r_packet(request_id: int, requested_data: Iterable[DataRequest]) -> bytes:
    if request_id < 0:
        raise ValueError(f"Request ID must not be negative. {request_id} passed.")
    packet = RPacket()
    packet.packet_type = b'R'
    packet.request_id = request_id
    packet.requested_types = []
    for request in requested_data:
        req_struct = RPacket.TypeRequest(None, packet, packet._root)
        req_struct.object_type = request.data_type
        req_struct.period = request.period
        req_struct._check()
        packet.requested_types.append(req_struct)
    packet._check()

    return create_bytes(packet, buffer_length=5+len(packet.requested_types)*3)


# noinspection PyProtectedMember
def serialize_s_packet(request_id: int, status: SPacket.StatusEnum) -> bytes:
    if request_id < 0:
        raise ValueError(f"Request ID must not be negative. {request_id} passed.")
    if status not in SPacket.StatusEnum:
        raise ValueError(f"Unknown request status: {status}.")
    packet = SPacket()
    packet.packet_type = b'S'
    packet.request_id = request_id
    packet.request_status = status
    packet._check()
    return create_bytes(packet, buffer_length=6)
