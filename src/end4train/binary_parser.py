import zlib
from enum import Enum, auto
from typing import Iterator, Tuple

import pandas as pd

from pathlib import Path
from operator import attrgetter

from end4train.log_file import LogFile
from end4train.p_packet import PPacket


class DataSource(Enum):
    LOG_FILE = auto()
    P_PACKET = auto()


SOURCE_DEVICES = {
    PPacket.ObjectTypeEnum.dict_version: "",
    PPacket.ObjectTypeEnum.pressure_current_eot: "eot",
    PPacket.ObjectTypeEnum.pressure_current_hot: "hot",
    PPacket.ObjectTypeEnum.pressure_history_eot: "eot",
    PPacket.ObjectTypeEnum.pressure_history_hot: "hot",
    PPacket.ObjectTypeEnum.gps_eot: "eot",
    PPacket.ObjectTypeEnum.gps_hot: "hot",
    PPacket.ObjectTypeEnum.fault_eot: "eot",
    PPacket.ObjectTypeEnum.fault_hot: "hot",
    PPacket.ObjectTypeEnum.eot_temp: "eot",
    PPacket.ObjectTypeEnum.hot_temp: "hot",
    PPacket.ObjectTypeEnum.brake: "hot",
}

DATA_EXTRACTORS = {
    PPacket.DictionaryVersion: {
        "version": attrgetter("version"),
    },
    PPacket.PressureTuple: {
        "pressure_a": attrgetter("pressure_a"),
        "pressure_b": attrgetter("pressure_b"),
    },
    PPacket.PressureArray: {
        "pressure_a": lambda data_object: [record.pressure_a for record in data_object.pressure_a_record],
    },
    PPacket.Gps: {
        "north": attrgetter("north"),
        "east": attrgetter("east"),
        "alt": attrgetter("alt"),
        "azimuth": attrgetter("azimuth"),
        "speed": attrgetter("speed"),
    },
    PPacket.Fault: {
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
    PPacket.EotPower: {
        "temp": attrgetter("temp"),
        "soc": attrgetter("soc"),
        "battery_voltage": attrgetter("battery_voltage"),
        "turbine_run": attrgetter("turbine_run"),
        "x1_voltage_high": attrgetter("x1_voltage_high"),
        "battery_full": attrgetter("battery_full"),
        "balancer_burn": attrgetter("balancer_burn"),
        "turbine_run_time": attrgetter("turbine_run_time"),
    },
    PPacket.Temperature: {
        "temp": attrgetter("temp"),
    },
    PPacket.BrakeArray: {
        "brake": lambda data_object: [record.name for record in data_object.brake_record],
    },
}


def get_records_from_log_file(stream: bytes) -> list:
    sector_bodies = [stream[i * 4096:(i + 1) * 4096][12:] for i in range(len(stream) // 4096)]
    log_file = LogFile.from_bytes(stream)

    for sector, body in zip(log_file.sectors.copy(), sector_bodies):
        if zlib.adler32(body, 0) != sector.header.check_sum:
            log_file.sectors.remove(sector)

    records = [
        record for sector in log_file.sectors for record in sector.records.records
    ]

    for i, (sector, next_sector) in enumerate(zip(log_file.sectors[:-1], log_file.sectors[1:])):
        if sector.header.serial_number + 1 != next_sector.header.serial_number:
            continue
        data = sector.records.next_sector_data + next_sector.previous_sector_data
        record_array = LogFile.RecordArray.from_bytes(data)
        records.extend(record_array.records)

    return records


def get_process_data_from_p_packet(stream: bytes) -> Iterator[Tuple[float, PPacket.ProcessData]]:
    packet = PPacket.from_bytes(stream)
    return ((packet.epoch_number, packet.body) for _ in range(1))


def filter_records(records: list, record_type: LogFile.RecordType):
    return list([
        record for record in records if record.record_type == record_type
    ])


def get_texts_from_records(records: list) -> pd.DataFrame:
    text_records = filter_records(records, LogFile.RecordType.text)
    timestamps = [record.time_of_record + record.text.milliseconds / 1000 for record in text_records]
    texts = [record.text.text for record in text_records]
    return pd.DataFrame({"time": pd.to_datetime(timestamps, unit="s"), "text": texts}).sort_index()


def get_data_from_process_data(process_data: Iterator[Tuple[float, PPacket.ProcessData]]) -> pd.DataFrame:
    data = {}
    for (timestamp, process_data_object) in process_data:
        for record_object in process_data_object.data:
            extractor = DATA_EXTRACTORS[type(record_object.object)]
            device = SOURCE_DEVICES[record_object.object_type]
            if device:
                extracted = {"_".join([device, key]): f(record_object.object) for key, f in extractor.items()}
            else:
                extracted = {key: f(record_object.object) for key, f in extractor.items()}
            if type(record_object.object) in [PPacket.PressureArray, PPacket.BrakeArray]:
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
        columns.append(column.set_index("time", drop=True))
    data = pd.concat(columns, axis="columns")
    data.index = pd.to_datetime(data.index, unit="s")
    return data.sort_index()


def get_process_data_from_records(records: list) -> Iterator[Tuple[float, PPacket.ProcessData]]:
    data_records = filter_records(records, LogFile.RecordType.data)
    return ((record.time_of_record, record.data.data) for record in data_records)


def parse_p_packet(stream: bytes) -> pd.DataFrame:
    proces_data = get_process_data_from_p_packet(stream)
    return pd.DataFrame()


def parse_log(stream: bytes) -> pd.DataFrame:
    records = get_records_from_log_file(stream)
    texts = get_texts_from_records(records)
    process_data = get_process_data_from_records(records)
    return get_data_from_process_data(process_data)


def main():
    path = Path("../../test/data/logeot2")
    data = parse_log(path.read_bytes())
    print(f"Loaded data from {data.index.min()} to {data.index.max()}, {len(data)} data-points.")


if __name__ == '__main__':
    main()
