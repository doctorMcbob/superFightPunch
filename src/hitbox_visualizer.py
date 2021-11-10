from copy import deepcopy

import pygame
from pygame import Surface, Rect
from pygame.locals import *

from src.fighter import Fighter, fighter_map
from src.utils import expect_input, get_text_input, expect_click, pick_angle, get_angle, visualized_angle, pos_from_angle, select_from_list

# COLORS
COLECB = (0, 0, 255)
COLHIT = (255, 0, 0)
COLHRT = (0, 255, 0)

SAVED = False
FIGHTER = None
STATE = "STAND"
FRAME = 0
FRAME_DATA = {}

SCRLX = 0
SCRLY = 0

def scroll(pos):
    if type(pos) == Rect:
        return Rect((pos.x + SCRLX, pos.y + SCRLY), (pos.w, pos.h))
    return pos[0] + SCRLX, pos[1] + SCRLY

def unscroll(pos):
    if type(pos) == Rect:
        return Rect((pos.x - SCRLX, pos.y - SCRLY), (pos.w, pos.h))
    return pos[0] - SCRLX, pos[1] - SCRLY

STATELIST = [
    "ARIAL",
    "ARIALATK0",
    "ARIALATK1",
    "STAND",
    "GROUNDATK0",
    "GROUNDATK1",
    "WALK",
    "DASH",
    "DASHATK0",
    "DASHATK1",
    "JUMPSQUAT",
    "LANDING",
    "HITLAND",
    "LANDINGLAG",
    "HITSTUN",
    "HITLAG",
]

def make_migrations(G):
    for identifier in FRAME_DATA:
        log(G, "migrating state {}".format(identifier))
        hitboxes = FRAME_DATA[identifier]["HITBOXES"]
        for hitbox in hitboxes:
            if "DI" not in hitbox:
                hitbox["DI"] = 20

BASE_HITBOX = {
    "PRIO"       : 100,
    "HITSTUN"    : 0,
    "HITLAG"     : 0,
    "ANGLE"      : (0, 1),
    "DI"         : 20,
    "STRENGTH"   : 2,
    "RECTS"       : [],
}

BASE_STATE = {
    "ACTIONABLE" : [],
    "HITBOXES"   : [],
    "HURTBOXES"  : [],
    "ECB"        : [],
}

LOG = Surface((256, 1024))
LOG.fill((150, 150, 150))

SHOW_LOG = False

def resize(r):
    return Rect(r.x*4, r.y*4, r.w*4, r.h*4)

def draw_box(G, surf, rect, col, data={}):
    rect = resize(rect)
    x, y = scroll((rect.x, rect.y))
    for key in data.keys():
        surf.blit(G["HEL16"].render("{}:{}".format(key, data[key]), 0, (col)), (x, y))
        y += 16
    pygame.draw.rect(surf, col, scroll(rect), width=1)

def drawn_fighter(G):
    global FIGHTER, FRAME, STATE
    FIGHTER.state = STATE
    FIGHTER.frame = FRAME
    surf = Surface((FIGHTER.W * 4, FIGHTER.H * 4))
    surf.fill((0, 100, 0))
    sprite = FIGHTER.get_sprite(G)
    for _ in range(2):
        sprite = pygame.transform.scale2x(sprite)
    surf.blit(sprite, (0, 0))
    return surf

def log(G, text):
    global LOG
    new = Surface((256, 1024))
    new.fill((150, 150, 150))
    new.blit(LOG, (0, 16))
    new.blit(G["HEL16"].render(text, 0, (0, 0, 0)), (0, 0))
    LOG = new

def draw_grid(G):
    x, y = -1, -1
    while x <= FIGHTER.W * 4:
        pygame.draw.line(G["SCREEN"], (30, 130, 30), scroll((x, 0)), scroll((x, FIGHTER.H * 4)))
        x += 4
    while y <= FIGHTER.H * 4:
        pygame.draw.line(G["SCREEN"], (30, 130, 30), scroll((y, 0)), scroll((y, FIGHTER.W * 4)))
        y += 4

def update_dict(G, data, pos):
    surf = Surface((640, 480))
    SLOT = 0
    while True:
        keys = list(data.keys())
        surf.fill((200, 200 , 255))
        y = 32
        surf.blit(G["HEL32"].render("{", 0, (150, 0, 0)), (32, y))
        for i, key in enumerate(keys):
            col = (150, 0, 0) if SLOT != i else (150, 150, 220)
            y += 32
            surf.blit(G["HEL32"].render("{}".format(key), 0, col), (64, y))        
            surf.blit(G["HEL32"].render(": {}".format(data[key]), 0, col), (256, y))        
        if SLOT == len(keys):
            y += 32
            surf.blit(G["HEL32"].render("[+]", 0, (150, 150, 220)), (64, y))        
        y += 32
        surf.blit(G["HEL32"].render("}", 0, (150, 0, 0)), (32, y))

        G["SCREEN"].blit(surf, pos)
        inp = expect_input()
        
        if inp == K_ESCAPE: return
        if inp == K_UP: SLOT = max(0, SLOT - 1)
        if inp == K_DOWN: SLOT = min(len(keys), SLOT + 1)

        if inp == K_a:
            ang = pick_angle(G, (256, 256))
            if ang: data["ANGLE"] = ang

        if inp in [K_RETURN, K_SPACE] and SLOT < len(keys) and pygame.key.get_mods() & KMOD_SHIFT:
            key = keys[SLOT]
            new_key = get_text_input(G, (64, 32 * (keys.index(key) + 2)))
            data[new_key] = data.pop(key)

        elif inp in [K_RETURN, K_SPACE] and SLOT < len(keys):
            key = keys[SLOT]
            text = get_text_input(G, (272, 32 * (keys.index(key) + 2)))
            try:
                data[key] = eval(text)
            except Exception as e:
                surf.blit(G["HEL32"].render("[ENTER] {}".format(repr(e)), 0, (150, 0, 0)), (32, 0))
                G["SCREEN"].blit(surf, pos)
                expect_input([K_RETURN])

        if inp in [K_RETURN, K_SPACE] and SLOT == len(keys):
            key = get_text_input(G, (64, 32 * (len(keys) + 2)))
            if not key: continue
            text = get_text_input(G, (272, 32 * (len(keys) + 2)))
            if not text: continue
            try:
                data[key] = eval(text)
            except Exception as e:
                surf.blit(G["HEL16"].render("[ENTER] {}".format(repr(e)), 0, (150, 0, 0)), (32, 16))
                G["SCREEN"].blit(surf, pos)
                expect_input([K_RETURN])

def load_moves(fighter):
    global SAVED
    SAVED = True
    return fighter._load_moves() or {}

def save_moves(updated):
    global SAVED
    SAVED = True
    filename = FIGHTER.frame_data_filename
    try:
        with open("src/bin/"+filename, "w") as f:
            f.write(repr(updated))
        return "Saved: "+filename
    except IOError:
        return "Failed to save: "+filename

def pick_fighter(G):
    G["SCREEN"].fill((200, 200, 250))
    G["SCREEN"].blit(G["HEL32"].render("CHARACTER NAME:", 0, (0, 0, 0)), (0, 0))
    return select_from_list(G, ["SWORDIE", "BRAWLER", "SPEEDLE"], (32, 32))

def input_rect(G):
    G["SCREEN"].blit(G["HEL32"].render("DRAW RECT", 0, (0, 0, 0)), (0, G["SCREEN"].get_height() - 128))
    def draw_helper_(G):
        draw(G)
        draw_grid(G)
        draw_boxes(G)
        mpos = pygame.mouse.get_pos()
        G["SCREEN"].blit(G["HEL16"].render("{}".format((mpos[0] // 4, mpos[1] // 4)), 0, (0, 0, 0)), mpos)
    pos, btn = expect_click(G, cb=draw_helper_)
    if not pos: return None
    pos = unscroll(pos)
    def draw_helper(G):
        draw_helper_(G)
        pos2 = unscroll(pygame.mouse.get_pos())
        x1 = min(pos[0], pos2[0]) // 4
        x2 = max(pos[0], pos2[0]) // 4
        y1 = min(pos[1], pos2[1]) // 4
        y2 = max(pos[1], pos2[1]) // 4
        draw_box(G, G["SCREEN"], Rect((x1, y1), (x2 - x1, y2 - y1)), (255, 255, 255))
    pos2, btn2 = expect_click(G, draw_helper)
    if not pos2: return None
    pos2 = unscroll(pos2)
    x1 = min(pos[0], pos2[0]) // 4
    x2 = max(pos[0], pos2[0]) // 4
    y1 = min(pos[1], pos2[1]) // 4
    y2 = max(pos[1], pos2[1]) // 4
    return (x1, y1), ((x2 - x1), (y2 - y1))

def draw_boxes(G):
    FIGHTER.update_boxes()
    for ecbox in FIGHTER.ECB:
        draw_box(G, G["SCREEN"], ecbox, COLECB)
    for hitbox in FIGHTER.hitboxes:
        hitbox_data = FIGHTER.get_hitbox_data(hitbox)
        draw_box(G, G["SCREEN"], hitbox, COLHIT, data={"id": FIGHTER.hitbox_data.index(hitbox_data)})
    for hurtbox in FIGHTER.hurtboxes:
        draw_box(G, G["SCREEN"], hurtbox, COLHRT)

def pick_hitbox(G, hitboxes):
    draw(G)
    def show_which(G, idx):
        y = 32
        for i, hitbox in enumerate(FRAME_DATA[FIGHTER._get_move_identifier()]["HITBOXES"]):
            bgc = (0, 100, 0) if idx == i else (100, 0, 0)
            draw_hitbox_icon(G, (G["SCREEN"].get_width() - 256, y), hitbox, name=i, bgc=bgc)
            y += 128
    G["SCREEN"].blit(G["HEL32"].render("PICK BOX", 0, (0, 0, 0)), (0, G["SCREEN"].get_height() - 128))
    return select_from_list(G, hitboxes, (G["SCREEN"].get_width() - 256, 0), cb=show_which)

def pick_box(G, boxes):
    draw(G)
    def show_which(G, idx):
        for i, box in enumerate(boxes):
            col = (0, 0, 0) if i != idx else (255, 0, 0)
            draw_box(G, G["SCREEN"], box, col, data={"this":"one"})
    G["SCREEN"].blit(G["HEL32"].render("PICK BOX", 0, (0, 0, 0)), (0, G["SCREEN"].get_height() - 128))
    return select_from_list(G, boxes, (G["SCREEN"].get_width() - 256, 0), cb=show_which)

def draw_hitbox_icon(G, pos, data, name="", bgc=(100, 0, 0)):
    surf = Surface((256, 128))
    surf.fill(bgc)
    pygame.draw.rect(surf, (255, 100, 100), Rect((16, 16), (256 - 32, 128 - 32)))
    x, y = 16, 32
    keys_to_draw = ["PRIO", "STRENGTH", "HITSTUN", "HITLAG", "DI"]
    surf.blit(G["HEL16"].render("{}".format(name), (120, 80, 80), 0), (16, 16))
    for key in keys_to_draw:
        surf.blit(G["HEL16"].render("{}:{}".format(key, data[key]), (120, 80, 80), 0), (x, y))
        y += 16
        if y == 256 - 16:
            x += 16
            y = 16
    surf.blit(visualized_angle(get_angle((0, 0), data["ANGLE"])), (128, 0))
    G["SCREEN"].blit(surf, pos)

def update_hitbox(G):
    boxes = FIGHTER.hitbox_data
    if not boxes: return "No hitboxes"
    box = pick_hitbox(G, boxes)
    if not box: return "No box selected"
    data = deepcopy(FRAME_DATA[FIGHTER._get_move_identifier()]["HITBOXES"][boxes.index(box)])
    update_dict(G, data, (0, 0))
    if box not in boxes:
        return "No changes"
    FRAME_DATA[FIGHTER._get_move_identifier()]["HITBOXES"][boxes.index(box)] = data
    SAVED = False
    return "Updated hitbox id {}".format(boxes.index(data))

def delete_box(G):
    global SAVED, FIGHTER
    G["SCREEN"].blit(G["HEL32"].render("TYPE TO REMOVE", 0, (0, 0, 0)), (0, G["SCREEN"].get_height() - 128))
    box_type = select_from_list(G, ["HITBOXES", "HURTBOXES", "ECB"], (G["SCREEN"].get_width() - 256, 0))
    boxes = []
    if box_type == "ECB":
        boxes = FIGHTER.ECB
    elif box_type == "HITBOXES":
        boxes = FIGHTER.hitboxes
    elif box_type == "HURTBOXES":
        boxes = FIGHTER.hurtboxes
    if not boxes:
        return "no boxes deleted"
    if box_type == "HITBOXES":
        box = pick_hitbox(G, FRAME_DATA[FIGHTER._get_move_identifier()]["HITBOXES"])
        FRAME_DATA[FIGHTER._get_move_identifier()]["HITBOXES"].pop(FRAME_DATA[FIGHTER._get_move_identifier()]["HITBOXES"].index(box))
    else:
        box = pick_box(G, boxes)
        FRAME_DATA[FIGHTER._get_move_identifier()][box_type].remove(((box.x, box.y), (box.w, box.h)))
    SAVED = False
    return "removed box".format()

def new_hitbox(G):
    global SAVED
    hitbox_type = select_from_list(G, ["ADD TO", "NEW"], (G["SCREEN"].get_width() - 256, 0))
    if hitbox_type == "NEW":
        hitbox = deepcopy(BASE_HITBOX)
    else:
        hitbox = pick_hitbox(G, FIGHTER.hitbox_data)
    rect = input_rect(G)
    if not rect: return
    pos, dim = rect
    hitbox["RECTS"].append(rect)
    FIGHTER.hitboxes.append(Rect(pos, dim))
    if hitbox_type == "NEW":
#        FIGHTER.hitbox_data.append(hitbox)
        FRAME_DATA[FIGHTER._get_move_identifier()]["HITBOXES"].append(hitbox)
    log(G, "  {}".format((pos, dim)))
    log(G, "Added new HITBOX")
    SAVED = False

def draw(G):
    G["SCREEN"].fill((200, 200, 250))
    if FIGHTER is not None:
        G["SCREEN"].blit(drawn_fighter(G), scroll((0, 0)))
        FIGHTER.update_boxes()
        draw_boxes(G)
        move_data = FIGHTER.get_move_data()
        G["SCREEN"].blit(G["HEL32"].render(FIGHTER._get_move_identifier(), 0, (0, 0, 0)), (0, G["SCREEN"].get_height() - 32))
        G["SCREEN"].blit(G["HEL32"].render("STATE:{}".format(STATE), 0, (0, 0, 0)), (0, G["SCREEN"].get_height() - 96))
        G["SCREEN"].blit(G["HEL32"].render("FRAME:{}".format(FRAME), 0, (0, 0, 0)), (0, G["SCREEN"].get_height() - 64))
        y = 0
        G["SCREEN"].blit(G["HEL16"].render("ACTIONABLE:", 0, (0, 0, 0)), (G["SCREEN"].get_width() - 256, y))
        y += 16
        G["SCREEN"].blit(G["HEL16"].render("{}".format(move_data["ACTIONABLE"]), 0, (0, 0, 0)), (G["SCREEN"].get_width() - 256 + 32, y))
        y += 16
        for i, hitbox in enumerate(FRAME_DATA[FIGHTER._get_move_identifier()]["HITBOXES"]):
            draw_hitbox_icon(G, (G["SCREEN"].get_width() - 256, y), hitbox, name=i)
            y += 128
    if SHOW_LOG:
        G["SCREEN"].blit(LOG, (G["W"] - 256, 0))
    else:
        G["SCREEN"].blit(LOG, (G["W"] - 256, G["H"] - 16))
    
    if G["REPLAYS"]:
        G["PRINTER"].save_surface(G["SCREEN"])

def run(G):
    global FRAME_DATA, SHOW_LOG, FIGHTER, STATE, FRAME, SAVED, SCRLX, SCRLY
    
    while "CHARACTER" not in G or not G["CHARACTER"]:
        G["CHARACTER"] = pick_fighter(G)
            
    G["FIGHTER"] = Fighter(fighter_map[G["CHARACTER"]])
    FIGHTER = G["FIGHTER"]
    FRAME_DATA = load_moves(G["FIGHTER"])
    log(G, "Loaded Fighter {}".format(G["CHARACTER"]))

    make_migrations(G)
    while True:
        draw(G)
        pygame.display.update()
        inp = expect_input()
        mods = pygame.key.get_mods()
        if inp == K_ESCAPE and (SAVED or mods & KMOD_CTRL):
            quit()
        if inp == K_TAB:
            SHOW_LOG = not SHOW_LOG

        if inp == K_s and mods & KMOD_SHIFT:
            state = select_from_list(G, STATELIST, (G["SCREEN"].get_width() - 256, 0))
            if not state: continue
            FIGHTER.state = state
            FIGHTER.frame = 0
            STATE = state
            FRAME = 0
            log(G, "state {}".format(state))
            if not FIGHTER._get_move_identifier():
                FRAME_DATA["{}:{}".format(STATE, FRAME)] = deepcopy(BASE_STATE)
                FIGHTER.data = FRAME_DATA
                log(G, " {}:{}".format(STATE, FRAME))
                log(G, "Added new state identifier")
                SAVED = False

        if inp == K_e and mods & KMOD_SHIFT:
            rect = input_rect(G)
            if not rect: continue
            pos, dim = rect
            FIGHTER.ECB.append(Rect(pos, dim))
            FRAME_DATA[FIGHTER._get_move_identifier()]["ECB"].append((pos, dim))
            log(G, "  {}".format((pos, dim)))
            log(G, "Added new ECBox")
            SAVED = False

        if inp == K_u and mods & KMOD_SHIFT:
            rect = input_rect(G)
            if not rect: continue
            pos, dim = rect
            FIGHTER.hurtboxes.append(Rect(pos, dim))
            FRAME_DATA[FIGHTER._get_move_identifier()]["HURTBOXES"].append((pos, dim))
            log(G, "  {}".format((pos, dim)))
            log(G, "Added new HURTBOX")
            SAVED = False
        
        if inp == K_h and mods & KMOD_SHIFT:
            new_hitbox(G)

        if inp == K_n and mods & KMOD_SHIFT:
            identifier = "{}:{}".format(STATE, FRAME)
            log(G, identifier)
            if identifier in FRAME_DATA:
                log(G, "state already exists")
                continue
            else:
                FRAME_DATA[identifier] = deepcopy(BASE_STATE)
                SAVED = False
                log(G, "Added new state")

        if inp == K_d and mods & KMOD_SHIFT:
            log(G, delete_box(G))

        if inp == K_f and mods & KMOD_SHIFT:
            log(G, update_hitbox(G))

        if inp == K_s and mods & KMOD_CTRL:
            log(G, save_moves(FRAME_DATA))

        if inp == K_o and mods & KMOD_CTRL:
            if not SAVED:
                log(G, "Abandon changes? [ENTER]")
                inp = expect_input()
                if inp != K_RETURN: continue
            G["CHARACTER"] = pick_fighter(G)
            G["FIGHTER"] = Fighter(fighter_map[G["CHARACTER"]])
            FIGHTER = G["FIGHTER"]
            FRAME_DATA = load_moves(G["FIGHTER"])
            log(G, "Loaded Fighter {}".format(G["CHARACTER"]))

        if inp == K_RIGHT:
            if mods & KMOD_CTRL or mods & KMOD_SHIFT:
                SCRLX += 16
            else:
                FRAME += 1

        if inp == K_LEFT:
            if mods & KMOD_CTRL or mods & KMOD_SHIFT:
                SCRLX -= 16                
            else:
                FRAME = max(0, FRAME - 1)

        if inp == K_UP and (mods & KMOD_CTRL or mods & KMOD_SHIFT):
            SCRLY -= 16

        if inp == K_DOWN and (mods & KMOD_CTRL or mods & KMOD_SHIFT):
            SCRLY += 16
