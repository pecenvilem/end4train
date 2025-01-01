from __future__ import annotations

from end4train.communication.parsers.record_object import RecordObject


class DictionaryVersion(RecordObject.DictionaryVersion):
    required_bits = 8


class PressureTuple(RecordObject.PressureTuple):
    required_bits = 24

    @RecordObject.PressureTuple.pressure_a.setter
    def pressure_a(self, value: float):
        self.pressure_a_raw = int(value / 0.002)

    @RecordObject.PressureTuple.pressure_b.setter
    def pressure_b(self, value: float):
        self.pressure_b_raw = int(value / 0.002)


class PressureArrayField(RecordObject.PressureArrayField):
    required_bits = 10

    @RecordObject.PressureArrayField.pressure_a.setter
    def pressure_a(self, value: float):
        self.pressure_a_raw = int(value / 0.008)


class PressureArray(RecordObject.PressureArray):
    required_bits = 100


class Gps(RecordObject.Gps):
    required_bits = 94

    @RecordObject.Gps.north.setter
    def north(self, value: float):
        self.north_raw = int(value * 60 / 0.0001)

    @RecordObject.Gps.east.setter
    def east(self, value: float):
        self.east_raw = int(value * 60 / 0.0001)

    @RecordObject.Gps.alt.setter
    def alt(self, value: float):
        self.alt_raw = int(value / 0.1)

    @RecordObject.Gps.speed.setter
    def speed(self, value: float):
        self.speed_raw = int(value / 0.1)

    @RecordObject.Gps.azimuth.setter
    def azimuth(self, value: float):
        self.azimuth_raw = int(value / 0.1)


class Fault(RecordObject.Fault):
    required_bits = 32
    reserved = 0


class EotPower(RecordObject.EotPower):
    required_bits = 64

    @RecordObject.EotPower.temp.setter
    def temp(self, value: int):
        self.temp_raw = value

    @RecordObject.EotPower.battery_voltage.setter
    def battery_voltage(self, value: float):
        self.battery_voltage_raw = int(value * 100)

    @RecordObject.EotPower.balancer_burn.setter
    def balancer_burn(self, value: float):
        self.balancer_burn_raw = int(value / 0.45)


class Temperature(RecordObject.Temperature):
    required_bits = 8

    @RecordObject.Temperature.temp.setter
    def temp(self, value: int):
        self.temp_raw = value


class BrakeArray(RecordObject.BrakePositionArray):
    required_bits = 40
