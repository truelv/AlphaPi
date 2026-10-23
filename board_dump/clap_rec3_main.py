import time
import controlBoardAlphaPiOne as cb
from basic import DataStruct

cb.set_volume(DataStruct(100))

# 三段 15 秒 PCM 录音窗口，中间播放出厂提示音（两种通路各一次）
cb.rec("c1.dat", 15, False)
cb.play("alert.dat", False)   # 0x15 原始 PCM 通路
cb.play("alert.dat", True)    # 0x16 ADPCM 通路
cb.rec("c2.dat", 15, False)
cb.play("alert.dat", False)
cb.play("alert.dat", True)
cb.rec("c3.dat", 15, False)
cb.play("alert.dat", False)
cb.play("alert.dat", True)
