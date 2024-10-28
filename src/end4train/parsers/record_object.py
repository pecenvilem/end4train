# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class RecordObject(ReadWriteKaitaiStruct):

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

    class BrakePositionEnum(IntEnum):
        bse_apply = 0
        bse_error = 1
        bse_emergency = 2
        bse_transition = 3
        bse_hold = 4
        bse_release = 5
        bse_cut_off = 6
        bse_overcharge = 7
        bse_fast_charge = 8
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

    def _read(self):
        self.object_type = KaitaiStream.resolve_enum(RecordObject.ObjectTypeEnum, self._io.read_bits_int_le(7))
        self.stop_flag = self._io.read_bits_int_le(1) != 0
        _on = self.object_type
        if _on == RecordObject.ObjectTypeEnum.pressure_current_hot:
            pass
            self.object = RecordObject.PressureTuple(self._io, self, self._root)
            self.object._read()
        elif _on == RecordObject.ObjectTypeEnum.pressure_history_eot:
            pass
            self.object = RecordObject.PressureArray(self._io, self, self._root)
            self.object._read()
        elif _on == RecordObject.ObjectTypeEnum.gps_eot:
            pass
            self.object = RecordObject.Gps(self._io, self, self._root)
            self.object._read()
        elif _on == RecordObject.ObjectTypeEnum.hot_temp:
            pass
            self.object = RecordObject.Temperature(self._io, self, self._root)
            self.object._read()
        elif _on == RecordObject.ObjectTypeEnum.gps_hot:
            pass
            self.object = RecordObject.Gps(self._io, self, self._root)
            self.object._read()
        elif _on == RecordObject.ObjectTypeEnum.eot_temp:
            pass
            self.object = RecordObject.EotPower(self._io, self, self._root)
            self.object._read()
        elif _on == RecordObject.ObjectTypeEnum.fault_hot:
            pass
            self.object = RecordObject.Fault(self._io, self, self._root)
            self.object._read()
        elif _on == RecordObject.ObjectTypeEnum.fault_eot:
            pass
            self.object = RecordObject.Fault(self._io, self, self._root)
            self.object._read()
        elif _on == RecordObject.ObjectTypeEnum.pressure_current_eot:
            pass
            self.object = RecordObject.PressureTuple(self._io, self, self._root)
            self.object._read()
        elif _on == RecordObject.ObjectTypeEnum.brake:
            pass
            self.object = RecordObject.BrakeArray(self._io, self, self._root)
            self.object._read()
        elif _on == RecordObject.ObjectTypeEnum.dict_version:
            pass
            self.object = RecordObject.DictionaryVersion(self._io, self, self._root)
            self.object._read()
        elif _on == RecordObject.ObjectTypeEnum.pressure_history_hot:
            pass
            self.object = RecordObject.PressureArray(self._io, self, self._root)
            self.object._read()


    def _fetch_instances(self):
        pass
        _on = self.object_type
        if _on == RecordObject.ObjectTypeEnum.pressure_current_hot:
            pass
            self.object._fetch_instances()
        elif _on == RecordObject.ObjectTypeEnum.pressure_history_eot:
            pass
            self.object._fetch_instances()
        elif _on == RecordObject.ObjectTypeEnum.gps_eot:
            pass
            self.object._fetch_instances()
        elif _on == RecordObject.ObjectTypeEnum.hot_temp:
            pass
            self.object._fetch_instances()
        elif _on == RecordObject.ObjectTypeEnum.gps_hot:
            pass
            self.object._fetch_instances()
        elif _on == RecordObject.ObjectTypeEnum.eot_temp:
            pass
            self.object._fetch_instances()
        elif _on == RecordObject.ObjectTypeEnum.fault_hot:
            pass
            self.object._fetch_instances()
        elif _on == RecordObject.ObjectTypeEnum.fault_eot:
            pass
            self.object._fetch_instances()
        elif _on == RecordObject.ObjectTypeEnum.pressure_current_eot:
            pass
            self.object._fetch_instances()
        elif _on == RecordObject.ObjectTypeEnum.brake:
            pass
            self.object._fetch_instances()
        elif _on == RecordObject.ObjectTypeEnum.dict_version:
            pass
            self.object._fetch_instances()
        elif _on == RecordObject.ObjectTypeEnum.pressure_history_hot:
            pass
            self.object._fetch_instances()


    def _write__seq(self, io=None):
        super(RecordObject, self)._write__seq(io)
        self._io.write_bits_int_le(7, int(self.object_type))
        self._io.write_bits_int_le(1, int(self.stop_flag))
        _on = self.object_type
        if _on == RecordObject.ObjectTypeEnum.pressure_current_hot:
            pass
            self.object._write__seq(self._io)
        elif _on == RecordObject.ObjectTypeEnum.pressure_history_eot:
            pass
            self.object._write__seq(self._io)
        elif _on == RecordObject.ObjectTypeEnum.gps_eot:
            pass
            self.object._write__seq(self._io)
        elif _on == RecordObject.ObjectTypeEnum.hot_temp:
            pass
            self.object._write__seq(self._io)
        elif _on == RecordObject.ObjectTypeEnum.gps_hot:
            pass
            self.object._write__seq(self._io)
        elif _on == RecordObject.ObjectTypeEnum.eot_temp:
            pass
            self.object._write__seq(self._io)
        elif _on == RecordObject.ObjectTypeEnum.fault_hot:
            pass
            self.object._write__seq(self._io)
        elif _on == RecordObject.ObjectTypeEnum.fault_eot:
            pass
            self.object._write__seq(self._io)
        elif _on == RecordObject.ObjectTypeEnum.pressure_current_eot:
            pass
            self.object._write__seq(self._io)
        elif _on == RecordObject.ObjectTypeEnum.brake:
            pass
            self.object._write__seq(self._io)
        elif _on == RecordObject.ObjectTypeEnum.dict_version:
            pass
            self.object._write__seq(self._io)
        elif _on == RecordObject.ObjectTypeEnum.pressure_history_hot:
            pass
            self.object._write__seq(self._io)


    def _check(self):
        pass
        _on = self.object_type
        if _on == RecordObject.ObjectTypeEnum.pressure_current_hot:
            pass
            if self.object._root != self._root:
                raise kaitaistruct.ConsistencyError(u"object", self.object._root, self._root)
            if self.object._parent != self:
                raise kaitaistruct.ConsistencyError(u"object", self.object._parent, self)
        elif _on == RecordObject.ObjectTypeEnum.pressure_history_eot:
            pass
            if self.object._root != self._root:
                raise kaitaistruct.ConsistencyError(u"object", self.object._root, self._root)
            if self.object._parent != self:
                raise kaitaistruct.ConsistencyError(u"object", self.object._parent, self)
        elif _on == RecordObject.ObjectTypeEnum.gps_eot:
            pass
            if self.object._root != self._root:
                raise kaitaistruct.ConsistencyError(u"object", self.object._root, self._root)
            if self.object._parent != self:
                raise kaitaistruct.ConsistencyError(u"object", self.object._parent, self)
        elif _on == RecordObject.ObjectTypeEnum.hot_temp:
            pass
            if self.object._root != self._root:
                raise kaitaistruct.ConsistencyError(u"object", self.object._root, self._root)
            if self.object._parent != self:
                raise kaitaistruct.ConsistencyError(u"object", self.object._parent, self)
        elif _on == RecordObject.ObjectTypeEnum.gps_hot:
            pass
            if self.object._root != self._root:
                raise kaitaistruct.ConsistencyError(u"object", self.object._root, self._root)
            if self.object._parent != self:
                raise kaitaistruct.ConsistencyError(u"object", self.object._parent, self)
        elif _on == RecordObject.ObjectTypeEnum.eot_temp:
            pass
            if self.object._root != self._root:
                raise kaitaistruct.ConsistencyError(u"object", self.object._root, self._root)
            if self.object._parent != self:
                raise kaitaistruct.ConsistencyError(u"object", self.object._parent, self)
        elif _on == RecordObject.ObjectTypeEnum.fault_hot:
            pass
            if self.object._root != self._root:
                raise kaitaistruct.ConsistencyError(u"object", self.object._root, self._root)
            if self.object._parent != self:
                raise kaitaistruct.ConsistencyError(u"object", self.object._parent, self)
        elif _on == RecordObject.ObjectTypeEnum.fault_eot:
            pass
            if self.object._root != self._root:
                raise kaitaistruct.ConsistencyError(u"object", self.object._root, self._root)
            if self.object._parent != self:
                raise kaitaistruct.ConsistencyError(u"object", self.object._parent, self)
        elif _on == RecordObject.ObjectTypeEnum.pressure_current_eot:
            pass
            if self.object._root != self._root:
                raise kaitaistruct.ConsistencyError(u"object", self.object._root, self._root)
            if self.object._parent != self:
                raise kaitaistruct.ConsistencyError(u"object", self.object._parent, self)
        elif _on == RecordObject.ObjectTypeEnum.brake:
            pass
            if self.object._root != self._root:
                raise kaitaistruct.ConsistencyError(u"object", self.object._root, self._root)
            if self.object._parent != self:
                raise kaitaistruct.ConsistencyError(u"object", self.object._parent, self)
        elif _on == RecordObject.ObjectTypeEnum.dict_version:
            pass
            if self.object._root != self._root:
                raise kaitaistruct.ConsistencyError(u"object", self.object._root, self._root)
            if self.object._parent != self:
                raise kaitaistruct.ConsistencyError(u"object", self.object._parent, self)
        elif _on == RecordObject.ObjectTypeEnum.pressure_history_hot:
            pass
            if self.object._root != self._root:
                raise kaitaistruct.ConsistencyError(u"object", self.object._root, self._root)
            if self.object._parent != self:
                raise kaitaistruct.ConsistencyError(u"object", self.object._parent, self)

    class PressureArray(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.pressure_a_record = []
            for i in range(10):
                _t_pressure_a_record = RecordObject.PressureArrayField(self._io, self, self._root)
                _t_pressure_a_record._read()
                self.pressure_a_record.append(_t_pressure_a_record)



        def _fetch_instances(self):
            pass
            for i in range(len(self.pressure_a_record)):
                pass
                self.pressure_a_record[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(RecordObject.PressureArray, self)._write__seq(io)
            for i in range(len(self.pressure_a_record)):
                pass
                self.pressure_a_record[i]._write__seq(self._io)



        def _check(self):
            pass
            if (len(self.pressure_a_record) != 10):
                raise kaitaistruct.ConsistencyError(u"pressure_a_record", len(self.pressure_a_record), 10)
            for i in range(len(self.pressure_a_record)):
                pass
                if self.pressure_a_record[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"pressure_a_record", self.pressure_a_record[i]._root, self._root)
                if self.pressure_a_record[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"pressure_a_record", self.pressure_a_record[i]._parent, self)



    class PressureArrayField(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.pressure_a_raw = self._io.read_bits_int_le(10)


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(RecordObject.PressureArrayField, self)._write__seq(io)
            self._io.write_bits_int_le(10, self.pressure_a_raw)


        def _check(self):
            pass

        @property
        def pressure_a(self):
            if hasattr(self, '_m_pressure_a'):
                return self._m_pressure_a

            self._m_pressure_a = (self.pressure_a_raw * 0.008)
            return getattr(self, '_m_pressure_a', None)

        def _invalidate_pressure_a(self):
            del self._m_pressure_a

    class Gps(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.north_raw = self._io.read_bits_int_le(28)
            self.east_raw = self._io.read_bits_int_le(28)
            self.alt_raw = self._io.read_bits_int_le(14)
            self.speed_raw = self._io.read_bits_int_le(12)
            self.azimuth_raw = self._io.read_bits_int_le(12)


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(RecordObject.Gps, self)._write__seq(io)
            self._io.write_bits_int_le(28, self.north_raw)
            self._io.write_bits_int_le(28, self.east_raw)
            self._io.write_bits_int_le(14, self.alt_raw)
            self._io.write_bits_int_le(12, self.speed_raw)
            self._io.write_bits_int_le(12, self.azimuth_raw)


        def _check(self):
            pass

        @property
        def east(self):
            """degrees, negative -> west."""
            if hasattr(self, '_m_east'):
                return self._m_east

            self._m_east = ((self.east_raw * 0.0001) / 60)
            return getattr(self, '_m_east', None)

        def _invalidate_east(self):
            del self._m_east
        @property
        def alt(self):
            """meters AMSL."""
            if hasattr(self, '_m_alt'):
                return self._m_alt

            self._m_alt = (self.alt_raw * 0.1)
            return getattr(self, '_m_alt', None)

        def _invalidate_alt(self):
            del self._m_alt
        @property
        def north(self):
            """degrees, negative -> south."""
            if hasattr(self, '_m_north'):
                return self._m_north

            self._m_north = ((self.north_raw * 0.0001) / 60)
            return getattr(self, '_m_north', None)

        def _invalidate_north(self):
            del self._m_north
        @property
        def azimuth(self):
            """degrees, 409,5 -> UNKNOWN."""
            if hasattr(self, '_m_azimuth'):
                return self._m_azimuth

            self._m_azimuth = (self.azimuth_raw * 0.1)
            return getattr(self, '_m_azimuth', None)

        def _invalidate_azimuth(self):
            del self._m_azimuth
        @property
        def speed(self):
            """km/h."""
            if hasattr(self, '_m_speed'):
                return self._m_speed

            self._m_speed = (self.speed_raw * 0.1)
            return getattr(self, '_m_speed', None)

        def _invalidate_speed(self):
            del self._m_speed

    class Temperature(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.temp_raw = self._io.read_bits_int_le(8)


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(RecordObject.Temperature, self)._write__seq(io)
            self._io.write_bits_int_le(8, self.temp_raw)


        def _check(self):
            pass

        @property
        def temp(self):
            if hasattr(self, '_m_temp'):
                return self._m_temp

            self._m_temp = self.temp_raw
            return getattr(self, '_m_temp', None)

        def _invalidate_temp(self):
            del self._m_temp

    class BrakeArray(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.brake_record = []
            for i in range(10):
                self.brake_record.append(KaitaiStream.resolve_enum(RecordObject.BrakePositionEnum, self._io.read_bits_int_le(4)))



        def _fetch_instances(self):
            pass
            for i in range(len(self.brake_record)):
                pass



        def _write__seq(self, io=None):
            super(RecordObject.BrakeArray, self)._write__seq(io)
            for i in range(len(self.brake_record)):
                pass
                self._io.write_bits_int_le(4, int(self.brake_record[i]))



        def _check(self):
            pass
            if (len(self.brake_record) != 10):
                raise kaitaistruct.ConsistencyError(u"brake_record", len(self.brake_record), 10)
            for i in range(len(self.brake_record)):
                pass



    class Fault(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.fault_rxmac = self._io.read_bits_int_le(1) != 0
            self.fault_nogps = self._io.read_bits_int_le(1) != 0
            self.fault_vref = self._io.read_bits_int_le(1) != 0
            self.fault_vcc = self._io.read_bits_int_le(1) != 0
            self.fault_24v = self._io.read_bits_int_le(1) != 0
            self.fault_hotprs = self._io.read_bits_int_le(1) != 0
            self.fault_accel = self._io.read_bits_int_le(1) != 0
            self.fault_batt = self._io.read_bits_int_le(1) != 0
            self.fault_dict_mismatch = self._io.read_bits_int_le(1) != 0
            self.fault_lm75 = self._io.read_bits_int_le(1) != 0
            self.fault_btemp = self._io.read_bits_int_le(1) != 0
            self._unnamed11 = self._io.read_bits_int_le(17)
            self.fault_flash = self._io.read_bits_int_le(1) != 0
            self.fault_logger = self._io.read_bits_int_le(1) != 0
            self.fault_objbuf = self._io.read_bits_int_le(1) != 0
            self.fault_txbuf = self._io.read_bits_int_le(1) != 0


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(RecordObject.Fault, self)._write__seq(io)
            self._io.write_bits_int_le(1, int(self.fault_rxmac))
            self._io.write_bits_int_le(1, int(self.fault_nogps))
            self._io.write_bits_int_le(1, int(self.fault_vref))
            self._io.write_bits_int_le(1, int(self.fault_vcc))
            self._io.write_bits_int_le(1, int(self.fault_24v))
            self._io.write_bits_int_le(1, int(self.fault_hotprs))
            self._io.write_bits_int_le(1, int(self.fault_accel))
            self._io.write_bits_int_le(1, int(self.fault_batt))
            self._io.write_bits_int_le(1, int(self.fault_dict_mismatch))
            self._io.write_bits_int_le(1, int(self.fault_lm75))
            self._io.write_bits_int_le(1, int(self.fault_btemp))
            self._io.write_bits_int_le(17, self._unnamed11)
            self._io.write_bits_int_le(1, int(self.fault_flash))
            self._io.write_bits_int_le(1, int(self.fault_logger))
            self._io.write_bits_int_le(1, int(self.fault_objbuf))
            self._io.write_bits_int_le(1, int(self.fault_txbuf))


        def _check(self):
            pass


    class DictionaryVersion(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.version = self._io.read_bits_int_le(8)


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(RecordObject.DictionaryVersion, self)._write__seq(io)
            self._io.write_bits_int_le(8, self.version)


        def _check(self):
            pass


    class PressureTuple(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.pressure_a_raw = self._io.read_bits_int_le(12)
            self.pressure_b_raw = self._io.read_bits_int_le(12)


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(RecordObject.PressureTuple, self)._write__seq(io)
            self._io.write_bits_int_le(12, self.pressure_a_raw)
            self._io.write_bits_int_le(12, self.pressure_b_raw)


        def _check(self):
            pass

        @property
        def pressure_a(self):
            if hasattr(self, '_m_pressure_a'):
                return self._m_pressure_a

            self._m_pressure_a = (self.pressure_a_raw * 0.002)
            return getattr(self, '_m_pressure_a', None)

        def _invalidate_pressure_a(self):
            del self._m_pressure_a
        @property
        def pressure_b(self):
            if hasattr(self, '_m_pressure_b'):
                return self._m_pressure_b

            self._m_pressure_b = (self.pressure_b_raw * 0.002)
            return getattr(self, '_m_pressure_b', None)

        def _invalidate_pressure_b(self):
            del self._m_pressure_b

    class EotPower(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.temp_raw = self._io.read_bits_int_le(8)
            self.soc = self._io.read_bits_int_le(8)
            self.battery_voltage_raw = self._io.read_bits_int_le(12)
            self.turbine_run = self._io.read_bits_int_le(1) != 0
            self.x1_voltage_high = self._io.read_bits_int_le(1) != 0
            self.battery_full = self._io.read_bits_int_le(1) != 0
            self.radio_high_power = self._io.read_bits_int_le(1) != 0
            self.balancer_burn_raw = self._io.read_bits_int_le(16)
            self.turbine_run_time = self._io.read_bits_int_le(16)


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(RecordObject.EotPower, self)._write__seq(io)
            self._io.write_bits_int_le(8, self.temp_raw)
            self._io.write_bits_int_le(8, self.soc)
            self._io.write_bits_int_le(12, self.battery_voltage_raw)
            self._io.write_bits_int_le(1, int(self.turbine_run))
            self._io.write_bits_int_le(1, int(self.x1_voltage_high))
            self._io.write_bits_int_le(1, int(self.battery_full))
            self._io.write_bits_int_le(1, int(self.radio_high_power))
            self._io.write_bits_int_le(16, self.balancer_burn_raw)
            self._io.write_bits_int_le(16, self.turbine_run_time)


        def _check(self):
            pass

        @property
        def temp(self):
            """degrees celsius."""
            if hasattr(self, '_m_temp'):
                return self._m_temp

            self._m_temp = self.temp_raw
            return getattr(self, '_m_temp', None)

        def _invalidate_temp(self):
            del self._m_temp
        @property
        def battery_voltage(self):
            """volts."""
            if hasattr(self, '_m_battery_voltage'):
                return self._m_battery_voltage

            self._m_battery_voltage = (self.battery_voltage_raw / 100)
            return getattr(self, '_m_battery_voltage', None)

        def _invalidate_battery_voltage(self):
            del self._m_battery_voltage
        @property
        def balancer_burn(self):
            """mAh."""
            if hasattr(self, '_m_balancer_burn'):
                return self._m_balancer_burn

            self._m_balancer_burn = (self.balancer_burn_raw * 0.45)
            return getattr(self, '_m_balancer_burn', None)

        def _invalidate_balancer_burn(self):
            del self._m_balancer_burn


