meta:
  id: g_packet
  endian: le
  bit-endian: le

seq:
  - id: packet_type
    contents: G
  - id: timestamp
    type: u4
  - id: millisecond
    type: u2
instances:
  is_gps:
    value: (millisecond & 0x8000) == 0
