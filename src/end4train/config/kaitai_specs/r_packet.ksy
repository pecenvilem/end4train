meta:
  id: r_packet
  endian: le
  bit-endian: le

seq:
  - id: packet_type
    contents: R
  - id: request_id
    type: u4
  - id: requested_types
    type: type_request
    repeat: eos

types:
  type_request:
    seq:
      - id: object_type
        type: u1
        enum: object_type_enum
      - id: period
        type: u2
        enum: request_period_enum

enums:
  request_period_enum:
    0: stop
    65535: now

  # import enum from 'record_object' instead of redefining it here
  object_type_enum:
    0: dict_version
    1: pressure_current_eot
    2: pressure_current_hot
    3: pressure_history_eot
    4: pressure_history_hot
    5: gps_eot
    6: gps_hot
    7: fault_eot
    8: fault_hot
    9: eot_temp
    10: hot_temp
    11: brake