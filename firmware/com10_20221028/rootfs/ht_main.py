import variable
import time
time.sleep_ms(1000)
import math
import basic
from basic import DataStruct
from basic import wait_time
import controlBoardAlphaPiOne


def Loop1():
    controlBoardAlphaPiOne.openHotspot(DataStruct("aiphapione"), DataStruct("12345678"))
    yield False


loop1 = Loop1()
loop1HasNext = True


def Start(static_buf):
    controlBoardAlphaPiOne.init()
    controlBoardAlphaPiOne.InitBackground_buf(static_buf)
    soundLoop = controlBoardAlphaPiOne.play_record_loop()
    loop1 = Loop1()
    loop1HasNext = True
    while True:
        controlBoardAlphaPiOne.Update()
        next(soundLoop)
        if loop1HasNext:
            loop1HasNext = next(loop1)


