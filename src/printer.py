"""
export frames as images
"""
import os
import sys
import imageio
import pygame
from pygame.locals import *
from pathlib import Path

from src.utils import expect_input

ROOT_PATH = Path('.')
PATH_TO_REPLAY = ROOT_PATH / ("pics/" if "-o" not in sys.argv else "pics/" + sys.argv[sys.argv.index("-o") + 1])

if not os.path.isdir(PATH_TO_REPLAY): os.mkdir(PATH_TO_REPLAY)

FRAME = 0
SAVED = []

START = None

def save_surface(surf):
    w, h = (surf.get_width(), surf.get_height())
    save = pygame.Surface((w, h))
    save.blit(surf, (0, 0))
    SAVED.append(save)

def save_em():
    for i, surf in enumerate(SAVED):
        pygame.image.save(surf, str(PATH_TO_REPLAY/"{}.png".format(i)))

def make_gif(start, end):
    images = []
    num_imgs = len(os.listdir(ROOT_PATH / PATH_TO_REPLAY))
    for i in range(num_imgs):
        file_name = "{}.png".format(i)
        file_path = os.path.join(ROOT_PATH / PATH_TO_REPLAY, file_name)
        images.append(imageio.imread(file_path))
    imageio.mimsave(os.path.join(ROOT_PATH, 'replay.gif'), images, fps=60)

def draw(G):
    G["SCREEN"].blit(SAVED[FRAME], (0, 0))
    G["SCREEN"].blit(G["HEL32"].render("{}".format(FRAME), 0, (0, 0, 0)), (32, 288))
    if START:
        pygame.draw.circle(G["SCREEN"], (255, 0, 0), (32, 256), 16)

def run(G):
    global START, FRAME
    def animate(G):
        global FRAME
        draw(G)
        G["SCREEN"].blit(G["HEL32"].render("Save Replay? (Y/N)", 0, (0, 0, 0)), (32, 256))
        FRAME += 1

    pygame.event.pump()
    inp = expect_input([K_y, K_n], args=G, cb=animate)

    print(inp)
    print(K_ESCAPE, K_y, K_n)
    if inp != K_y:
        return

    save_em()

    while True:
        draw(G)
    
        inp = expect_input()
        mods = pygame.key.get_mods()

        if inp == K_LEFT and mods & KMOD_SHIFT: FRAME -= 16
        elif inp == K_RIGHT and mods & KMOD_SHIFT: FRAME += 16
        elif inp == K_LEFT: FRAME -= 1
        elif inp == K_RIGHT: FRAME += 1

        elif inp == K_SPACE:
            if START is not None:
                make_gif(START, FRAME)
                START = None
            else:
                START = FRAME

        elif inp == K_BACKSPACE:
            START = None

        elif inp == K_ESCAPE:
            return
