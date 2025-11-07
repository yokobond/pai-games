"""
Flappy Bird Game for Raspberry Pi Pico
128x160 TFT Display with ST7735R
"""

from machine import Pin, SPI, PWM
import time
import random
import st7735

# ハードウェア設定
# ディスプレイ用SPI設定（ST7735S）
spi = SPI(0, baudrate=20000000, polarity=0, phase=0,
          sck=Pin(2), mosi=Pin(3))
cs = Pin(6, Pin.OUT)
dc = Pin(5, Pin.OUT)
rst = Pin(4, Pin.OUT)
# BL(バックライト)はVCCに接続

# ボタン設定
btn_a = Pin(8, Pin.IN, Pin.PULL_UP)  # ジャンプボタン

# ブザー設定
buzzer = PWM(Pin(22))

# ディスプレイ初期化
# Some ST7735 modules use BGR byte order. If your display shows
# a strong blue tint, set bgr=False to use RGB ordering.
# xoffset=2, yoffset=1 で右端と下端のランダムドットを修正
display = st7735.ST7735R(spi, cs=cs, dc=dc, rst=rst, width=128, height=160, bgr=False, xoffset=2, yoffset=1)
display.init()

# ゲーム定数
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 160
BIRD_SIZE = 8
PIPE_WIDTH = 20
PIPE_GAP = 40
PIPE_SPEED = 2
GRAVITY = 1
JUMP_STRENGTH = -6

# 色定義
SKY_BLUE = 0x5D9F
GROUND_GREEN = 0x2C40
BIRD_YELLOW = 0xFFE0
PIPE_GREEN = 0x2C40
WHITE = 0xFFFF
BLACK = 0x0000
RED = 0xF800
GREEN = 0x07E0
BLUE = 0x001F

class Bird:
    def __init__(self):
        self.x = 30
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.size = BIRD_SIZE
    
    def jump(self):
        self.velocity = JUMP_STRENGTH
        play_sound(600, 50)  # ジャンプ音
    
    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        
        # 画面外に出ないように制限
        if self.y < 0:
            self.y = 0
            self.velocity = 0
        if self.y > SCREEN_HEIGHT - self.size:
            self.y = SCREEN_HEIGHT - self.size
            self.velocity = 0
    
    def draw(self):
        display.fill_rect(self.x, self.y, self.size, self.size, BIRD_YELLOW)
        # 目を描画
        display.fill_rect(self.x + 5, self.y + 2, 2, 2, BLACK)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.gap_y = random.randint(30, SCREEN_HEIGHT - PIPE_GAP - 30)
        self.width = PIPE_WIDTH
        self.scored = False
    
    def update(self):
        self.x -= PIPE_SPEED
    
    def draw(self):
        # 上のパイプ
        display.fill_rect(self.x, 0, self.width, self.gap_y, PIPE_GREEN)
        display.rect(self.x, 0, self.width, self.gap_y, WHITE)
        
        # 下のパイプ
        bottom_y = self.gap_y + PIPE_GAP
        bottom_height = SCREEN_HEIGHT - bottom_y
        display.fill_rect(self.x, bottom_y, self.width, bottom_height, PIPE_GREEN)
        display.rect(self.x, bottom_y, self.width, bottom_height, WHITE)
    
    def is_offscreen(self):
        return self.x + self.width < 0
    
    def collides_with(self, bird):
        # 鳥がパイプの横の範囲内にいるか
        if bird.x + bird.size > self.x and bird.x < self.x + self.width:
            # 上のパイプまたは下のパイプに当たったか
            if bird.y < self.gap_y or bird.y + bird.size > self.gap_y + PIPE_GAP:
                return True
        return False

def play_sound(frequency, duration):
    """ブザーで音を鳴らす"""
    try:
        buzzer.freq(frequency)
        buzzer.duty_u16(32768)  # 50% duty cycle
        time.sleep_ms(duration)
        buzzer.duty_u16(0)
    except Exception:
        pass

# ボタンの前回の状態を記憶
button_state = {"prev": 1}

def read_button():
    """ボタン入力を読み取る（押した瞬間のみ検出）"""
    current = btn_a.value()
    # 前回が押されていない(1)で、今回押されている(0)場合のみTrue
    if button_state["prev"] == 1 and current == 0:
        button_state["prev"] = current
        return True
    button_state["prev"] = current
    return False

def draw_background():
    """背景を描画"""
    # 空
    display.fill_rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT - 20, SKY_BLUE)
    # 地面
    display.fill_rect(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20, GROUND_GREEN)

def game_over_screen(score):
    """ゲームオーバー画面"""
    display.fill_rect(20, 60, 88, 40, BLACK)
    display.rect(20, 60, 88, 40, RED)
    display.text("GAME OVER", 25, 70, RED)
    display.text("Score: " + str(score), 30, 85, WHITE)
    display.show()
    
    # ゲームオーバー音
    play_sound(300, 100)
    time.sleep_ms(100)
    play_sound(200, 100)
    time.sleep_ms(100)
    play_sound(100, 200)
    
    # リスタート待ち
    display.text("Press A", 35, 110, WHITE)
    display.show()
    
    while True:
        if read_button():
            break
        time.sleep_ms(50)

def title_screen():
    """タイトル画面"""
    display.fill(SKY_BLUE)
    display.text("FLAPPY BIRD", 20, 50, BIRD_YELLOW)
    display.text("Press A", 35, 90, WHITE)
    display.text("to Start", 30, 105, WHITE)
    display.show()
    
    while True:
        if read_button():
            break
        time.sleep_ms(50)

def main_game():
    """メインゲームループ"""
    bird = Bird()
    pipes = [Pipe(SCREEN_WIDTH + i * 80) for i in range(3)]
    score = 0
    
    while True:
        # 入力処理
        if read_button():
            bird.jump()
        
        # 更新処理
        bird.update()
        
        for pipe in pipes:
            pipe.update()
            
            # スコア処理
            if not pipe.scored and pipe.x + pipe.width < bird.x:
                pipe.scored = True
                score += 1
                play_sound(800, 50)  # スコア音
            
            # 衝突判定
            if pipe.collides_with(bird):
                return score
        
        # 地面との衝突
        if bird.y >= SCREEN_HEIGHT - 20 - bird.size:
            return score
        
        # パイプの再生成
        if pipes[0].is_offscreen():
            pipes.pop(0)
            pipes.append(Pipe(pipes[-1].x + 80))
        
        # 描画処理
        draw_background()
        
        for pipe in pipes:
            pipe.draw()
        
        bird.draw()
        
        # スコア表示
        display.text("Score:" + str(score), 5, 5, WHITE)
        
        display.show()
        
        # フレームレート制御
        time.sleep_ms(30)

def main():
    """メイン関数"""
    print("Flappy Bird starting...")
    
    while True:
        title_screen()
        score = main_game()
        game_over_screen(score)

# ゲーム開始
if __name__ == "__main__":
    main()
