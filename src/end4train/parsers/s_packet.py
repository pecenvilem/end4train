# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class SPacket(ReadWriteKaitaiStruct):

    class StatusEnum(IntEnum):
        available_locally = 0
        requesting_from_remote = 1
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

    def _read(self):
        self.packet_type = self._io.read_bytes(1)
        if not (self.packet_type == b"\x53"):
            raise kaitaistruct.ValidationNotEqualError(b"\x53", self.packet_type, self._io, u"/seq/0")
        self.request_id = self._io.read_u4le()
        self.request_status = KaitaiStream.resolve_enum(SPacket.StatusEnum, self._io.read_u1())


    def _fetch_instances(self):
        pass


    def _write__seq(self, io=None):
        super(SPacket, self)._write__seq(io)
        self._io.write_bytes(self.packet_type)
        self._io.write_u4le(self.request_id)
        self._io.write_u1(int(self.request_status))


    def _check(self):
        pass
        if (len(self.packet_type) != 1):
            raise kaitaistruct.ConsistencyError(u"packet_type", len(self.packet_type), 1)
        if not (self.packet_type == b"\x53"):
            raise kaitaistruct.ValidationNotEqualError(b"\x53", self.packet_type, None, u"/seq/0")


