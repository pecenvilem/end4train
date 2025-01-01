from __future__ import annotations

from math import ceil
from typing import Any

import pandas as pd

from end4train.communication.constants import EPOCH_DURATION
from end4train.communication.ksy import KaitaiType
from end4train.communication.parsers.p_packet import PPacket
from end4train.communication.parsers.process_data import ProcessData
from end4train.communication.parsers.record_object import RecordObject
from end4train.communication.serializers.basic_packets import create_bytes
import end4train.communication.serializers.record_object as record_object_module


# noinspection PyProtectedMember
def serialize_p_packet(
        second: int, data: pd.DataFrame,
        object_type_enum_int_value_to_kaitai_type_map: dict[int, KaitaiType],
        is_gps_time: bool, is_remote_from_eot: bool
) -> bytes:
    millisecond = 0
    buffer_length_bits = 8 + 32 + 16

    packet = PPacket()
    packet.packet_type = b'P'
    packet.epoch_number = second
    packet.time = PPacket.EpochTime(_parent=packet, _root=packet._root)
    packet.time.millisecond = millisecond
    packet.time.eot_data = is_remote_from_eot
    packet.time.eot_link_fail = False
    packet.time.remote_eot_no_gps_time = False
    packet.time.local_no_gps_time = not is_gps_time
    packet.time._check()

    packet.body = ProcessData(_parent=packet, _root=packet._root)
    packet.body.records = store_data_attributes(
        data, object_type_enum_int_value_to_kaitai_type_map,
        packet.body, packet.body._root
    )
    if packet.body.records:
        packet.body.records[-1].stop_flag = True
    for record in packet.body.records:
        record._check()
        buffer_length_bits += record.object.required_bits + 8

    packet._check()
    return create_bytes(packet, buffer_length=ceil(buffer_length_bits / 8))


def assemble_kaitai_type(source_data: pd.DataFrame, kaitai_type: KaitaiType, parent: Any, root: Any) -> Any:
    # record_object = globals()[kaitai_type.python_class](_parent=parent, _root=root)
    record_object = getattr(record_object_module, kaitai_type.python_class)(_parent=parent, _root=root)
    for attribute in kaitai_type.data_attributes:
        if attribute.repetitions is not None:
            time_increment = EPOCH_DURATION / attribute.repetitions
            first_item_millisecond = time_increment / 2
            container = []
            setattr(record_object, attribute.name, container)
            for index in range(attribute.repetitions):
                millisecond = int(first_item_millisecond + index * time_increment)
                period_data = source_data[source_data["millisecond"] == millisecond]
                if attribute.user_type is not None:
                    value = assemble_kaitai_type(period_data, attribute.user_type, record_object, record_object._root)
                else:
                    value = period_data.at[attribute.name, "value"]
                container.append(value)
        else:
            if attribute.user_type is not None:
                value = assemble_kaitai_type(source_data, attribute.user_type, record_object, record_object._root)
            else:
                value = source_data.at[attribute.name, "value"]
            setattr(record_object, attribute.name, value)
    return record_object


def store_data_attributes(
        source_data: pd.DataFrame,
        data_object_type_value_to_kaitai_type_map: dict[int, KaitaiType],
        parent: Any, root: Any
) -> list[RecordObject]:
    if source_data["second"].nunique() != 1:
        raise ValueError("Multiple epoch numbers present in data!")
    record_objects = []
    for object_type, subframe in source_data.groupby("data_object_type", group_keys=False):
        subframe = subframe.set_index("variable", drop=True)
        record_object = RecordObject(_parent=parent, _root=root)
        record_object.object_type = object_type
        record_object.stop_flag = False
        kaitai_type_to_assemble = data_object_type_value_to_kaitai_type_map[object_type]
        record_object.object = assemble_kaitai_type(subframe, kaitai_type_to_assemble, record_object, root)
        record_objects.append(record_object)
    return record_objects
