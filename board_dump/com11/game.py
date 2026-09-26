"""打砖块 —— AlphaPi 游戏机（COM11，摇杆手柄硬件）

硬件映射（remoteControlSensorOne.status_list）:
    [0..3]  按键 A/B/C/D，按下为 1
    [4]     摇杆 X，0..1023
    [5]     摇杆 Y，0..1023
    [6..13] 八方向，阈值 <210 或 >810
    [14]    电位器

操作:
    摇杆左右 -> 移动挡板
    按键 A   -> 暂停 / 继续
    按键 B   -> 重新开始

用法（在 REPL 里）:
    import controlBoardAlphaPiOne as c
    c.init()
    import game
    game.run()

注意:
    文字由 controlBoardAlphaPiOne.showStringWithXY 绘制，它内部固定调用
    textzh((x, y), s, TFT.WHITE, sysfont_zh16)，即**字体 16x16、颜色白色**，
    所以一行最多放 10 个字符，提示语必须写短。
"""

import time

import controlBoardAlphaPiOne as c
import remoteControlSensorOne as r

W, H = 160, 128
HUD_H = 18                       # 顶部信息栏高度（字体 16px + 边距）

PAD_W, PAD_H, PAD_Y = 34, 5, 118

BALL_R = 2
BALL_SIZE = BALL_R * 2 + 1

BRICK_W, BRICK_H = 30, 10
BRICK_COLS, BRICK_ROWS = 5, 4
BRICK_X0, BRICK_Y0, BRICK_DY = 5, 22, 11

FRAME_MS = 16                    # 约 60 帧/秒


class Breakout(object):

    def __init__(self):
        self.t = c.tft
        self.colors = [self.t.RED, self.t.YELLOW, self.t.GREEN, self.t.CYAN]
        self.new_game()

    # ---------------- 开局 ----------------
    def new_game(self):
        self.t.fill(self.t.BLACK)
        self.score = 0
        self.lives = 3
        self.paused = False
        self.over = False
        self.btn_a = 0
        self.btn_b = 0
        self.bricks = []
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                self.bricks.append([BRICK_X0 + col * BRICK_W,
                                    BRICK_Y0 + row * BRICK_DY,
                                    True])
        self.draw_bricks()
        self.pad_x = (W - PAD_W) // 2
        self.draw_pad()
        self.new_ball()
        self.draw_hud()

    # ---------------- 绘制 ----------------
    def draw_pad(self):
        self.t.fillrect((self.pad_x, PAD_Y), (PAD_W, PAD_H), self.t.CYAN)

    def erase_pad(self):
        self.t.fillrect((self.pad_x, PAD_Y), (PAD_W, PAD_H), self.t.BLACK)

    def draw_bricks(self):
        for b in self.bricks:
            self.t.fillrect((b[0], b[1]), (BRICK_W - 1, BRICK_H - 1),
                            self.colors[(b[1] - BRICK_Y0) // BRICK_DY])

    def draw_hud(self):
        self.t.fillrect((0, 0), (W, HUD_H), self.t.BLACK)
        c.showStringWithXY(2, 1, 'S%d' % self.score)
        c.showStringWithXY(126, 1, 'L%d' % self.lives)

    def draw_ball(self, color):
        self.t.fillrect((self.bx - BALL_R, self.by - BALL_R),
                        (BALL_SIZE, BALL_SIZE), color)

    def new_ball(self):
        self.bx = W // 2
        self.by = 92
        self.dx = 2
        self.dy = -2
        self.draw_ball(self.t.WHITE)

    def finish(self, msg):
        self.over = True
        self.t.fillrect((0, 54), (W, 20), self.t.BLACK)
        c.showStringWithXY((W - len(msg) * 16) // 2, 55, msg)

    # ---------------- 每帧推进 ----------------
    def step(self):
        if self.over:                         # 结束后不再推进（防止反复扣命）
            return
        self.draw_ball(self.t.BLACK)          # 擦掉旧位置

        self.bx += self.dx
        self.by += self.dy

        # 左右墙
        if self.bx - BALL_R < 0:
            self.bx = BALL_R
            self.dx = -self.dx
        elif self.bx + BALL_R > W - 1:
            self.bx = W - 1 - BALL_R
            self.dx = -self.dx

        # 上沿（信息栏下沿）
        if self.by - BALL_R < HUD_H:
            self.by = HUD_H + BALL_R
            self.dy = -self.dy

        # 挡板
        if (self.dy > 0 and self.by + BALL_R >= PAD_Y
                and self.by - BALL_R <= PAD_Y + PAD_H
                and self.bx + BALL_R >= self.pad_x
                and self.bx - BALL_R <= self.pad_x + PAD_W):
            self.by = PAD_Y - BALL_R
            self.dy = -self.dy
            off = (self.bx - self.pad_x) * 4 // PAD_W - 2   # -2..2
            if off:
                self.dx = off                              # 命中位置决定反弹角

        # 砖块
        for b in self.bricks:
            if (b[2] and self.bx + BALL_R >= b[0]
                    and self.bx - BALL_R <= b[0] + BRICK_W - 1
                    and self.by + BALL_R >= b[1]
                    and self.by - BALL_R <= b[1] + BRICK_H - 1):
                b[2] = False
                self.t.fillrect((b[0], b[1]), (BRICK_W - 1, BRICK_H - 1),
                                self.t.BLACK)
                self.dy = -self.dy
                self.score += 1
                self.draw_hud()
                if self.score == BRICK_COLS * BRICK_ROWS:
                    self.finish('WIN')
                break

        # 掉出底部
        if self.by - BALL_R > H:
            self.lives -= 1
            self.draw_hud()
            if self.lives <= 0:
                self.finish('GAME OVER')
            else:
                self.new_ball()
            return

        self.draw_ball(self.t.WHITE)          # 画到新位置

    # ---------------- 主循环 ----------------
    def loop(self):
        last = time.ticks_ms()
        while True:
            r.Update()
            st = r.status_list

            if st[1] and not self.btn_b:      # B 键：重开
                self.new_game()
            self.btn_b = st[1]

            if st[0] and not self.btn_a:      # A 键：暂停
                self.paused = not self.paused
            self.btn_a = st[0]

            if not self.paused and not self.over:
                nx = st[4] * (W - PAD_W) // 1023
                if nx != self.pad_x:
                    self.erase_pad()
                    self.pad_x = nx
                    self.draw_pad()
                self.step()

            now = time.ticks_ms()
            dt = time.ticks_diff(now, last)
            if dt < FRAME_MS:
                time.sleep_ms(FRAME_MS - dt)
            last = time.ticks_ms()


def run(static_buf=None):
    c.init()
    if static_buf is not None:
        c.InitBackground_buf(static_buf)
    Breakout().loop()
