# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

from end4train.communication.parsers import ffff_packet
from end4train.communication.parsers import j_packet
from end4train.communication.parsers import t_packet
from end4train.communication.parsers import g_packet
from end4train.communication.parsers import d_packet
from end4train.communication.parsers import r_packet
from end4train.communication.parsers import i_packet
from end4train.communication.parsers import e_packet
from end4train.communication.parsers import s_packet
from end4train.communication.parsers import p_packet
from end4train.communication.parsers import c_packet
class Packets(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._should_write_body = False
        self.body__to_write = True

    def _read(self):
        self.packet_type = (self._io.read_bytes(1)).decode("ASCII")


    def _fetch_instances(self):
        pass
        _ = self.body
        _on = self.packet_type
        if _on == u"I":
            pass
            self.body._fetch_instances()
        elif _on == u"C":
            pass
            self.body._fetch_instances()
        elif _on == u"E":
            pass
            self.body._fetch_instances()
        elif _on == u"R":
            pass
            self.body._fetch_instances()
        elif _on == u"T":
            pass
            self.body._fetch_instances()
        elif _on == u"S":
            pass
            self.body._fetch_instances()
        elif _on == u"G":
            pass
            self.body._fetch_instances()
        elif _on == u"F":
            pass
            self.body._fetch_instances()
        elif _on == u"J":
            pass
            self.body._fetch_instances()
        elif _on == u"P":
            pass
            self.body._fetch_instances()
        elif _on == u"D":
            pass
            self.body._fetch_instances()


    def _write__seq(self, io=None):
        super(Packets, self)._write__seq(io)
        self._should_write_body = self.body__to_write
        self._io.write_bytes((self.packet_type).encode(u"ASCII"))


    def _check(self):
        pass
        if (len((self.packet_type).encode(u"ASCII")) != 1):
            raise kaitaistruct.ConsistencyError(u"packet_type", len((self.packet_type).encode(u"ASCII")), 1)

    @property
    def body(self):
        if self._should_write_body:
            self._write_body()
        if hasattr(self, '_m_body'):
            return self._m_body

        _pos = self._io.pos()
        self._io.seek(0)
        _on = self.packet_type
        if _on == u"I":
            pass
            self._m_body = i_packet.IPacket(self._io)
            self._m_body._read()
        elif _on == u"C":
            pass
            self._m_body = c_packet.CPacket(self._io)
            self._m_body._read()
        elif _on == u"E":
            pass
            self._m_body = e_packet.EPacket(self._io)
            self._m_body._read()
        elif _on == u"R":
            pass
            self._m_body = r_packet.RPacket(self._io)
            self._m_body._read()
        elif _on == u"T":
            pass
            self._m_body = t_packet.TPacket(self._io)
            self._m_body._read()
        elif _on == u"S":
            pass
            self._m_body = s_packet.SPacket(self._io)
            self._m_body._read()
        elif _on == u"G":
            pass
            self._m_body = g_packet.GPacket(self._io)
            self._m_body._read()
        elif _on == u"F":
            pass
            self._m_body = ffff_packet.FfffPacket(self._io)
            self._m_body._read()
        elif _on == u"J":
            pass
            self._m_body = j_packet.JPacket(self._io)
            self._m_body._read()
        elif _on == u"P":
            pass
            self._m_body = p_packet.PPacket(self._io)
            self._m_body._read()
        elif _on == u"D":
            pass
            self._m_body = d_packet.DPacket(self._io)
            self._m_body._read()
        self._io.seek(_pos)
        return getattr(self, '_m_body', None)

    @body.setter
    def body(self, v):
        self._m_body = v

    def _write_body(self):
        self._should_write_body = False
        _pos = self._io.pos()
        self._io.seek(0)
        _on = self.packet_type
        if _on == u"I":
            pass
            self.body._write__seq(self._io)
        elif _on == u"C":
            pass
            self.body._write__seq(self._io)
        elif _on == u"E":
            pass
            self.body._write__seq(self._io)
        elif _on == u"R":
            pass
            self.body._write__seq(self._io)
        elif _on == u"T":
            pass
            self.body._write__seq(self._io)
        elif _on == u"S":
            pass
            self.body._write__seq(self._io)
        elif _on == u"G":
            pass
            self.body._write__seq(self._io)
        elif _on == u"F":
            pass
            self.body._write__seq(self._io)
        elif _on == u"J":
            pass
            self.body._write__seq(self._io)
        elif _on == u"P":
            pass
            self.body._write__seq(self._io)
        elif _on == u"D":
            pass
            self.body._write__seq(self._io)
        self._io.seek(_pos)


    def _check_body(self):
        pass
        _on = self.packet_type
        if _on == u"I":
            pass
        elif _on == u"C":
            pass
        elif _on == u"E":
            pass
        elif _on == u"R":
            pass
        elif _on == u"T":
            pass
        elif _on == u"S":
            pass
        elif _on == u"G":
            pass
        elif _on == u"F":
            pass
        elif _on == u"J":
            pass
        elif _on == u"P":
            pass
        elif _on == u"D":
            pass


