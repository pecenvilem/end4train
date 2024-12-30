import pandas as pd

from end4train.communication.parsers.p_packet import PPacket
from end4train.communication.parsers.process_data import ProcessData
from end4train.communication.parsers.record_object import RecordObject
from end4train.communication.serializers.basic_packets import create_bytes
from end4train.communication.ksy import get_class_name_for_ksy_type, DATA_VARIABLES_FOR_DATA_OBJECT_TYPE, \
    KSY_TYPE_PER_OBJECT_TYPE


class DictionaryVersion(RecordObject.DictionaryVersion):
    required_bits = 8


# noinspection PyAttributeOutsideInit
class PressureTuple(RecordObject.PressureTuple):
    required_bits = 24

    @RecordObject.PressureTuple.pressure_a.setter
    def pressure_a(self, value: float):
        self.pressure_a_raw = int(value / 0.002)

    @RecordObject.PressureTuple.pressure_b.setter
    def pressure_b(self, value: float):
        self.pressure_b_raw = int(value / 0.002)


# noinspection PyAttributeOutsideInit
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


# noinspection PyAttributeOutsideInit
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


# noinspection PyAttributeOutsideInit
class Temperature(RecordObject.Temperature):
    required_bits = 8

    @RecordObject.Temperature.temp.setter
    def temp(self, value: int):
        self.temp_raw = value


# TODO: fix (using dynamic parsing)
class BrakeArray(RecordObject.BrakePositionArray):
    required_bits = 40

    @property
    def adasd(self):
        return

    @adasd.setter
    def adasd(self, value):
        pass


# noinspection PyProtectedMember
# TODO: rework using dynamic parsing
def serialize_p_packet(
        is_gps_time: bool, is_remote_from_eot: bool, data: pd.DataFrame
) -> bytes:
    data["timestamp"] = data["timestamp"].dt.floor("s")
    if data["timestamp"].nunique() != 1:
        raise ValueError("Not all timestamps are the same! They can't be sent in one P-packet")
    timestamp = data["timestamp"].iloc[0].value // 10**9
    millisecond = 0

    packet = PPacket()
    time_object = PPacket.EpochTime(_parent=packet, _root=packet._root)
    data_object = ProcessData(_parent=packet, _root=packet._root)
    data_object.records = []

    for object_type, subframe in data.groupby("object_type"):
        subframe = subframe.set_index("variable", drop=True)
        if (subframe.groupby("variable")["value"].nunique() > 1).any():
            raise ValueError()
        # TODO: replace import of following two dicts with using some method of KSYInfoStore
        required_variables = DATA_VARIABLES_FOR_DATA_OBJECT_TYPE[object_type]
        cls_name = get_class_name_for_ksy_type(KSY_TYPE_PER_OBJECT_TYPE[object_type])

        cls_to_instantiate = globals()[cls_name]
        record_object = RecordObject(_parent=data_object, _root=data_object._root)
        record_object.object_type = object_type
        record_object.stop_flag = False
        record_object.object = cls_to_instantiate(_parent=record_object, _root=record_object._root)
        for variable in required_variables:
            setattr(record_object.object, variable, data.loc[data["variable"] == variable, "value"].iloc[0])
        record_object.object._check()
        data_object.records.append(record_object)

    data_object.records[-1].stop_flag = True

    time_object.millisecond = millisecond
    time_object.eot_data = is_remote_from_eot
    time_object.eot_link_fail = False
    time_object.remote_eot_no_gps_time = False
    time_object.local_no_gps_time = not is_gps_time
    time_object._check()

    packet.packet_type = b'P'
    packet.epoch_number = timestamp
    packet.time = time_object
    packet.body = data_object

    packet._check()
    return create_bytes(packet, buffer_length=13)
