import sys
if "remote_car" in sys.modules:
    del sys.modules["remote_car"]
import remote_car
print("ATTRS=" + ",".join(sorted([a for a in dir(remote_car) if not a.startswith("_")])))
print("HAS_APPLY=" + str(hasattr(remote_car, "apply")))
print("HAS_MAIN=" + str(hasattr(remote_car, "main")))
print("HAS_RUN=" + str(hasattr(remote_car, "run")))
