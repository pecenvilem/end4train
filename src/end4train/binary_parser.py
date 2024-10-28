import zlib
from enum import Enum, auto
from typing import Iterator, Tuple

import pandas as pd

from operator import attrgetter

from end4train.parsers.log_file import LogFile
from end4train.parsers.p_packet import PPacket
from end4train.parsers.record_object import RecordObject
from end4train.parsers.process_data import ProcessData


class DataSource(Enum):
    LOG_FILE = auto()
    P_PACKET = auto()


SOURCE_DEVICES = {
    RecordObject.ObjectTypeEnum.dict_version: "",
    RecordObject.ObjectTypeEnum.pressure_current_eot: "eot",
    RecordObject.ObjectTypeEnum.pressure_current_hot: "hot",
    RecordObject.ObjectTypeEnum.pressure_history_eot: "eot",
    RecordObject.ObjectTypeEnum.pressure_history_hot: "hot",
    RecordObject.ObjectTypeEnum.gps_eot: "eot",
    RecordObject.ObjectTypeEnum.gps_hot: "hot",
    RecordObject.ObjectTypeEnum.fault_eot: "eot",
    RecordObject.ObjectTypeEnum.fault_hot: "hot",
    RecordObject.ObjectTypeEnum.eot_temp: "eot",
    RecordObject.ObjectTypeEnum.hot_temp: "hot",
    RecordObject.ObjectTypeEnum.brake: "hot",
}

def get_variable_names(record_object: RecordObject) -> list[str]:
    """

    :param record_object:
    :return:
    """
    variable_names = []
    for attr_name in dir(record_object):
        if attr_name.startswith("_"):
            continue
        if "raw" in attr_name:
            continue
    return variable_names

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
    RecordObject.BrakeArray: {
        "brake": lambda data_object: [record.name for record in data_object.brake_record],
    },
}


def get_records_from_log_file(stream: bytes) -> list:
    log_file = LogFile.from_bytes(stream)
    log_file._read()

    for sector in log_file.sectors.copy():
        if zlib.adler32(sector.previous_sector_data + sector._raw_records, 0) != sector.header.check_sum:
            log_file.sectors.remove(sector)

    records = [record for sector in log_file.sectors for record in sector.records.records]

    # TODO: modify log_file.ksy to only leave the last record in the "unprocessed data", don't use the magic number 51

    for sector, next_sector in zip(log_file.sectors[:-1], log_file.sectors[1:]):
        if sector.header.serial_number + 1 != next_sector.header.serial_number:
            continue
        data = sector.records.next_sector_data + next_sector.previous_sector_data
        record_array = LogFile.RecordArray.from_bytes(data)
        record_array._read()
        records.extend(record_array.records)

    return records


def get_process_data_from_p_packet(stream: bytes) -> Iterator[Tuple[float, ProcessData]]:
    packet = PPacket.from_bytes(stream)
    return ((packet.epoch_number, packet.body) for _ in range(1))


def filter_records(records: list, record_type: LogFile.RecordType):
    return list([
        record for record in records if record.rec_type == record_type
    ])


def get_texts_from_records(records: list) -> pd.DataFrame:
    text_records = filter_records(records, LogFile.RecordType.text)
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
    data_records = filter_records(records, LogFile.RecordType.data)
    return ((record.time_of_record, record.data.data) for record in data_records)


def parse_p_packet(stream: bytes) -> pd.DataFrame:
    proces_data = get_process_data_from_p_packet(stream)
    return pd.DataFrame()


def parse_log(stream: bytes) -> pd.DataFrame:
    records = get_records_from_log_file(stream)
    process_data = get_process_data_from_records(records)
    return get_data_from_process_data(process_data)


def record_objects_to_list_of_series(record_objects: list[LogFile.Record]) -> list[pd.Series]:
    data = []
    for record_object in record_objects:
        if record_object.rec_type == LogFile.RecordType.data:
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
