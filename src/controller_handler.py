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
        "LEFT": K_a,
        "UP": K_w,
        "RIGHT": K_d,
        "DOWN": K_s,
        "BTN0": K_g,
        "BTN1": K_h,
        "BTN2": K_t,
        "BTN3": K_y,
    },
    "JOY": {
        "LEFT": 0,
        "UP": 1,
        "RIGHT": 0,
        "DOWN": 1,
        "BTN0": 0,
        "BTN1": 1,
        "BTN2": 2,
        "BTN3": 3,
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

    def update_player(self, p, obj):
        if p == "P1" and self.P1 is not None:
            self.P1["player"] = obj
        elif p == "P2" and self.P2 is not None:
            self.P2["player"] = obj

    def get_exists(self, p):
        return self.P1 is not None if p == "P1" else self.P2 is not None

    def update(self, SENS=0.4):
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        if keys[self.QUITKEY] or pygame.event.peek(QUIT): quit()
        
        for P in [self.P1, self.P2]:
            if P is None: continue
            player = P["player"]
            if P["type"] == "key":
                for key in player.inp:
                    player.inp[key] = keys[P["map"][key]]

            if P["type"] == "joy":
                check_axis = True
                joy = P["joy"]
                if joy.get_numhats():
                    hat = joy.get_hat(0)
                    if any(hat): check_axis = False
                    player.inp["LEFT"] = hat[0] == -1 
                    player.inp["RIGHT"] = hat[0] == 1
                    player.inp["UP"] = hat[1] == 1
                    player.inp["DOWN"] = hat[1] == -1

                
                if joy.get_numaxes() and check_axis:
                    player.inp["LEFT"] = joy.get_axis(P["map"]["LEFT"]) < 0-SENS
                    player.inp["RIGHT"] = joy.get_axis(P["map"]["RIGHT"]) > SENS
                    player.inp["UP"] = joy.get_axis(P["map"]["UP"]) < 0-SENS
                    player.inp["DOWN"] = joy.get_axis(P["map"]["DOWN"]) > SENS
                
                player.inp["BTN0"] = joy.get_button(P["map"]["BTN0"])
                player.inp["BTN1"] = joy.get_button(P["map"]["BTN1"])
                player.inp["BTN2"] = joy.get_button(P["map"]["BTN2"])
                player.inp["BTN3"] = joy.get_button(P["map"]["BTN3"])
                
