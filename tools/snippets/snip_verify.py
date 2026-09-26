import network, sys
if "remote_car" in sys.modules:
    del sys.modules["remote_car"]
import remote_car as rc
import controlBoardAlphaPiOne as board
from basic import DataStruct

ap = network.WLAN(network.AP_IF)
sta = network.WLAN(network.STA_IF)
print("AP_ACTIVE=" + str(ap.active()) + " AP_CONN=" + str(ap.isconnected()))
print("STA_ACTIVE=" + str(sta.active()) + " STA_CONN=" + str(sta.isconnected()))

# 注入一条命令，验证识别/取值/执行逻辑
board.receive_message.append("上")
board.receive_map["上"] = "40"
print("HAS_UP=" + str(board.hasBroadcast(DataStruct("上"))))
print("VAL=" + str(board.getBroadcastValue(DataStruct("上"))))
rc.apply("停")
print("APPLY_OK")
print("DONE")
