from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path

import pytest
from geopandas import GeoDataFrame, GeoSeries
from yaml import safe_load

from end4train.communication.decode import load_file, pivot_per_variable
from end4train.communication.ksy import load_kaitai_types, \
    load_kaitai_data_objects, Device, KSYInfoStore
from end4train.communication.constants import RECORD_OBJECT_KSY_PATH
from end4train.communication.parsers.record_object import RecordObject


# TODO: add some example data for loading tests to see, if correct values are being loaded,
#  not just if function crashes, or not...

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


@pytest.mark.skip(reason="Takes too long...")
def test_hot_data_load():
    store = KSYInfoStore(RECORD_OBJECT_KSY_PATH)

    hot_file = Path("data") / "20240923" / "hot.dat"
    load_file(hot_file, store.get_class_to_kaitai_type_map())
    # 55 sec (59 sec in 021643fb8e1c187be8aca2ec7c28d7ca12f8912f)


def test_eot_data_load():
    store = KSYInfoStore(RECORD_OBJECT_KSY_PATH)

    eot_file = Path("data") / "20240923" / "eot.dat"
    load_file(eot_file, store.get_class_to_kaitai_type_map())
    # 3 sec (3 sec in 021643fb8e1c187be8aca2ec7c28d7ca12f8912f)


def test_eot_data_pivoting():
    store = KSYInfoStore(RECORD_OBJECT_KSY_PATH)

    eot_file = Path("data") / "20240923" / "eot.dat"
    data = load_file(eot_file, store.get_class_to_kaitai_type_map())

    for data_frame in data.values():
        pivot_per_variable(data_frame)


@pytest.mark.skip(reason="Takes too long...")
def test_log_file_load():
    hot_file = Path("data") / "20240923" / "hot.dat"
    eot_file = Path("data") / "20240923" / "eot.dat"

    store = KSYInfoStore(RECORD_OBJECT_KSY_PATH)

    eot_data = load_file(eot_file,
                         store.get_class_to_kaitai_type_map())  # 2 sec (3 sec in 021643fb8e1c187be8aca2ec7c28d7ca12f8912f)
    hot_data = load_file(hot_file,
                         store.get_class_to_kaitai_type_map())  # 37 sec (59 sec in 021643fb8e1c187be8aca2ec7c28d7ca12f8912f)

    hot_data_merged = pd.concat(hot_data.values())
    eot_data_merged = pd.concat(eot_data.values())

    hot_cache = Path("data") / "20240923" / "cache" / "20241230" / "hot.parquet"
    eot_cache = Path("data") / "20240923" / "cache" / "20241230" / "eot.parquet"

    # hot_data_merged.to_parquet(hot_cache)
    # eot_data_merged.to_parquet(eot_cache)

    hot_data = pd.read_parquet(hot_cache)
    eot_data = pd.read_parquet(eot_cache)

    hot_data["loaded_from"] = "hot"
    eot_data["loaded_from"] = "eot"

    # TODO: add column 'device' to dataframe - previously already present after loading, now needs to be
    #  inferred from the 'data_object_type' column
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
