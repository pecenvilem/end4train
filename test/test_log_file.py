from __future__ import annotations

import zlib
from typing import Any, Type

import numpy as np
import pandas as pd
from pathlib import Path

from geopandas import GeoDataFrame, GeoSeries
from numpy.dtypes import StringDType
from yaml import safe_load

from end4train.communication.ksy import load_kaitai_types, SOURCE_DEVICES_PER_OBJECT_TYPE, \
    DATA_VARIABLES_FOR_DATA_OBJECT_TYPE, load_kaitai_data_objects, Device, KSYInfoStore, KaitaiDataObject, \
    KaitaiDataAttribute, KaitaiType
from end4train.communication.constants import RECORD_OBJECT_KSY_PATH, SIZE_INCREMENT
from end4train.communication.parsers.log_file import LogFile
from end4train.communication.parsers.record_array import RecordArray
from end4train.communication.parsers.record_object import RecordObject


def test_type_loading():
    data = safe_load(RECORD_OBJECT_KSY_PATH.read_text())
    load_kaitai_types(data["types"])


def test_data_object_loading():
    data = safe_load(RECORD_OBJECT_KSY_PATH.read_text())
    types = load_kaitai_types(data["types"])
    cases_enum = data["seq"][2]["type"]["cases"]
    load_kaitai_data_objects(cases_enum, RecordObject.ObjectTypeEnum, types, Device)


def test_ksy_load():
    KSYInfoStore(RECORD_OBJECT_KSY_PATH)


def get_variable_names_for_data_object_type(data_object_type: int) -> list[str]:
    return DATA_VARIABLES_FOR_DATA_OBJECT_TYPE[data_object_type]


def get_variables_via_object_type(data_object: RecordObject) -> dict[str, Any]:
    return {
        key: getattr(data_object.object, key)
        for key in DATA_VARIABLES_FOR_DATA_OBJECT_TYPE.get(data_object.object_type, [])
    }


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


def parse_records(records: pd.DataFrame, class_to_kaitai_type_map: dict[str, KaitaiType]) -> dict[Type, pd.DataFrame]:
    arrs = {}
    indices = {}

    def create_arrays(key: type) -> None:
        arrs.setdefault(key, {})
        indices.setdefault(key, 0)
        arrs[key]["second"] = np.zeros(SIZE_INCREMENT, dtype=int)
        arrs[key]["millisecond"] = np.zeros(SIZE_INCREMENT, dtype=int)
        arrs[key]["data_object_type"] = np.empty(SIZE_INCREMENT, dtype=int)
        arrs[key]["variable"] = np.empty(SIZE_INCREMENT, dtype=StringDType())
        arrs[key]["value"] = np.empty(SIZE_INCREMENT, dtype=key)

    def enlarge_arrays(key: Type) -> None:
        arrs[key]["second"] = np.append(arrs[key]["second"], np.zeros(SIZE_INCREMENT, dtype=int))
        arrs[key]["millisecond"] = np.append(arrs[key]["millisecond"], np.zeros(SIZE_INCREMENT, dtype=int))
        arrs[key]["data_object_type"] = np.append(
            arrs[key]["data_object_type"], np.empty(SIZE_INCREMENT, dtype=int)
        )
        arrs[key]["variable"] = np.append(arrs[key]["variable"], np.empty(SIZE_INCREMENT, dtype=StringDType()))
        arrs[key]["value"] = np.append(arrs[key]["value"], np.empty( SIZE_INCREMENT, dtype=key))

    def store_attribute(value: Any, object_type: int, variable_name: str, millisecond: int = 0) -> Any:
        value_type = type(value)
        if value_type not in arrs:
            create_arrays(value_type)
        data_store = arrs[value_type]
        index = indices[value_type]
        try:
            data_store["second"][index] = second
            data_store["millisecond"][index] = millisecond
            data_store["data_object_type"][index] = object_type
            data_store["variable"][index] = variable_name
            data_store["value"][index] = value
        except IndexError:
            enlarge_arrays(value_type)
            data_store["second"][index] = second
            data_store["millisecond"][index] = millisecond
            data_store["data_object_type"][index] = object_type
            data_store["variable"][index] = variable_name
            data_store["value"][index] = value
        indices[value_type] += 1

    def load_data_attributes(source_object: Any, parent_object_type: int, millisecond: int = 0) -> None:
        # TODO: get all data-variables and store them in an array according to their types;
        #  use data structure loaded via 'load_kaitai_types' function;
        #  design rules on how to access required attributes based on the info from 'KaitaiType' dataclass
        kaitai_type_to_extract = class_to_kaitai_type_map[type(source_object).__name__]
        for attribute in kaitai_type_to_extract.data_attributes:
            if attribute.repetitions is not None:
                # TODO: define function to calculate inter-measurement period from on number of repetitions
                epoch_duration = 1000  # millisecond
                time_increment = epoch_duration / attribute.repetitions
                first_item_millisecond = time_increment / 2
                container = getattr(source_object, attribute.name)
                for index, item in enumerate(getattr(source_object, attribute.name)):
                    millisecond = int(first_item_millisecond + index * time_increment)
                    if attribute.user_type is not None:
                        # TODO: define a function that (possibly using recursion) parses attributes with some user-type
                        load_data_attributes(container[index], parent_object_type, millisecond)
                    else:
                        value = container[index]
                        store_attribute(value, parent_object_type, attribute.name, millisecond)
                continue
            if attribute.user_type is not None:
                # TODO: define a function that (possibly using recursion) parses attributes with some user-type
                load_data_attributes(getattr(source_object, attribute.name), parent_object_type, millisecond)
            else:
                value = getattr(source_object, attribute.name)
                store_attribute(value, parent_object_type, attribute.name, millisecond)

    complete_records = records[~records["incomplete"]]
    data_records = complete_records[complete_records["type"] == RecordArray.RecordType.data]
    data_records = data_records[["second", "data"]]
    data_records["second"] = data_records["second"].astype(pd.Int64Dtype())

    for second, data in data_records.itertuples(index=False):
        for record_object in data.records:
            load_data_attributes(record_object.object, record_object.object_type)

    result = {}
    for arr_type, arrs in arrs.items():
        result[arr_type] = pd.DataFrame(arrs).iloc[0:indices[arr_type]]

    return result


def load_file(path: Path, data_object_map: dict[str, KaitaiType]) -> dict[Type, pd.DataFrame]:
    log_file = LogFile.from_bytes(path.read_bytes())
    log_file._read()

    sectors = get_sector_dataframe(log_file)
    contiguous_sector_blocks = sectors.groupby("sequence_id").apply(join_sector_bodies, include_groups = False)

    records = pd.DataFrame({
        'type': pd.Series(dtype='int'), 'size': pd.Series(dtype='int'), 'incomplete': pd.Series(dtype='bool'),
        'leftover_data': pd.Series(dtype='object'), 'second': pd.Series(dtype='int'),
        'data': pd.Series(dtype='object'), 'millisecond': pd.Series(dtype='int'), 'text': pd.Series(dtype='str')
    })

    for block in contiguous_sector_blocks:
        # TODO: check dtypes and correct 'records' df to match
        records = pd.concat([records, get_records(block)])

    return parse_records(records, data_object_map)


def test_hot_data_load():
    store = KSYInfoStore(RECORD_OBJECT_KSY_PATH)

    hot_file = Path("data") / "20240923" / "hot.dat"
    load_file(hot_file, store.get_class_to_kaitai_type_map())  # 37 sec (59 sec in 021643fb8e1c187be8aca2ec7c28d7ca12f8912f)


def test_eot_data_load():
    store = KSYInfoStore(RECORD_OBJECT_KSY_PATH)

    eot_file = Path("data") / "20240923" / "eot.dat"
    load_file(eot_file, store.get_class_to_kaitai_type_map())  # 37 sec (59 sec in 021643fb8e1c187be8aca2ec7c28d7ca12f8912f)


def test_log_file_load():
    hot_file = Path("data") / "20240923" / "hot.dat"
    eot_file = Path("data") / "20240923" / "eot.dat"

    store = KSYInfoStore(RECORD_OBJECT_KSY_PATH)

    eot_data = load_file(eot_file, store.get_class_to_kaitai_type_map())  # 2 sec (3 sec in 021643fb8e1c187be8aca2ec7c28d7ca12f8912f)
    hot_data = load_file(hot_file, store.get_class_to_kaitai_type_map())  # 37 sec (59 sec in 021643fb8e1c187be8aca2ec7c28d7ca12f8912f)

    hot_data_merged = pd.concat(hot_data.values())
    eot_data_merged = pd.concat(eot_data.values())
    #
    # hot_cache = Path("data") / "20240923" / "cache" / "20241230" / "hot.parquet"
    # eot_cache = Path("data") / "20240923" / "cache" / "20241230" / "eot.parquet"
    #
    # # hot_data_merged.to_parquet(hot_cache)
    # # eot_data_merged.to_parquet(eot_cache)
    #
    # hot_data = pd.read_parquet(hot_cache)
    # eot_data = pd.read_parquet(eot_cache)
    #
    # hot_data["loaded_from"] = "hot"
    # eot_data["loaded_from"] = "eot"
    #
    # # TODO: add column 'device' to dataframe - previously already present after loading, now needs to be
    # #  inferred from the 'data_object_type' column
    # data = pd.concat([hot_data, eot_data])
    # data = data[["timestamp", "loaded_from", "device", "variable", "value"]].sort_values("timestamp", ignore_index=True)
    # data["data_object_received"] = (data["loaded_from"] == "hot") & (data["device"] == "eot")
    #
    # data = pd.concat([data, data.pivot(columns="variable", values="value")], axis="columns")
    # data = data.drop(["variable", "value"], axis="columns")
    # data[["north", "east"]] = data[["north", "east"]].replace(0, np.nan)
    #
    # coordinates = data.groupby(by=["timestamp", "loaded_from", "device"])[["north", "east"]].first().reset_index()
    #
    # eot_recorded_position = coordinates.loc[
    #     (coordinates["loaded_from"] == "eot") & (coordinates["device"] == "eot"), ["timestamp", "north", "east"]]
    # eot_recorded_position = GeoSeries.from_xy(
    #     eot_recorded_position["east"], eot_recorded_position["north"], index=eot_recorded_position["timestamp"],
    #     name="eot_recorded_position", crs="epsg:4326"
    # )
    #
    # hot_recorded_position = coordinates.loc[
    #     (coordinates["loaded_from"] == "hot") & (coordinates["device"] == "hot"), ["timestamp", "north", "east"]
    # ]
    # hot_recorded_position = GeoSeries.from_xy(
    #     hot_recorded_position["east"], hot_recorded_position["north"], index=hot_recorded_position["timestamp"],
    #     name="hot_recorded_position", crs="epsg:4326"
    # )
    #
    # eot_received_position = coordinates.loc[
    #     (coordinates["loaded_from"] == "hot") & (coordinates["device"] == "eot"), ["timestamp", "north", "east"]
    # ]
    # eot_received_position = GeoSeries.from_xy(
    #     eot_received_position["east"], eot_received_position["north"], index=eot_received_position["timestamp"],
    #     name="eot_received_position", crs="epsg:4326"
    # )
    #
    # data_object_received = data.groupby("timestamp")["data_object_received"].any()
    # radio_power = data.groupby("timestamp")["radio_high_power"].first()
    # unique_power_values_per_epoch = data.groupby("timestamp")["radio_high_power"].nunique()
    # contradicting_epochs = unique_power_values_per_epoch[unique_power_values_per_epoch > 1]
    #
    # data = pd.concat(
    #     [radio_power, data_object_received, hot_recorded_position, eot_received_position, eot_recorded_position],
    #     axis="columns"
    # )
    # data.loc[data["radio_high_power"] == 1, "radio_power"] = "high"
    # data.loc[data["radio_high_power"] == 0, "radio_power"] = "low"
    # data = data.drop("radio_high_power", axis="columns")
    # data["hot_position"] = data["hot_recorded_position"]
    # data["eot_position"] = data["eot_received_position"]
    # data.loc[
    #     data["eot_position"].isna(), "eot_position"
    # ] = data.loc[data["eot_position"].isna(), "eot_recorded_position"]
    # data = data.drop(["hot_recorded_position", "eot_received_position", "eot_recorded_position"], axis="columns")
    #
    # gdf = GeoDataFrame(data)
    # gdf.index = gdf.index.strftime("%Y-%m-%d %X")
    # lines = gdf.melt(value_vars=["eot_position", "hot_position"], var_name="device", value_name="position",
    #                  ignore_index=False).set_geometry("position").dissolve(by="timestamp").convex_hull
    # lines = lines[lines.count_coordinates() >= 2]
    # lines.name = "line"
    # lines = pd.merge(lines, gdf["data_object_received"], left_index=True, right_index=True)
    #
    # gdf[gdf.columns.difference(["eot_position"])].to_file("hot.shp")
    # gdf[gdf.columns.difference(["hot_position"])].to_file("eot.shp")
    # lines.to_file("lines.shp")


if __name__ == "__main__":
    test_log_file_load()
