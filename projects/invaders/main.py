"""
Space Invaders Game - Main Entry Point
Raspberry Pi Pico + ST7735 TFT Display
"""
from invaders import SpaceInvaders

if __name__ == "__main__":
    game = SpaceInvaders()
    game.run()