import pygame
import pygame.gfxdraw
from pygame import Surface, Rect
from pygame.locals import *

from src.fighter import Fighter, fighter_map

# COLORS
COLECB = (0, 0, 255)
COLHIT = (255, 0, 0)
COLHRT = (0, 255, 0)

SAVED = False
FIGHTER = None
STATE = "STAND"
FRAME = 0
FRAME_DATA = {}

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
    "LANDINGLAG",
]

ALPHABET_KEY_MAP = {
    K_a: "a", K_b: "b", K_c: "c", K_d: "d", K_e: "e",
    K_f: "f", K_g: "g", K_h: "h", K_i: "i", K_j: "j",
    K_k: "k", K_l: "l", K_m: "m", K_n: "n", K_o: "o",
    K_p: "p", K_q: "q", K_r: "r", K_s: "s", K_t: "t",
    K_u: "u", K_v: "v", K_w: "w", K_x: "x", K_y: "y",
    K_z: "z", K_SPACE: " ", K_UNDERSCORE: "_",
    K_0: "0", K_1: "1", K_2: "2", K_3: "3", K_4: "4",
    K_5: "5", K_6: "6", K_7: "7", K_8: "8", K_9: "9",
    K_PLUS: "+", K_MINUS: "-", K_COLON: ":",
}

LOG = Surface((256, 1024))
LOG.fill((150, 150, 150))

SHOW_LOG = False

def resize(r):
    return Rect(r.x*4, r.y*4, r.w*4, r.h*4)

def draw_box(G, surf, rect, col, data={}):
    rect = resize(rect)
    x, y = rect.x, rect.y
    for key in data.keys():
        surf.blit(G["HEL8"].render("{}:{}".render(key, data[key]), 0, (col)), (x, y))
    pygame.draw.rect(surf, col, rect, width=1)

def drawn_fighter():
    global FIGHTER, FRAME, STATE
    FIGHTER.state = STATE
    FIGHTER.frame = FRAME
    surf = Surface((FIGHTER.W * 4, FIGHTER.H * 4))
    surf.fill((0, 100, 0))
    sprite = FIGHTER.get_sprite()
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

def expect_input(expectlist=[]):
    while True:
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == QUIT: quit()
            if e.type == KEYDOWN:
                if expectlist:
                    if e.key in expectlist: return e.key
                else: return e.key

def select_from_list(G, list, pos):
    idx = 0
    while True:
        surf = Surface((256, 32*len(list)))
        surf.fill((230, 230, 230))
        for i, text in enumerate(list):
            col = (0, 0, 0) if i != idx else (60, 90, 60)
            surf.blit(G["HEL32"].render(str(text), 0, col), (0, i*32))
        G["SCREEN"].blit(surf, pos)
        inp = expect_input()

        if inp == K_UP: idx -= 1
        if inp == K_DOWN: idx += 1
        if inp in [K_RETURN, K_SPACE]: return list[idx]
        if inp in [K_ESCAPE, K_BACKSPACE] or not list: return False
        idx %= len(list)

def get_text_input(G, pos):
    string = ''
    while True:
        surf = Surface((256, 32))
        surf.fill((230, 230, 230))
        surf.blit(G["HEL32"].render(string, 0, (0, 0, 0)), (0, 0))
        G["SCREEN"].blit(surf, pos)
        pygame.display.update()

        inp = expect_input()
        if inp == K_ESCAPE: return False
        if inp == K_BACKSPACE: string = string[:-1]
        if inp == K_RETURN: return string
        
        if pygame.key.get_mods() & KMOD_SHIFT:
            if inp in ALPHABET_KEY_MAP:
                string = string + ALPHABET_KEY_MAP[inp].upper()
        elif inp in ALPHABET_KEY_MAP:
            string = string + ALPHABET_KEY_MAP[inp]

def load_moves(fighter):
    global SAVED
    SAVED = True
    return fighter._load_moves() or {}

def save_moves(moves):
    global SAVED
    SAVED = True
    filename = FIGHTER.frame_data_filename
    try:
        with open("src/bin/"+filename, "w") as f:
            f.write(repr(moves))
        return "Saved: "+filename
    except IOError:
        return "Failed to save: "+filename
    
def run(G):
    global FRAME_DATA, SHOW_LOG, FIGHTER, STATE, FRAME
    while True:
        G["SCREEN"].fill((200, 200, 250))
        if "CHARACTER" not in G:
            G["SCREEN"].blit(G["HEL32"].render("CHARACTER NAME:", 0, (0, 0, 0)), (0, 0))
            G["CHARACTER"] = select_from_list(G, ["SWORDIE", "BRAWLER", "SPEEDLE"], (32, 32))
            G["FIGHTER"] = Fighter(fighter_map[G["CHARACTER"]])
            FIGHTER = G["FIGHTER"]
            FRAME_DATA = load_moves(G["FIGHTER"])
        

        if SHOW_LOG:
            G["SCREEN"].blit(LOG, (G["W"] - 256, 0))
        else:
            G["SCREEN"].blit(LOG, (G["W"] - 256, G["H"] - 16))

        if FIGHTER is not None:
            G["SCREEN"].blit(drawn_fighter(), (0, 0))
            for ecbox in FIGHTER.ECB:
                draw_box(G, G["SCREEN"], ecbox, COLECB)
            G["SCREEN"].blit(G["HEL32"].render(FIGHTER._get_move_identifier(), 0, (0, 0, 0)), (0, G["SCREEN"].get_height() - 32))
            G["SCREEN"].blit(G["HEL32"].render("STATE:{}".format(STATE), 0, (0, 0, 0)), (0, G["SCREEN"].get_height() - 96))
            G["SCREEN"].blit(G["HEL32"].render("FRAME:{}".format(FRAME), 0, (0, 0, 0)), (0, G["SCREEN"].get_height() - 64))

        pygame.display.update()
        inp = expect_input()
        mods = pygame.key.get_mods()
        if inp == K_ESCAPE and (SAVED or mods & KMOD_CTRL):
            quit()
        if inp == K_TAB:
            SHOW_LOG = not SHOW_LOG

        if inp == K_s and mods & KMOD_SHIFT:
            state = select_from_list(G, STATELIST, (G["SCREEN"].get_width() - 256, 0))
            FIGHTER.STATE = state
            FIGHTER.FRAME = 0
            STATE = state
            FRAME = 0
        if inp == K_s and mods & KMOD_CTRL:
            log(G, save_moves(FRAME_DATA))

