# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

from end4train.parsers import process_data
class RecordArray(ReadWriteKaitaiStruct):

    class RecordType(IntEnum):
        data = 0
        text = 1
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

    def _read(self):
        self.records = []
        i = 0
        while not self._io.is_eof():
            _t_records = RecordArray.Record(self._io, self, self._root)
            _t_records._read()
            self.records.append(_t_records)
            i += 1



    def _fetch_instances(self):
        pass
        for i in range(len(self.records)):
            pass
            self.records[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(RecordArray, self)._write__seq(io)
        for i in range(len(self.records)):
            pass
            if self._io.is_eof():
                raise kaitaistruct.ConsistencyError(u"records", self._io.size() - self._io.pos(), 0)
            self.records[i]._write__seq(self._io)

        if not self._io.is_eof():
            raise kaitaistruct.ConsistencyError(u"records", self._io.size() - self._io.pos(), 0)


    def _check(self):
        pass
        for i in range(len(self.records)):
            pass
            if self.records[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"records", self.records[i]._root, self._root)
            if self.records[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"records", self.records[i]._parent, self)


    class Record(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.type = KaitaiStream.resolve_enum(RecordArray.RecordType, self._io.read_bits_int_be(1))
            self.size = self._io.read_bits_int_be(7)
            if not (self.incomplete):
                pass
                self.body = RecordArray.RecordBody(self._io, self, self._root)
                self.body._read()

            if self.incomplete:
                pass
                self.leftover_data = self._io.read_bytes_full()



        def _fetch_instances(self):
            pass
            if not (self.incomplete):
                pass
                self.body._fetch_instances()

            if self.incomplete:
                pass



        def _write__seq(self, io=None):
            super(RecordArray.Record, self)._write__seq(io)
            self._io.write_bits_int_be(1, int(self.type))
            self._io.write_bits_int_be(7, self.size)
            if not (self.incomplete):
                pass
                if self.body._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"body", self.body._root, self._root)
                if self.body._parent != self:
                    raise kaitaistruct.ConsistencyError(u"body", self.body._parent, self)
                self.body._write__seq(self._io)

            if self.incomplete:
                pass
                self._io.write_bytes(self.leftover_data)
                if not self._io.is_eof():
                    raise kaitaistruct.ConsistencyError(u"leftover_data", self._io.size() - self._io.pos(), 0)



        def _check(self):
            pass

        @property
        def incomplete(self):
            if hasattr(self, '_m_incomplete'):
                return self._m_incomplete

            self._m_incomplete = ((self._io.pos() + self.size) >= self._io.size())
            return getattr(self, '_m_incomplete', None)

        def _invalidate_incomplete(self):
            del self._m_incomplete

    class RecordBody(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.timestamp = self._io.read_u4le()
            if (self._parent.type == RecordArray.RecordType.text):
                pass
                self.milliseconds = self._io.read_u1()

            if (self._parent.type == RecordArray.RecordType.text):
                pass
                self.text = (self._io.read_bytes((self._parent.size - 6))).decode("ASCII")

            if (self._parent.type == RecordArray.RecordType.data):
                pass
                self._raw_data = self._io.read_bytes((self._parent.size - 5))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = process_data.ProcessData(_io__raw_data)
                self.data._read()



        def _fetch_instances(self):
            pass
            if (self._parent.type == RecordArray.RecordType.text):
                pass

            if (self._parent.type == RecordArray.RecordType.text):
                pass

            if (self._parent.type == RecordArray.RecordType.data):
                pass
                self.data._fetch_instances()



        def _write__seq(self, io=None):
            super(RecordArray.RecordBody, self)._write__seq(io)
            self._io.write_u4le(self.timestamp)
            if (self._parent.type == RecordArray.RecordType.text):
                pass
                self._io.write_u1(self.milliseconds)

            if (self._parent.type == RecordArray.RecordType.text):
                pass
                self._io.write_bytes((self.text).encode(u"ASCII"))

            if (self._parent.type == RecordArray.RecordType.data):
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._parent.size - 5))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._parent.size - 5)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if (len(self._raw_data) != (self._parent.size - 5)):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", len(self._raw_data), (self._parent.size - 5))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)



        def _check(self):
            pass
            if (self._parent.type == RecordArray.RecordType.text):
                pass

            if (self._parent.type == RecordArray.RecordType.text):
                pass
                if (len((self.text).encode(u"ASCII")) != (self._parent.size - 6)):
                    raise kaitaistruct.ConsistencyError(u"text", len((self.text).encode(u"ASCII")), (self._parent.size - 6))

            if (self._parent.type == RecordArray.RecordType.data):
                pass




