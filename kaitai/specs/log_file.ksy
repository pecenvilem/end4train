meta:
  id: log_file
  file-extension: log_file
  imports:
    - process_data
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
        size: 12
      - id: previous_sector_data
        size: header.payload_offset
      - id: records
        type: record_array
        size: 4084 - header.payload_offset

  sector_header:
    seq:
      - id: unix_time
        type: u4
      - id: check_sum
        type: u4
      - id: serial_number
        type: u2
      - id: payload_offset
        type: u1
      - id: reserved
        size: 1
    instances:
      bad: unix_time == 0x00000000
      empty: unix_time == 0xFFFFFFFF

  record_array:
    seq:
      - id: records
        type: record
        # repeat: eos
        repeat: until
        repeat-until: (_io.pos + 51) >= _io.size
      - id: next_sector_data
        size-eos: true

  record:
    seq:
      - id: rec_type
        type: b1be
        enum: record_type
      - id: record_size
        type: b7be
      - id: time_of_record
        type: u4
      - id: text
        type: text_record
        if: rec_type == (record_type::text)
      - id: data
        type: data_record
        if: rec_type == (record_type::data)

  text_record:
    seq:
      - id: milliseconds
        type: u1
      - id: text
        type: str
        size: _parent.record_size - 6
        encoding: ASCII

  data_record:
    seq:
      - id: data
        type: process_data
        size: _parent.record_size - 5


enums:
  record_type:
    0: data
    1: text
