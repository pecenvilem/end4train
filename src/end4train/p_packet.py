# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class PPacket(KaitaiStruct):

    class ObjectTypeEnum(Enum):
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

    class BrakePositionEnum(Enum):
        bse_apply = 0
        bse_error = 1
        bse_emergency = 2
        bse_transition = 3
        bse_hold = 4
        bse_release = 5
        bse_cut_off = 6
        bse_overcharge = 7
        bse_fast_charge = 8
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.packet_type = self._io.read_bytes(1)
        if not self.packet_type == b"\x50":
            raise kaitaistruct.ValidationNotEqualError(b"\x50", self.packet_type, self._io, u"/seq/0")
        self.epoch_number = self._io.read_bits_int_le(32)
        self._io.align_to_byte()
        self.time = PPacket.EpochTime(self._io, self, self._root)
        self.body = PPacket.ProcessData(self._io, self, self._root)

    class PressureArray(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pressure_a_record = []
            for i in range(10):
                self.pressure_a_record.append(PPacket.PressureArrayField(self._io, self, self._root))



    class PressureArrayField(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pressure_a_raw = self._io.read_bits_int_le(10)

        @property
        def pressure_a(self):
            if hasattr(self, '_m_pressure_a'):
                return self._m_pressure_a

            self._m_pressure_a = (self.pressure_a_raw * 0.008)
            return getattr(self, '_m_pressure_a', None)


    class Gps(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.north_raw = self._io.read_bits_int_le(28)
            self.east_raw = self._io.read_bits_int_le(28)
            self.alt_raw = self._io.read_bits_int_le(14)
            self.speed_raw = self._io.read_bits_int_le(12)
            self.azimuth_raw = self._io.read_bits_int_le(12)

        @property
        def east(self):
            """degrees, negative -> west."""
            if hasattr(self, '_m_east'):
                return self._m_east

            self._m_east = ((self.east_raw * 0.0001) / 60)
            return getattr(self, '_m_east', None)

        @property
        def alt(self):
            """meters AMSL."""
            if hasattr(self, '_m_alt'):
                return self._m_alt

            self._m_alt = (self.alt_raw * 0.1)
            return getattr(self, '_m_alt', None)

        @property
        def north(self):
            """degrees, negative -> south."""
            if hasattr(self, '_m_north'):
                return self._m_north

            self._m_north = ((self.north_raw * 0.0001) / 60)
            return getattr(self, '_m_north', None)

        @property
        def azimuth(self):
            """degrees, 409,5 -> UNKNOWN."""
            if hasattr(self, '_m_azimuth'):
                return self._m_azimuth

            self._m_azimuth = (self.azimuth_raw * 0.1)
            return getattr(self, '_m_azimuth', None)

        @property
        def speed(self):
            """km/h."""
            if hasattr(self, '_m_speed'):
                return self._m_speed

            self._m_speed = (self.speed_raw * 0.1)
            return getattr(self, '_m_speed', None)


    class RecordObject(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.object_type = KaitaiStream.resolve_enum(PPacket.ObjectTypeEnum, self._io.read_bits_int_le(7))
            self.stop_flag = self._io.read_bits_int_le(1) != 0
            # self._io.align_to_byte()
            _on = self.object_type
            if _on == PPacket.ObjectTypeEnum.pressure_current_hot:
                self.object = PPacket.PressureTuple(self._io, self, self._root)
            elif _on == PPacket.ObjectTypeEnum.pressure_history_eot:
                self.object = PPacket.PressureArray(self._io, self, self._root)
            elif _on == PPacket.ObjectTypeEnum.gps_eot:
                self.object = PPacket.Gps(self._io, self, self._root)
            elif _on == PPacket.ObjectTypeEnum.hot_temp:
                self.object = PPacket.Temperature(self._io, self, self._root)
            elif _on == PPacket.ObjectTypeEnum.gps_hot:
                self.object = PPacket.Gps(self._io, self, self._root)
            elif _on == PPacket.ObjectTypeEnum.eot_temp:
                self.object = PPacket.EotPower(self._io, self, self._root)
            elif _on == PPacket.ObjectTypeEnum.fault_hot:
                self.object = PPacket.Fault(self._io, self, self._root)
            elif _on == PPacket.ObjectTypeEnum.fault_eot:
                self.object = PPacket.Fault(self._io, self, self._root)
            elif _on == PPacket.ObjectTypeEnum.pressure_current_eot:
                self.object = PPacket.PressureTuple(self._io, self, self._root)
            elif _on == PPacket.ObjectTypeEnum.brake:
                self.object = PPacket.BrakeArray(self._io, self, self._root)
            elif _on == PPacket.ObjectTypeEnum.dict_version:
                self.object = PPacket.DictionaryVersion(self._io, self, self._root)
            elif _on == PPacket.ObjectTypeEnum.pressure_history_hot:
                self.object = PPacket.PressureArray(self._io, self, self._root)


    class Temperature(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.temp_raw = self._io.read_bits_int_le(8)

        @property
        def temp(self):
            if hasattr(self, '_m_temp'):
                return self._m_temp

            self._m_temp = self.temp_raw
            return getattr(self, '_m_temp', None)


    class EpochTime(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.millisecond = self._io.read_bits_int_le(12)
            self.eot_data = self._io.read_bits_int_le(1) != 0
            self.eot_link_fail = self._io.read_bits_int_le(1) != 0
            self.remote_eot_no_gps_time = self._io.read_bits_int_le(1) != 0
            self.local_no_gps_time = self._io.read_bits_int_le(1) != 0


    class ProcessData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = []
            i = 0
            while True:
                _ = PPacket.RecordObject(self._io, self, self._root)
                self.data.append(_)
                if _.stop_flag == True:
                    break
                i += 1


    class BrakeArray(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.brake_record = []
            for i in range(10):
                self.brake_record.append(KaitaiStream.resolve_enum(PPacket.BrakePositionEnum, self._io.read_bits_int_le(4)))



    class Fault(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

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


    class DictionaryVersion(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version = self._io.read_bits_int_le(8)


    class PressureTuple(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pressure_a_raw = self._io.read_bits_int_le(12)
            self.pressure_b_raw = self._io.read_bits_int_le(12)

        @property
        def pressure_a(self):
            if hasattr(self, '_m_pressure_a'):
                return self._m_pressure_a

            self._m_pressure_a = (self.pressure_a_raw * 0.002)
            return getattr(self, '_m_pressure_a', None)

        @property
        def pressure_b(self):
            if hasattr(self, '_m_pressure_b'):
                return self._m_pressure_b

            self._m_pressure_b = (self.pressure_b_raw * 0.002)
            return getattr(self, '_m_pressure_b', None)


    class EotPower(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.temp_raw = self._io.read_bits_int_le(8)
            self.soc = self._io.read_bits_int_le(8)
            self.battery_voltage_raw = self._io.read_bits_int_le(12)
            self.turbine_run = self._io.read_bits_int_le(1) != 0
            self.x1_voltage_high = self._io.read_bits_int_le(1) != 0
            self._unnamed5 = self._io.read_bits_int_le(1) != 0
            self.battery_full = self._io.read_bits_int_le(1) != 0
            self.balancer_burn_raw = self._io.read_bits_int_le(16)
            self.turbine_run_time = self._io.read_bits_int_le(16)

        @property
        def temp(self):
            """degrees celsius."""
            if hasattr(self, '_m_temp'):
                return self._m_temp

            self._m_temp = self.temp_raw
            return getattr(self, '_m_temp', None)

        @property
        def battery_voltage(self):
            """volts."""
            if hasattr(self, '_m_battery_voltage'):
                return self._m_battery_voltage

            self._m_battery_voltage = (self.battery_voltage_raw / 100)
            return getattr(self, '_m_battery_voltage', None)

        @property
        def balancer_burn(self):
            """mAh."""
            if hasattr(self, '_m_balancer_burn'):
                return self._m_balancer_burn

            self._m_balancer_burn = (self.balancer_burn_raw * 0.45)
            return getattr(self, '_m_balancer_burn', None)
