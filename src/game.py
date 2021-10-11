"""
Super Fight Punch
3 character platform fighter
no stage offs, health bar
"""

import pygame
from pygame.locals import *
pygame.init()

import sys

W, H = 800, 640

def set_up():
    G = {}
    if "-f" in sys.argv:
        G["SCREEN"] = pygame.display.set_mode((W, H), FULLSCREEN)
    else:
        G["SCREEN"] = pygame.display.set_mode((W, H))
    G["W"], G["H"] = W, H    
    G["HEL16"] = pygame.font.SysFont("Helvetica", 16)
    G["HEL32"] = pygame.font.SysFont("Helvetica", 32)
    G["INMENU"] = True
    G["PAUSE"] = False

    G["SCREEN"].fill((200, 200, 255))
    G["SCREEN"].blit(G["HEL32"].render("Loading...", 0, (0, 0, 0)), (16, 16))
    pygame.display.update()
    return load(G)

def load(G):
    from src import menu
    from src import fight
    G["MENU"] = menu
    G["FIGHT"] = fight
    return G

def run(G):
    while True:
        if G["INMENU"]:
            G = G["MENU"].run(G)
        else:
            G["FIGHT"].run(G)
        
