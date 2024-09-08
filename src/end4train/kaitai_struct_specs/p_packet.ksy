meta:
  id: p_packet
  endian: le
  bit-endian: le
  
seq:
  - id: packet_type
    contents: P
  - id: epoch_number
    type: b32
  - id: time
    type: epoch_time
  - id: body
    type: record_object
    repeat: until
    repeat-until: _.stop_flag == true

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
    
  
  record_object:
    seq:
    - id: object_type
      type: b7
      enum: object_type_enum
    - id: stop_flag
      type: b1
    - id: object
      type:
        switch-on: object_type
        cases:
          object_type_enum::dict_version: dictionary_version
          object_type_enum::pressure_current_eot: pressure_tuple
          object_type_enum::pressure_current_hot: pressure_tuple
          object_type_enum::pressure_history_eot: pressure_array
          object_type_enum::pressure_history_hot: pressure_array
          object_type_enum::gps_eot: gps
          object_type_enum::gps_hot: gps
          object_type_enum::fault_eot: fault
          object_type_enum::fault_hot: fault
          object_type_enum::eot_temp: eot_power
          object_type_enum::hot_temp: temperature
          object_type_enum::brake: brake_array
  
  dictionary_version:
    seq:
    - id: version
      type: b8
  
  pressure_tuple:
    seq:
    - id: pressure_a_raw
      type: b12
    - id: pressure_b_raw
      type: b12
    instances:
      pressure_a:
        value: pressure_a_raw * 0.002
      pressure_b:
        value: pressure_b_raw * 0.002
  
  pressure_array_field:
    seq:
      - id: pressure_a_raw
        type: b10
    instances:
      pressure_a:
        value: pressure_a_raw * 0.008
  
  pressure_array:
    seq:
      - id: pressure_a_record
        type: pressure_array_field
        repeat: expr
        repeat-expr: 10
  
  gps:
    seq:
      - id: north_raw
        type: b28
      - id: east_raw
        type: b28
      - id: alt_raw
        type: b14
      - id: speed_raw
        type: b12
      - id: azimuth_raw
        type: b12
    instances:
      north:
        value: north_raw.as<s4>.as<f4> * 0.0001 / 60
        doc: degrees, negative -> south
      east:
        value: east_raw.as<s4>.as<f4> * 0.0001 / 60
        doc: degrees, negative -> west
      alt:
        value: alt_raw.as<f4> * 0.1
        doc: meters AMSL
      speed:
        value: speed_raw.as<f4> * 0.1
        doc: km/h
      azimuth:
        value: azimuth_raw.as<f4> * 0.1
        doc: degrees, 409,5 -> UNKNOWN
  
  fault:
    seq:
      - id: fault_rxmac
        type: b1
        doc: Nelze precist MAC adresu
      - id: fault_nogps
        type: b1
        doc: GPS nebyla radne inicializovana
      - id: fault_vref
        type: b1
        doc: Pomer napeti bandgap a reference neni ok
      - id: fault_vcc
        type: b1
        doc: Pomer napeti reference a 3V3 neni o
      - id: fault_24v
        type: b1
        doc: Vystupni napeti 24V neni ok
      - id: fault_hotprs
        type: b1
        doc: Delsi dobu neprijimame data z HOTPRS
      - id: fault_accel
        type: b1
        doc: Akcelerometr nebyl nalezen
      - id: fault_batt
        type: b1
        doc: Selhani baterie, nelze nabijet
      - id: fault_dict_mismatch
        type: b1
        doc: Verze slovniku protistrany neodpovida
      - id: fault_lm75
        type: b1
        doc: Chyba cteni teploty
      - id: fault_btemp
        type: b1
        doc: Teplota je (byla) takova ze neni mozno nabijet baterii
      - type: b17
      - id: fault_flash
        type: b1
        doc: (Interni) Doslo k chybe zapisu nebo mazani Flash
      - id: fault_logger
        type: b1
        doc: (Interni) Logger buffer overflow - neulozilo se do Flash
      - id: fault_objbuf
        type: b1
        doc: (Interni) Delka bufferu pro obj_run je moc mala
      - id: fault_txbuf
        type: b1
        doc: (Interni) Zarovnani txbuf v cmx469.c je spatne
  
  eot_power:
    seq:
      - id: temp_raw
        type: b8
      - id: soc
        type: b8
        doc: percent (integer 0 - 127)
      - id: battery_voltage_raw
        type: b12
      - id: turbine_run
        type: b1
      - id: x1_voltage_high
        type: b1
      - type: b1
      - id: battery_full
        type: b1
      - id: balancer_burn_raw
        type: b16
      - id: turbine_run_time
        type: b16
        doc: hour
    instances:
      temp:
        value: temp_raw.as<s1>
        doc: degrees celsius
      battery_voltage:
        value: battery_voltage_raw.as<f4> / 100
        doc: volts
      balancer_burn:
        value: balancer_burn_raw.as<f4> * 0.45
        doc: mAh
  
  temperature:
    seq:
      - id: temp_raw
        type: b8
    instances:
      temp:
        value: temp_raw.as<s1>
  
  brake_array:
    seq:
      - id: brake_record
        type: b4
        enum: brake_position_enum
        repeat: expr
        repeat-expr: 10


enums:
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
  
  brake_position_enum:
    0: bse_apply
    1: bse_error
    2: bse_emergency
    3: bse_transition
    4: bse_hold
    5: bse_release
    6: bse_cut_off
    7: bse_overcharge
    8: bse_fast_charge
