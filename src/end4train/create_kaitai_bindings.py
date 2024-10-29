from pathlib import Path

from yaml import safe_load


if __name__ == '__main__':
    path = Path("kaitai") / "specs" / "record_object.ksy"
    data = safe_load(path.read_bytes())
    type_enum = {value: key for key, value in data["enums"]["object_type_enum"].items()}

    record_array_attributes = {attribute["id"]: attribute for attribute in data["seq"]}
    object_attribute = record_array_attributes["object"]
    object_type_mapping = {
        type_enum[key.replace("object_type_enum::", "")]: value for key, value in object_attribute["type"]["cases"].items()
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

    result = {type_number: attribute_mapping[type_name] for type_number, type_name in object_type_mapping.items() if type_name in attribute_mapping}
