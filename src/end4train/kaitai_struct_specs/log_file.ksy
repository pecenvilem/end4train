meta:
  id: log_file
  file-extension: log_file
  imports:
    - p_packet
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

    # instances:
    #   stream_size:
    #     value: records._io.size
    #   stream_position:
    #     value: records._io.pos
    #   remaining_bytes:
    #     value: stream_size - stream_position

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

  record_array:
    seq:
      - id: records
        type: record
        repeat: until
        repeat-until: (_io.pos + 51) >= _io.size
        # repeat-until: (_io.pos + _.record_size) >= _io.size
        # repeat-until: (_io.pos + (_.next_record_discriminator & 0x7F)) >= _io.size
      - id: next_sector_data
        size-eos: true
    # instances:
    #   stream_size:
    #     value: _io.size
    #   stream_position:
    #     value: _io.pos
    #   last_record_type:
    #     value: records.last.discriminator

  record:
    seq:
      - id: discriminator
        type: u1
      - id: time_of_record
        type: u4
      - id: text
        type: text_record
        # size: record_size
        if: record_type == record_type::text
      - id: data
        type: data_record
        # size: record_size
        if: record_type == record_type::data
    instances:
      record_type:
        value: discriminator > 127 ? record_type::text : record_type::data
      record_size:
        value: discriminator & 0x7F
        # value: (discriminator & 0x7F) - (record_type == record_type::text ? 6 : 5)
      # next_record_discriminator:
      #   pos: _root._io.pos + 1
      #   type: u1

  text_record:
    seq:
      - id: milliseconds
        type: u1
      - id: text
        type: str
        size: _parent.record_size - 6
        # size: (_parent.record_size - 1) >= 0 ? (_parent.record_size - 1) : 0
        encoding: ASCII

  data_record:
    seq:
      - id: data
        type: p_packet::process_data
        size: _parent.record_size - 5


enums:
  record_type:
    0: text
    1: data
