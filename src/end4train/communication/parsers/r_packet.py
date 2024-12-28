# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class RPacket(ReadWriteKaitaiStruct):

    class RequestPeriodEnum(IntEnum):
        stop = 0
        now = 65535

    class ObjectTypeEnum(IntEnum):
        dict_version = 0
        pressure_current_eot = 1
        pressure_current_hot = 2
        pressure_history_eot = 3
        pressure_history_hot = 4
        gps_eot = 5
        gps_hot = 6
        fault_eot = 7
        fault_hot = 8
        eot_temp = 9
        hot_temp = 10
        brake = 11
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

    def _read(self):
        self.packet_type = self._io.read_bytes(1)
        if not (self.packet_type == b"\x52"):
            raise kaitaistruct.ValidationNotEqualError(b"\x52", self.packet_type, self._io, u"/seq/0")
        self.request_id = self._io.read_u4le()
        self.requested_types = []
        i = 0
        while not self._io.is_eof():
            _t_requested_types = RPacket.TypeRequest(self._io, self, self._root)
            _t_requested_types._read()
            self.requested_types.append(_t_requested_types)
            i += 1



    def _fetch_instances(self):
        pass
        for i in range(len(self.requested_types)):
            pass
            self.requested_types[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(RPacket, self)._write__seq(io)
        self._io.write_bytes(self.packet_type)
        self._io.write_u4le(self.request_id)
        for i in range(len(self.requested_types)):
            pass
            if self._io.is_eof():
                raise kaitaistruct.ConsistencyError(u"requested_types", self._io.size() - self._io.pos(), 0)
            self.requested_types[i]._write__seq(self._io)

        if not self._io.is_eof():
            raise kaitaistruct.ConsistencyError(u"requested_types", self._io.size() - self._io.pos(), 0)


    def _check(self):
        pass
        if (len(self.packet_type) != 1):
            raise kaitaistruct.ConsistencyError(u"packet_type", len(self.packet_type), 1)
        if not (self.packet_type == b"\x52"):
            raise kaitaistruct.ValidationNotEqualError(b"\x52", self.packet_type, None, u"/seq/0")
        for i in range(len(self.requested_types)):
            pass
            if self.requested_types[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"requested_types", self.requested_types[i]._root, self._root)
            if self.requested_types[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"requested_types", self.requested_types[i]._parent, self)


    class TypeRequest(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.object_type = KaitaiStream.resolve_enum(RPacket.ObjectTypeEnum, self._io.read_u1())
            self.period = KaitaiStream.resolve_enum(RPacket.RequestPeriodEnum, self._io.read_u2le())


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(RPacket.TypeRequest, self)._write__seq(io)
            self._io.write_u1(int(self.object_type))
            self._io.write_u2le(int(self.period))


        def _check(self):
            pass



