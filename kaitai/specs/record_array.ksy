meta:
  id: record_array
  file-extension: record_array
  endian: le
  bit-endian: le
  imports:
    - process_data

seq:
  - id: records
    type: record
    repeat: eos
    # repeat: until
    # repeat-until: (_io.pos + 51) >= _io.size

types:
  record:
    seq:
      - id: type
        type: b1be
        enum: record_type
      - id: size
        type: b7be
      - id: body
        type: record_body
        if: not incomplete
      - id: leftover_data
        size-eos: true
        if: incomplete
    instances:
      incomplete:
        value: (_io.pos + size) >= _io.size

  record_body:
    seq:
      - id: timestamp
        type: u4
      - id: milliseconds
        type: u1
        if: _parent.type == record_type::text
      - id: text
        type: str
        size: _parent.size - 6
        encoding: ASCII
        if: _parent.type == record_type::text
      - id: data
        type: process_data
        size: _parent.size - 5
        if: _parent.type == record_type::data


enums:
  record_type:
    0: data
    1: text
