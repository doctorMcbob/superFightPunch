import pygame
from pygame import Rect
from pygame.locals import *

from src.fighter import Fighter, fighter_map
from src.controller_handler import ControllerHandler, DEFAULT_KEY_MAP
from src.stage import get_stage

SCROLX, SCROLY = 0, 0

METER_IN_COLOR = [(110, 120, 200), (110, 200, 120), (110, 200, 200), (250,  80,  80)]
METER_OU_COLOR = [( 80,  80, 140), ( 80, 140,  80), ( 80, 140, 140), (180,  20,  20)]

def load_character(G, p):
    G[p]["ACTIVE"] = Fighter(fighter_map[G[p]["CHARACTERS"].pop(0)])
    if G[p]["JOY"]:
        G["CONTROLLER"].add_player(G[p]["ACTIVE"], DEFAULT_KEY_MAP["JOY"], joystick=G[p]["JOY"])
    else:
        G["CONTROLLER"].add_player(G[p]["ACTIVE"], DEFAULT_KEY_MAP[p])

def percentage(part, whole): return float(part)/float(whole)

def update_scroller(G):
    global SCROLX, SCROLY
    # calculate center between the fighters
    p1, p2 = G["P1"]["ACTIVE"], G["P2"]["ACTIVE"]
    x1, y1 = p1.X + p1.W // 2, p1.Y
    x2, y2 = p2.X + p2.W // 2, p2.Y
    x = abs(x1 - x2) // 2 + min(x1, x2)
    y = abs(y1 - y2) // 2 + min(y1, y2)
    SCROLX = x - G["SCREEN"].get_width() // 2
    SCROLY = y - G["STAGE"]["HEIGHT"]// 2
    SCROLX = max(0, SCROLX)
    SCROLX = min(G["STAGE"]["WIDTH"] - G["SCREEN"].get_width(), SCROLX)

def scroll(pos):
    if type(pos) == Rect:
        return Rect(scroll((pos.x, pos.y)), (pos.w, pos.h))
    x, y = pos
    return x-SCROLX, y-SCROLY

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


def draw_fighter(G, dest, fighter):
    sprite = fighter.get_sprite(G)
    dest.blit(sprite, scroll((fighter.X, fighter.Y)))


def draw_stage(dest, stage):
    for rect in stage["PLAT"]:
        pygame.draw.rect(dest, (80, 80, 80), scroll(rect))
    pygame.draw.rect(dest, (80, 80, 80), scroll(Rect((0, stage["HEIGHT"]), (stage["WIDTH"], 4))))

def center_fighters(G):
    G["P1"]["ACTIVE"].X = G["STAGE"]["WIDTH"] // 2 - 256
    G["P1"]["ACTIVE"].Y = G["STAGE"]["HEIGHT"]- G["P1"]["ACTIVE"].H

    G["P2"]["ACTIVE"].X = G["STAGE"]["WIDTH"] // 2 - G["P2"]["ACTIVE"].W + 256
    G["P2"]["ACTIVE"].Y = G["STAGE"]["HEIGHT"]- G["P2"]["ACTIVE"].H
    G["P2"]["ACTIVE"].direction = -1

def update_characters(G):
    center = False
    for p in ["P1", "P2"]:
        if "ACTIVE" not in G[p] or G[p]["ACTIVE"].state == "DEAD":
            if len(G[p]["CHARACTERS"]) == 0:
                return False
            load_character(G, p)
            center = True
    if center: center_fighters(G)
    return True

def run(G, stage="airplane"):
    # re do all this once the moving pieces are finished
    # ie: fighters and stages
    G["CONTROLLER"] = ControllerHandler()
    G["SCROLL"] = scroll
    get_stage(G, stage)

    while update_characters(G):
        G["CLOCK"].tick(G["FPS"])
        update_scroller(G)
        G["SCREEN"].fill((200, 200, 250))
        draw_stage(G["SCREEN"], G["STAGE"])

        G["SCREEN"].blit(G["HEL16"].render(str(int(G["CLOCK"].get_fps())), 0, (0, 0, 0)), (G["W"] - 32, G["H"] - 32))

        draw_HUD(G, G["SCREEN"])
        for fighter in (G["P1"]["ACTIVE"], G["P2"]["ACTIVE"]):
            fighter.update(G)
            draw_fighter(G, G["SCREEN"], fighter)

            if G["DEBUG"]:
                fighter.DEBUG(G)

        if G["REPLAYS"]: G["PRINTER"].save_surface(G["SCREEN"])
        pygame.display.update()

        G["CONTROLLER"].update()
    G["INMENU"] = True

