"""
export frames as images
"""
import os
import sys
import imageio
import pygame
from pathlib import Path

ROOT_PATH = Path('.')
PATH_TO_REPLAY = ROOT_PATH / ("pics/" if "-o" not in sys.argv else "pics/" + sys.argv[sys.argv.index("-o") + 1])

if not os.path.isdir(PATH_TO_REPLAY): os.mkdir(PATH_TO_REPLAY)

SAVED = []

def save_surface(surf):
    w, h = (surf.get_width(), surf.get_height())
    save = pygame.Surface((w, h))
    save.blit(surf, (0, 0))
    SAVED.append(save)

def save_em():
    for i, surf in enumerate(SAVED):
        pygame.image.save(surf, str(PATH_TO_REPLAY/"{}.png".format(i)))
    SAVED.clear()

def make_gif():
    images = []
    num_imgs = len(os.listdir(ROOT_PATH / PATH_TO_REPLAY))
    for i in range(num_imgs):
        file_name = "{}.png".format(i)
        file_path = os.path.join(ROOT_PATH / PATH_TO_REPLAY, file_name)
        images.append(imageio.imread(file_path))
    imageio.mimsave(os.path.join(ROOT_PATH, 'replay.gif'), images, fps=60)
