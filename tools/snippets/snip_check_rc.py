import remote_car
print("FSIZE=" + str(len(open("remote_car.py", "rb").read())))
print("ATTRS=" + ",".join(sorted([a for a in dir(remote_car) if not a.startswith("_")])))
try:
    print("HAS_APPLY=" + str(hasattr(remote_car, "apply")))
except Exception as e:
    print("E=" + str(e))
