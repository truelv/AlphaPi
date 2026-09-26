import autoMotionOne as car
from basic import DataStruct
print("NP=" + str(car.np))
print("N=" + str(car.np.n))
c = car.packRGBd(DataStruct(255), DataStruct(255), DataStruct(255))
print("COLOR=" + hex(c))
car.SetBrightness(DataStruct(100))
for i in range(car.np.n):
    car.setPixelColor(DataStruct(i), DataStruct(c))
print("LIGHT_ON_OK")
