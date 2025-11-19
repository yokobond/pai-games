"""
Color Test Screen for ST7735 Display
RGB/BGR configuration verification
"""

from machine import Pin, SPI
import time
import st7735 as st7735

def color_test_screen(display, btn_a):
    """
    色確認用テスト画面 - RGB/BGR設定の確認
    
    Args:
        display: ST7735R display object
        btn_a: Button Pin object for input
    """
    # 色定義
    RED = 0xF800
    GREEN = 0x07E0
    BLUE = 0x001F
    BIRD_YELLOW = 0xFFE0
    WHITE = 0xFFFF
    BLACK = 0x0000
    
    SCREEN_WIDTH = 128
    
    display.fill(BLACK)
    
    # カラーバーを表示（上から順に）
    bar_height = 25
    
    # 赤
    display.fill_rect(0, 0, SCREEN_WIDTH, bar_height, RED)
    display.text("RED", 50, 8, WHITE)
    
    # 緑
    display.fill_rect(0, bar_height, SCREEN_WIDTH, bar_height, GREEN)
    display.text("GREEN", 45, bar_height + 8, WHITE)
    
    # 青
    display.fill_rect(0, bar_height * 2, SCREEN_WIDTH, bar_height, BLUE)
    display.text("BLUE", 48, bar_height * 2 + 8, WHITE)
    
    # 黄色
    display.fill_rect(0, bar_height * 3, SCREEN_WIDTH, bar_height, BIRD_YELLOW)
    display.text("YELLOW", 43, bar_height * 3 + 8, BLACK)
    
    # 白
    display.fill_rect(0, bar_height * 4, SCREEN_WIDTH, bar_height, WHITE)
    display.text("WHITE", 45, bar_height * 4 + 8, BLACK)
    
    # 説明テキスト
    display.text("Color Test", 30, bar_height * 5 + 5, WHITE)
    display.text("If RED looks", 25, bar_height * 5 + 20, WHITE)
    display.text("BLUE, change", 25, bar_height * 5 + 30, WHITE)
    display.text("bgr flag", 35, bar_height * 5 + 40, WHITE)
    display.text("Press A", 40, bar_height * 5 + 55, WHITE)
    
    display.show()
    
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
    
    # ボタン待ち
    while True:
        if read_button():
            break
        time.sleep_ms(50)

def setup_display_and_test():
    """
    スタンドアロンでディスプレイをセットアップし、カラーテストを実行
    """
    # ディスプレイ用SPI設定（ST7735S）
    spi = SPI(0, baudrate=20000000, polarity=0, phase=0,
              sck=Pin(2), mosi=Pin(3))
    cs = Pin(6, Pin.OUT)
    dc = Pin(5, Pin.OUT)
    rst = Pin(4, Pin.OUT)
    # BL(バックライト)はVCCに接続
    
    # ボタン設定
    btn_exit = Pin(11, Pin.IN, Pin.PULL_UP)
    
    # ディスプレイ初期化
    # bgr=True: BGR byte order (青が強く表示される場合はFalseに変更)
    # xoffset=2, yoffset=1 で右端と下端のランダムドットを修正
    display = st7735.ST7735(spi, cs=cs, dc=dc, rst=rst, width=128, height=160, bgr=False, xoffset=2, yoffset=1)
    display.init()
    
    print("Color Test Screen - Connect GPIO 11 to GND for exit")
    color_test_screen(display, btn_exit)
    print("Color Test Complete")

if __name__ == "__main__":
    setup_display_and_test()
