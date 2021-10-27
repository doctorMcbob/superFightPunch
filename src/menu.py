import pygame
from pygame.locals import *

from src.sprites import load_spritesheet

FALLBACK_KEY_MAP = {
    "P1" : {
        "START": K_RETURN,
        "SWORDIE": K_LEFT,
        "BRAWLER": K_DOWN,
        "SPEEDLE": K_RIGHT,
        "QUIT": K_ESCAPE,
        "NAMES": ["LEFT", "DOWN", "RIGHT"]
    },
    "P2" : {
        "START": K_TAB,
        "SWORDIE": K_a,
        "BRAWLER": K_s,
        "SPEEDLE": K_d,
        "QUIT": K_BACKSPACE,
        "NAMES": ["A", "S", "D"]
    }
}

FALLBACK_BTN_MAP = {
    "START": 9,
    "SWORDIE": 3,
    "BRAWLER": 0,
    "SPEEDLE": 1,
    "QUIT": 10,
    "NAMES": ["□", "X", "O"]
}

ICONS = load_spritesheet(
    "icons-Sheet.png",
    {
        "SWORDIE": ((0, 0), (64, 64)),
        "BRAWLER": ((64, 0), (64, 64)),
        "SPEEDLE": ((128, 0), (64, 64)),
    }
)

def drawn_character_menu(G, KEY_MAP):
    W = G["SCREEN"].get_width()
    H = G["SCREEN"].get_height()
    surf = pygame.Surface((W, H))
    surf.fill((200, 200, 250))
    # draw the 3 characters icons
    x = W // 5
    for i, icon in enumerate(("SWORDIE", "BRAWLER", "SPEEDLE")):
        surf.blit(ICONS[icon], (x, H // 4))
        surf.blit(G["HEL32"].render(icon, 0, (100, 0, 0)), (x-32, H // 4 - 48))
        surf.blit(G["HEL16"].render(KEY_MAP["P1"]["NAMES"][i], 0, (100, 0, 0)), (x-16, H // 4 + 48 + 64))
        surf.blit(G["HEL16"].render(KEY_MAP["P2"]["NAMES"][i], 0, (100, 0, 0)), (x-16, H // 4 + 48 + 64 + 16))
        x += W // 4
    # draw icons for how many characters have been picked
    for i in range(3):
        col = (0, 0, 150) if i >= len(G["P2"]["CHARACTERS"]) else (0, 200, 0)
        pygame.draw.circle(surf, col, (W // 3 - 128 + (i * 64), (H // 3) * 2), 32)
        col = (0, 0, 150) if i >= len(G["P1"]["CHARACTERS"]) else (0, 200, 0)
        pygame.draw.circle(surf, col, ((W // 3)*2 + (i * 64), (H // 3) * 2), 32)    
    # draw READY button (lit up if both players have order selected
    col = (255, 100, 100) if len(G["P1"]["CHARACTERS"] + G["P2"]["CHARACTERS"]) == 6 else (150, 150, 150)
    pygame.draw.circle(surf, col, (W // 2, (H // 3) * 2), 64)
    surf.blit(G["HEL16"].render("SUPER", 0, (0, 0, 0)), (W // 2 - 32, (H // 3) * 2 - 16))
    surf.blit(G["HEL16"].render("FIGHT", 0, (0, 0, 0)), (W // 2 - 32, (H // 3) * 2))
    surf.blit(G["HEL16"].render("PUNCH", 0, (0, 0, 0)), (W // 2 - 32, (H // 3) * 2 + 16))
    return surf

def run(G, KEY_MAP=FALLBACK_KEY_MAP, BTN_MAP=FALLBACK_BTN_MAP):
    for player in ("P1", "P2"):
        G[player] = {
            "CHARACTERS": [],
            "JOY": None,
        }
    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    while True:
        G["SCREEN"].blit(drawn_character_menu(G, KEY_MAP), (0, 0))
        for joy in joysticks:
            if joy not in [G[P]["JOY"] for P in ("P1", "P2")]:
                if not joy.get_init():
                    joy.init()
                    print(joy.get_name())
                for btn in range(joy.get_numbuttons()):
                    if not joy.get_button(btn): continue
                    player = G["P1"] if G["P1"]["JOY"] is None else G["P2"]
                    player["JOY"] = joy
                
        pygame.display.update()
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        if pygame.event.peek(QUIT) or any(keys[KEY_MAP[p]["QUIT"]] for p in ["P1", "P2"]):
                quit()
        
        for player in ("P1", "P2"):
            for character in ("SWORDIE", "BRAWLER", "SPEEDLE"):
                
                if ((keys[KEY_MAP[player][character]] or G[player]["JOY"] is not None and G[player]["JOY"].get_button(BTN_MAP[character])) and character not in G[player]["CHARACTERS"]):
                    G[player]["CHARACTERS"].append(character)

            if ((keys[KEY_MAP[player]["START"]] or G[player]["JOY"] is not None and G[player]["JOY"].get_button(BTN_MAP["START"])) and len(G["P1"]["CHARACTERS"] + G["P2"]["CHARACTERS"]) == 6):
                G["INMENU"] = False
                return G
                            
