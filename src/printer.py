"""
export frames as images
"""
import sys
import pygame

PATH_TO_REPLAY = "pics/" if "-o" not in sys.argv else "pics/" + sys.argv[sys.argv.index("-o") + 1]

FRAME = 0

def save_surface(surf):
    global FRAME
    pygame.image.save(surf, PATH_TO_REPLAY+str(FRAME)+".png")
    FRAME += 1

