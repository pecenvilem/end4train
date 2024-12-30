import struct

import pandas as pd
import pytest

from end4train.communication.parsers.c_packet import CPacket
from end4train.communication.parsers.d_packet import DPacket
from end4train.communication.parsers.e_packet import EPacket
from end4train.communication.parsers.ffff_packet import FfffPacket
from end4train.communication.parsers.g_packet import GPacket
from end4train.communication.parsers.i_packet import IPacket
from end4train.communication.parsers.j_packet import JPacket
from end4train.communication.parsers.p_packet import PPacket
from end4train.communication.parsers.r_packet import RPacket
from end4train.communication.parsers.record_object import RecordObject
from end4train.communication.parsers.s_packet import SPacket
from end4train.communication.serializers.basic_packets import serialize_i_packet, serialize_c_packet, \
    serialize_e_packet, InvalidDisplayIntensityError, serialize_d_packet, serialize_g_packet, serialize_ffff_packet, \
    serialize_j_packet, serialize_r_packet, DataRequest, serialize_s_packet
from end4train.communication.ksy import Device
from end4train.communication.serializers.p_packet import serialize_p_packet


def test_i_packet():
    assert serialize_i_packet(Device.MASTER) == b'IM'

    for sender in Device:
        packet = serialize_i_packet(sender)
        loaded = IPacket.from_bytes(packet)
        loaded._read()
        assert loaded.packet_type == b"I"
        assert loaded.i_am == sender.value.identifier


def test_j_packet():
    assert serialize_j_packet(Device.EOT) == b'JE'

    for sender in Device:
        packet = serialize_j_packet(sender)
        loaded = JPacket.from_bytes(packet)
        loaded._read()
        assert loaded.packet_type == b"J"
        assert loaded.i_am == sender.value.identifier


def test_c_packet():
    packet = serialize_c_packet()
    assert packet == b'C'
    loaded = CPacket.from_bytes(packet)
    loaded._read()
    assert loaded.packet_type == b"C"


def test_d_packet():
    packet = serialize_d_packet()
    assert packet == b'D'
    loaded = DPacket.from_bytes(packet)
    loaded._read()
    assert loaded.packet_type == b"D"


def test_ffff_packet():
    packet = serialize_ffff_packet()
    assert packet == b'FFFF'
    loaded = FfffPacket.from_bytes(packet)
    loaded._read()
    assert loaded.packet_type == b"FFFF"


def test_e_packet():
    assert serialize_e_packet(4) == b'E\x04'
    assert serialize_e_packet(0) == b'E\x00'

    for intensity in range(0, 16):
        packet = serialize_e_packet(intensity)
        loaded = EPacket.from_bytes(packet)
        loaded._read()
        assert loaded.packet_type == b"E"
        assert loaded.intensity == intensity

    with pytest.raises(InvalidDisplayIntensityError):
        serialize_e_packet(100)
    with pytest.raises(InvalidDisplayIntensityError):
        serialize_e_packet(-1)
    with pytest.raises(struct.error):
        serialize_e_packet(1.5)


def test_g_packet():
    # 2024-12-15 18:54:21.287 UTC
    assert serialize_g_packet(1734288861, 287, True) == b'G\xdd%_g\x1f\x01'
    assert serialize_g_packet(1734288861, 287, False) == b'G\xdd%_g\x1f\x81'
    with pytest.raises(ValueError):
        serialize_g_packet(-5, 287, True)
    with pytest.raises(ValueError):
        serialize_g_packet(1734288861, -98, True)
    with pytest.raises(ValueError):
        serialize_g_packet(1734288861, 1001, True)

    for timestamp in range(1734288861, 1734288861 + 3600):
        packet = serialize_g_packet(timestamp, 0, True)
        loaded = GPacket.from_bytes(packet)
        loaded._read()
        assert loaded.packet_type == b"G"
        assert loaded.timestamp == timestamp
        assert loaded.millisecond == 0
        assert loaded.is_gps is True


def test_r_packet():
    assert serialize_r_packet(0, []) == b'R\x00\x00\x00\x00'
    requests = [
        DataRequest(data_type, period) for data_type in RPacket.ObjectTypeEnum for period in RPacket.RequestPeriodEnum
    ]
    for request_id in [0, 0xFF_FF_FF_FF, 123456]:
        packet = serialize_r_packet(request_id, requests)
        loaded = RPacket.from_bytes(packet)
        loaded._read()
        assert loaded.packet_type == b"R"
        assert loaded.request_id == request_id
        assert requests == [DataRequest(request.object_type, request.period) for request in loaded.requested_types]


def test_s_packet():
    assert serialize_s_packet(0, SPacket.StatusEnum.available_locally) == b'S\x00\x00\x00\x00\x00'
    assert serialize_s_packet(0, SPacket.StatusEnum.requesting_from_remote) == b'S\x00\x00\x00\x00\x01'

    with pytest.raises(ValueError):
        serialize_s_packet(0, 5)

    for request_id in [0, 0xFF_FF_FF_FF, 123456]:
        for status in SPacket.StatusEnum:
            packet = serialize_s_packet(request_id, status)
            loaded = SPacket.from_bytes(packet)
            loaded._read()
            assert loaded.packet_type == b"S"
            assert loaded.request_id == request_id
            assert loaded.request_status == status


def test_p_packet():

    # TODO: add more test cases

    second = 1734288861
    millisecond = 287
    timestamp = second + millisecond / 1000
    data = pd.DataFrame(data={
        "variable": ["pressure_a", "pressure_b"], "value": [0, 4.853],
        "object_type": [
            RecordObject.ObjectTypeEnum.pressure_current_hot.value,
            RecordObject.ObjectTypeEnum.pressure_current_hot.value
        ],
        "timestamp": [pd.to_datetime(timestamp, unit="s"), pd.to_datetime(timestamp, unit="s")]
    })
    packet = serialize_p_packet(True, False, data)
    loaded = PPacket.from_bytes(packet)
    loaded._read()
    pass
