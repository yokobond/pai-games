"""
Rotation Test for ST7735 Display
Tests 180-degree rotation functionality
"""

from machine import Pin, SPI
import time
import st7735 as st7735

def rotation_test_screen(display):
    """
    Rotation test screen - shows text in different orientations
    
    Args:
        display: ST7735 display object
    """
    # Color definitions
    RED = 0xF800
    GREEN = 0x07E0
    BLUE = 0x001F
    YELLOW = 0xFFE0
    WHITE = 0xFFFF
    BLACK = 0x0000
    
    SCREEN_WIDTH = 128
    SCREEN_HEIGHT = 160
    
    display.fill(BLACK)
    
    # Draw border
    display.rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, WHITE)
    display.rect(5, 5, SCREEN_WIDTH-10, SCREEN_HEIGHT-10, GREEN)
    
    # Draw diagonal lines
    display.line(0, 0, SCREEN_WIDTH-1, SCREEN_HEIGHT-1, RED)
    display.line(SCREEN_WIDTH-1, 0, 0, SCREEN_HEIGHT-1, BLUE)
    
    # Draw center circle
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2
    display.fill_rect(center_x-10, center_y-10, 20, 20, YELLOW)
    
    # Add text
    display.text("ROTATION", 35, 20, WHITE)
    display.text("TEST", 50, 35, WHITE)
    display.text("180 DEG", 40, SCREEN_HEIGHT-40, WHITE)
    
    display.show()

def setup_display_and_test():
    """
    Setup display and run rotation test
    """
    # Display SPI configuration (ST7735S)
    spi = SPI(0, baudrate=20000000, polarity=0, phase=0,
              sck=Pin(2), mosi=Pin(3))
    cs = Pin(6, Pin.OUT)
    dc = Pin(5, Pin.OUT)
    rst = Pin(4, Pin.OUT)
    # BL (backlight) connected to VCC
    
    # Button configuration
    btn_next = Pin(11, Pin.IN, Pin.PULL_UP)
    
    print("180-Degree Rotation Test")
    print("Initializing display with normal orientation...")
    
    # Initialize display with normal orientation
    display_normal = st7735.ST7735(spi, cs=cs, dc=dc, rst=rst, 
                                   width=128, height=160, bgr=False, 
                                   xoffset=2, yoffset=1, rotation=0)
    display_normal.init()
    rotation_test_screen(display_normal)
    
    print("Normal orientation displayed. Connect GPIO 11 to GND to continue...")
    
    # Wait for button press
    while btn_next.value() == 1:
        time.sleep_ms(50)
    # Debounce
    time.sleep_ms(200)
    
    print("Initializing display with 180-degree rotation...")
    
    # Initialize display with 180-degree rotation
    display_rotated = st7735.ST7735(spi, cs=cs, dc=dc, rst=rst, 
                                    width=128, height=160, bgr=False, 
                                    xoffset=2, yoffset=1, rotation=180)
    display_rotated.init()
    rotation_test_screen(display_rotated)
    
    print("180-degree rotation displayed. Connect GPIO 11 to GND to exit...")
    
    # Wait for button press
    while btn_next.value() == 1:
        time.sleep_ms(50)
    
    print("Rotation Test Complete")

if __name__ == "__main__":
    setup_display_and_test()