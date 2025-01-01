meta:
  id: log_file
  file-extension: log_file
  endian: le
  bit-endian: le

seq:
  - id: sectors
    type: sector
    size: 4096
    repeat: eos

types:
  sector:
    seq:
      - id: header
        type: sector_header
      - id: body
        size: 4084

  sector_header:
    seq:
      - id: timestamp
        type: u4
      - id: check_sum
        type: u4
      - id: serial_number
        type: u2
      - id: payload_offset
        type: u1
      - id: flags
        size: 1
    instances:
      bad:
        value: timestamp == 0x00000000
      empty:
        value: timestamp == 0xFFFFFFFF
