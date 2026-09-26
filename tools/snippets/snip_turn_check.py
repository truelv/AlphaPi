import remote_car as rc
import autoMotionOne as car
import time
from basic import DataStruct


def p(m):
    try:
        return car.get_position(m)
    except Exception as e:
        return "err"


l0 = p(car.MOTOR_L); r0 = p(car.MOTOR_R)
rc.apply("左")
time.sleep_ms(700)
car.stop_motor(DataStruct(2))
time.sleep_ms(250)
print("AFTER_LEFT  L %s->%s | R %s->%s" % (l0, p(car.MOTOR_L), r0, p(car.MOTOR_R)))

l1 = p(car.MOTOR_L); r1 = p(car.MOTOR_R)
rc.apply("右")
time.sleep_ms(700)
car.stop_motor(DataStruct(2))
time.sleep_ms(250)
print("AFTER_RIGHT L %s->%s | R %s->%s" % (l1, p(car.MOTOR_L), r1, p(car.MOTOR_R)))
print("DONE")
