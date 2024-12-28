# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

from end4train.communication.parsers import record_object
class ProcessData(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

    def _read(self):
        self.records = []
        i = 0
        while True:
            _t_records = record_object.RecordObject(self._io)
            _t_records._read()
            _ = _t_records
            self.records.append(_)
            if _.stop_flag:
                break
            i += 1


    def _fetch_instances(self):
        pass
        for i in range(len(self.records)):
            pass
            self.records[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(ProcessData, self)._write__seq(io)
        for i in range(len(self.records)):
            pass
            self.records[i]._write__seq(self._io)



    def _check(self):
        pass
        if (len(self.records) == 0):
            raise kaitaistruct.ConsistencyError(u"records", len(self.records), 0)
        for i in range(len(self.records)):
            pass
            _ = self.records[i]
            if (_.stop_flag != (i == (len(self.records) - 1))):
                raise kaitaistruct.ConsistencyError(u"records", _.stop_flag, (i == (len(self.records) - 1)))



