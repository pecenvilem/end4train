import pytest

from end4train.parsers.c_packet import CPacket
from end4train.parsers.d_packet import DPacket
from end4train.parsers.e_packet import EPacket
from end4train.parsers.ffff_packet import FfffPacket
from end4train.parsers.i_packet import IPacket
from end4train.parsers.j_packet import JPacket
from end4train.parsers.r_packet import RPacket
from end4train.serializers.basic_packets import serialize_i_packet, SenderDevice, serialize_c_packet, \
    serialize_e_packet, InvalidDisplayIntensityError, serialize_d_packet, serialize_g_packet, serialize_ffff_packet, \
    serialize_j_packet, serialize_r_packet, DataRequest


def test_i_packet():
    assert serialize_i_packet(SenderDevice.MASTER) == b'IM'

    for sender in SenderDevice:
        packet = serialize_i_packet(sender)
        loaded = IPacket.from_bytes(packet)
        loaded._read()
        assert loaded.packet_type == b"I"
        assert loaded.i_am == sender


def test_j_packet():
    assert serialize_j_packet(SenderDevice.EOT) == b'JE'

    for sender in SenderDevice:
        packet = serialize_j_packet(sender)
        loaded = JPacket.from_bytes(packet)
        loaded._read()
        assert loaded.packet_type == b"J"
        assert loaded.i_am == sender


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


def test_r_packet():
    request = DataRequest(RPacket.ObjectTypeEnum.pressure_current_hot, RPacket.RequestPeriodEnum.now)
    r = serialize_r_packet(127, [request])


def test_s_packet():
    pass


def test_p_packet():
    pass
