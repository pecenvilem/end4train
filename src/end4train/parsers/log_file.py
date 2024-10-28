# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

from end4train.parsers import process_data
class LogFile(ReadWriteKaitaiStruct):

    class RecordType(IntEnum):
        data = 0
        text = 1
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

    def _read(self):
        self._raw_sectors = []
        self.sectors = []
        i = 0
        while not self._io.is_eof():
            self._raw_sectors.append(self._io.read_bytes(4096))
            _io__raw_sectors = KaitaiStream(BytesIO(self._raw_sectors[-1]))
            _t_sectors = LogFile.Sector(_io__raw_sectors, self, self._root)
            _t_sectors._read()
            self.sectors.append(_t_sectors)
            i += 1



    def _fetch_instances(self):
        pass
        for i in range(len(self.sectors)):
            pass
            self.sectors[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(LogFile, self)._write__seq(io)
        self._raw_sectors = []
        for i in range(len(self.sectors)):
            pass
            if self._io.is_eof():
                raise kaitaistruct.ConsistencyError(u"sectors", self._io.size() - self._io.pos(), 0)
            _io__raw_sectors = KaitaiStream(BytesIO(bytearray(4096)))
            self._io.add_child_stream(_io__raw_sectors)
            _pos2 = self._io.pos()
            self._io.seek(self._io.pos() + (4096))
            def handler(parent, _io__raw_sectors=_io__raw_sectors):
                self._raw_sectors.append(_io__raw_sectors.to_byte_array())
                if (len(self._raw_sectors[(len(self._raw_sectors) - 1)]) != 4096):
                    raise kaitaistruct.ConsistencyError(u"raw(sectors)", len(self._raw_sectors[(len(self._raw_sectors) - 1)]), 4096)
                parent.write_bytes(self._raw_sectors[(len(self._raw_sectors) - 1)])
            _io__raw_sectors.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
            self.sectors[i]._write__seq(_io__raw_sectors)

        if not self._io.is_eof():
            raise kaitaistruct.ConsistencyError(u"sectors", self._io.size() - self._io.pos(), 0)


    def _check(self):
        pass
        for i in range(len(self.sectors)):
            pass
            if self.sectors[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"sectors", self.sectors[i]._root, self._root)
            if self.sectors[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"sectors", self.sectors[i]._parent, self)


    class RecordArray(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.records = []
            i = 0
            while True:
                _t_records = LogFile.Record(self._io, self, self._root)
                _t_records._read()
                _ = _t_records
                self.records.append(_)
                if ((self._io.pos() + 51) >= self._io.size()):
                    break
                i += 1
            self.next_sector_data = self._io.read_bytes_full()


        def _fetch_instances(self):
            pass
            for i in range(len(self.records)):
                pass
                self.records[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(LogFile.RecordArray, self)._write__seq(io)
            for i in range(len(self.records)):
                pass
                self.records[i]._write__seq(self._io)
                _ = self.records[i]
                if (((self._io.pos() + 51) >= self._io.size()) != (i == (len(self.records) - 1))):
                    raise kaitaistruct.ConsistencyError(u"records", ((self._io.pos() + 51) >= self._io.size()), (i == (len(self.records) - 1)))

            self._io.write_bytes(self.next_sector_data)
            if not self._io.is_eof():
                raise kaitaistruct.ConsistencyError(u"next_sector_data", self._io.size() - self._io.pos(), 0)


        def _check(self):
            pass
            if (len(self.records) == 0):
                raise kaitaistruct.ConsistencyError(u"records", len(self.records), 0)
            for i in range(len(self.records)):
                pass
                if self.records[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"records", self.records[i]._root, self._root)
                if self.records[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"records", self.records[i]._parent, self)



    class DataRecord(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self._raw_data = self._io.read_bytes((self._parent.record_size - 5))
            _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
            self.data = process_data.ProcessData(_io__raw_data)
            self.data._read()


        def _fetch_instances(self):
            pass
            self.data._fetch_instances()


        def _write__seq(self, io=None):
            super(LogFile.DataRecord, self)._write__seq(io)
            _io__raw_data = KaitaiStream(BytesIO(bytearray((self._parent.record_size - 5))))
            self._io.add_child_stream(_io__raw_data)
            _pos2 = self._io.pos()
            self._io.seek(self._io.pos() + ((self._parent.record_size - 5)))
            def handler(parent, _io__raw_data=_io__raw_data):
                self._raw_data = _io__raw_data.to_byte_array()
                if (len(self._raw_data) != (self._parent.record_size - 5)):
                    raise kaitaistruct.ConsistencyError(u"raw(data)", len(self._raw_data), (self._parent.record_size - 5))
                parent.write_bytes(self._raw_data)
            _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
            self.data._write__seq(_io__raw_data)


        def _check(self):
            pass


    class TextRecord(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.milliseconds = self._io.read_u1()
            self.text = (self._io.read_bytes((self._parent.record_size - 6))).decode("ASCII")


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(LogFile.TextRecord, self)._write__seq(io)
            self._io.write_u1(self.milliseconds)
            self._io.write_bytes((self.text).encode(u"ASCII"))


        def _check(self):
            pass
            if (len((self.text).encode(u"ASCII")) != (self._parent.record_size - 6)):
                raise kaitaistruct.ConsistencyError(u"text", len((self.text).encode(u"ASCII")), (self._parent.record_size - 6))


    class Sector(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self._raw_header = self._io.read_bytes(12)
            _io__raw_header = KaitaiStream(BytesIO(self._raw_header))
            self.header = LogFile.SectorHeader(_io__raw_header, self, self._root)
            self.header._read()
            self.previous_sector_data = self._io.read_bytes(self.header.payload_offset)
            self._raw_records = self._io.read_bytes((4084 - self.header.payload_offset))
            _io__raw_records = KaitaiStream(BytesIO(self._raw_records))
            self.records = LogFile.RecordArray(_io__raw_records, self, self._root)
            self.records._read()


        def _fetch_instances(self):
            pass
            self.header._fetch_instances()
            self.records._fetch_instances()


        def _write__seq(self, io=None):
            super(LogFile.Sector, self)._write__seq(io)
            _io__raw_header = KaitaiStream(BytesIO(bytearray(12)))
            self._io.add_child_stream(_io__raw_header)
            _pos2 = self._io.pos()
            self._io.seek(self._io.pos() + (12))
            def handler(parent, _io__raw_header=_io__raw_header):
                self._raw_header = _io__raw_header.to_byte_array()
                if (len(self._raw_header) != 12):
                    raise kaitaistruct.ConsistencyError(u"raw(header)", len(self._raw_header), 12)
                parent.write_bytes(self._raw_header)
            _io__raw_header.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
            self.header._write__seq(_io__raw_header)
            self._io.write_bytes(self.previous_sector_data)
            _io__raw_records = KaitaiStream(BytesIO(bytearray((4084 - self.header.payload_offset))))
            self._io.add_child_stream(_io__raw_records)
            _pos2 = self._io.pos()
            self._io.seek(self._io.pos() + ((4084 - self.header.payload_offset)))
            def handler(parent, _io__raw_records=_io__raw_records):
                self._raw_records = _io__raw_records.to_byte_array()
                if (len(self._raw_records) != (4084 - self.header.payload_offset)):
                    raise kaitaistruct.ConsistencyError(u"raw(records)", len(self._raw_records), (4084 - self.header.payload_offset))
                parent.write_bytes(self._raw_records)
            _io__raw_records.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
            self.records._write__seq(_io__raw_records)


        def _check(self):
            pass
            if self.header._root != self._root:
                raise kaitaistruct.ConsistencyError(u"header", self.header._root, self._root)
            if self.header._parent != self:
                raise kaitaistruct.ConsistencyError(u"header", self.header._parent, self)
            if (len(self.previous_sector_data) != self.header.payload_offset):
                raise kaitaistruct.ConsistencyError(u"previous_sector_data", len(self.previous_sector_data), self.header.payload_offset)
            if self.records._root != self._root:
                raise kaitaistruct.ConsistencyError(u"records", self.records._root, self._root)
            if self.records._parent != self:
                raise kaitaistruct.ConsistencyError(u"records", self.records._parent, self)


    class SectorHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.unix_time = self._io.read_u4le()
            self.check_sum = self._io.read_u4le()
            self.serial_number = self._io.read_u2le()
            self.payload_offset = self._io.read_u1()
            self.reserved = self._io.read_bytes(1)


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(LogFile.SectorHeader, self)._write__seq(io)
            self._io.write_u4le(self.unix_time)
            self._io.write_u4le(self.check_sum)
            self._io.write_u2le(self.serial_number)
            self._io.write_u1(self.payload_offset)
            self._io.write_bytes(self.reserved)


        def _check(self):
            pass
            if (len(self.reserved) != 1):
                raise kaitaistruct.ConsistencyError(u"reserved", len(self.reserved), 1)


    class Record(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.rec_type = KaitaiStream.resolve_enum(LogFile.RecordType, self._io.read_bits_int_be(1))
            self.record_size = self._io.read_bits_int_be(7)
            self.time_of_record = self._io.read_u4le()
            if (self.rec_type == LogFile.RecordType.text):
                pass
                self.text = LogFile.TextRecord(self._io, self, self._root)
                self.text._read()

            if (self.rec_type == LogFile.RecordType.data):
                pass
                self.data = LogFile.DataRecord(self._io, self, self._root)
                self.data._read()



        def _fetch_instances(self):
            pass
            if (self.rec_type == LogFile.RecordType.text):
                pass
                self.text._fetch_instances()

            if (self.rec_type == LogFile.RecordType.data):
                pass
                self.data._fetch_instances()



        def _write__seq(self, io=None):
            super(LogFile.Record, self)._write__seq(io)
            self._io.write_bits_int_be(1, int(self.rec_type))
            self._io.write_bits_int_be(7, self.record_size)
            self._io.write_u4le(self.time_of_record)
            if (self.rec_type == LogFile.RecordType.text):
                pass
                self.text._write__seq(self._io)

            if (self.rec_type == LogFile.RecordType.data):
                pass
                self.data._write__seq(self._io)



        def _check(self):
            pass
            if (self.rec_type == LogFile.RecordType.text):
                pass
                if self.text._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"text", self.text._root, self._root)
                if self.text._parent != self:
                    raise kaitaistruct.ConsistencyError(u"text", self.text._parent, self)

            if (self.rec_type == LogFile.RecordType.data):
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self.data._root, self._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self.data._parent, self)




