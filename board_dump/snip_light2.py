import autoMotionOne as car
print("N=" + str(car.np.n))
car.SetBrightness(100)
c = car.packRGBd(255, 255, 255)
for i in range(car.np.n):
    car.setPixelColor(i, c)
print("LIGHT_ON_SENT")
