"""
Super Fight Punch
3 character platform fighter
no stage offs, health bar
"""

import pygame
from pygame.locals import *

import sys

W, H = 800, 640

def set_up():
    G = {}
    if "-f" in sys.argv:
        G["SCREEN"] = pygame.display.set_mode((W, H), FULLSCREEN)
    else:
        G["SCREEN"] = pygame.display.set_mode((W, H))
    G["MENU"] = True
    G["PAUSE"] = False
    
    return G

def run(G):
    return
