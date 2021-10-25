import pygame
from pygame import Surface
from pygame.locals import *

SAVED = False
MOVES = {}

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

def get_text_input(G, pos):
    string = ''
    while True:
        surf = Surface((512, 32))
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

def load_moves(filename):
    global SAVED
    SAVED = True
    try:
        with open("src/bin/"+filename) as f:
            return eval(f.read())

    except IOError:
        return {}

def save_moves(moves, filename):
    global SAVED
    SAVED = True
    try:
        with open("src/bin/"+filename, "w") as f:
            f.write(repr(moves))
        return "Saved: "+filename
    except IOError:
        return "Failed to save: "+filename
    
def run(G):
    global MOVES, SHOW_LOG
    while True:
        G["SCREEN"].fill((200, 200, 250))
        if "CHARACTER" not in G:
            G["SCREEN"].blit(G["HEL32"].render("CHARACTER NAME:", 0, (0, 0, 0)), (0, 0))
            G["CHARACTER"] = get_text_input(G, (64, 64))
            MOVES = load_moves(G["CHARACTER"])

        if SHOW_LOG:
            G["SCREEN"].blit(LOG, (G["W"] - 256, 0))
        else:
            G["SCREEN"].blit(LOG, (G["W"] - 256, G["H"] - 16))

        pygame.display.update()
        inp = expect_input()
        mods = pygame.key.get_mods()
        if inp == K_ESCAPE and (SAVED or mods & KMOD_SHIFT):
            quit()
        if inp == K_TAB:
            SHOW_LOG = not SHOW_LOG

        if inp == K_s and mods & KMOD_SHIFT:
            log(G, save_moves(MOVES, G["CHARACTER"]))

