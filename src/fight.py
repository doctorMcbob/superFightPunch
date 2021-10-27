import pygame
from pygame import Rect
from pygame.locals import *

from src.fighter import Fighter, fighter_map
from src.controller_handler import ControllerHandler, DEFAULT_KEY_MAP
from src.stage import get_stage

METER_IN_COLOR = [(110, 120, 200), (110, 200, 120), (110, 200, 200), (250,  80,  80)]
METER_OU_COLOR = [( 80,  80, 140), ( 80, 140,  80), ( 80, 140, 140), (180,  20,  20)]

def percentage(part, whole): return float(part)/float(whole)

def draw_HUD(G, dest):
    W = dest.get_width()
    H = dest.get_height()
    P1 = G["P1"]["ACTIVE"]
    P2 = G["P2"]["ACTIVE"]
    
    # draw health bars
    hlth = percentage(P1.HP,P1.MAXHP)
    pygame.draw.rect(dest, (180, 80, 95), Rect((0, 0), (W//2, 32)))
    pygame.draw.rect(dest, (250, 50, 70), Rect((4, 4), (int((W//2 - 8) * hlth), 24)))
    hlth = percentage(P2.HP, P2.MAXHP)
    pygame.draw.rect(dest, (180, 80, 95), Rect((W//2, 0), (W//2, 32)))
    pygame.draw.rect(dest, (250, 50, 70), Rect((W//2 + (W//2 - int(((W//2 - 8) * hlth))), 4), (int((W//2) * hlth - 8), 24)))

    # draw combo meeters
    for i in range(4):
        pygame.draw.rect(dest, METER_OU_COLOR[i], Rect((i * 64, 32), (64, 32)))
        if P1.combo > i:
            pygame.draw.rect(dest, METER_IN_COLOR[i], Rect((i * 64, 36), (64, 24)))

    for i in range(4):
        pygame.draw.rect(dest, METER_OU_COLOR[i], Rect((W - (i + 1) * 64, 32), (64, 32)))
        if P2.combo > i:
            pygame.draw.rect(dest, METER_IN_COLOR[i], Rect((W - (i + 1) * 64, 36), (64, 24)))


def draw_fighter(dest, fighter):
    sprite = fighter.get_sprite()
    dest.blit(sprite, (fighter.X, fighter.Y))


def draw_stage(dest, stage):
    for rect in stage["PLAT"]:
        pygame.draw.rect(dest, (80, 80, 80), rect)

def run(G, stage="airplane"):
    # re do all this once the moving pieces are finished
    # ie: fighters and stages
    G["CONTROLLER"] = ControllerHandler()
    
    get_stage(G, stage)
    # Remove this once loading characters is written
    G["P1"]["ACTIVE"] = Fighter(fighter_map[G["P1"]["CHARACTERS"].pop(0)])
    G["P2"]["ACTIVE"] = Fighter(fighter_map[G["P2"]["CHARACTERS"].pop(0)])
    
    for P in ["P1", "P2"]:
        if G[P]["JOY"]:
            G["CONTROLLER"].add_player(G[P]["ACTIVE"], DEFAULT_KEY_MAP["JOY"], joystick=G[P]["JOY"])
            continue
        G["CONTROLLER"].add_player(G[P]["ACTIVE"], DEFAULT_KEY_MAP[P])
    
    G["P1"]["ACTIVE"].X = 32
    G["P1"]["ACTIVE"].Y = G["SCREEN"].get_height() - G["P1"]["ACTIVE"].H

    G["P2"]["ACTIVE"].X = G["SCREEN"].get_width() - G["P2"]["ACTIVE"].W - 32
    G["P2"]["ACTIVE"].Y = G["SCREEN"].get_height() - G["P2"]["ACTIVE"].H
    G["P2"]["ACTIVE"].direction = -1

    while True:
        G["CLOCK"].tick(G["FPS"])
        G["SCREEN"].fill((200, 200, 250))
        draw_stage(G["SCREEN"], G["STAGE"])

        G["SCREEN"].blit(G["HEL16"].render(str(int(G["CLOCK"].get_fps())), 0, (0, 0, 0)), (G["W"] - 32, G["H"] - 32))

        draw_HUD(G, G["SCREEN"])
        for fighter in (G["P1"]["ACTIVE"], G["P2"]["ACTIVE"]):
            fighter.update(G)
            draw_fighter(G["SCREEN"], fighter)

            if G["DEBUG"]:
                fighter.DEBUG(G)

        if G["REPLAYS"]: G["PRINTER"].save_surface(G["SCREEN"])
        pygame.display.update()

        G["CONTROLLER"].update()

