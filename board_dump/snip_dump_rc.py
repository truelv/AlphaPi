d = open("remote_car.py", "rb").read()
print("LEN=%d" % len(d))
print("HEAD=" + repr(d[:100]))
print("TAIL=" + repr(d[-100:]))
print("HAS_DEF_APPLY=" + str(b"def apply" in d))
print("HAS_GET_BUFFER=" + str(b"def get_buffer" in d))
print("HAS_MAIN=" + str(b"def main" in d))
import sys
print("IN_SYSMOD=" + str("remote_car" in sys.modules))
