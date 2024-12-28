from __future__ import annotations

import zlib
from typing import Any

import numpy as np
import pandas as pd
from pathlib import Path

from geopandas import GeoDataFrame, GeoSeries
from numpy.dtypes import StringDType
from yaml import safe_load

from end4train.communication.ksy import load_kaitai_types, SOURCE_DEVICES_PER_OBJECT_TYPE, \
    DATA_VARIABLES_FOR_DATA_OBJECT_TYPE, load_kaitai_data_objects, Device
from end4train.communication.constants import RECORD_OBJECT_KSY_PATH, SIZE_INCREMENT
from end4train.communication.parsers.log_file import LogFile
from end4train.communication.parsers.record_array import RecordArray
from end4train.communication.parsers.record_object import RecordObject


def test_type_loading():
    data = safe_load(RECORD_OBJECT_KSY_PATH.read_text())
    types = load_kaitai_types(data["types"])
    pass


def test_data_object_loading():
    data = safe_load(RECORD_OBJECT_KSY_PATH.read_text())
    types = load_kaitai_types(data["types"])
    cases_enum = data["seq"][2]["type"]["cases"]
    data_objects = load_kaitai_data_objects(cases_enum, RecordObject.ObjectTypeEnum, types, Device)
    pass

# TODO: replace with dict[str, KaitaiType]


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


def parse_block(block: bytes | bytearray, ) -> pd.DataFrame:
    record_array = RecordArray.from_bytes(block)
    record_array._read()
    record_dict = {
        "type": [], "size": [], "incomplete": [], "leftover_data": [],
        "timestamp": [], "data": [], "milliseconds": [], "text": []
    }
    for record in record_array.records:
        record_dict["type"].append(record.type)
        record_dict["size"].append(record.size)
        record_dict["incomplete"].append(record.incomplete)
        if record.incomplete:
            record_dict["leftover_data"].append(record.leftover_data)
            record_dict["timestamp"].append(None)
            record_dict["data"].append(None)
            record_dict["milliseconds"].append(None)
            record_dict["text"].append(None)
            continue
        record_dict["leftover_data"].append(None)
        record_dict["timestamp"].append(record.body.timestamp)
        if record.type == RecordArray.RecordType.data:
            record_dict["data"].append(record.body.data)
            record_dict["milliseconds"].append(None)
            record_dict["text"].append(None)
            continue
        record_dict["data"].append(None)
        record_dict["milliseconds"].append(record.body.milliseconds)
        record_dict["text"].append(record.body.text)

    records = pd.DataFrame(record_dict)
    arrays = {
        int: {
            "second": np.zeros(SIZE_INCREMENT, dtype=int), "millisecond": np.zeros(SIZE_INCREMENT, dtype=int),
            "variable": np.empty(SIZE_INCREMENT, dtype=StringDType()), "value": np.empty(SIZE_INCREMENT, dtype=int)
        },
        float: {
            "second": np.zeros(SIZE_INCREMENT, dtype=int), "millisecond": np.zeros(SIZE_INCREMENT, dtype=int),
            "variable": np.empty(SIZE_INCREMENT, dtype=StringDType()), "value": np.empty(SIZE_INCREMENT, dtype=float)
        },
        bool: {
            "second": np.zeros(SIZE_INCREMENT, dtype=int), "millisecond": np.zeros(SIZE_INCREMENT, dtype=int),
            "variable": np.empty(SIZE_INCREMENT, dtype=StringDType()), "value": np.empty(SIZE_INCREMENT, dtype=bool)
        },
    }
    indices = {int: 0, float: 0, bool: 0}

    complete_records = records.loc[~records["incomplete"]]
    data_records = complete_records.loc[records["type"] == RecordArray.RecordType.data]

    for timestamp, data in data_records[["timestamp", "data"]].itertuples():
        for record_object in data.records:
            for variable_name in DATA_VARIABLES_FOR_DATA_OBJECT_TYPE[record_object.object_type]:
                pass
                # TODO: get all data-variables and store them in an array according to their types;
                #  use data structure loaded via 'load_kaitai_types' function;
                #  design rules on how to access required attributes based on the info from 'KaitaiType' dataclass

    data_objects = pd.DataFrame({"record_object": data_records["body"].apply(lambda body: body.data.records).explode()})
    data_objects["timestamp"] = data_records["timestamp"]
    data_objects["type"] = data_objects["record_object"].apply(lambda data_object: data_object.object_type)
    data_objects = data_objects.set_index(['type'], append=True)
    variables_series = data_objects.apply(
        lambda row: get_variables_via_object_type(row["record_object"]), axis="columns"
    )
    variables = pd.DataFrame(data=pd.json_normalize(variables_series))
    variables.index = data_objects.index
    devices = pd.Series(SOURCE_DEVICES_PER_OBJECT_TYPE, name="device")
    variables = pd.melt(variables, ignore_index=False).dropna().sort_index()
    variables = variables.merge(devices, left_on="type", right_index=True)
    variables = variables.join(data_objects["timestamp"])
    variables["timestamp"] = pd.to_datetime(variables["timestamp"], unit="s")
    return variables.reset_index(drop=False, names=["process_data_object_id", "data_object_type"])


def load_file(path: Path) -> pd.DataFrame:
    log_file = LogFile.from_bytes(path.read_bytes())
    log_file._read()

    sectors = get_sector_dataframe(log_file)
    contiguous_sector_blocks = sectors.groupby("sequence_id").apply(join_sector_bodies)

    parsed_blocks = [parse_block(block) for block in contiguous_sector_blocks]
    data = pd.concat(parsed_blocks)
    return data.sort_values(by=["timestamp", "device"])


def test_log_file_load():
    hot_file = Path("data") / "20240923" / "hot.dat"
    eot_file = Path("data") / "20240923" / "eot.dat"

    hot_data = load_file(hot_file)
    eot_data = load_file(eot_file)

    hot_cache = Path("data") / "20240923" / "cache" / "20241029" / "hot.parquet"
    eot_cache = Path("data") / "20240923" / "cache" / "20241029" / "eot.parquet"

    # hot_data.to_parquet(hot_cache)
    # eot_data.to_parquet(eot_cache)

    hot_data = pd.read_parquet(hot_cache)
    eot_data = pd.read_parquet(eot_cache)

    hot_data["loaded_from"] = "hot"
    eot_data["loaded_from"] = "eot"

    data = pd.concat([hot_data, eot_data])
    data = data[["timestamp", "loaded_from", "device", "variable", "value"]].sort_values("timestamp", ignore_index=True)
    data["data_object_received"] = (data["loaded_from"] == "hot") & (data["device"] == "eot")

    data = pd.concat([data, data.pivot(columns="variable", values="value")], axis="columns")
    data = data.drop(["variable", "value"], axis="columns")
    data[["north", "east"]] = data[["north", "east"]].replace(0, np.nan)

    coordinates = data.groupby(by=["timestamp", "loaded_from", "device"])[["north", "east"]].first().reset_index()

    eot_recorded_position = coordinates.loc[
        (coordinates["loaded_from"] == "eot") & (coordinates["device"] == "eot"), ["timestamp", "north", "east"]]
    eot_recorded_position = GeoSeries.from_xy(
        eot_recorded_position["east"], eot_recorded_position["north"], index=eot_recorded_position["timestamp"],
        name="eot_recorded_position", crs="epsg:4326"
    )

    hot_recorded_position = coordinates.loc[
        (coordinates["loaded_from"] == "hot") & (coordinates["device"] == "hot"), ["timestamp", "north", "east"]
    ]
    hot_recorded_position = GeoSeries.from_xy(
        hot_recorded_position["east"], hot_recorded_position["north"], index=hot_recorded_position["timestamp"],
        name="hot_recorded_position", crs="epsg:4326"
    )

    eot_received_position = coordinates.loc[
        (coordinates["loaded_from"] == "hot") & (coordinates["device"] == "eot"), ["timestamp", "north", "east"]
    ]
    eot_received_position = GeoSeries.from_xy(
        eot_received_position["east"], eot_received_position["north"], index=eot_received_position["timestamp"],
        name="eot_received_position", crs="epsg:4326"
    )

    data_object_received = data.groupby("timestamp")["data_object_received"].any()
    radio_power = data.groupby("timestamp")["radio_high_power"].first()
    unique_power_values_per_epoch = data.groupby("timestamp")["radio_high_power"].nunique()
    contradicting_epochs = unique_power_values_per_epoch[unique_power_values_per_epoch > 1]

    data = pd.concat(
        [radio_power, data_object_received, hot_recorded_position, eot_received_position, eot_recorded_position],
        axis="columns"
    )
    data.loc[data["radio_high_power"] == 1, "radio_power"] = "high"
    data.loc[data["radio_high_power"] == 0, "radio_power"] = "low"
    data = data.drop("radio_high_power", axis="columns")
    data["hot_position"] = data["hot_recorded_position"]
    data["eot_position"] = data["eot_received_position"]
    data.loc[
        data["eot_position"].isna(), "eot_position"
    ] = data.loc[data["eot_position"].isna(), "eot_recorded_position"]
    data = data.drop(["hot_recorded_position", "eot_received_position", "eot_recorded_position"], axis="columns")

    gdf = GeoDataFrame(data)
    gdf.index = gdf.index.strftime("%Y-%m-%d %X")
    lines = gdf.melt(value_vars=["eot_position", "hot_position"], var_name="device", value_name="position",
                     ignore_index=False).set_geometry("position").dissolve(by="timestamp").convex_hull
    lines = lines[lines.count_coordinates() >= 2]
    lines.name = "line"
    lines = pd.merge(lines, gdf["data_object_received"], left_index=True, right_index=True)

    gdf[gdf.columns.difference(["eot_position"])].to_file("hot.shp")
    gdf[gdf.columns.difference(["hot_position"])].to_file("eot.shp")
    lines.to_file("lines.shp")


if __name__ == "__main__":
    test_log_file_load()
