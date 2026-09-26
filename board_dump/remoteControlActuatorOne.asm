mpy_source_file: dumped/remoteControlActuatorOne.mpy
source_file: .\remoteControlActuatorOne.py
header: 4d:06:00:1f
arch: NONE
qstr_table[59] (* for static qstrs):
    '.\\remoteControlActuatorOne.py' 
    '<module>' *
    'DataStruct' 
    'basic' 
    'controlBoardAlphaPiOne' 
    'neopixel' 
    'machine' 
    'time' 
    'NeoPixel' 
    'Pin' 
    'n' 
    'insert' *
    'NP_write' 
    'write' *
    'sleep_ms' 
    'BrightnessUp' 
    'IntValue' 
    'SetBrightness' 
    'UpdateBrightness' 
    'GetBrightness' 
    'setPixelColorWithoutWrightRGBOne' 
    'setPixelColorWithoutWright' 
    'setPixelColor' 
    'clamp' 
    'hsl' 
    'packRGB' 
    'packRGBd' 
    'unpackR' 
    'unpackG' 
    'unpackB' 
    'set_shake' 
    'WritePwm' 
    'stop_shake' 
    'Update' 
    'version' 
    'brightness' 
    'np' 
    'rawRGB' 
    'i' 
    'br_d' 
    'index' *
    'rgb' 
    'r' 
    'g' 
    'b' 
    'index_d' 
    'rgb_d' 
    'minValue' 
    'maxValue' 
    'value' *
    'h' 
    's' 
    'l' 
    'round' *
    'abs' *
    'r_d' 
    'g_d' 
    'b_d' 
    'shake_d' 
obj_table: [(0, 0, 0), 'v_2022_11_01']
simple_name: <module>
  raw bytecode: 230 28:62:01:2c:26:26:26:66:84:07:23:30:24:2a:2b:30:65:84:08:84:07:84:0d:64:20:84:07:84:10:84:0b:84:08:84:2e:64:20:84:07:64:40:64:40:64:40:64:40:64:20:64:20:80:10:02:2a:01:1b:03:1c:02:16:02:59:80:51:1b:04:16:04:80:51:1b:05:16:05:80:51:1b:06:16:06:80:51:1b:07:16:07:32:00:16:0c:8a:17:23:11:05:14:08:11:06:14:09:91:36:01:83:36:02:17:24:2b:00:16:25:12:24:13:0a:80:42:57:57:16:26:11:25:14:0b:11:26:23:00:36:02:59:23:00:12:24:11:26:56:81:e5:58:5a:d7:43:24:59:59:11:0c:34:00:59:32:01:16:0f:32:02:16:11:32:03:16:12:32:04:16:13:32:05:16:14:32:06:16:15:32:07:16:16:32:08:16:17:32:09:16:18:32:0a:16:19:32:0b:16:1a:32:0c:16:1b:32:0d:16:1c:32:0e:16:1d:32:0f:16:1e:32:10:16:20:32:11:16:21:32:12:16:22:51:63
  prelude: (6, 0, 0, 0, 0, 0)
  args: []
  line info: 2c:26:26:26:66:84:07:23:30:24:2a:2b:30:65:84:08:84:07:84:0d:64:20:84:07:84:10:84:0b:84:08:84:2e:64:20:84:07:64:40:64:40:64:40:64:40:64:20:64:20
  80          LOAD_CONST_SMALL_INT 0 
  10:02       LOAD_CONST_STRING DataStruct
  2a:01       BUILD_TUPLE 1
  1b:03       IMPORT_NAME basic
  1c:02       IMPORT_FROM DataStruct
  16:02       STORE_NAME DataStruct
  59          POP_TOP 
  80          LOAD_CONST_SMALL_INT 0 
  51          LOAD_CONST_NONE 
  1b:04       IMPORT_NAME controlBoardAlphaPiOne
  16:04       STORE_NAME controlBoardAlphaPiOne
  80          LOAD_CONST_SMALL_INT 0 
  51          LOAD_CONST_NONE 
  1b:05       IMPORT_NAME neopixel
  16:05       STORE_NAME neopixel
  80          LOAD_CONST_SMALL_INT 0 
  51          LOAD_CONST_NONE 
  1b:06       IMPORT_NAME machine
  16:06       STORE_NAME machine
  80          LOAD_CONST_SMALL_INT 0 
  51          LOAD_CONST_NONE 
  1b:07       IMPORT_NAME time
  16:07       STORE_NAME time
  32:00       MAKE_FUNCTION 0
  16:0c       STORE_NAME NP_write
  8a          LOAD_CONST_SMALL_INT 10 
  17:23       STORE_GLOBAL brightness
  11:05       LOAD_NAME neopixel
  14:08       LOAD_METHOD NeoPixel
  11:06       LOAD_NAME machine
  14:09       LOAD_METHOD Pin
  91          LOAD_CONST_SMALL_INT 17 
  36:01       CALL_METHOD 1
  83          LOAD_CONST_SMALL_INT 3 
  36:02       CALL_METHOD 2
  17:24       STORE_GLOBAL np
  2b:00       BUILD_LIST 0
  16:25       STORE_NAME rawRGB
  12:24       LOAD_GLOBAL np
  13:0a       LOAD_ATTR n
  80          LOAD_CONST_SMALL_INT 0 
  42:57       JUMP 23
  57          DUP_TOP 
  16:26       STORE_NAME i
  11:25       LOAD_NAME rawRGB
  14:0b       LOAD_METHOD insert
  11:26       LOAD_NAME i
  23:00       LOAD_CONST_OBJ (0, 0, 0)
  36:02       CALL_METHOD 2
  59          POP_TOP 
  23:00       LOAD_CONST_OBJ (0, 0, 0)
  12:24       LOAD_GLOBAL np
  11:26       LOAD_NAME i
  56          STORE_SUBSCR 
  81          LOAD_CONST_SMALL_INT 1 
  e5          BINARY_OP 14 __iadd__ 
  58          DUP_TOP_TWO 
  5a          ROT_TWO 
  d7          BINARY_OP 0 __lt__ 
  43:24       POP_JUMP_IF_TRUE -28
  59          POP_TOP 
  59          POP_TOP 
  11:0c       LOAD_NAME NP_write
  34:00       CALL_FUNCTION 0
  59          POP_TOP 
  32:01       MAKE_FUNCTION 1
  16:0f       STORE_NAME BrightnessUp
  32:02       MAKE_FUNCTION 2
  16:11       STORE_NAME SetBrightness
  32:03       MAKE_FUNCTION 3
  16:12       STORE_NAME UpdateBrightness
  32:04       MAKE_FUNCTION 4
  16:13       STORE_NAME GetBrightness
  32:05       MAKE_FUNCTION 5
  16:14       STORE_NAME setPixelColorWithoutWrightRGBOne
  32:06       MAKE_FUNCTION 6
  16:15       STORE_NAME setPixelColorWithoutWright
  32:07       MAKE_FUNCTION 7
  16:16       STORE_NAME setPixelColor
  32:08       MAKE_FUNCTION 8
  16:17       STORE_NAME clamp
  32:09       MAKE_FUNCTION 9
  16:18       STORE_NAME hsl
  32:0a       MAKE_FUNCTION 10
  16:19       STORE_NAME packRGB
  32:0b       MAKE_FUNCTION 11
  16:1a       STORE_NAME packRGBd
  32:0c       MAKE_FUNCTION 12
  16:1b       STORE_NAME unpackR
  32:0d       MAKE_FUNCTION 13
  16:1c       STORE_NAME unpackG
  32:0e       MAKE_FUNCTION 14
  16:1d       STORE_NAME unpackB
  32:0f       MAKE_FUNCTION 15
  16:1e       STORE_NAME set_shake
  32:10       MAKE_FUNCTION 16
  16:20       STORE_NAME stop_shake
  32:11       MAKE_FUNCTION 17
  16:21       STORE_NAME Update
  32:12       MAKE_FUNCTION 18
  16:22       STORE_NAME version
  51          LOAD_CONST_NONE 
  63          RETURN_VALUE 
  children: [NP_write, BrightnessUp, SetBrightness, UpdateBrightness, GetBrightness, setPixelColorWithoutWrightRGBOne, setPixelColorWithoutWright, setPixelColor, clamp, hsl, packRGB, packRGBd, unpackR, unpackG, unpackB, set_shake, stop_shake, Update, version]
simple_name: NP_write
  raw bytecode: 32 10:0c:0c:80:08:20:27:28:12:24:14:0d:36:00:59:12:07:14:0e:81:36:01:59:12:24:14:0d:36:00:59:51:63
  prelude: (3, 0, 0, 0, 0, 0)
  args: []
  line info: 80:08:20:27:28
  12:24       LOAD_GLOBAL np
  14:0d       LOAD_METHOD write
  36:00       CALL_METHOD 0
  59          POP_TOP 
  12:07       LOAD_GLOBAL time
  14:0e       LOAD_METHOD sleep_ms
  81          LOAD_CONST_SMALL_INT 1 
  36:01       CALL_METHOD 1
  59          POP_TOP 
  12:24       LOAD_GLOBAL np
  14:0d       LOAD_METHOD write
  36:00       CALL_METHOD 0
  59          POP_TOP 
  51          LOAD_CONST_NONE 
  63          RETURN_VALUE 
  children: []
simple_name: BrightnessUp
  raw bytecode: 45 29:10:0f:27:80:18:2a:20:26:2c:12:02:b0:34:01:14:10:36:00:c1:12:23:b1:e5:17:23:12:17:80:22:80:64:12:23:34:03:17:23:12:12:34:00:59:51:63
  prelude: (6, 0, 0, 1, 0, 0)
  args: ['br_d']
  line info: 80:18:2a:20:26:2c
  12:02       LOAD_GLOBAL DataStruct
  b0          LOAD_FAST 0 
  34:01       CALL_FUNCTION 1
  14:10       LOAD_METHOD IntValue
  36:00       CALL_METHOD 0
  c1          STORE_FAST 1 
  12:23       LOAD_GLOBAL brightness
  b1          LOAD_FAST 1 
  e5          BINARY_OP 14 __iadd__ 
  17:23       STORE_GLOBAL brightness
  12:17       LOAD_GLOBAL clamp
  80          LOAD_CONST_SMALL_INT 0 
  22:80:64    LOAD_CONST_SMALL_INT 100
  12:23       LOAD_GLOBAL brightness
  34:03       CALL_FUNCTION 3
  17:23       STORE_GLOBAL brightness
  12:12       LOAD_GLOBAL UpdateBrightness
  34:00       CALL_FUNCTION 0
  59          POP_TOP 
  51          LOAD_CONST_NONE 
  63          RETURN_VALUE 
  children: []
simple_name: SetBrightness
  raw bytecode: 37 29:0e:11:27:80:20:2a:20:2b:12:02:b0:34:01:14:10:36:00:c1:12:17:80:22:80:64:b1:34:03:17:23:12:12:34:00:59:51:63
  prelude: (6, 0, 0, 1, 0, 0)
  args: ['br_d']
  line info: 80:20:2a:20:2b
  12:02       LOAD_GLOBAL DataStruct
  b0          LOAD_FAST 0 
  34:01       CALL_FUNCTION 1
  14:10       LOAD_METHOD IntValue
  36:00       CALL_METHOD 0
  c1          STORE_FAST 1 
  12:17       LOAD_GLOBAL clamp
  80          LOAD_CONST_SMALL_INT 0 
  22:80:64    LOAD_CONST_SMALL_INT 100
  b1          LOAD_FAST 1 
  34:03       CALL_FUNCTION 3
  17:23       STORE_GLOBAL brightness
  12:12       LOAD_GLOBAL UpdateBrightness
  34:00       CALL_FUNCTION 0
  59          POP_TOP 
  51          LOAD_CONST_NONE 
  63          RETURN_VALUE 
  children: []
simple_name: UpdateBrightness
  raw bytecode: 86 48:18:12:80:27:20:2b:20:29:29:26:26:26:32:12:23:22:81:7f:f4:22:80:64:f6:c0:12:24:13:0a:80:42:68:57:c1:12:25:b1:55:30:03:c2:c3:c4:b2:b0:f4:88:f1:c2:b3:b0:f4:88:f1:c3:b4:b0:f4:88:f1:c4:b2:b3:b4:2a:03:12:24:b1:56:81:e5:58:5a:d7:43:13:59:59:12:0c:34:00:59:51:63
  prelude: (10, 0, 0, 0, 0, 0)
  args: []
  line info: 80:27:20:2b:20:29:29:26:26:26:32
  12:23       LOAD_GLOBAL brightness
  22:81:7f    LOAD_CONST_SMALL_INT 255
  f4          BINARY_OP 29 __mul__ 
  22:80:64    LOAD_CONST_SMALL_INT 100
  f6          BINARY_OP 31 __floordiv__ 
  c0          STORE_FAST 0 
  12:24       LOAD_GLOBAL np
  13:0a       LOAD_ATTR n
  80          LOAD_CONST_SMALL_INT 0 
  42:68       JUMP 40
  57          DUP_TOP 
  c1          STORE_FAST 1 
  12:25       LOAD_GLOBAL rawRGB
  b1          LOAD_FAST 1 
  55          LOAD_SUBSCR 
  30:03       UNPACK_SEQUENCE 3
  c2          STORE_FAST 2 
  c3          STORE_FAST 3 
  c4          STORE_FAST 4 
  b2          LOAD_FAST 2 
  b0          LOAD_FAST 0 
  f4          BINARY_OP 29 __mul__ 
  88          LOAD_CONST_SMALL_INT 8 
  f1          BINARY_OP 26 __rshift__ 
  c2          STORE_FAST 2 
  b3          LOAD_FAST 3 
  b0          LOAD_FAST 0 
  f4          BINARY_OP 29 __mul__ 
  88          LOAD_CONST_SMALL_INT 8 
  f1          BINARY_OP 26 __rshift__ 
  c3          STORE_FAST 3 
  b4          LOAD_FAST 4 
  b0          LOAD_FAST 0 
  f4          BINARY_OP 29 __mul__ 
  88          LOAD_CONST_SMALL_INT 8 
  f1          BINARY_OP 26 __rshift__ 
  c4          STORE_FAST 4 
  b2          LOAD_FAST 2 
  b3          LOAD_FAST 3 
  b4          LOAD_FAST 4 
  2a:03       BUILD_TUPLE 3
  12:24       LOAD_GLOBAL np
  b1          LOAD_FAST 1 
  56          STORE_SUBSCR 
  81          LOAD_CONST_SMALL_INT 1 
  e5          BINARY_OP 14 __iadd__ 
  58          DUP_TOP_TWO 
  5a          ROT_TWO 
  d7          BINARY_OP 0 __lt__ 
  43:13       POP_JUMP_IF_TRUE -45
  59          POP_TOP 
  59          POP_TOP 
  12:0c       LOAD_GLOBAL NP_write
  34:00       CALL_FUNCTION 0
  59          POP_TOP 
  51          LOAD_CONST_NONE 
  63          RETURN_VALUE 
  children: []
simple_name: GetBrightness
  raw bytecode: 8 00:06:13:80:34:12:23:63
  prelude: (1, 0, 0, 0, 0, 0)
  args: []
  line info: 80:34
  12:23       LOAD_GLOBAL brightness
  63          RETURN_VALUE 
  children: []
simple_name: setPixelColorWithoutWrightRGBOne
  raw bytecode: 39 4a:10:14:28:29:80:38:26:26:26:12:1b:b1:34:01:c2:12:1c:b1:34:01:c3:12:1d:b1:34:01:c4:12:15:b0:b2:b3:b4:34:04:59:51:63
  prelude: (10, 0, 0, 2, 0, 0)
  args: ['index', 'rgb']
  line info: 80:38:26:26:26
  12:1b       LOAD_GLOBAL unpackR
  b1          LOAD_FAST 1 
  34:01       CALL_FUNCTION 1
  c2          STORE_FAST 2 
  12:1c       LOAD_GLOBAL unpackG
  b1          LOAD_FAST 1 
  34:01       CALL_FUNCTION 1
  c3          STORE_FAST 3 
  12:1d       LOAD_GLOBAL unpackB
  b1          LOAD_FAST 1 
  34:01       CALL_FUNCTION 1
  c4          STORE_FAST 4 
  12:15       LOAD_GLOBAL setPixelColorWithoutWright
  b0          LOAD_FAST 0 
  b2          LOAD_FAST 2 
  b3          LOAD_FAST 3 
  b4          LOAD_FAST 4 
  34:04       CALL_FUNCTION 4
  59          POP_TOP 
  51          LOAD_CONST_NONE 
  63          RETURN_VALUE 
  children: []
simple_name: setPixelColorWithoutWright
  raw bytecode: 116 e8:04:24:15:28:2a:2b:2c:80:3f:20:20:2b:26:26:26:28:29:29:54:29:12:23:22:81:7f:f4:22:80:64:f6:c4:b1:b4:f4:88:f1:c5:b2:b4:f4:88:f1:c6:b3:b4:f4:88:f1:c7:b0:12:24:13:0a:db:44:66:12:24:13:0a:80:42:56:57:c8:b5:b6:b7:2a:03:12:24:b8:56:b1:b2:b3:2a:03:12:25:b8:56:81:e5:58:5a:d7:43:25:59:59:42:52:b5:b6:b7:2a:03:12:24:b0:56:b1:b2:b3:2a:03:12:25:b0:56:51:63
  prelude: (14, 0, 0, 4, 0, 0)
  args: ['index', 'r', 'g', 'b']
  line info: 80:3f:20:20:2b:26:26:26:28:29:29:54:29
  12:23       LOAD_GLOBAL brightness
  22:81:7f    LOAD_CONST_SMALL_INT 255
  f4          BINARY_OP 29 __mul__ 
  22:80:64    LOAD_CONST_SMALL_INT 100
  f6          BINARY_OP 31 __floordiv__ 
  c4          STORE_FAST 4 
  b1          LOAD_FAST 1 
  b4          LOAD_FAST 4 
  f4          BINARY_OP 29 __mul__ 
  88          LOAD_CONST_SMALL_INT 8 
  f1          BINARY_OP 26 __rshift__ 
  c5          STORE_FAST 5 
  b2          LOAD_FAST 2 
  b4          LOAD_FAST 4 
  f4          BINARY_OP 29 __mul__ 
  88          LOAD_CONST_SMALL_INT 8 
  f1          BINARY_OP 26 __rshift__ 
  c6          STORE_FAST 6 
  b3          LOAD_FAST 3 
  b4          LOAD_FAST 4 
  f4          BINARY_OP 29 __mul__ 
  88          LOAD_CONST_SMALL_INT 8 
  f1          BINARY_OP 26 __rshift__ 
  c7          STORE_FAST 7 
  b0          LOAD_FAST 0 
  12:24       LOAD_GLOBAL np
  13:0a       LOAD_ATTR n
  db          BINARY_OP 4 __ge__ 
  44:66       POP_JUMP_IF_FALSE 38
  12:24       LOAD_GLOBAL np
  13:0a       LOAD_ATTR n
  80          LOAD_CONST_SMALL_INT 0 
  42:56       JUMP 22
  57          DUP_TOP 
  c8          STORE_FAST 8 
  b5          LOAD_FAST 5 
  b6          LOAD_FAST 6 
  b7          LOAD_FAST 7 
  2a:03       BUILD_TUPLE 3
  12:24       LOAD_GLOBAL np
  b8          LOAD_FAST 8 
  56          STORE_SUBSCR 
  b1          LOAD_FAST 1 
  b2          LOAD_FAST 2 
  b3          LOAD_FAST 3 
  2a:03       BUILD_TUPLE 3
  12:25       LOAD_GLOBAL rawRGB
  b8          LOAD_FAST 8 
  56          STORE_SUBSCR 
  81          LOAD_CONST_SMALL_INT 1 
  e5          BINARY_OP 14 __iadd__ 
  58          DUP_TOP_TWO 
  5a          ROT_TWO 
  d7          BINARY_OP 0 __lt__ 
  43:25       POP_JUMP_IF_TRUE -27
  59          POP_TOP 
  59          POP_TOP 
  42:52       JUMP 18
  b5          LOAD_FAST 5 
  b6          LOAD_FAST 6 
  b7          LOAD_FAST 7 
  2a:03       BUILD_TUPLE 3
  12:24       LOAD_GLOBAL np
  b0          LOAD_FAST 0 
  56          STORE_SUBSCR 
  b1          LOAD_FAST 1 
  b2          LOAD_FAST 2 
  b3          LOAD_FAST 3 
  2a:03       BUILD_TUPLE 3
  12:25       LOAD_GLOBAL rawRGB
  b0          LOAD_FAST 0 
  56          STORE_SUBSCR 
  51          LOAD_CONST_NONE 
  63          RETURN_VALUE 
  children: []
simple_name: setPixelColor
  raw bytecode: 68 5a:18:16:2d:2e:80:4f:20:2a:2a:26:26:26:29:12:02:b0:34:01:14:10:36:00:c2:12:02:b1:34:01:14:10:36:00:c3:12:1b:b3:34:01:c4:12:1c:b3:34:01:c5:12:1d:b3:34:01:c6:12:15:b2:b4:b5:b6:34:04:59:12:0c:34:00:59:51:63
  prelude: (12, 0, 0, 2, 0, 0)
  args: ['index_d', 'rgb_d']
  line info: 80:4f:20:2a:2a:26:26:26:29
  12:02       LOAD_GLOBAL DataStruct
  b0          LOAD_FAST 0 
  34:01       CALL_FUNCTION 1
  14:10       LOAD_METHOD IntValue
  36:00       CALL_METHOD 0
  c2          STORE_FAST 2 
  12:02       LOAD_GLOBAL DataStruct
  b1          LOAD_FAST 1 
  34:01       CALL_FUNCTION 1
  14:10       LOAD_METHOD IntValue
  36:00       CALL_METHOD 0
  c3          STORE_FAST 3 
  12:1b       LOAD_GLOBAL unpackR
  b3          LOAD_FAST 3 
  34:01       CALL_FUNCTION 1
  c4          STORE_FAST 4 
  12:1c       LOAD_GLOBAL unpackG
  b3          LOAD_FAST 3 
  34:01       CALL_FUNCTION 1
  c5          STORE_FAST 5 
  12:1d       LOAD_GLOBAL unpackB
  b3          LOAD_FAST 3 
  34:01       CALL_FUNCTION 1
  c6          STORE_FAST 6 
  12:15       LOAD_GLOBAL setPixelColorWithoutWright
  b2          LOAD_FAST 2 
  b4          LOAD_FAST 4 
  b5          LOAD_FAST 5 
  b6          LOAD_FAST 6 
  34:04       CALL_FUNCTION 4
  59          POP_TOP 
  12:0c       LOAD_GLOBAL NP_write
  34:00       CALL_FUNCTION 0
  59          POP_TOP 
  51          LOAD_CONST_NONE 
  63          RETURN_VALUE 
  children: []
simple_name: clamp
  raw bytecode: 28 23:14:17:2f:30:31:80:5a:25:22:25:22:b2:b0:d7:44:42:b0:63:b2:b1:d8:44:42:b1:63:b2:63
  prelude: (5, 0, 0, 3, 0, 0)
  args: ['minValue', 'maxValue', 'value']
  line info: 80:5a:25:22:25:22
  b2          LOAD_FAST 2 
  b0          LOAD_FAST 0 
  d7          BINARY_OP 0 __lt__ 
  44:42       POP_JUMP_IF_FALSE 2
  b0          LOAD_FAST 0 
  63          RETURN_VALUE 
  b2          LOAD_FAST 2 
  b1          LOAD_FAST 1 
  d8          BINARY_OP 1 __gt__ 
  44:42       POP_JUMP_IF_FALSE 2
  b1          LOAD_FAST 1 
  63          RETURN_VALUE 
  b2          LOAD_FAST 2 
  63          RETURN_VALUE 
  children: []
simple_name: hsl
  raw bytecode: 284 93:10:60:18:32:33:34:80:62:26:26:26:26:2a:2a:39:25:2e:30:2a:22:22:22:25:22:22:25:25:22:22:24:25:22:22:24:25:22:22:24:25:22:22:24:25:22:22:24:2e:24:24:24:12:35:b0:34:01:c0:12:35:b1:34:01:c1:12:35:b2:34:01:c2:b0:22:82:68:f8:c0:12:17:80:22:80:63:b1:34:03:c1:12:17:80:22:80:63:b2:34:03:c2:22:80:64:12:36:82:b2:f4:22:80:64:f3:34:01:f3:b1:f4:88:f0:22:80:ce:10:f6:c3:b0:22:3c:f6:c4:b0:b4:22:3c:f4:f3:22:82:00:f4:22:3c:f6:c5:12:36:b4:82:f8:88:f0:b5:f2:22:82:00:f3:34:01:c6:b3:22:82:00:b6:f3:f4:88:f1:c7:80:c8:80:c9:80:ca:b4:80:d9:44:49:b7:c8:b3:c9:80:ca:42:c1:80:b4:81:d9:44:48:b3:c8:b7:c9:80:ca:42:74:b4:82:d9:44:48:80:c8:b3:c9:b7:ca:42:67:b4:83:d9:44:48:80:c8:b7:c9:b3:ca:42:5a:b4:84:d9:44:48:b7:c8:80:c9:b3:ca:42:4d:b4:85:d9:44:48:b3:c8:80:c9:b7:ca:42:40:b2:82:f4:88:f0:22:80:64:f6:b3:f3:82:f6:cb:b8:bb:f2:cc:b9:bb:f2:cd:ba:bb:f2:ce:12:19:bc:bd:be:34:03:63
  prelude: (19, 0, 0, 3, 0, 0)
  args: ['h', 's', 'l']
  line info: 80:62:26:26:26:26:2a:2a:39:25:2e:30:2a:22:22:22:25:22:22:25:25:22:22:24:25:22:22:24:25:22:22:24:25:22:22:24:25:22:22:24:2e:24:24:24
  12:35       LOAD_GLOBAL round
  b0          LOAD_FAST 0 
  34:01       CALL_FUNCTION 1
  c0          STORE_FAST 0 
  12:35       LOAD_GLOBAL round
  b1          LOAD_FAST 1 
  34:01       CALL_FUNCTION 1
  c1          STORE_FAST 1 
  12:35       LOAD_GLOBAL round
  b2          LOAD_FAST 2 
  34:01       CALL_FUNCTION 1
  c2          STORE_FAST 2 
  b0          LOAD_FAST 0 
  22:82:68    LOAD_CONST_SMALL_INT 360
  f8          BINARY_OP 33 __mod__ 
  c0          STORE_FAST 0 
  12:17       LOAD_GLOBAL clamp
  80          LOAD_CONST_SMALL_INT 0 
  22:80:63    LOAD_CONST_SMALL_INT 99
  b1          LOAD_FAST 1 
  34:03       CALL_FUNCTION 3
  c1          STORE_FAST 1 
  12:17       LOAD_GLOBAL clamp
  80          LOAD_CONST_SMALL_INT 0 
  22:80:63    LOAD_CONST_SMALL_INT 99
  b2          LOAD_FAST 2 
  34:03       CALL_FUNCTION 3
  c2          STORE_FAST 2 
  22:80:64    LOAD_CONST_SMALL_INT 100
  12:36       LOAD_GLOBAL abs
  82          LOAD_CONST_SMALL_INT 2 
  b2          LOAD_FAST 2 
  f4          BINARY_OP 29 __mul__ 
  22:80:64    LOAD_CONST_SMALL_INT 100
  f3          BINARY_OP 28 __sub__ 
  34:01       CALL_FUNCTION 1
  f3          BINARY_OP 28 __sub__ 
  b1          LOAD_FAST 1 
  f4          BINARY_OP 29 __mul__ 
  88          LOAD_CONST_SMALL_INT 8 
  f0          BINARY_OP 25 __lshift__ 
  22:80:ce:10 LOAD_CONST_SMALL_INT 10000
  f6          BINARY_OP 31 __floordiv__ 
  c3          STORE_FAST 3 
  b0          LOAD_FAST 0 
  22:3c       LOAD_CONST_SMALL_INT 60
  f6          BINARY_OP 31 __floordiv__ 
  c4          STORE_FAST 4 
  b0          LOAD_FAST 0 
  b4          LOAD_FAST 4 
  22:3c       LOAD_CONST_SMALL_INT 60
  f4          BINARY_OP 29 __mul__ 
  f3          BINARY_OP 28 __sub__ 
  22:82:00    LOAD_CONST_SMALL_INT 256
  f4          BINARY_OP 29 __mul__ 
  22:3c       LOAD_CONST_SMALL_INT 60
  f6          BINARY_OP 31 __floordiv__ 
  c5          STORE_FAST 5 
  12:36       LOAD_GLOBAL abs
  b4          LOAD_FAST 4 
  82          LOAD_CONST_SMALL_INT 2 
  f8          BINARY_OP 33 __mod__ 
  88          LOAD_CONST_SMALL_INT 8 
  f0          BINARY_OP 25 __lshift__ 
  b5          LOAD_FAST 5 
  f2          BINARY_OP 27 __add__ 
  22:82:00    LOAD_CONST_SMALL_INT 256
  f3          BINARY_OP 28 __sub__ 
  34:01       CALL_FUNCTION 1
  c6          STORE_FAST 6 
  b3          LOAD_FAST 3 
  22:82:00    LOAD_CONST_SMALL_INT 256
  b6          LOAD_FAST 6 
  f3          BINARY_OP 28 __sub__ 
  f4          BINARY_OP 29 __mul__ 
  88          LOAD_CONST_SMALL_INT 8 
  f1          BINARY_OP 26 __rshift__ 
  c7          STORE_FAST 7 
  80          LOAD_CONST_SMALL_INT 0 
  c8          STORE_FAST 8 
  80          LOAD_CONST_SMALL_INT 0 
  c9          STORE_FAST 9 
  80          LOAD_CONST_SMALL_INT 0 
  ca          STORE_FAST 10 
  b4          LOAD_FAST 4 
  80          LOAD_CONST_SMALL_INT 0 
  d9          BINARY_OP 2 __eq__ 
  44:49       POP_JUMP_IF_FALSE 9
  b7          LOAD_FAST 7 
  c8          STORE_FAST 8 
  b3          LOAD_FAST 3 
  c9          STORE_FAST 9 
  80          LOAD_CONST_SMALL_INT 0 
  ca          STORE_FAST 10 
  42:c1:80    JUMP 65
  b4          LOAD_FAST 4 
  81          LOAD_CONST_SMALL_INT 1 
  d9          BINARY_OP 2 __eq__ 
  44:48       POP_JUMP_IF_FALSE 8
  b3          LOAD_FAST 3 
  c8          STORE_FAST 8 
  b7          LOAD_FAST 7 
  c9          STORE_FAST 9 
  80          LOAD_CONST_SMALL_INT 0 
  ca          STORE_FAST 10 
  42:74       JUMP 52
  b4          LOAD_FAST 4 
  82          LOAD_CONST_SMALL_INT 2 
  d9          BINARY_OP 2 __eq__ 
  44:48       POP_JUMP_IF_FALSE 8
  80          LOAD_CONST_SMALL_INT 0 
  c8          STORE_FAST 8 
  b3          LOAD_FAST 3 
  c9          STORE_FAST 9 
  b7          LOAD_FAST 7 
  ca          STORE_FAST 10 
  42:67       JUMP 39
  b4          LOAD_FAST 4 
  83          LOAD_CONST_SMALL_INT 3 
  d9          BINARY_OP 2 __eq__ 
  44:48       POP_JUMP_IF_FALSE 8
  80          LOAD_CONST_SMALL_INT 0 
  c8          STORE_FAST 8 
  b7          LOAD_FAST 7 
  c9          STORE_FAST 9 
  b3          LOAD_FAST 3 
  ca          STORE_FAST 10 
  42:5a       JUMP 26
  b4          LOAD_FAST 4 
  84          LOAD_CONST_SMALL_INT 4 
  d9          BINARY_OP 2 __eq__ 
  44:48       POP_JUMP_IF_FALSE 8
  b7          LOAD_FAST 7 
  c8          STORE_FAST 8 
  80          LOAD_CONST_SMALL_INT 0 
  c9          STORE_FAST 9 
  b3          LOAD_FAST 3 
  ca          STORE_FAST 10 
  42:4d       JUMP 13
  b4          LOAD_FAST 4 
  85          LOAD_CONST_SMALL_INT 5 
  d9          BINARY_OP 2 __eq__ 
  44:48       POP_JUMP_IF_FALSE 8
  b3          LOAD_FAST 3 
  c8          STORE_FAST 8 
  80          LOAD_CONST_SMALL_INT 0 
  c9          STORE_FAST 9 
  b7          LOAD_FAST 7 
  ca          STORE_FAST 10 
  42:40       JUMP 0
  b2          LOAD_FAST 2 
  82          LOAD_CONST_SMALL_INT 2 
  f4          BINARY_OP 29 __mul__ 
  88          LOAD_CONST_SMALL_INT 8 
  f0          BINARY_OP 25 __lshift__ 
  22:80:64    LOAD_CONST_SMALL_INT 100
  f6          BINARY_OP 31 __floordiv__ 
  b3          LOAD_FAST 3 
  f3          BINARY_OP 28 __sub__ 
  82          LOAD_CONST_SMALL_INT 2 
  f6          BINARY_OP 31 __floordiv__ 
  cb          STORE_FAST 11 
  b8          LOAD_FAST 8 
  bb          LOAD_FAST 11 
  f2          BINARY_OP 27 __add__ 
  cc          STORE_FAST 12 
  b9          LOAD_FAST 9 
  bb          LOAD_FAST 11 
  f2          BINARY_OP 27 __add__ 
  cd          STORE_FAST 13 
  ba          LOAD_FAST 10 
  bb          LOAD_FAST 11 
  f2          BINARY_OP 27 __add__ 
  ce          STORE_FAST 14 
  12:19       LOAD_GLOBAL packRGB
  bc          LOAD_FAST 12 
  bd          LOAD_FAST 13 
  be          LOAD_FAST 14 
  34:03       CALL_FUNCTION 3
  63          RETURN_VALUE 
  children: []
simple_name: packRGB
  raw bytecode: 30 2b:0c:19:2a:2b:2c:80:90:b0:22:81:7f:ef:90:f0:b1:22:81:7f:ef:88:f0:ed:b2:22:81:7f:ef:ed:63
  prelude: (6, 0, 0, 3, 0, 0)
  args: ['r', 'g', 'b']
  line info: 80:90
  b0          LOAD_FAST 0 
  22:81:7f    LOAD_CONST_SMALL_INT 255
  ef          BINARY_OP 24 __and__ 
  90          LOAD_CONST_SMALL_INT 16 
  f0          BINARY_OP 25 __lshift__ 
  b1          LOAD_FAST 1 
  22:81:7f    LOAD_CONST_SMALL_INT 255
  ef          BINARY_OP 24 __and__ 
  88          LOAD_CONST_SMALL_INT 8 
  f0          BINARY_OP 25 __lshift__ 
  ed          BINARY_OP 22 __or__ 
  b2          LOAD_FAST 2 
  22:81:7f    LOAD_CONST_SMALL_INT 255
  ef          BINARY_OP 24 __and__ 
  ed          BINARY_OP 22 __or__ 
  63          RETURN_VALUE 
  children: []
simple_name: packRGBd
  raw bytecode: 67 4b:12:1a:37:38:39:80:94:2a:2a:2a:12:02:b0:34:01:14:10:36:00:c3:12:02:b1:34:01:14:10:36:00:c4:12:02:b2:34:01:14:10:36:00:c5:12:02:b3:22:81:7f:ef:90:f0:b4:22:81:7f:ef:88:f0:ed:b5:22:81:7f:ef:ed:34:01:63
  prelude: (10, 0, 0, 3, 0, 0)
  args: ['r_d', 'g_d', 'b_d']
  line info: 80:94:2a:2a:2a
  12:02       LOAD_GLOBAL DataStruct
  b0          LOAD_FAST 0 
  34:01       CALL_FUNCTION 1
  14:10       LOAD_METHOD IntValue
  36:00       CALL_METHOD 0
  c3          STORE_FAST 3 
  12:02       LOAD_GLOBAL DataStruct
  b1          LOAD_FAST 1 
  34:01       CALL_FUNCTION 1
  14:10       LOAD_METHOD IntValue
  36:00       CALL_METHOD 0
  c4          STORE_FAST 4 
  12:02       LOAD_GLOBAL DataStruct
  b2          LOAD_FAST 2 
  34:01       CALL_FUNCTION 1
  14:10       LOAD_METHOD IntValue
  36:00       CALL_METHOD 0
  c5          STORE_FAST 5 
  12:02       LOAD_GLOBAL DataStruct
  b3          LOAD_FAST 3 
  22:81:7f    LOAD_CONST_SMALL_INT 255
  ef          BINARY_OP 24 __and__ 
  90          LOAD_CONST_SMALL_INT 16 
  f0          BINARY_OP 25 __lshift__ 
  b4          LOAD_FAST 4 
  22:81:7f    LOAD_CONST_SMALL_INT 255
  ef          BINARY_OP 24 __and__ 
  88          LOAD_CONST_SMALL_INT 8 
  f0          BINARY_OP 25 __lshift__ 
  ed          BINARY_OP 22 __or__ 
  b5          LOAD_FAST 5 
  22:81:7f    LOAD_CONST_SMALL_INT 255
  ef          BINARY_OP 24 __and__ 
  ed          BINARY_OP 22 __or__ 
  34:01       CALL_FUNCTION 1
  63          RETURN_VALUE 
  children: []
simple_name: unpackR
  raw bytecode: 17 19:0a:1b:29:80:9b:28:b0:90:f1:22:81:7f:ef:c1:b1:63
  prelude: (4, 0, 0, 1, 0, 0)
  args: ['rgb']
  line info: 80:9b:28
  b0          LOAD_FAST 0 
  90          LOAD_CONST_SMALL_INT 16 
  f1          BINARY_OP 26 __rshift__ 
  22:81:7f    LOAD_CONST_SMALL_INT 255
  ef          BINARY_OP 24 __and__ 
  c1          STORE_FAST 1 
  b1          LOAD_FAST 1 
  63          RETURN_VALUE 
  children: []
simple_name: unpackG
  raw bytecode: 17 19:0a:1c:29:80:a0:28:b0:88:f1:22:81:7f:ef:c1:b1:63
  prelude: (4, 0, 0, 1, 0, 0)
  args: ['rgb']
  line info: 80:a0:28
  b0          LOAD_FAST 0 
  88          LOAD_CONST_SMALL_INT 8 
  f1          BINARY_OP 26 __rshift__ 
  22:81:7f    LOAD_CONST_SMALL_INT 255
  ef          BINARY_OP 24 __and__ 
  c1          STORE_FAST 1 
  b1          LOAD_FAST 1 
  63          RETURN_VALUE 
  children: []
simple_name: unpackB
  raw bytecode: 15 19:0a:1d:29:80:a5:26:b0:22:81:7f:ef:c1:b1:63
  prelude: (4, 0, 0, 1, 0, 0)
  args: ['rgb']
  line info: 80:a5:26
  b0          LOAD_FAST 0 
  22:81:7f    LOAD_CONST_SMALL_INT 255
  ef          BINARY_OP 24 __and__ 
  c1          STORE_FAST 1 
  b1          LOAD_FAST 1 
  63          RETURN_VALUE 
  children: []
simple_name: set_shake
  raw bytecode: 28 29:0a:1e:3a:80:aa:2a:12:02:b0:34:01:14:10:36:00:c1:12:04:14:1f:84:b1:36:02:59:51:63
  prelude: (6, 0, 0, 1, 0, 0)
  args: ['shake_d']
  line info: 80:aa:2a
  12:02       LOAD_GLOBAL DataStruct
  b0          LOAD_FAST 0 
  34:01       CALL_FUNCTION 1
  14:10       LOAD_METHOD IntValue
  36:00       CALL_METHOD 0
  c1          STORE_FAST 1 
  12:04       LOAD_GLOBAL controlBoardAlphaPiOne
  14:1f       LOAD_METHOD WritePwm
  84          LOAD_CONST_SMALL_INT 4 
  b1          LOAD_FAST 1 
  36:02       CALL_METHOD 2
  59          POP_TOP 
  51          LOAD_CONST_NONE 
  63          RETURN_VALUE 
  children: []
simple_name: stop_shake
  raw bytecode: 16 18:06:20:80:af:12:04:14:1f:84:80:36:02:59:51:63
  prelude: (4, 0, 0, 0, 0, 0)
  args: []
  line info: 80:af
  12:04       LOAD_GLOBAL controlBoardAlphaPiOne
  14:1f       LOAD_METHOD WritePwm
  84          LOAD_CONST_SMALL_INT 4 
  80          LOAD_CONST_SMALL_INT 0 
  36:02       CALL_METHOD 2
  59          POP_TOP 
  51          LOAD_CONST_NONE 
  63          RETURN_VALUE 
  children: []
simple_name: Update
  raw bytecode: 7 00:06:21:80:b3:51:63
  prelude: (1, 0, 0, 0, 0, 0)
  args: []
  line info: 80:b3
  51          LOAD_CONST_NONE 
  63          RETURN_VALUE 
  children: []
simple_name: version
  raw bytecode: 8 00:06:22:80:b7:23:01:63
  prelude: (1, 0, 0, 0, 0, 0)
  args: []
  line info: 80:b7
  23:01       LOAD_CONST_OBJ 'v_2022_11_01'
  63          RETURN_VALUE 
  children: []
