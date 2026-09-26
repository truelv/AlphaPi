import time

import remoteControlSensorOne as r

for i in range(15):
    r.Update()
    st = r.status_list
    print("btn=%s X=%d Y=%d pot=%d dir=%s" % (st[0:4], st[4], st[5], st[14], st[6:14]))
    time.sleep_ms(120)
print("DONE")
