meta:
  id: record_object
  endian: le
  bit-endian: le

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
        object_type_enum::temp_eot: eot_power
        object_type_enum::temp_hot: temperature
        object_type_enum::brake_hot: brake_array

types:
  dictionary_version:
    seq:
    - id: version
      type: b8
      doc: <data>
  
  pressure_tuple:
    seq:
    - id: pressure_a_raw
      type: b12
    - id: pressure_b_raw
      type: b12
    instances:
      pressure_a:
        value: pressure_a_raw * 0.002
        doc: <data>
      pressure_b:
        value: pressure_b_raw * 0.002
        doc: <data>
  
  pressure_array_field:
    seq:
      - id: pressure_a_raw
        type: b10
    instances:
      pressure_a:
        value: pressure_a_raw * 0.008
        doc: <data>
  
  pressure_array:
    seq:
      - id: pressure_a_record
        type: pressure_array_field
        repeat: expr
        repeat-expr: 10
        doc: <data>
  
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
        doc: <data>; degrees, negative -> south
      east:
        value: east_raw.as<s4>.as<f4> * 0.0001 / 60
        doc: <data>; degrees, negative -> west
      alt:
        value: alt_raw.as<f4> * 0.1
        doc: <data>; meters AMSL
      speed:
        value: speed_raw.as<f4> * 0.1
        doc: <data>; km/h
      azimuth:
        value: azimuth_raw.as<f4> * 0.1
        doc: <data>; degrees, 409,5 -> UNKNOWN
  
  fault:
    seq:
      - id: fault_rxmac
        type: b1
        doc: <data>; Nelze precist MAC adresu
      - id: fault_nogps
        type: b1
        doc: <data>; GPS nebyla radne inicializovana
      - id: fault_vref
        type: b1
        doc: <data>; Pomer napeti bandgap a reference neni ok
      - id: fault_vcc
        type: b1
        doc: <data>; Pomer napeti reference a 3V3 neni ok
      - id: fault_24v
        type: b1
        doc: <data>; Vystupni napeti 24V neni ok
      - id: fault_hotprs
        type: b1
        doc: <data>; Delsi dobu neprijimame data z HOTPRS
      - id: fault_accel
        type: b1
        doc: <data>; Akcelerometr nebyl nalezen
      - id: fault_batt
        type: b1
        doc: <data>; Selhani baterie, nelze nabijet
      - id: fault_dict_mismatch
        type: b1
        doc: <data>; Verze slovniku protistrany neodpovida
      - id: fault_lm75
        type: b1
        doc: <data>; Chyba cteni teploty
      - id: fault_btemp
        type: b1
        doc: <data>; Teplota je (byla) takova ze neni mozno nabijet baterii
      - type: b17
      - id: fault_flash
        type: b1
        doc: <data>; (Interni) Doslo k chybe zapisu nebo mazani Flash
      - id: fault_logger
        type: b1
        doc: <data>; (Interni) Logger buffer overflow - neulozilo se do Flash
      - id: fault_objbuf
        type: b1
        doc: <data>; (Interni) Delka bufferu pro obj_run je moc mala
      - id: fault_txbuf
        type: b1
        doc: <data>; (Interni) Zarovnani txbuf v cmx469.c je spatne
  
  eot_power:
    seq:
      - id: temp_raw
        type: b8
      - id: soc
        type: b8
        doc: <data>; percent (integer 0 - 127)
      - id: battery_voltage_raw
        type: b12
      - id: turbine_run
        type: b1
        doc: <data>
      - id: x1_voltage_high
        type: b1
        doc: <data>
      - id: battery_full
        type: b1
        doc: <data>
      - id: radio_high_power
        type: b1
        doc: <data>
      - id: balancer_burn_raw
        type: b16
      - id: turbine_run_time
        type: b16
        doc: <data>; hour
    instances:
      temp:
        value: temp_raw.as<s1>
        doc: degrees celsius
      battery_voltage:
        value: battery_voltage_raw.as<f4> / 100
        doc: <data>; volts
      balancer_burn:
        value: balancer_burn_raw.as<f4> * 0.45
        doc: <data>; mAh
  
  temperature:
    seq:
      - id: temp_raw
        type: b8
    instances:
      temp:
        value: temp_raw.as<s1>
        doc: <data>
  
  brake_array:
    seq:
      - id: brake_record
        type: b4
        enum: brake_position_enum
        repeat: expr
        repeat-expr: 10
        doc: <data>


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
    9: temp_eot
    10: temp_hot
    11: brake_hot
  
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
