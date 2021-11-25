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

def set_up(vis=False):
    global W, H
    G = {}
    if vis:
        W, H = 1200, 1000
    else:
        W = W if "-w" not in sys.argv else int(sys.argv[sys.argv.index("-w") + 1])
        H = H if "-h" not in sys.argv else int(sys.argv[sys.argv.index("-h") + 1])
    if "-f" in sys.argv:
        G["SCREEN"] = pygame.display.set_mode((W, H), FULLSCREEN)
    else:
        G["SCREEN"] = pygame.display.set_mode((W, H))

    pygame.display.set_caption("༼ つ ◕_◕ ༽つ Super Fight Punch ༼ つ ◕_◕ ༽つ")
    G["DEBUG"] = "-d" in sys.argv
    G["REPLAYS"] = "-r" in sys.argv

    G["CLOCK"] = pygame.time.Clock()
    G["FPS"] = 60 if "-fps" not in sys.argv else int(sys.argv[sys.argv.index("-fps") + 1])
    
    G["W"], G["H"] = W, H
    G["HEL8"] = pygame.font.SysFont("Helvetica", 8)
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
    if G["REPLAYS"]:
        from src import printer
        G["PRINTER"] = printer
    else:
        G["PRINTER"] = None
    G["MENU"] = menu
    G["FIGHT"] = fight
    return G

def run(G):
    while True:
        if G["INMENU"]:
            G = G["MENU"].run(G)
        else:
            G["FIGHT"].run(G)
            if G["PRINTER"] is not None:
                G["PRINTER"].run(G)
