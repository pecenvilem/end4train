import zlib
from enum import StrEnum
from typing import Any

import pandas as pd
from pathlib import Path

from yaml import safe_load

# from end4train.binary_parser import get_records_from_log_file, record_objects_to_list_of_series, parse_log, \
#     get_process_data_from_records, get_data_from_process_data
from end4train.parsers.log_file import LogFile
from end4train.parsers.record_array import RecordArray
from end4train.parsers.record_object import RecordObject

RECORD_OBJECT_KSY_PATH = Path("..") / "kaitai" / "specs" / "record_object.ksy"

DATA_VARIABLES: dict[Any, list[str]] = {
    RecordObject.DictionaryVersion: ["version", ],
    RecordObject.PressureTuple: ["pressure_a", "pressure_b", ],
    RecordObject.PressureArray: ["pressure_a_record", ],
    RecordObject.Gps: ["north", "east", "alt", "speed", "azimuth", ],
    RecordObject.Fault: [
        "fault_rxmac", "fault_nogps", "fault_vref", "fault_vcc", "fault_24v", "fault_hotprs", "fault_accel",
        "fault_batt", "fault_dict_mismatch", "fault_lm75", "fault_btemp", "fault_flash", "fault_logger", "fault_objbuf",
        "fault_txbuf",
    ],
    RecordObject.EotPower: [
        "temp", "soc", "battery_voltage", "turbine_run", "x1_voltage_high", "battery_full", "radio_high_power",
        "balancer_burn", "turbine_run_time",
    ],
    RecordObject.Temperature: ["temp", ],
    RecordObject.BrakeArray: ["brake_record", ],
}


class SourceDevice(StrEnum):
    HOT = "hot"
    EOT = "eot"
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
    RecordObject.ObjectTypeEnum.eot_temp: SourceDevice.EOT,
    RecordObject.ObjectTypeEnum.hot_temp: SourceDevice.HOT,
    RecordObject.ObjectTypeEnum.brake: SourceDevice.HOT,
}


def load_device_per_object_type(path: Path) -> dict[int, str]:
    device_names = [device.value for device in SourceDevice if device.value]
    data = safe_load(path.read_text())
    result = {}
    for key, value in data["enums"]["object_type_enum"].items():
        matches = []
        for name in device_names:
            if name in value:
                matches.append(name)
        if len(matches) > 1:
            raise ValueError(f"Can't select device for {value}! Matched against: {matches}")
        result[key] = matches[0] if matches else ""
    return result


SOURCE_DEVICES_PER_OBJECT_TYPE = load_device_per_object_type(RECORD_OBJECT_KSY_PATH)


def load_data_variables_per_object_type(path: Path) -> dict[int, list[str]]:
    data = safe_load(path.read_text())
    type_enum = {value: key for key, value in data["enums"]["object_type_enum"].items()}

    record_array_attributes = {attribute["id"]: attribute for attribute in data["seq"]}
    object_attribute = record_array_attributes["object"]
    object_type_mapping = {
        type_enum[key.replace("object_type_enum::", "")]: value for key, value in
        object_attribute["type"]["cases"].items()
    }

    attribute_mapping = {}
    for type_name, type_details in data["types"].items():
        if type_name not in object_type_mapping.values():
            continue
        attribute_names = []
        for attribute in type_details["seq"]:
            if "repeat" in attribute.keys():
                continue
            if "id" not in attribute:
                continue
            if "raw" in attribute["id"]:
                continue
            attribute_names.append(attribute['id'])
        if "instances" in type_details:
            for instance in type_details["instances"]:
                attribute_names.append(instance)
        if attribute_names:
            attribute_mapping[type_name] = attribute_names

    return {type_number: attribute_mapping[type_name] for type_number, type_name in object_type_mapping.items() if
            type_name in attribute_mapping}


DATA_VARIABLES_FOR_DATA_OBJECT_TYPE = load_data_variables_per_object_type(RECORD_OBJECT_KSY_PATH)


def get_variable_names(data_object: RecordObject) -> list[str]:
    return DATA_VARIABLES[type(data_object.object)]


def get_variable_names_for_data_object_type(data_object_type: int) -> list[str]:
    return DATA_VARIABLES_FOR_DATA_OBJECT_TYPE[data_object_type]


def get_variables_via_object_type(data_object: RecordObject) -> dict[str, Any]:
    return {
        key: getattr(data_object.object, key)
        for key in DATA_VARIABLES_FOR_DATA_OBJECT_TYPE.get(data_object.object_type, [])
    }


def get_variables(data_object: RecordObject) -> dict[str, Any]:
    return {key: getattr(data_object.object, key) for key in get_variable_names(data_object)}


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


def test_log_file_load():
    # file = Path("data") / "20240318" / "eot.dat"
    file = Path("data") / "20240923" / "hot.dat"

    log_file = LogFile.from_bytes(file.read_bytes())
    log_file._read()

    sectors = get_sector_dataframe(log_file)
    contiguous_sector_blocks = sectors.groupby("sequence_id").apply(join_sector_bodies)

    block = contiguous_sector_blocks.iloc[0]
    record_array = RecordArray.from_bytes(block)
    record_array._read()

    record_dict = {"body": [], "incomplete": [], "size": [], "type": [], "timestamp": []}
    for record in record_array.records:
        record_dict["incomplete"].append(record.incomplete)
        record_dict["body"].append(record.body if not record.incomplete else None)
        record_dict["size"].append(record.size)
        record_dict["type"].append(record.type)
        record_dict["timestamp"].append(record.body.timestamp if not record.incomplete else None)
    records = pd.DataFrame(record_dict)
    complete_records = records.loc[~records["incomplete"]]
    data_records = complete_records.loc[records["type"] == RecordArray.RecordType.data]

    data_objects = pd.DataFrame({"record_object": data_records["body"].apply(lambda body: body.data.records).explode()})
    data_objects["timestamp"] = data_records["timestamp"]
    data_objects["type"] = data_objects["record_object"].apply(lambda data_object: data_object.object_type)
    data_objects = data_objects.set_index(['type'], append=True)
    data_objects["variables"] = data_objects["record_object"].apply(
        lambda data_object: DATA_VARIABLES[type(data_object.object)]
    )

    # variables_series = data_objects.apply(lambda row: get_variables(row["record_object"]), axis="columns")
    variables_series = data_objects.apply(
        lambda row: get_variables_via_object_type(row["record_object"]), axis="columns"
    )
    variables = pd.DataFrame(data=pd.json_normalize(variables_series))
    variables.index = data_objects.index

    # devices = pd.Series(SOURCE_DEVICES, name="device")
    devices = pd.Series(SOURCE_DEVICES_PER_OBJECT_TYPE, name="device")
    variables = pd.melt(variables, ignore_index=False).dropna().sort_index()
    variables = variables.merge(devices, left_on="type", right_index=True)
    variables = variables.join(data_objects["timestamp"])


    pass


if __name__ == "__main__":
    test_log_file_load()
