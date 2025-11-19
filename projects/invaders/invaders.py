"""
Space Invaders Game for Raspberry Pi Pico
MicroPython implementation with ST7735 TFT display
"""
from machine import Pin, PWM, SPI
from st7735 import ST7735
import time
import random
import gc

# 色定義 (RGB565)
BLACK = 0x0000
WHITE = 0xFFFF
RED = 0xF800
GREEN = 0x07E0
YELLOW = 0xFFE0

# ゲーム定数
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 160
FPS = 30
FRAME_TIME = 1.0 / FPS

# スプライトサイズ
PLAYER_WIDTH = 8
PLAYER_HEIGHT = 6
ENEMY_WIDTH = 8
ENEMY_HEIGHT = 8
BULLET_WIDTH = 2
BULLET_HEIGHT = 4

# ゲーム設定
PLAYER_SPEED = 2
BULLET_SPEED = 3
ENEMY_BULLET_SPEED = 2
MAX_PLAYER_BULLETS = 3
ENEMY_COLS = 5
ENEMY_ROWS = 4
ENEMY_SPACING_X = 20
ENEMY_SPACING_Y = 16
ENEMY_MOVE_SPEED = 10
ENEMY_SHOOT_CHANCE = 0.003

class Bullet:
    """弾クラス"""
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction  # 1: 上, -1: 下
        self.active = True
    
    def update(self):
        if self.direction > 0:
            self.y -= BULLET_SPEED
        else:
            self.y += ENEMY_BULLET_SPEED
        
        # 画面外判定
        if self.y < 0 or self.y > SCREEN_HEIGHT:
            self.active = False
    
    def draw(self, display):
        if self.active:
            display.fill_rect(int(self.x), int(self.y), BULLET_WIDTH, BULLET_HEIGHT, WHITE)

class Player:
    """プレイヤークラス"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.bullets = []
    
    def move_left(self):
        self.x = max(0, self.x - PLAYER_SPEED)
    
    def move_right(self):
        self.x = min(SCREEN_WIDTH - PLAYER_WIDTH, self.x + PLAYER_SPEED)
    
    def shoot(self):
        # 最大弾数チェック
        active_bullets = sum(1 for b in self.bullets if b.active)
        if active_bullets < MAX_PLAYER_BULLETS:
            bullet = Bullet(self.x + PLAYER_WIDTH // 2 - 1, self.y - BULLET_HEIGHT, 1)
            self.bullets.append(bullet)
            return True
        return False
    
    def update(self):
        # 弾を更新
        for bullet in self.bullets:
            if bullet.active:
                bullet.update()
        
        # 非アクティブな弾を削除
        self.bullets = [b for b in self.bullets if b.active]
    
    def draw(self, display):
        # シンプルな宇宙船の形
        # 上部
        display.fill_rect(int(self.x + 3), int(self.y), 2, 2, GREEN)
        # 中央部
        display.fill_rect(int(self.x + 1), int(self.y + 2), 6, 2, GREEN)
        # 下部
        display.fill_rect(int(self.x), int(self.y + 4), 8, 2, GREEN)
        
        # 弾を描画
        for bullet in self.bullets:
            bullet.draw(display)

class Enemy:
    """敵クラス"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = True
    
    def draw(self, display):
        if self.active:
            # インベーダーの形
            display.fill_rect(int(self.x + 2), int(self.y), 4, 2, RED)
            display.fill_rect(int(self.x + 1), int(self.y + 2), 6, 2, RED)
            display.fill_rect(int(self.x), int(self.y + 4), 8, 2, RED)
            display.fill_rect(int(self.x), int(self.y + 6), 2, 2, RED)
            display.fill_rect(int(self.x + 6), int(self.y + 6), 2, 2, RED)

class EnemyFormation:
    """敵編隊クラス"""
    def __init__(self):
        self.enemies = []
        self.bullets = []
        self.direction = 1  # 1: 右, -1: 左
        self.move_timer = 0
        self.move_interval = 10  # フレーム数
        self.offset_x = 10
        self.offset_y = 20
        
        # 敵を配置
        for row in range(ENEMY_ROWS):
            for col in range(ENEMY_COLS):
                x = self.offset_x + col * ENEMY_SPACING_X
                y = self.offset_y + row * ENEMY_SPACING_Y
                self.enemies.append(Enemy(x, y))
    
    def update(self):
        self.move_timer += 1
        
        # 横移動
        if self.move_timer >= self.move_interval:
            self.move_timer = 0
            
            # 端の検出
            leftmost = min(e.x for e in self.enemies if e.active)
            rightmost = max(e.x for e in self.enemies if e.active)
            
            if (self.direction > 0 and rightmost >= SCREEN_WIDTH - ENEMY_WIDTH - 5) or \
               (self.direction < 0 and leftmost <= 5):
                # 方向転換と下降
                self.direction *= -1
                for enemy in self.enemies:
                    if enemy.active:
                        enemy.y += 8
            else:
                # 横移動
                for enemy in self.enemies:
                    if enemy.active:
                        enemy.x += self.direction * ENEMY_MOVE_SPEED
        
        # ランダムに弾を発射
        active_enemies = [e for e in self.enemies if e.active]
        if active_enemies and random.random() < ENEMY_SHOOT_CHANCE * len(active_enemies):
            shooter = random.choice(active_enemies)
            bullet = Bullet(shooter.x + ENEMY_WIDTH // 2 - 1, shooter.y + ENEMY_HEIGHT, -1)
            self.bullets.append(bullet)
        
        # 弾を更新
        for bullet in self.bullets:
            if bullet.active:
                bullet.update()
        
        # 非アクティブな弾を削除
        self.bullets = [b for b in self.bullets if b.active]
    
    def draw(self, display):
        for enemy in self.enemies:
            enemy.draw(display)
        
        for bullet in self.bullets:
            bullet.draw(display)
    
    def all_destroyed(self):
        return all(not e.active for e in self.enemies)
    
    def reached_bottom(self):
        return any(e.active and e.y + ENEMY_HEIGHT >= SCREEN_HEIGHT - 20 for e in self.enemies)

class SpaceInvaders:
    """インベーダーゲームメインクラス"""
    def __init__(self):
        # ディスプレイ初期化
        spi = SPI(0, baudrate=20000000, polarity=0, phase=0,
                  sck=Pin(2), mosi=Pin(3))
        self.display = ST7735(spi, cs=Pin(6), dc=Pin(5), rst=Pin(4),
                             width=128, height=160, rotation=180, bgr=False,
                             xoffset=2, yoffset=1)
        self.display.init()
        self.display.fill(BLACK)
        self.display.show()
        
        # ボタン初期化
        self.btn_left = Pin(21, Pin.IN, Pin.PULL_UP)
        self.btn_right = Pin(27, Pin.IN, Pin.PULL_UP)
        self.btn_a = Pin(28, Pin.IN, Pin.PULL_UP)
        self.btn_start = Pin(11, Pin.IN, Pin.PULL_UP)
        
        # ブザー初期化
        self.buzzer = PWM(Pin(0))
        self.buzzer.duty_u16(0)
        
        # ゲーム状態
        self.reset_game()
    
    def reset_game(self):
        """ゲームをリセット"""
        self.player = Player(SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2, SCREEN_HEIGHT - 20)
        self.enemies = EnemyFormation()
        self.score = 0
        self.game_over = False
        self.paused = False
        self.prev_start = 1
        self.prev_a = 1
        gc.collect()
    
    def play_sound(self, freq, duration_ms):
        """効果音を再生"""
        if freq > 0:
            self.buzzer.freq(freq)
            self.buzzer.duty_u16(32768)
            time.sleep_ms(duration_ms)
        self.buzzer.duty_u16(0)
    
    def check_collisions(self):
        """衝突判定"""
        # プレイヤーの弾と敵
        for bullet in self.player.bullets:
            if not bullet.active:
                continue
            for enemy in self.enemies.enemies:
                if not enemy.active:
                    continue
                if (bullet.x < enemy.x + ENEMY_WIDTH and
                    bullet.x + BULLET_WIDTH > enemy.x and
                    bullet.y < enemy.y + ENEMY_HEIGHT and
                    bullet.y + BULLET_HEIGHT > enemy.y):
                    bullet.active = False
                    enemy.active = False
                    self.score += 10
                    self.play_sound(1000, 50)
                    break
        
        # 敵の弾とプレイヤー
        for bullet in self.enemies.bullets:
            if not bullet.active:
                continue
            if (bullet.x < self.player.x + PLAYER_WIDTH and
                bullet.x + BULLET_WIDTH > self.player.x and
                bullet.y < self.player.y + PLAYER_HEIGHT and
                bullet.y + BULLET_HEIGHT > self.player.y):
                self.game_over = True
                self.play_sound(200, 500)
                return
    
    def draw_text(self, text, x, y, color):
        """シンプルなテキスト描画（1文字8x8ピクセル）"""
        # 簡易的な数字とテキスト表示
        for i, char in enumerate(text):
            cx = x + i * 8
            if char.isdigit():
                self.draw_digit(int(char), cx, y, color)
    
    def draw_digit(self, digit, x, y, color):
        """数字を描画（簡易版）"""
        # 0-9の簡易パターン
        patterns = [
            [1,1,1,1,0,1,1,1,1],  # 0
            [0,1,0,0,1,0,0,1,0],  # 1
            [1,1,1,0,1,1,1,0,0],  # 2
            [1,1,1,0,1,1,0,0,1],  # 3
            [1,0,1,1,1,1,0,0,1],  # 4
            [1,1,1,1,1,0,0,0,1],  # 5
            [1,1,1,1,1,0,1,1,1],  # 6
            [1,1,1,0,0,1,0,0,1],  # 7
            [1,1,1,1,1,1,1,1,1],  # 8
            [1,1,1,1,1,1,0,0,1],  # 9
        ]
        
        if 0 <= digit <= 9:
            pattern = patterns[digit]
            for i in range(9):
                if pattern[i]:
                    px = x + (i % 3) * 2
                    py = y + (i // 3) * 2
                    self.display.fill_rect(px, py, 2, 2, color)
    
    def update(self):
        """ゲーム状態を更新"""
        # スタートボタンでポーズ切り替え
        curr_start = self.btn_start.value()
        if self.prev_start == 1 and curr_start == 0:
            if self.game_over:
                self.reset_game()
            else:
                self.paused = not self.paused
        self.prev_start = curr_start
        
        if self.paused or self.game_over:
            return
        
        # プレイヤー操作
        if self.btn_left.value() == 0:
            self.player.move_left()
        if self.btn_right.value() == 0:
            self.player.move_right()
        
        # 弾発射
        curr_a = self.btn_a.value()
        if self.prev_a == 1 and curr_a == 0:
            if self.player.shoot():
                self.play_sound(800, 30)
        self.prev_a = curr_a
        
        # 更新
        self.player.update()
        self.enemies.update()
        
        # 衝突判定
        self.check_collisions()
        
        # 全滅したら新しい編隊を生成
        if self.enemies.all_destroyed():
            self.play_sound(1500, 200)
            self.enemies = EnemyFormation()
            # プレイヤーの弾をクリア
            self.player.bullets = []
            gc.collect()
        
        # 敗北条件
        if self.enemies.reached_bottom():
            self.game_over = True
            self.play_sound(200, 500)
    
    def draw(self):
        """画面を描画"""
        self.display.fill(BLACK)
        
        if not self.game_over:
            self.player.draw(self.display)
            self.enemies.draw(self.display)
            
            # スコア表示
            self.draw_text(str(self.score), 5, 5, YELLOW)
            
            if self.paused:
                # PAUSE表示
                self.display.text("PAUSE", 45, 75, YELLOW)
        else:
            # ゲームオーバー表示
            self.display.fill_rect(15, 60, 98, 50, BLACK)
            self.display.rect(15, 60, 98, 50, RED)
            self.display.text("GAME OVER", 25, 70, RED)
            self.display.text("Score:", 35, 85, WHITE)
            self.draw_text(str(self.score), 45, 95, YELLOW)
        
        # 画面を更新
        self.display.show()
    
    def run(self):
        """メインゲームループ"""
        print("Space Invaders Starting...")
        
        while True:
            frame_start = time.ticks_ms()
            
            self.update()
            self.draw()
            
            # フレームレート制御
            frame_time = time.ticks_diff(time.ticks_ms(), frame_start)
            if frame_time < FRAME_TIME * 1000:
                time.sleep_ms(int(FRAME_TIME * 1000 - frame_time))
            
            # メモリ管理
            if time.ticks_ms() % 5000 < 50:
                gc.collect()