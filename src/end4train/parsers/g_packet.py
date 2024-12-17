# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class GPacket(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

    def _read(self):
        self.packet_type = self._io.read_bytes(1)
        if not (self.packet_type == b"\x47"):
            raise kaitaistruct.ValidationNotEqualError(b"\x47", self.packet_type, self._io, u"/seq/0")
        self.timestamp = self._io.read_u4le()
        self.millisecond = self._io.read_u2le()


    def _fetch_instances(self):
        pass


    def _write__seq(self, io=None):
        super(GPacket, self)._write__seq(io)
        self._io.write_bytes(self.packet_type)
        self._io.write_u4le(self.timestamp)
        self._io.write_u2le(self.millisecond)


    def _check(self):
        pass
        if (len(self.packet_type) != 1):
            raise kaitaistruct.ConsistencyError(u"packet_type", len(self.packet_type), 1)
        if not (self.packet_type == b"\x47"):
            raise kaitaistruct.ValidationNotEqualError(b"\x47", self.packet_type, None, u"/seq/0")

    @property
    def is_gps(self):
        if hasattr(self, '_m_is_gps'):
            return self._m_is_gps

        self._m_is_gps = ((self.millisecond & 32768) == 0)
        return getattr(self, '_m_is_gps', None)

    def _invalidate_is_gps(self):
        del self._m_is_gps

