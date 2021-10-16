import pygame
from pygame.locals import *

DEFAULT_KEY_MAP = {
    "P1" : {
        "LEFT": K_LEFT,
        "UP": K_UP,
        "RIGHT": K_RIGHT,
        "DOWN": K_DOWN,
        "BTN0": K_n,
        "BTN1": K_m,
        "BTN2": K_j,
        "BTN3": K_k,
    },
    "P2" : {
        "LEFT": K_A,
        "UP": K_w,
        "RIGHT": K_d,
        "DOWN": K_s,
        "BTN0": K_g,
        "BTN1": K_h,
        "BTN2": K_t,
        "BTN3": K_y,
    },
}
class ControllerHandler(object):
    def __init__(self, QUITKEY=K_ESCAPE):
        self.P1 = None
        self.P2 = None
        self.QUITKEY = QUITKEY

    def add_player(self, player_obj, btn_map, joystick=None):
        controller = {
            "player" : player_obj,
            "type"   : "joy" if joystick else "key",
            "joy"    : joystick,
            "map"    : btn_map,
        }
        if self.P1 is None:
            self.P1 = controller
        elif self.P2 is None:
            self.P2 = controller

    def update(self):
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        if keys[self.QUITKEY]: quit()
        
        for P in [self.P1, self.P2, self.P3, self.P4]:
            if P is None: continue
            player = P["player"]
            if P["type"] == "key":
                for key in player.inp:
                    player.inp[key] = keys[P["map"][key]]

#            if P["type"] == "joy":
#                check_axis = True
                # joy = P["joy"]
                # if joy.get_numhats():
                #     hat = joy.get_hat(0)
                #     if any(hat): check_axis = False
                #     player.MOV_LEFT = hat[0] == -1
                #     player.MOV_RIGHT = hat[0] == 1
                #     player.MOV_UP = hat[1] == 1
                #     player.MOV_DOWN = hat[1] == -1

                
                # if joy.get_numaxes() and check_axis:
                #     player.MOV_LEFT = joy.get_axis(P["map"]["left"]) < -.4
                #     player.MOV_RIGHT = joy.get_axis(P["map"]["right"]) > .4
                #     player.MOV_UP = joy.get_axis(P["map"]["up"]) < -.4
                #     player.MOV_DOWN = joy.get_axis(P["map"]["down"]) > .4
                
                # player.BTN_0 = joy.get_button(P["map"]["btn 0"])
                # player.BTN_1 = joy.get_button(P["map"]["btn 1"])
                
