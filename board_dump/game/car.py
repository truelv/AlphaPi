from machine import I2C, SoftI2C, Pin
import uctypes
import time

i2c = I2C(1, scl=Pin(9), sda=Pin(8), freq=100000)
# i2c = SoftI2C(scl=Pin(9), sda=Pin(8), freq=100000)
CAR_ADDR = 32
MOTOR_L = 0x20
MOTOR_R = 0x10
MOTOR_Z = 0x30

i2c.scan()

# print(i2c.scan())


def speed_mode(l: bool = True, r: bool = True):
    data = bytearray(2)
    if l:
        data[0] = 1
    i2c.writeto_mem(CAR_ADDR, MOTOR_L + 12, data)
    if not r:
        data[0] = 0
    i2c.writeto_mem(CAR_ADDR, MOTOR_R + 12, data)


def set_speed(motor, speed: int):
    # print("set " + str(motor) + " with speed " + str(speed))
    if (speed > 1024):
        speed = 1024
    if (speed < -1024):
        speed = -1024
    data = speed.to_bytes(4, 'little')
    i2c.writeto_mem(CAR_ADDR, motor + 0, data)


def set_power(motor, power: int):
    if (power > 1024):
        power = 1024
    if (power < -1024):
        power = -1024
    data = power.to_bytes(2, 'little')
    i2c.writeto_mem(CAR_ADDR, motor + 4, data)


def set_ON_OFF(motor, ON_OFF_MODE: num):
    data = ON_OFF_MODE.to_bytes(2, 'little')
    i2c.writeto_mem(CAR_ADDR, motor + 12, data)


def stop(motor):
    set_speed(motor, 0)


def position_mode(pos_mode: bool = True):
    speed_mode(True, True)


def get_position(motor):
    data = i2c.readfrom_mem(CAR_ADDR, motor + 8, 4)
    pos = int.from_bytes(data, 'little', True)
    if (pos >= 0x80000000):
        pos = pos - 0x100000000
    return pos


def position_pid_poll(motor, target_pos, vel):
    data = i2c.readfrom_mem(CAR_ADDR, motor + 8, 4)
    pos = int.from_bytes(data, 'little', True)
    if (pos >= 0x80000000):
        pos = pos - 0x100000000
    error = pos - target_pos
    #     print(error)

    if -error > vel:
        error = -vel
    if error > vel:
        error = vel

    set_speed(motor, -error)
    if abs(error) < 30:
        set_speed(motor, 0)
        return True
    else:
        return False


def demo_run_to(l, r, vel):
    position_mode()
    done_l = False
    done_r = False
    while (True):
        if (not done_l):
            done_l = position_pid_poll(MOTOR_L, l, vel)
        if (not done_r):
            done_r = position_pid_poll(MOTOR_R, r, vel)
        time.sleep_ms(30)
        # print(str(get_position(MOTOR_L)) + '_' + str(get_position(MOTOR_R)))
        if (done_l and done_r):
            break


# print("HT_CAR 0815")

def read_bottom_adc():
    data = i2c.readfrom_mem(CAR_ADDR + 1, 0, 12)
    line_sensors = [0] * 6
    for i in range(0, 6):
        line_sensors[i] = (data[i * 2] + data[i * 2 + 1] * 256) >> 2
    return line_sensors;


def set_bottom_rgb(r, g, b):
    data = bytearray(4)
    data[0] = g
    data[1] = r
    data[2] = b
    data = i2c.writeto_mem(CAR_ADDR + 1, 0x10, data)


def demo_get_bottom_color():
    set_bottom_rgb(255, 0, 0)
    time.sleep_ms(100)
    adc_r = read_bottom_adc()[5]
    set_bottom_rgb(0, 255, 0)
    time.sleep_ms(100)
    adc_g = read_bottom_adc()[5]
    set_bottom_rgb(0, 0, 255)
    time.sleep_ms(100)
    adc_b = read_bottom_adc()[5]
    set_bottom_rgb(0, 0, 0)
    time.sleep_ms(100)
    adc_d = read_bottom_adc()[5]
    # print(adc_r - adc_d)
    # print(adc_g - adc_d)
    # print(adc_b - adc_d)
    # print('--------')


def Read_RFID_ID():
    data_cmd = bytearray(2)
    data_cmd[0] = 1
    i2c.writeto_mem(CAR_ADDR + 1, 0x20 + 14, data_cmd)

    data_len = bytearray(2)
    data_len[0] = 12
    i2c.writeto_mem(CAR_ADDR + 1, 0x20 + 12, data_len)

    for i in range(5):
        cmd = i2c.readfrom_mem(CAR_ADDR + 1, 0x20 + 14, 2)
        num = int.from_bytes(cmd, 'little', True)
        time.sleep(0.1)

    if num == 0:
        # ID = i2c.readfrom_mem(CAR_ADDR+1, 0x20, 2)
        # print(ID)
        return True
    else:
        return False


space_byte = " ".encode('UTF-8')


def Write_RFID_bytes(content):
    # mid_con = content.encode('UTF-8')
    data = bytearray(12)
    if len(content) > 12:
        for i in range(12):
            data[i] = content[i]
    else:
        for i in range(len(content)):
            data[i] = content[i]
        for i in range(12-len(content)):
            data[len(content) + i] = space_byte[0]
    i2c.writeto_mem(CAR_ADDR + 1, 0x20, data)

    data_len = bytearray(2)
    data_len[0] = 12
    i2c.writeto_mem(CAR_ADDR + 1, 0x20 + 12, data_len)

    data_cmd = bytearray(2)
    data_cmd[0] = 3
    i2c.writeto_mem(CAR_ADDR + 1, 0x20 + 14, data_cmd)
    while True:
        cmd = i2c.readfrom_mem(CAR_ADDR + 1, 0x20 + 14, 2)
        num = int.from_bytes(cmd, 'little', True)
        if num == 0:
            break


def Read_RFID_bytes():
    data_cmd = bytearray(2)
    data_cmd[0] = 2
    i2c.writeto_mem(CAR_ADDR + 1, 0x20 + 14, data_cmd)

    data_len = bytearray(2)
    data_len[0] = 12
    i2c.writeto_mem(CAR_ADDR + 1, 0x20 + 12, data_len)

    while (True):
        cmd = i2c.readfrom_mem(CAR_ADDR + 1, 0x20 + 14, 2)
        num = int.from_bytes(cmd, 'little', True)
        if num == 0:
            break
        time.sleep_ms(100)

    data = i2c.readfrom_mem(CAR_ADDR + 1, 0x20, 12)
    return data
