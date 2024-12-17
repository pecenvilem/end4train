meta:
  id: j_packet
  endian: le
  bit-endian: le

seq:
  - id: packet_type
    contents: J
  - id: i_am
    type: str
    size: 1
    encoding: ASCII