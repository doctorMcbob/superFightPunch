import pygame
from pygame import Rect
from pygame.locals import *

METER_IN_COLOR = [(110, 120, 200), (110, 200, 120), (110, 200, 200), (250,  80,  80)]
METER_OU_COLOR = [( 80,  80, 140), ( 80, 140,  80), ( 80, 140, 140), (180,  20,  20)]

def percentage(part, whole): return float(part)/float(whole)

def draw_HUD(G, dest):
    W = dest.get_width()
    H = dest.get_height()
    # draw health bars
    hlth = percentage(G["P1"]["ACTIVE"]["HP"], G["P1"]["ACTIVE"]["MAXHP"])
    pygame.draw.rect(dest, (180, 80, 95), Rect((0, 0), (W//2, 32)))
    pygame.draw.rect(dest, (250, 50, 70), Rect((4, 4), (int((W//2 - 8) * hlth), 24)))
    hlth = percentage(G["P2"]["ACTIVE"]["HP"], G["P2"]["ACTIVE"]["MAXHP"])
    pygame.draw.rect(dest, (180, 80, 95), Rect((W//2, 0), (W//2, 32)))
    pygame.draw.rect(dest, (250, 50, 70), Rect((W//2 + (W//2 - int(((W//2 - 8) * hlth))), 4), (int((W//2) * hlth - 8), 24)))

    # draw combo meeters
    for i in range(4):
        pygame.draw.rect(dest, METER_OU_COLOR[i], Rect((i * 64, 32), (64, 32)))
        if G["P1"]["ACTIVE"]["COMBO"] > i:
            pygame.draw.rect(dest, METER_IN_COLOR[i], Rect((i * 64, 36), (64, 24)))

    for i in range(4):
        pygame.draw.rect(dest, METER_OU_COLOR[i], Rect((W - (i + 1) * 64, 32), (64, 32)))
        if G["P2"]["ACTIVE"]["COMBO"] > i:
            pygame.draw.rect(dest, METER_IN_COLOR[i], Rect((W - (i + 1) * 64, 36), (64, 24)))

def run(G):
    # Remove this once loading characters is written
    G["P1"]["ACTIVE"] = {
        "HP": 100,
        "MAXHP": 100,
        "COMBO": 1,
    }
    G["P2"]["ACTIVE"] = {
        "HP": 100,
        "MAXHP": 100,
        "COMBO": 0,
    }
    while True:
        G["SCREEN"].fill((200, 200, 250))
        draw_HUD(G, G["SCREEN"])
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE:
                quit()
