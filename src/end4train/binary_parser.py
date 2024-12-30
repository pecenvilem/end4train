# TODO: replace this module using dynamic parsing

import zlib
from enum import Enum, auto, StrEnum
from typing import Iterator, Tuple, Any

import pandas as pd

from operator import attrgetter

from end4train.communication.parsers.log_file import LogFile
from end4train.communication.parsers.p_packet import PPacket
from end4train.communication.parsers.record_object import RecordObject
from end4train.communication.parsers.process_data import ProcessData
from end4train.communication.parsers.record_array import RecordArray


class DataSource(Enum):
    LOG_FILE = auto()
    P_PACKET = auto()


class SourceDevice(StrEnum):
    HOT = auto()
    EOT = auto()
    UNDEFINED = ""


SOURCE_DEVICES = {
    RecordObject.ObjectTypeEnum.dict_version: SourceDevice.UNDEFINED,
    RecordObject.ObjectTypeEnum.pressure_current_eot: SourceDevice.EOT,
    RecordObject.ObjectTypeEnum.pressure_current_hot: SourceDevice.HOT,
    RecordObject.ObjectTypeEnum.pressure_history_eot: SourceDevice.EOT,
    RecordObject.ObjectTypeEnum.pressure_history_hot: SourceDevice.HOT,
    RecordObject.ObjectTypeEnum.gps_eot: SourceDevice.EOT,
    RecordObject.ObjectTypeEnum.gps_hot: SourceDevice.HOT,
    RecordObject.ObjectTypeEnum.fault_eot: SourceDevice.EOT,
    RecordObject.ObjectTypeEnum.fault_hot: SourceDevice.HOT,
    RecordObject.ObjectTypeEnum.temp_eot: SourceDevice.EOT,
    RecordObject.ObjectTypeEnum.temp_hot: SourceDevice.HOT,
    RecordObject.ObjectTypeEnum.brake_hot: SourceDevice.HOT,
}

DATA_EXTRACTORS = {
    RecordObject.DictionaryVersion: {
        "version": attrgetter("version"),
    },
    RecordObject.PressureTuple: {
        "pressure_a": attrgetter("pressure_a"),
        "pressure_b": attrgetter("pressure_b"),
    },
    RecordObject.PressureArray: {
        "pressure_a": lambda data_object: [record.pressure_a for record in data_object.pressure_a_record],
    },
    RecordObject.Gps: {
        "north": attrgetter("north"),
        "east": attrgetter("east"),
        "alt": attrgetter("alt"),
        "azimuth": attrgetter("azimuth"),
        "speed": attrgetter("speed"),
    },
    RecordObject.Fault: {
        "fault_rxmac": attrgetter("fault_rxmac"),
        "fault_nogps": attrgetter("fault_nogps"),
        "fault_vref": attrgetter("fault_vref"),
        "fault_vcc": attrgetter("fault_vcc"),
        "fault_24v": attrgetter("fault_24v"),
        "fault_hotprs": attrgetter("fault_hotprs"),
        "fault_accel": attrgetter("fault_accel"),
        "fault_batt": attrgetter("fault_batt"),
        "fault_dict_mismatch": attrgetter("fault_dict_mismatch"),
        "fault_lm75": attrgetter("fault_lm75"),
        "fault_btemp": attrgetter("fault_btemp"),
        "fault_flash": attrgetter("fault_flash"),
        "fault_logger": attrgetter("fault_logger"),
        "fault_objbuf": attrgetter("fault_objbuf"),
        "fault_txbuf": attrgetter("fault_txbuf"),
    },
    RecordObject.EotPower: {
        "temp": attrgetter("temp"),
        "soc": attrgetter("soc"),
        "battery_voltage": attrgetter("battery_voltage"),
        "turbine_run": attrgetter("turbine_run"),
        "x1_voltage_high": attrgetter("x1_voltage_high"),
        "battery_full": attrgetter("battery_full"),
        "radio_high_power": attrgetter("radio_high_power"),
        "balancer_burn": attrgetter("balancer_burn"),
        "turbine_run_time": attrgetter("turbine_run_time"),
    },
    RecordObject.Temperature: {
        "temp": attrgetter("temp"),
    },
    RecordObject.BrakePositionArray: {
        "brake": lambda data_object: [record.name for record in data_object.brake_record],
    },
}


def get_records_from_log_file(stream: bytes) -> list:

    return []


def get_process_data_from_p_packet(stream: bytes) -> Iterator[Tuple[float, ProcessData]]:
    packet = PPacket.from_bytes(stream)
    return ((packet.epoch_number, packet.body) for _ in range(1))


def filter_records(records: list, record_type: RecordArray.RecordType):
    return list([
        record for record in records if record.rec_type == record_type
    ])


def get_texts_from_records(records: list) -> pd.DataFrame:
    text_records = filter_records(records, RecordArray.RecordType.text)
    timestamps = [record.time_of_record + record.text.milliseconds / 1000 for record in text_records]
    texts = [record.text.text for record in text_records]
    return pd.DataFrame({"time": pd.to_datetime(timestamps, unit="s"), "text": texts}).sort_index()


def get_data_from_process_data(process_data: Iterator[Tuple[float, ProcessData]]) -> pd.DataFrame:
    data = {}
    for (timestamp, process_data_object) in process_data:
        for record_object in process_data_object.records:
            extractor = DATA_EXTRACTORS[type(record_object.object)]
            device = SOURCE_DEVICES[record_object.object_type]
            if device:
                extracted = {"_".join([device, key]): f(record_object.object) for key, f in extractor.items()}
            else:
                extracted = {key: f(record_object.object) for key, f in extractor.items()}
            if type(record_object.object) in [RecordObject.PressureArray, RecordObject.BrakeArray]:
                timestamps = [timestamp - 0.95 + i * 0.1 for i in range(10)]
                for key, value in extracted.items():
                    try:
                        data[key].extend(zip(timestamps, value))
                    except KeyError:
                        data[key] = list(zip(timestamps, value))
            else:
                for key, value in extracted.items():
                    try:
                        data[key].append((timestamp, value))
                    except KeyError:
                        data[key] = [(timestamp, value)]
    columns = []
    for column_name, values in data.items():
        column = pd.DataFrame(values, columns=["time", column_name])
        column = column.set_index("time", drop=True)
        column = column[~column.index.duplicated(keep="last")]
        columns.append(column)
    data = pd.concat(columns, axis="columns")
    data.index = pd.to_datetime(data.index, unit="s")
    return data.sort_index()


def get_process_data_from_records(records: list) -> Iterator[Tuple[float, ProcessData]]:
    data_records = filter_records(records, RecordArray.RecordType.data)
    return ((record.time_of_record, record.data.data) for record in data_records)


def parse_p_packet(stream: bytes) -> pd.DataFrame:
    proces_data = get_process_data_from_p_packet(stream)
    return pd.DataFrame()


def parse_log(stream: bytes) -> pd.DataFrame:
    records = get_records_from_log_file(stream)
    process_data = get_process_data_from_records(records)
    return get_data_from_process_data(process_data)


def record_objects_to_list_of_series(record_objects: list[RecordArray.Record]) -> list[pd.Series]:
    data = []
    for record_object in record_objects:
        if record_object.rec_type == RecordArray.RecordType.data:
            data_dict = {}
            for record in record_object.data.data.records:
                for key, value in vars(record.object).items():
                    if key.startswith("_"):
                        continue
                    if "raw" in key:
                        continue
                    if isinstance(value, list):
                        continue
                    data_dict[key] = value
                data.append(pd.Series(data=data_dict, name=record_object.time_of_record))
    return data
