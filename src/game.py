"""
Super Fight Punch
3 character platform fighter
no stage offs, health bar
"""

import pygame
from pygame.locals import *

W, H = 800, 640

def set_up():
    G = {}
    G["SCREEN"] = pygame.display.set_mode(())
    G["MENU"] = True
    G["PAUSE"] = False
    
    return G

def run(G):
    
