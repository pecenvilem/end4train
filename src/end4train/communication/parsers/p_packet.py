# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

from end4train.communication.parsers import process_data
class PPacket(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

    def _read(self):
        self.packet_type = self._io.read_bytes(1)
        if not (self.packet_type == b"\x50"):
            raise kaitaistruct.ValidationNotEqualError(b"\x50", self.packet_type, self._io, u"/seq/0")
        self.epoch_number = self._io.read_bits_int_le(32)
        self.time = PPacket.EpochTime(self._io, self, self._root)
        self.time._read()
        self.body = process_data.ProcessData(self._io)
        self.body._read()


    def _fetch_instances(self):
        pass
        self.time._fetch_instances()
        self.body._fetch_instances()


    def _write__seq(self, io=None):
        super(PPacket, self)._write__seq(io)
        self._io.write_bytes(self.packet_type)
        self._io.write_bits_int_le(32, self.epoch_number)
        self.time._write__seq(self._io)
        self.body._write__seq(self._io)


    def _check(self):
        pass
        if (len(self.packet_type) != 1):
            raise kaitaistruct.ConsistencyError(u"packet_type", len(self.packet_type), 1)
        if not (self.packet_type == b"\x50"):
            raise kaitaistruct.ValidationNotEqualError(b"\x50", self.packet_type, None, u"/seq/0")
        if self.time._root != self._root:
            raise kaitaistruct.ConsistencyError(u"time", self.time._root, self._root)
        if self.time._parent != self:
            raise kaitaistruct.ConsistencyError(u"time", self.time._parent, self)

    class EpochTime(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.millisecond = self._io.read_bits_int_le(12)
            self.eot_data = self._io.read_bits_int_le(1) != 0
            self.eot_link_fail = self._io.read_bits_int_le(1) != 0
            self.remote_eot_no_gps_time = self._io.read_bits_int_le(1) != 0
            self.local_no_gps_time = self._io.read_bits_int_le(1) != 0


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(PPacket.EpochTime, self)._write__seq(io)
            self._io.write_bits_int_le(12, self.millisecond)
            self._io.write_bits_int_le(1, int(self.eot_data))
            self._io.write_bits_int_le(1, int(self.eot_link_fail))
            self._io.write_bits_int_le(1, int(self.remote_eot_no_gps_time))
            self._io.write_bits_int_le(1, int(self.local_no_gps_time))


        def _check(self):
            pass



