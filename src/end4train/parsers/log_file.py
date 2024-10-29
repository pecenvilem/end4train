# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class LogFile(ReadWriteKaitaiStruct):
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


    class Sector(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.header = LogFile.SectorHeader(self._io, self, self._root)
            self.header._read()
            self.body = self._io.read_bytes(4084)


        def _fetch_instances(self):
            pass
            self.header._fetch_instances()


        def _write__seq(self, io=None):
            super(LogFile.Sector, self)._write__seq(io)
            self.header._write__seq(self._io)
            self._io.write_bytes(self.body)


        def _check(self):
            pass
            if self.header._root != self._root:
                raise kaitaistruct.ConsistencyError(u"header", self.header._root, self._root)
            if self.header._parent != self:
                raise kaitaistruct.ConsistencyError(u"header", self.header._parent, self)
            if (len(self.body) != 4084):
                raise kaitaistruct.ConsistencyError(u"body", len(self.body), 4084)


    class SectorHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.timestamp = self._io.read_u4le()
            self.check_sum = self._io.read_u4le()
            self.serial_number = self._io.read_u2le()
            self.payload_offset = self._io.read_u1()
            self.flags = self._io.read_bytes(1)


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(LogFile.SectorHeader, self)._write__seq(io)
            self._io.write_u4le(self.timestamp)
            self._io.write_u4le(self.check_sum)
            self._io.write_u2le(self.serial_number)
            self._io.write_u1(self.payload_offset)
            self._io.write_bytes(self.flags)


        def _check(self):
            pass
            if (len(self.flags) != 1):
                raise kaitaistruct.ConsistencyError(u"flags", len(self.flags), 1)

        @property
        def bad(self):
            if hasattr(self, '_m_bad'):
                return self._m_bad

            self._m_bad = (self.timestamp == 0)
            return getattr(self, '_m_bad', None)

        def _invalidate_bad(self):
            del self._m_bad
        @property
        def empty(self):
            if hasattr(self, '_m_empty'):
                return self._m_empty

            self._m_empty = (self.timestamp == 4294967295)
            return getattr(self, '_m_empty', None)

        def _invalidate_empty(self):
            del self._m_empty


