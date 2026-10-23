import controlBoardAlphaPiOne as cb

# PCM 模式录 8 秒（adpcm=False），用户需在此期间拍手
cb.rec("clap.dat", 8, False)
