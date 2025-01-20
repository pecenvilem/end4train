meta:
  id: packets
  endian: le
  bit-endian: le
  imports:
    - c_packet
    - d_packet
    - e_packet
    - ffff_packet
    - g_packet
    - i_packet
    - j_packet
    - p_packet
    - r_packet
    - s_packet
    - t_packet

seq:
  - id: packet_type
    type: str
    size: 1
    encoding: ASCII

instances:
  body:
    pos: 0
    type:
      switch-on: packet_type
      cases:
        '"C"': c_packet
        '"D"': d_packet
        '"E"': e_packet
        '"F"': ffff_packet
        '"G"': g_packet
        '"I"': i_packet
        '"J"': j_packet
        '"P"': p_packet
        '"R"': r_packet
        '"S"': s_packet
        '"T"': t_packet
