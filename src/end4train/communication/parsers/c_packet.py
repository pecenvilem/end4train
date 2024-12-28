# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class CPacket(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

    def _read(self):
        self.packet_type = self._io.read_bytes(1)
        if not (self.packet_type == b"\x43"):
            raise kaitaistruct.ValidationNotEqualError(b"\x43", self.packet_type, self._io, u"/seq/0")


    def _fetch_instances(self):
        pass


    def _write__seq(self, io=None):
        super(CPacket, self)._write__seq(io)
        self._io.write_bytes(self.packet_type)


    def _check(self):
        pass
        if (len(self.packet_type) != 1):
            raise kaitaistruct.ConsistencyError(u"packet_type", len(self.packet_type), 1)
        if not (self.packet_type == b"\x43"):
            raise kaitaistruct.ValidationNotEqualError(b"\x43", self.packet_type, None, u"/seq/0")


