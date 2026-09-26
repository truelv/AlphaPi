import network
import controlBoardAlphaPiOne as board
from basic import DataStruct

print("STA_CONN=" + str(network.WLAN(network.STA_IF).isconnected()))
print("HAS_broadcastWithValue=" + str(hasattr(board, "broadcastWithValue")))
try:
    board.broadcastWithValue(DataStruct("ack"), DataStruct("停"))
    print("ACK_SENT")
except Exception as e:
    print("ACK_ERR " + type(e).__name__ + " " + str(e))
print("DONE")
