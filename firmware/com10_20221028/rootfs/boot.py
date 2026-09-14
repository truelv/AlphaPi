import protocal as p

b = p.uart_read(0,1)[3]
if b&0x0C == 0x0C:
    import factory_reset


static_buf=bytearray(40960)
