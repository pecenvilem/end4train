from __future__ import annotations

import zlib
from pathlib import Path
from typing import Type, Any

import pandas as pd

from end4train.communication.constants import EPOCH_DURATION
from end4train.communication.data_store import RecordDataStore
from end4train.communication.ksy import KaitaiType

from end4train.communication.parsers.log_file import LogFile
from end4train.communication.parsers.record_array import RecordArray
from end4train.communication.timestamp_conversion import combine_timestamp, TimestampTuple


def is_sector_checksum_valid(body: bytes | bytearray, check_sum: int) -> bool:
    return zlib.adler32(body, 0) == check_sum


def get_sector_dataframe(log_file: LogFile) -> pd.DataFrame:
    sector_dict = {
        "body": [], "check_sum": [], "corrupted": [], "empty": [], "bad": [], "serial_number": [], "payload_offset": [],
        "timestamp": []
    }
    for sector in log_file.sectors:
        sector_dict["body"].append(sector.body)
        sector_dict["check_sum"].append(sector.header.check_sum)
        sector_dict["corrupted"].append(not is_sector_checksum_valid(sector.body, sector.header.check_sum))
        sector_dict["empty"].append(sector.header.empty)
        sector_dict["bad"].append(sector.header.bad)
        sector_dict["serial_number"].append(sector.header.serial_number)
        sector_dict["payload_offset"].append(sector.header.payload_offset)
        sector_dict["timestamp"].append(sector.header.timestamp)
    sectors = pd.DataFrame(sector_dict)

    sectors["sequence_interrupted"] = (
            (sectors["serial_number"].diff() != 1) | sectors["bad"] | sectors["empty"] | sectors["corrupted"]
    )
    sectors["sequence_id"] = sectors["sequence_interrupted"].cumsum()
    sectors["timestamp"] = pd.to_datetime(sectors["timestamp"], unit="s")
    sectors["inconsistent_time"] = sectors["timestamp"].diff() < pd.Timedelta(0, unit="s")

    return sectors


def join_sector_bodies(sectors: pd.DataFrame) -> bytearray:
    first_body, offset = sectors.iloc[0].loc[["body", "payload_offset"]]
    bodies = sectors.iloc[1:].loc[:, "body"].values
    data_content = bytearray(first_body[offset:])
    for body in bodies:
        data_content.extend(body)
    return data_content


def get_records(block: bytes | bytearray) -> pd.DataFrame:
    record_array = RecordArray.from_bytes(block)
    record_array._read()
    record_dict = {
        "type": [], "size": [], "incomplete": [], "leftover_data": [],
        "second": [], "data": [], "millisecond": [], "text": []
    }
    for record in record_array.records:
        record_dict["type"].append(record.type)
        record_dict["size"].append(record.size)
        record_dict["incomplete"].append(record.incomplete)
        if record.incomplete:
            record_dict["leftover_data"].append(record.leftover_data)
            record_dict["second"].append(None)
            record_dict["data"].append(None)
            record_dict["millisecond"].append(None)
            record_dict["text"].append(None)
            continue
        record_dict["leftover_data"].append(None)
        record_dict["second"].append(record.body.timestamp)
        if record.type == RecordArray.RecordType.data:
            record_dict["data"].append(record.body.data)
            record_dict["millisecond"].append(None)
            record_dict["text"].append(None)
            continue
        record_dict["data"].append(None)
        record_dict["millisecond"].append(record.body.milliseconds)
        record_dict["text"].append(record.body.text)

    return pd.DataFrame(record_dict)


# TODO: define a function for storing data from a DataFrame as records - for now only consider records in a P-packet
def load_data_attributes(
        source_object: Any, class_to_kaitai_type_map: dict[str, KaitaiType], parent_object_type: int,
        second: int, data_store: RecordDataStore, millisecond: int = 0
) -> None:
    kaitai_type_to_extract = class_to_kaitai_type_map[type(source_object).__name__]
    for attribute in kaitai_type_to_extract.data_attributes:
        if attribute.repetitions is not None:
            time_increment = EPOCH_DURATION / attribute.repetitions
            first_item_millisecond = time_increment / 2
            container = getattr(source_object, attribute.name)
            for index, item in enumerate(container):
                millisecond = int(first_item_millisecond + index * time_increment)
                if attribute.user_type is not None:
                    load_data_attributes(
                        item, class_to_kaitai_type_map, parent_object_type, second, data_store, millisecond
                    )
                else:
                    data_store.store_value(item, parent_object_type, attribute.name, second, millisecond)
        else:
            if attribute.user_type is not None:
                load_data_attributes(
                    getattr(source_object, attribute.name), class_to_kaitai_type_map, parent_object_type, second,
                    data_store, millisecond
                )
            else:
                value = getattr(source_object, attribute.name)
                data_store.store_value(value, parent_object_type, attribute.name, second, millisecond)


def parse_records(records: pd.DataFrame, class_to_kaitai_type_map: dict[str, KaitaiType]) -> dict[Type, pd.DataFrame]:
    complete_records = records[~records["incomplete"]]
    data_records = complete_records[complete_records["type"] == RecordArray.RecordType.data]
    data_records = data_records[["second", "data"]]
    data_records["second"] = data_records["second"].astype(pd.Int64Dtype())

    data_store = RecordDataStore()
    for current_second, data in data_records.itertuples(index=False):
        for record_object in data.records:
            load_data_attributes(
                record_object.object, class_to_kaitai_type_map, record_object.object_type, current_second, data_store
            )

    return data_store.get_all_data()


def decode_log_file(content: bytes | bytearray, data_object_map: dict[str, KaitaiType]) -> dict[Type, pd.DataFrame]:
    log_file = LogFile.from_bytes(content)
    log_file._read()

    sectors = get_sector_dataframe(log_file)
    contiguous_sector_blocks = sectors.groupby("sequence_id").apply(join_sector_bodies, include_groups=False)

    all_records = pd.DataFrame({
        'type': pd.Series(dtype='int'), 'size': pd.Series(dtype='int'), 'incomplete': pd.Series(dtype='bool'),
        'leftover_data': pd.Series(dtype='object'), 'second': pd.Series(dtype='int'),
        'data': pd.Series(dtype='object'), 'millisecond': pd.Series(dtype='int'), 'text': pd.Series(dtype='str')
    })

    for block in contiguous_sector_blocks:
        # TODO: ensure 'get_records(block)' returns DataFrame with the same dtypes as 'all_records'
        #  (otherwise a pandas warning will be issued)
        all_records = pd.concat([all_records, get_records(block)])

    return parse_records(all_records, data_object_map)


def load_file(path: Path, data_object_map: dict[str, KaitaiType]) -> dict[Type, pd.DataFrame]:
    content = path.read_bytes()
    return decode_log_file(content, data_object_map)


def pivot_per_variable(molten_data: pd.DataFrame) -> pd.DataFrame:
    molten_data["timestamp"] = combine_timestamp(TimestampTuple(molten_data["second"], molten_data["millisecond"]))
    if molten_data["value"].dtype == int:
        molten_data["value"] = molten_data["value"].astype(pd.Int64Dtype())
    return pd.pivot_table(
            molten_data, values='value', index="timestamp", columns='variable', aggfunc="first"
    )
