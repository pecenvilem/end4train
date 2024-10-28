meta:
  id: process_data
  endian: le
  bit-endian: le
  imports:
    - record_object

seq:
    - id: records
      type: record_object
      repeat: until
      repeat-until: _.stop_flag
