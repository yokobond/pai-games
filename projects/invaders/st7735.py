"""
ST7735R/ST7735S TFT Display Driver for MicroPython
128x160 pixel display with SPI interface
"""

import time
import framebuf
import micropython

# Viperネイティブコードで超高速バイトスワップ
@micropython.viper
def swap_bytes(dest, src, length: int):
    """RGB565バイトスワップ（ネイティブコード生成で最高速）"""
    d = ptr8(dest)
    s = ptr8(src)
    i = 0
    # 8バイト（4ピクセル）ずつ処理してさらに高速化
    while i < length - 7:
        d[i] = s[i + 1]
        d[i + 1] = s[i]
        d[i + 2] = s[i + 3]
        d[i + 3] = s[i + 2]
        d[i + 4] = s[i + 5]
        d[i + 5] = s[i + 4]
        d[i + 6] = s[i + 7]
        d[i + 7] = s[i + 6]
        i += 8
    # 残りを処理
    while i < length:
        d[i] = s[i + 1]
        d[i + 1] = s[i]
        i += 2

# ST7735 commands
ST7735_NOP = 0x00
ST7735_SWRESET = 0x01
ST7735_SLPOUT = 0x11
ST7735_NORON = 0x13
ST7735_INVOFF = 0x20
ST7735_INVON = 0x21
ST7735_DISPON = 0x29
ST7735_CASET = 0x2A
ST7735_RASET = 0x2B
ST7735_RAMWR = 0x2C
ST7735_COLMOD = 0x3A
ST7735_MADCTL = 0x36
ST7735_FRMCTR1 = 0xB1
ST7735_FRMCTR2 = 0xB2
ST7735_FRMCTR3 = 0xB3
ST7735_INVCTR = 0xB4
ST7735_PWCTR1 = 0xC0
ST7735_PWCTR2 = 0xC1
ST7735_PWCTR3 = 0xC2
ST7735_PWCTR4 = 0xC3
ST7735_PWCTR5 = 0xC4
ST7735_VMCTR1 = 0xC5
ST7735_GMCTRP1 = 0xE0
ST7735_GMCTRN1 = 0xE1

# Color definitions (RGB565 format)
BLACK = 0x0000
BLUE = 0x001F
RED = 0xF800
GREEN = 0x07E0
CYAN = 0x07FF
MAGENTA = 0xF81F
YELLOW = 0xFFE0
WHITE = 0xFFFF

class ST7735:
    def __init__(self, spi, cs, dc, rst, width=128, height=160, bgr=True, xoffset=0, yoffset=0, rotation=0):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.width = width
        self.height = height
        # BGR color ordering flag (most ST7735 displays use BGR)
        # If colors look wrong, try toggling this value
        self.bgr = bgr
        # Display rotation (0, 90, 180, 270 degrees)
        self.rotation = rotation
        # Display RAM offset (common for 128x160 displays: xoffset=2, yoffset=1)
        self.xoffset = xoffset
        self.yoffset = yoffset
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=1)
        self.buffer = bytearray(self.width * self.height * 2)
        self.fbuf = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.RGB565)
        # バイトスワップ用の一時バッファ（常に必要、高速化のため事前確保）
        self.swapped = bytearray(self.width * self.height * 2)
    
    def write_cmd(self, cmd):
        self.dc.value(0)
        self.cs.value(0)
        self.spi.write(bytearray([cmd]))
        self.cs.value(1)
    
    def write_data(self, data):
        self.dc.value(1)
        self.cs.value(0)
        self.spi.write(data)
        self.cs.value(1)
    
    def reset(self):
        self.rst.value(1)
        time.sleep_ms(50)
        self.rst.value(0)
        time.sleep_ms(50)
        self.rst.value(1)
        time.sleep_ms(50)
    
    def init(self):
        self.reset()
        
        # Software reset
        self.write_cmd(ST7735_SWRESET)
        time.sleep_ms(150)
        
        # Out of sleep mode
        self.write_cmd(ST7735_SLPOUT)
        time.sleep_ms(255)
        
        # Frame rate control
        self.write_cmd(ST7735_FRMCTR1)
        self.write_data(bytearray([0x01, 0x2C, 0x2D]))
        
        self.write_cmd(ST7735_FRMCTR2)
        self.write_data(bytearray([0x01, 0x2C, 0x2D]))
        
        self.write_cmd(ST7735_FRMCTR3)
        self.write_data(bytearray([0x01, 0x2C, 0x2D, 0x01, 0x2C, 0x2D]))
        
        # Display inversion control
        self.write_cmd(ST7735_INVCTR)
        self.write_data(bytearray([0x07]))
        
        # Power control
        self.write_cmd(ST7735_PWCTR1)
        self.write_data(bytearray([0xA2, 0x02, 0x84]))
        
        self.write_cmd(ST7735_PWCTR2)
        self.write_data(bytearray([0xC5]))
        
        self.write_cmd(ST7735_PWCTR3)
        self.write_data(bytearray([0x0A, 0x00]))
        
        self.write_cmd(ST7735_PWCTR4)
        self.write_data(bytearray([0x8A, 0x2A]))
        
        self.write_cmd(ST7735_PWCTR5)
        self.write_data(bytearray([0x8A, 0xEE]))
        
        # VCOM control
        self.write_cmd(ST7735_VMCTR1)
        self.write_data(bytearray([0x0E]))
        
        # Inversion off
        self.write_cmd(ST7735_INVOFF)

        # Memory data access control (orientation + RGB/BGR)
        # Set bit 0x08 for BGR ordering (default), clear for RGB ordering
        # Determine MADCTL value based on rotation and color ordering
        if self.rotation == 0:
            madctl = 0xC8 if self.bgr else 0xC0  # Normal orientation
        elif self.rotation == 90:
            madctl = 0x68 if self.bgr else 0x60  # 90 degrees clockwise
        elif self.rotation == 180:
            madctl = 0x08 if self.bgr else 0x00  # 180 degrees
        elif self.rotation == 270:
            madctl = 0xA8 if self.bgr else 0xA0  # 270 degrees clockwise (90 counter-clockwise)
        else:
            # Default to normal orientation if invalid rotation value
            madctl = 0xC8 if self.bgr else 0xC0
        
        self.write_cmd(ST7735_MADCTL)
        self.write_data(bytearray([madctl]))

        # Color mode - 16-bit color
        self.write_cmd(ST7735_COLMOD)
        self.write_data(bytearray([0x05]))
        
        # Normal display on
        self.write_cmd(ST7735_NORON)
        time.sleep_ms(10)
        
        # Display on
        self.write_cmd(ST7735_DISPON)
        time.sleep_ms(100)
        
        self.fill(BLACK)
        self.show()
    
    def set_window(self, x0, y0, x1, y1):
        # Apply display offset to align with physical display
        # Adjust coordinates based on rotation
        if self.rotation == 0:
            x0, x1 = x0 + self.xoffset, x1 + self.xoffset
            y0, y1 = y0 + self.yoffset, y1 + self.yoffset
        elif self.rotation == 90:
            x0, x1 = x0 + self.yoffset, x1 + self.yoffset
            y0, y1 = y0 + self.xoffset, y1 + self.xoffset
            # Swap width and height for 90-degree rotation
            self.width, self.height = self.height, self.width
        elif self.rotation == 180:
            x0, x1 = x0 + self.xoffset, x1 + self.xoffset
            y0, y1 = y0 + self.yoffset, y1 + self.yoffset
        elif self.rotation == 270:
            x0, x1 = x0 + self.yoffset, x1 + self.yoffset
            y0, y1 = y0 + self.xoffset, y1 + self.xoffset
            # Swap width and height for 270-degree rotation
            self.width, self.height = self.height, self.width
        
        self.write_cmd(ST7735_CASET)
        self.write_data(bytearray([0x00, x0, 0x00, x1]))
        
        self.write_cmd(ST7735_RASET)
        self.write_data(bytearray([0x00, y0, 0x00, y1]))
        
        self.write_cmd(ST7735_RAMWR)
    
    def show(self):
        self.set_window(0, 0, self.width - 1, self.height - 1)
        # FrameBufferはRGB565リトルエンディアン形式
        # ST7735はビッグエンディアンを期待するので常にバイトスワップが必要
        # Viperネイティブコードで超高速バイトスワップ
        swap_bytes(self.swapped, self.buffer, len(self.buffer))
        self.write_data(self.swapped)
    
    def fill(self, color):
        self.fbuf.fill(color)
    
    def pixel(self, x, y, color):
        self.fbuf.pixel(x, y, color)
    
    def hline(self, x, y, w, color):
        self.fbuf.hline(x, y, w, color)
    
    def vline(self, x, y, h, color):
        self.fbuf.vline(x, y, h, color)
    
    def line(self, x1, y1, x2, y2, color):
        self.fbuf.line(x1, y1, x2, y2, color)
    
    def rect(self, x, y, w, h, color):
        self.fbuf.rect(x, y, w, h, color)
    
    def fill_rect(self, x, y, w, h, color):
        self.fbuf.fill_rect(x, y, w, h, color)
    
    def text(self, string, x, y, color):
        self.fbuf.text(string, x, y, color)
