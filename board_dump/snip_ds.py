from basic import DataStruct
import autoMotionOne as car

def t(name, fn):
    try:
        print(name + " = " + str(fn()))
    except Exception as e:
        print(name + " ERR " + str(e))

t("ds_int", lambda: DataStruct(50).IntValue())
t("ds_ds", lambda: DataStruct(DataStruct(50)).IntValue())
t("ds_str", lambda: DataStruct("50").IntValue())
t("pack_int", lambda: hex(car.packRGBd(255, 255, 255)))
t("pack_ds", lambda: hex(car.packRGBd(DataStruct(255), DataStruct(255), DataStruct(255))))
t("setbr_int", lambda: car.SetBrightness(100))
t("pix_int", lambda: car.setPixelColor(0, car.packRGBd(255, 255, 255)))
print("DONE")
