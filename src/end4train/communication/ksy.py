from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum, Enum
from operator import attrgetter
from pathlib import Path
from typing import Any, Callable, Iterable
from collections.abc import Mapping

from yaml import safe_load

from end4train.communication.constants import DATA_ATTRIBUTE_LABEL, RECORD_OBJECT_KSY_PATH
from end4train.communication.errors import KSYSpecMissingIDError, KSYSpecInvalidRepeatConditionError, \
    KSYSpecInvalidRepeatExpressionError, AmbiguousObjectTypeEnumNameError
from end4train.communication.parsers.record_object import RecordObject


@dataclass
class DeviceDescription:
    object_type_enum_suffix: str
    identifier: str


class Device(Enum):
    MASTER = DeviceDescription("master", "M")
    HOT = DeviceDescription("hot", "H")
    EOT = DeviceDescription("eot", "E")
    DISPLAY = DeviceDescription("display", "D")


@dataclass
class KaitaiDataAttribute:
    name: str
    user_type: None | KaitaiType
    repetitions: None | int


@dataclass
class KaitaiType:
    kaitai_name: str
    python_class: str
    data_attributes: list[KaitaiDataAttribute]


@dataclass
class KaitaiDataObject:
    enum_value: int
    enum_name: str
    source_device: Device | None
    kaitai_type: KaitaiType


def select_device(object_type_enum_name: str, device_enum: type(Device)) -> Device:
    matches = [device for device in device_enum if object_type_enum_name.endswith(device.value.object_type_enum_suffix)]
    if len(matches) > 1:
        raise AmbiguousObjectTypeEnumNameError(object_type_enum_name, matches)
    return matches[0] if matches else None


def load_kaitai_types(types: dict) -> dict[str, KaitaiType]:
    loaded_types = {}
    loaded_names = []
    names_to_load = set(types.keys())
    while names_to_load:
        names_loaded_this_iteration = []
        for type_name in names_to_load:
            data_attributes = []
            type_spec = types[type_name]
            if "instances" in type_spec:
                for instance_name, instance_spec in type_spec["instances"].items():
                    if "doc" not in instance_spec:
                        continue
                    if instance_spec["doc"].startswith(DATA_ATTRIBUTE_LABEL):
                        data_attributes.append(KaitaiDataAttribute(instance_name, None, None))
            for index, attribute in enumerate(type_spec["seq"]):
                if "doc" not in attribute:
                    continue
                if attribute["doc"].startswith(DATA_ATTRIBUTE_LABEL):
                    if "id" not in attribute:
                        raise KSYSpecMissingIDError(type_name, index)
                    if "repeat" in attribute and attribute["repeat"] != "expr":
                        raise KSYSpecInvalidRepeatConditionError(type_name, attribute["id"], attribute["repeat"])
                    if "repeat-expr" in attribute and not isinstance(attribute["repeat-expr"], int):
                        raise KSYSpecInvalidRepeatExpressionError(type_name, attribute["id"], attribute["repeat-expr"])
                    repeat = attribute.get("repeat-expr")
                    if attribute["type"] not in loaded_names:
                        if attribute["type"] in names_to_load:
                            break
                        data_attributes.append(KaitaiDataAttribute(attribute["id"], None, repeat))
                    else:
                        data_attributes.append(
                            KaitaiDataAttribute(attribute["id"], loaded_types[attribute["type"]], repeat)
                        )
            else:  # no unknown user-type was encountered - type can be marked as loaded
                assembled_type = KaitaiType(
                    type_name, get_class_name_for_ksy_type(type_name), data_attributes
                )
                loaded_types[type_name] = assembled_type
                loaded_names.append(type_name)
                names_loaded_this_iteration.append(type_name)
        names_to_load -= set(names_loaded_this_iteration)
    return loaded_types


def load_kaitai_data_objects(
        cases_mapping: dict[str, str], object_type_enum: type(IntEnum), kaitai_types: dict[str, KaitaiType],
        devices: type(Device)
) -> dict[int, KaitaiDataObject]:
    data_objects: dict[int, KaitaiDataObject] = {}
    object_type_enum_value_to_name_mapping: dict[str, int] = {
        item.name: item.value for item in object_type_enum
    }

    for enum_name, type_name in cases_mapping.items():
        enum_name = enum_name.replace("object_type_enum::", "")
        int_key = object_type_enum_value_to_name_mapping[enum_name]
        data_object = KaitaiDataObject(int_key, enum_name, select_device(enum_name, devices), kaitai_types[type_name])
        data_objects[int_key] = data_object

    return data_objects


def load_object_type_enum_to_ksy_type_mapping(path: Path) -> dict[str, str]:
    """
    Loads mapping of e.g.:
        pressure_current_eot: pressure_tuple
        gps_eot: gps
    from record_object.ksy specification
    """
    data = safe_load(path.read_text())
    type_enum = {value: key for key, value in data["enums"]["object_type_enum"].items()}

    record_array_attributes = {attribute["id"]: attribute for attribute in data["seq"]}
    object_attribute = record_array_attributes["object"]
    return {
        type_enum[key.replace("object_type_enum::", "")]: value for key, value in
        object_attribute["type"]["cases"].items()
    }


def get_class_name_for_ksy_type(ksy_type_name: str) -> str:
    parts = ksy_type_name.split("_")
    return "".join([part.capitalize() for part in parts])


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


@dataclass
class CollectionLookup:
    key: str
    lookup_value: Any

    def resolve(self, parent_collection: Iterable) -> Any:
        matches = [item for item in parent_collection if item[self.key] == self.lookup_value]
        if len(matches) != 1:
            raise ValueError(f"Found {len(matches)} occurrences of '{self.lookup_value}' "
                             f"under '{self.key}' key in {parent_collection}")
        return matches[0]


@dataclass
class Key:
    key: str

    def resolve(self, parent_mapping: Mapping) -> Any:
        return parent_mapping[self.key]


@dataclass
class KSYElementSpecifier:
    accessors: list[Key | CollectionLookup]


def get_ksy_element(ksy_object: Any, specifier: KSYElementSpecifier) -> Any:
    if not specifier.accessors:
        return None
    current_parent = ksy_object
    for accessor in specifier.accessors:
        current_parent = accessor.resolve(current_parent)
    return current_parent


TYPES = KSYElementSpecifier([
    Key("types")
])

TYPE_SWITCH = KSYElementSpecifier([
    Key("seq"), CollectionLookup("id", "object"), Key("type"), Key("cases")
])


class KSYInfoStore:
    def __init__(self, ksy_file: Path):
        self.ksy_file = ksy_file
        ksy_object = safe_load(ksy_file.read_text())
        types_element = get_ksy_element(ksy_object, TYPES)
        self.types = load_kaitai_types(types_element)
        type_switch_element = get_ksy_element(ksy_object, TYPE_SWITCH)
        self.data_objects = load_kaitai_data_objects(
            type_switch_element, RecordObject.ObjectTypeEnum, self.types, Device
        )

    def get_int_to_obj_type_map(self) -> dict[int, KaitaiDataObject]:
        return self.data_objects

    def get_class_to_kaitai_type_map(self) -> dict[str, KaitaiType]:
        return {kaitai_type.python_class: kaitai_type for kaitai_type in self.types.values()}

    def get_enum_value_to_kaitai_type_name_map(self) -> dict[int, KaitaiType]:
        return {
            int_enum_value: kaitai_data_object.kaitai_type
            for int_enum_value, kaitai_data_object
            in self.data_objects.items()
        }
    # TODO: add methods returning some mapping equivalent to
    #  'KSY_TYPE_PER_OBJECT_TYPE' and 'DATA_VARIABLES_FOR_DATA_OBJECT_TYPE'


# TODO: remove following two global dicts
KSY_TYPE_PER_OBJECT_TYPE = load_object_type_enum_to_ksy_type_mapping(RECORD_OBJECT_KSY_PATH)
DATA_VARIABLES_FOR_DATA_OBJECT_TYPE = load_data_variables_per_object_type(RECORD_OBJECT_KSY_PATH)
