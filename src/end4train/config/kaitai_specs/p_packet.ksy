meta:
  id: p_packet
  endian: le
  bit-endian: le
  imports:
    - process_data
  
seq:
  - id: packet_type
    contents: P
  - id: epoch_number
    type: b32
  - id: time
    type: epoch_time
  - id: body
    type: process_data

types:
  epoch_time:
    seq:
    - id: millisecond
      type: b12
    - id: eot_data
      type: b1
    - id: eot_link_fail
      type: b1
    - id: remote_eot_no_gps_time
      type: b1
    - id: local_no_gps_time
      type: b1
