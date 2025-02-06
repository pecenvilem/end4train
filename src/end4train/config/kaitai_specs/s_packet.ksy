meta:
  id: s_packet
  endian: le
  bit-endian: le
  imports:
    - record_object

seq:
  - id: packet_type
    contents: S
  - id: request_id
    type: u4
  - id: request_status
    type: u1
    enum: status_enum

enums:
  status_enum:
    0: available_locally
    1: requesting_from_remote