import autoMotionOne as car
import time
from basic import DataStruct


def pos(m):
    try:
        return car.get_position(m)
    except Exception as e:
        return "err:" + str(e)


p0 = pos(car.MOTOR_L)
car.set_all_power(DataStruct(-30), DataStruct(-30))   # 后退
time.sleep_ms(700)
car.stop_motor(DataStruct(2))
time.sleep_ms(300)
print("BACK  L %s -> %s" % (p0, pos(car.MOTOR_L)))

l0 = pos(car.MOTOR_L)
r0 = pos(car.MOTOR_R)
car.set_all_power(DataStruct(30), DataStruct(-30))    # 左转
time.sleep_ms(700)
car.stop_motor(DataStruct(2))
time.sleep_ms(300)
print("LEFT  L %s -> %s | R %s -> %s" % (l0, pos(car.MOTOR_L), r0, pos(car.MOTOR_R)))

l1 = pos(car.MOTOR_L)
r1 = pos(car.MOTOR_R)
car.set_all_power(DataStruct(-30), DataStruct(30))    # 右转
time.sleep_ms(700)
car.stop_motor(DataStruct(2))
time.sleep_ms(300)
print("RIGHT L %s -> %s | R %s -> %s" % (l1, pos(car.MOTOR_L), r1, pos(car.MOTOR_R)))
print("DONE")
