import pygame
from pygame.locals import *

from sprites imoprt load_spritesheet

FALLBACK_KEY_MAP = {
    "P1" : {
        "START": K_RETURN,
        "SWORDIE": K_LEFT,
        "BRAWLER": K_DOWN,
        "SPEEDLE": K_RIGHT,
        "QUIT": K_ESCAPE,
    },
    "P2" : {
        "START": K_TAB,
        "SWORDIE": K_a,
        "BRAWLER": K_s,
        "SPEEDLE": K_d,
        "QUIT": K_BACKSPACE,
    }
}

ICONS = load_spritesheet(
    "icons-Sheet.png",
    {
        "icon1": ((0, 0), (64, 64)),
        "icon2": ((64, 0), (64, 64)),
        "icon3": ((128, 0), (64, 64)),
    }
)

def drawn_character_menu():
    surf = pygame.Surface((800, 640))
    # draw the 3 characters icons
    # draw the key / button to pick
    # draw icons for how many characters have been picked
    # draw READY button (lit up if both players have order selected
    return surf

def run(G, KEY_MAP=FALLBACK_KEY_MAP):
    while True:
        for e in pygame.event.get():
            if e.type == QUIT or e.type == KEYDOWN and any(KEY_MAP[p]["QUIT"] for p in ["P1", "P2"]):
                quit()
            if e.type == KEYDOWN:
                pass
        return G
