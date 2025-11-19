"""
Button Pin Assignment Test Program
Press each button to see the result in serial console
"""
from machine import Pin
import time

# Button pin assignments (based on HARDWARE.md)
buttons = {
    'UP': Pin(23, Pin.IN, Pin.PULL_UP),
    'DOWN': Pin(26, Pin.IN, Pin.PULL_UP),
    'LEFT': Pin(21, Pin.IN, Pin.PULL_UP),
    'RIGHT': Pin(27, Pin.IN, Pin.PULL_UP),
    'A': Pin(28, Pin.IN, Pin.PULL_UP),
    'B': Pin(29, Pin.IN, Pin.PULL_UP),
    'START': Pin(11, Pin.IN, Pin.PULL_UP),
    'SELECT': Pin(10, Pin.IN, Pin.PULL_UP),
}

# Onboard LED for visual feedback
led = Pin(25, Pin.OUT)

# Track previous button states (for debouncing)
last_state = {name: 1 for name in buttons.keys()}
last_press_time = {name: 0 for name in buttons.keys()}

# Debounce delay in milliseconds
DEBOUNCE_MS = 50

print("=" * 40)
print("Button Pin Assignment Test")
print("=" * 40)
print("Press each button to test")
print("-" * 40)
print("Button assignments:")
for name, pin in buttons.items():
    print("  {:<8s}: GPIO {}".format(name, pin))
print("-" * 40)
print("Press Ctrl+C to exit")
print("=" * 40)
print()

try:
    while True:
        current_time = time.ticks_ms()
        
        for name, button in buttons.items():
            current_state = button.value()
            
            # Detect button press (1->0 transition)
            if last_state[name] == 1 and current_state == 0:
                # Debounce: check if enough time has passed since last press
                if time.ticks_diff(current_time, last_press_time[name]) > DEBOUNCE_MS:
                    print("[OK] {:<8s} button pressed (GPIO {})".format(name, button))
                    led.on()  # Turn on LED
                    last_press_time[name] = current_time
            
            # Detect button release (0->1 transition)
            elif last_state[name] == 0 and current_state == 1:
                led.off()  # Turn off LED
            
            last_state[name] = current_state
        
        time.sleep_ms(10)  # Reduce CPU load

except KeyboardInterrupt:
    print("\n" + "=" * 40)
    print("Test completed")
    print("=" * 40)
    led.off()
