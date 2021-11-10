import pygame
from pygame.locals import *
from pygame import Rect, Surface

from math import cos, sin, atan, radians, degrees

ALPHABET_KEY_MAP = {
    K_a: "a", K_b: "b", K_c: "c", K_d: "d", K_e: "e",
    K_f: "f", K_g: "g", K_h: "h", K_i: "i", K_j: "j",
    K_k: "k", K_l: "l", K_m: "m", K_n: "n", K_o: "o",
    K_p: "p", K_q: "q", K_r: "r", K_s: "s", K_t: "t",
    K_u: "u", K_v: "v", K_w: "w", K_x: "x", K_y: "y",
    K_z: "z", K_SPACE: " ", K_UNDERSCORE: "_",
    K_0: "0", K_1: "1", K_2: "2", K_3: "3", K_4: "4",
    K_5: "5", K_6: "6", K_7: "7", K_8: "8", K_9: "9",
    K_PLUS: "+", K_MINUS: "-", K_COLON: ":", K_PERIOD:".",
    K_LEFTPAREN: "(", K_RIGHTPAREN: ")", K_COMMA: ",",
    K_ASTERISK: "*", K_SLASH: "/"
}
ALPHABET_SHIFT_MAP = {
    K_0: ")", K_1: "!", K_2: "@", K_3: "#", K_4: "$",
    K_5: "%", K_6: "^", K_7: "&", K_8: "*", K_9: "(",
}

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
            if inp in ALPHABET_SHIFT_MAP:
                string = string + ALPHABET_SHIFT_MAP[inp]
            elif inp in ALPHABET_KEY_MAP:
                string = string + ALPHABET_KEY_MAP[inp].upper()
        elif inp in ALPHABET_KEY_MAP:
            string = string + ALPHABET_KEY_MAP[inp]

def pick_angle(G, pos):
    deg = [0]
    def drangle(G):
        pos1 = pos[0] + 64, pos[1] + 64
        pos2 = pygame.mouse.get_pos()
        deg[0] = get_angle(pos1, pos2)
        G["SCREEN"].blit(visualized_angle(deg[0]), pos)
    pos, btn = expect_click(G, cb=drangle)
    return pos_from_angle(deg[0]) if pos else pos

def get_angle(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    if x1 == x2: return 90 if y1 < y2 else 270
    if y1 == y2: return 0
    a = y1 - y2
    b = x1 - x2

    deg = degrees(atan(a / b)) + (180 * (b > 0))
    if deg < 0: deg += 360
    return deg

def visualized_angle(deg):
    x, y = pos_from_angle(deg)
    surf = Surface((128, 128))
    surf.fill((255, 255, 255))
    pygame.draw.circle(surf, (0, 0, 0), (64, 64), 64, width=4)
    pygame.draw.line(surf, (255, 0, 0), (64, 64), (64+64*x, 64+64*y), width=4)
    return surf

def angle_from_pos(pos):
    return get_angle((0, 0), pos)

def pos_from_angle(deg):
    deg = radians(deg)
    return cos(deg), sin(deg)

def select_from_list(G, list, pos, cb=lambda *args: None):
    idx = 0
    while True:
        surf = Surface((256, 32*len(list)))
        surf.fill((230, 230, 230))
        cb(G, idx)
        for i, text in enumerate(list):
            col = (0, 0, 0) if i != idx else (160, 110, 190)
            surf.blit(G["HEL32"].render(str(text), 0, col), (0, i*32))
        G["SCREEN"].blit(surf, pos)
        inp = expect_input()

        if inp == K_UP: idx -= 1
        if inp == K_DOWN: idx += 1
        if inp in [K_RETURN, K_SPACE]: return list[idx]
        if inp in [K_ESCAPE, K_BACKSPACE] or not list: return False
        idx %= len(list)

def expect_click(G, cb=lambda *args: None):
    while True:
        cb(G)
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == QUIT and SAVED: quit()
            if e.type == KEYDOWN and e.key == K_ESCAPE: return None, None
            if e.type == MOUSEBUTTONDOWN:
                return e.pos, e.button

def expect_input(expectlist=[]):
    while True:
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == QUIT and SAVED: quit()
            if e.type == KEYDOWN:
                if expectlist:
                    if e.key in expectlist: return e.key
                else: return e.key

def shift_angle(angle, shift):
    return angle
