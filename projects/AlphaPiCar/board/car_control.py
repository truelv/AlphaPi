# car_control.py  —— AlphaPi-One 小车「轮子 + 爪子」控制示例
#
# 依赖板子自带的车体运动库 autoMotionOne（I2C 0x20 电机控制器）。
# 用法（任选其一）：
#   A. REPL 里：Ctrl-C 停掉主程序后，执行：
#        import car_control
#        car_control.forward(50, 1)     # 前进 1 秒
#        car_control.claw_close()       # 合爪
#   B. 自动运行：把本文件传到板子根目录，然后新建/修改 main.py 内容为：
#        import car_control
#        car_control.demo()
#
# 注意：speed 取 -100 ~ 100（内部 ×10，限幅 ±1000）。正=前进，负=后退。

import time
import autoMotionOne as car
from basic import DataStruct


# ---------- 轮子：底盘运动 ----------
def wheels(l, r):
    """左右轮分别给速度：l / r 取 -100 ~ 100。"""
    car.set_all_power(DataStruct(int(l)), DataStruct(int(r)))


def forward(speed=50, t=1.0):
    """前进 speed 档，持续 t 秒。"""
    wheels(speed, speed)
    time.sleep(t)


def backward(speed=50, t=1.0):
    """后退。"""
    wheels(-speed, -speed)
    time.sleep(t)


def turn_left(speed=50, t=1.0):
    """原地左转（左轮反转/右轮正转）。"""
    wheels(speed, -speed)
    time.sleep(t)


def turn_right(speed=50, t=1.0):
    """原地右转。"""
    wheels(-speed, speed)
    time.sleep(t)


def stop():
    """左右轮停止。"""
    car.stop_motor(DataStruct(2))   # 2 既不是 0 也不是 1 -> 两轮都停


# ---------- 爪子：Z 轴电机 ----------
def claw_close():
    """合爪（Z 轴一个方向，功率 700）。"""
    car.set_claw(DataStruct(1))


def claw_open():
    """开爪（Z 轴相反方向）。"""
    car.set_claw(DataStruct(0))


def claw_stop():
    """停止 Z 轴（避免持续堵转）。"""
    car.set_raw_power(car.MOTOR_Z, 0)


# ---------- 演示 ----------
def demo():
    print("forward")
    forward(50, 1); stop(); time.sleep(0.5)
    print("backward")
    backward(50, 1); stop(); time.sleep(0.5)
    print("turn left")
    turn_left(50, 0.8); stop(); time.sleep(0.5)
    print("turn right")
    turn_right(50, 0.8); stop(); time.sleep(0.5)
    print("claw open/close")
    claw_open(); time.sleep(1.0); claw_stop(); time.sleep(0.4)
    claw_close(); time.sleep(1.0); claw_stop()
    print("done")


if __name__ == "__main__":
    demo()
