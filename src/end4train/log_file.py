# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum

from end4train.p_packet import PPacket


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class LogFile(KaitaiStruct):

    class RecordType(Enum):
        text = 0
        data = 1
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self._raw_sectors = []
        self.sectors = []
        i = 0
        while not self._io.is_eof():
            self._raw_sectors.append(self._io.read_bytes(4096))
            _io__raw_sectors = KaitaiStream(BytesIO(self._raw_sectors[-1]))
            self.sectors.append(LogFile.Sector(_io__raw_sectors, self, self._root))
            i += 1


    class RecordArray(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.records = []
            i = 0
            while True:
                _ = LogFile.Record(self._io, self, self._root)
                self.records.append(_)
                if (self._io.pos() + 51) >= self._io.size():
                    break
                i += 1
            self.next_sector_data = self._io.read_bytes_full()


    class DataRecord(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw_data = self._io.read_bytes((self._parent.record_size - 5))
            _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
            self.data = PPacket.ProcessData(_io__raw_data, self, self._root)


    class TextRecord(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.milliseconds = self._io.read_u1()
            self.text = (self._io.read_bytes((self._parent.record_size - 6))).decode(u"ASCII")


    class Sector(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw_header = self._io.read_bytes(12)
            _io__raw_header = KaitaiStream(BytesIO(self._raw_header))
            self.header = LogFile.SectorHeader(_io__raw_header, self, self._root)
            self.previous_sector_data = self._io.read_bytes(self.header.payload_offset)
            self._raw_records = self._io.read_bytes((4084 - self.header.payload_offset))
            _io__raw_records = KaitaiStream(BytesIO(self._raw_records))
            self.records = LogFile.RecordArray(_io__raw_records, self, self._root)


    class SectorHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unix_time = self._io.read_u4le()
            self.check_sum = self._io.read_u4le()
            self.serial_number = self._io.read_u2le()
            self.payload_offset = self._io.read_u1()
            self.reserved = self._io.read_bytes(1)


    class Record(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.discriminator = self._io.read_u1()
            self.time_of_record = self._io.read_u4le()
            if self.record_type == LogFile.RecordType.text:
                self.text = LogFile.TextRecord(self._io, self, self._root)

            if self.record_type == LogFile.RecordType.data:
                self.data = LogFile.DataRecord(self._io, self, self._root)


        @property
        def record_type(self):
            if hasattr(self, '_m_record_type'):
                return self._m_record_type

            self._m_record_type = (LogFile.RecordType.text if self.discriminator > 127 else LogFile.RecordType.data)
            return getattr(self, '_m_record_type', None)

        @property
        def record_size(self):
            if hasattr(self, '_m_record_size'):
                return self._m_record_size

            self._m_record_size = (self.discriminator & 127)
            return getattr(self, '_m_record_size', None)
