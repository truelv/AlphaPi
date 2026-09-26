import variable
import time
time.sleep_ms(1000)
import math
import basic
from basic import DataStruct
from basic import wait_time
import controlBoardAlphaPiOne
import autoMotionOne


def Loop1():
    controlBoardAlphaPiOne.openHotspot(DataStruct("01"), DataStruct("01"))
    yield False


loop1 = Loop1()
loop1HasNext = True


def Loop2():
    autoMotionOne.set_all_power(DataStruct(50), DataStruct(50))
    controlBoardAlphaPiOne.openHotspot(DataStruct("01"), DataStruct("01"))
    yield False


def Loop2Trigger(first):
    while True:
        if first:
            while controlBoardAlphaPiOne.hasBroadcast(DataStruct("上")):
                yield True
        while not controlBoardAlphaPiOne.hasBroadcast(DataStruct("上")):
            yield True
        break
    yield False


loop2 = None
loop2HasNext = False
loop2Trigger = Loop2Trigger(False)
loop2TriggerHasNext = True


def Loop3():
    autoMotionOne.set_all_power(DataStruct(-50), DataStruct(-50))
    controlBoardAlphaPiOne.openHotspot(DataStruct("01"), DataStruct("01"))
    yield False


def Loop3Trigger(first):
    while True:
        if first:
            while controlBoardAlphaPiOne.hasBroadcast(DataStruct("下")):
                yield True
        while not controlBoardAlphaPiOne.hasBroadcast(DataStruct("下")):
            yield True
        break
    yield False


loop3 = None
loop3HasNext = False
loop3Trigger = Loop3Trigger(False)
loop3TriggerHasNext = True


def Loop4():
    autoMotionOne.set_all_power(DataStruct(50), DataStruct(-50))
    controlBoardAlphaPiOne.openHotspot(DataStruct("01"), DataStruct("01"))
    yield False


def Loop4Trigger(first):
    while True:
        if first:
            while controlBoardAlphaPiOne.hasBroadcast(DataStruct("左")):
                yield True
        while not controlBoardAlphaPiOne.hasBroadcast(DataStruct("左")):
            yield True
        break
    yield False


loop4 = None
loop4HasNext = False
loop4Trigger = Loop4Trigger(False)
loop4TriggerHasNext = True


def Loop5():
    autoMotionOne.set_all_power(DataStruct(-50), DataStruct(50))
    controlBoardAlphaPiOne.openHotspot(DataStruct("01"), DataStruct("01"))
    yield False


def Loop5Trigger(first):
    while True:
        if first:
            while controlBoardAlphaPiOne.hasBroadcast(DataStruct("右")):
                yield True
        while not controlBoardAlphaPiOne.hasBroadcast(DataStruct("右")):
            yield True
        break
    yield False


loop5 = None
loop5HasNext = False
loop5Trigger = Loop5Trigger(False)
loop5TriggerHasNext = True


def Loop6():
    autoMotionOne.stop_motor(DataStruct('2'))
    controlBoardAlphaPiOne.openHotspot(DataStruct("01"), DataStruct("01"))
    yield False


def Loop6Trigger(first):
    while True:
        if first:
            while controlBoardAlphaPiOne.hasBroadcast(DataStruct("停")):
                yield True
        while not controlBoardAlphaPiOne.hasBroadcast(DataStruct("停")):
            yield True
        break
    yield False


loop6 = None
loop6HasNext = False
loop6Trigger = Loop6Trigger(False)
loop6TriggerHasNext = True


def Start(static_buf):
    controlBoardAlphaPiOne.init()
    controlBoardAlphaPiOne.InitBackground_buf(static_buf)
    soundLoop = controlBoardAlphaPiOne.play_record_loop()
    loop1 = Loop1()
    loop1HasNext = True
    loop2 = None
    loop2HasNext = False
    loop2Trigger = Loop2Trigger(False)
    loop2TriggerHasNext = True
    loop3 = None
    loop3HasNext = False
    loop3Trigger = Loop3Trigger(False)
    loop3TriggerHasNext = True
    loop4 = None
    loop4HasNext = False
    loop4Trigger = Loop4Trigger(False)
    loop4TriggerHasNext = True
    loop5 = None
    loop5HasNext = False
    loop5Trigger = Loop5Trigger(False)
    loop5TriggerHasNext = True
    loop6 = None
    loop6HasNext = False
    loop6Trigger = Loop6Trigger(False)
    loop6TriggerHasNext = True
    while True:
        controlBoardAlphaPiOne.Update()
        next(soundLoop)
        autoMotionOne.Update()
        if loop1HasNext:
            loop1HasNext = next(loop1)
        if loop2TriggerHasNext:
            loop2TriggerHasNext = next(loop2Trigger)
            if loop2TriggerHasNext is False and loop2HasNext is False:
                loop2 = Loop2()
                loop2HasNext = True
        if loop2HasNext:
            loop2HasNext = next(loop2)
            if loop2TriggerHasNext is False and loop2HasNext is False:
                loop2Trigger = Loop2Trigger(True)
                loop2TriggerHasNext = True
        if loop3TriggerHasNext:
            loop3TriggerHasNext = next(loop3Trigger)
            if loop3TriggerHasNext is False and loop3HasNext is False:
                loop3 = Loop3()
                loop3HasNext = True
        if loop3HasNext:
            loop3HasNext = next(loop3)
            if loop3TriggerHasNext is False and loop3HasNext is False:
                loop3Trigger = Loop3Trigger(True)
                loop3TriggerHasNext = True
        if loop4TriggerHasNext:
            loop4TriggerHasNext = next(loop4Trigger)
            if loop4TriggerHasNext is False and loop4HasNext is False:
                loop4 = Loop4()
                loop4HasNext = True
        if loop4HasNext:
            loop4HasNext = next(loop4)
            if loop4TriggerHasNext is False and loop4HasNext is False:
                loop4Trigger = Loop4Trigger(True)
                loop4TriggerHasNext = True
        if loop5TriggerHasNext:
            loop5TriggerHasNext = next(loop5Trigger)
            if loop5TriggerHasNext is False and loop5HasNext is False:
                loop5 = Loop5()
                loop5HasNext = True
        if loop5HasNext:
            loop5HasNext = next(loop5)
            if loop5TriggerHasNext is False and loop5HasNext is False:
                loop5Trigger = Loop5Trigger(True)
                loop5TriggerHasNext = True
        if loop6TriggerHasNext:
            loop6TriggerHasNext = next(loop6Trigger)
            if loop6TriggerHasNext is False and loop6HasNext is False:
                loop6 = Loop6()
                loop6HasNext = True
        if loop6HasNext:
            loop6HasNext = next(loop6)
            if loop6TriggerHasNext is False and loop6HasNext is False:
                loop6Trigger = Loop6Trigger(True)
                loop6TriggerHasNext = True


