import control_board_v1
import actuator_led
import sensor_infrared
import variable
import time
import math
import basic
from basic import DataStruct
from basic import wait_time


control_board_v1.led_show_bytes(bytearray([0x00, 0x00, 0x00, 0x00, 0x00]))
soundLoop = control_board_v1.play_record_loop()


def Loop1():
    actuator_led.InitNP(5)
    while True:
        if (((DataStruct(sensor_infrared.read_infrared_sensor(4))) == (DataStruct("1")))).BoolValue():
            actuator_led.setPixelColor((DataStruct(1)) - 1, DataStruct(16777215))
            actuator_led.setPixelColor((DataStruct(13)) - 1, DataStruct(16777215))
            actuator_led.setPixelColor((DataStruct(14)) - 1, DataStruct(16777215))
            actuator_led.setPixelColor((DataStruct(7)) - 1, DataStruct(16777215))
            play_loop = control_board_v1.playUntilDone("r1.dat")
            play_loop_has_next = True
            while (play_loop_has_next):
                play_loop_has_next = next(play_loop)
                yield True
            yield True
        else:
            actuator_led.setPixelColor((DataStruct(15)) - 1 , DataStruct(0))
            yield True
        yield True
    yield False


loop1 = Loop1()
loop1HasNext = True


while True:
    control_board_v1.UpdateButtonStatus()
    next(soundLoop)
    if loop1HasNext:
        loop1HasNext = next(loop1)


