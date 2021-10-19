import json

import pygame
from pygame import Surface

from src.sprites import load_spritesheet

HEL16 = pygame.font.SysFont("Helvetica", 16)

fighter_map = {
    "SWORDIE": {
        "MAXHP": 100,
        "W": 128,
        "H": 128,
        "WALKSPEED": 5,
        "DASHSPEED": 10,
        "JUMPSTRENGTH": -16,
        "SHORTHOPTRENGTH": -8,
        "ARIALSPEED": 8,
        "DOUBLEJUMPSTRENGTH": 20,
        "GRAV": 1,
        "FLOAT": 8,
        "SPRITESHEET": {
            "STAND": ((0, 0), (128, 128)),
            "DASH": ((128, 0), (128, 128)),
            "WALK": ((256, 0), (128, 128)),
            "JUMPSQUAT": ((384, 0), (128, 128)),
            "ARIAL": ((512, 0), (128, 128)),
            "LAND": ((640, 0), (128, 128)),
        },
        "SSFILENAME": "swordie.png",
        "MSFILENAME": "swordie.json"
    },
    "BRAWLER": {
        "MAXHP": 100,
        "W": 128,
        "H": 128,
        "WALKSPEED": 5,
        "DASHSPEED": 10,
        "JUMPSTRENGTH": -16,
        "SHORTHOPTRENGTH": -8,
        "ARIALSPEED": 8,
        "DOUBLEJUMPSTRENGTH": 20,
        "GRAV": 1,
        "FLOAT": 8,
        "SPRITESHEET": {
            "STAND": ((0, 0), (128, 128)),
            "DASH": ((128, 0), (128, 128)),
            "WALK": ((256, 0), (128, 128)),
            "JUMPSQUAT": ((384, 0), (128, 128)),
            "ARIAL": ((512, 0), (128, 128)),
            "LAND": ((640, 0), (128, 128)),
        },
        "SSFILENAME": "brawler.png",
        "MSFILENAME": "brawler.json"
    },
    "SPEEDLE": {
        "MAXHP": 100,
        "W": 128,
        "H": 128,
        "WALKSPEED": 5,
        "DASHSPEED": 10,
        "JUMPSTRENGTH": -16,
        "SHORTHOPTRENGTH": -8,
        "ARIALSPEED": 8,
        "DOUBLEJUMPSTRENGTH": 20,
        "GRAV": 1,
        "FLOAT": 8,
        "SPRITESHEET": {
            "STAND": ((0, 0), (128, 128)),
            "DASH": ((128, 0), (128, 128)),
            "WALK": ((256, 0), (128, 128)),
            "JUMPSQUAT": ((384, 0), (128, 128)),
            "ARIAL": ((512, 0), (128, 128)),
            "LAND": ((640, 0), (128, 128)),
        },
        "SSFILENAME": "speedle.png",
        "MSFILENAME": "speedle.json"
    }
}

class Fighter(object):
    def __init__(self, template):
        self.HP = template["MAXHP"]
        self.MAXHP = self.HP

        self.W = template["W"]
        self.H = template["H"]

        self.walk_speed = template["WALKSPEED"]
        self.dash_speed = template["DASHSPEED"]
        self.arial_speed = template["ARIALSPEED"]

        self.jump_strength = template["JUMPSTRENGTH"]
        self.short_hop_strength = template["SHORTHOPTRENGTH"]
        self.double_jump_strength = template["DOUBLEJUMPSTRENGTH"]
        self.has_double_jump = True
        
        self.grav = template["GRAV"]
        self.floaty = template["FLOAT"]

        self.inp = {
            "LEFT": 0,
            "UP": 0,
            "RIGHT": 0,
            "DOWN": 0,

            "BTN0": 0, # ATTACK 1
            "BTN1": 0, # ATTACK 2
            "BTN2": 0, # RUN BUTTON
            "BTN3": 0, # DASH BUTTON
        }

        self.X = 0
        self.Y = 0
        self.X_VEL = 0
        self.Y_VEL = 0

        self.knockback = (0, 0) # velocity mod
        self.hitstun = 0
        self.hitlag = 0
        
        self.combo = 0

        self.spritesheet = load_spritesheet(template["SSFILENAME"], template["SPRITESHEET"])

        self.state = "STAND"
        self.frame = 0
        self.direction = 1

        try:
            with open("src/bin/"+template["MSFILENAME"]) as f:
                self.data = json.load(f)
        except IOError:
            print("Missing file: " + template["MSFILENAME"])
            quit()

        self.hitboxes = []
        self.hitbox_data = []
        self.hurtboxes = []

    def get_move_data(self):
        if self.state in self.data:
            return self.data[self.state]
        x = self.frame
        while x >= 0:
            name = self.state + ":" + str(x)
            if name in self.data: return self.data[name]
            x -= 1
        return []

    def update_boxes(self):
        move_data = self.get_move_data()
        self.hitboxes = []
        self.hitbox_data = []
        for hitbox in move_data["HITBOXES"]:
            self.hitboxes.append(Rect(hitbox["RECT"][0] + self.X, hitbox["RECT"][0] + self.Y))
            self.hitbox_data.append(hitbox)
        self.hurtboxes = [Rect(hurtbox["RECT"][0] + self.X, hurtbox["RECT"][1] + self.Y)
                          for hurtbox in move_data["HURTBOXES"]]

    def check_collision(self, enemy):
        priority_hitbox = {"PRIO": 100}
        for hurtbox in self.hurtboxes:
            for hitbox in hurtbox.collidelistall(enemy.hitboxes):
                data = enemy.hitbox_data[enemy.hitboxes.index(hitbox)]
                priority_hitbox = data if data["PRIO"] < priority_hitbox["PRIO"] else priority_hitbox
        self.hitstun = priority_hitbox["HITSTUN"]
        self.hitlag = priority_hitbox["HITLAG"]

    def get_sprite(self):
        if self.direction > 0:
            return pygame.transform.flip(self._get_sprite(), 1, 0)
        return self._get_sprite()
            
    def _get_sprite(self):
        if self.state in self.spritesheet:
            return self.spritesheet[self.state]
        x = self.frame
        while x:
            name = self.state +":"+ str(x)
            if name in self.spritesheet:
                return self.spritesheet[name]
            x -= 1

        # if the sprite was not found, return a placeholder
        surf = Surface((self.W, self.H))
        surf.fill((1, 255, 1))
        surf.blit(HEL16.render(STATE, 0, (0, 0, 0)), (0, 0))
        return surf
        
    def update_state(self):
        move_data = self.get_move_data()
        state = self.state
        if self.inp["BTN3"] and "DASH" in move_data["ACTIONABLE"] and (self.inp["LEFT"] or self.inp["RIGHT"]):
                self.state = "DASH"
        elif not self.inp["BTN3"] and "WALK" in move_data["ACTIONABLE"] and (self.inp["LEFT"] or self.inp["RIGHT"]):
                self.state = "WALK"

        elif self.inp["BTN2"] and "JUMPSQUAT" in move_data["ACTIONABLE"]:
            self.state = "JUMPSQUAT"
        elif self.inp["BTN2"] and "DOUBLEJUMP" in move_data["ACTIONABLE"] and self.has_double_jump:
            self.state = "DOUBLEJUMP"

        elif self.state == "JUMPSQUAT" and "JUMP" in move_data["ACTIONABLE"]:
            self.state = "JUMP"

        elif self.inp["BTN0"] and "GROUNDATK0" in move_data["ACTIONABLE"]:
            self.state = "GROUNDATK0"
        elif self.inp["BTN1"] and "GROUNDATK1" in move_data["ACTIONABLE"]:
            self.state = "GROUNDATK1"

        elif self.inp["BTN0"] and "ARIALATK0" in move_data["ACTIONABLE"]:
            self.state = "ARIALATK0"
        elif self.inp["BTN1"] and "ARIALATK1" in move_data["ACTIONABLE"]:
            self.state = "ARIALATK1"

        elif self.inp["BTN0"] and "DASHATK0" in move_data["ACTIONABLE"]:
            self.state = "DASHATK0"
        elif self.inp["BTN1"] and "DASHATK1" in move_data["ACTIONABLE"]:
            self.state = "DASHATK1"

        elif "STAND" in move_data["ACTIONABLE"]:
            self.state = "STAND"

        if state != self.state:
            self.frame = 0

    def _dir_as_tuple(self):
        x = self.inp["LEFT"] * -1 + self.inp["RIGHT"] * 1
        y = self.inp["UP"] * -1 + self.inp["DOWN"] * 1
        return (x, y)
        
    def apply_state(self):
        d = self._dir_as_tuple()
        if self.frame == 0:
            if self.state == "JUMP":
                self.Y_VEL = self.jump_strength
                self.state = "ARIAL"
            if self.state == "DOUBLEJUMP":
                self.X_VEL = self.double_jump_strength * d[0]
                self.Y_VEL = self.double_jump_strength * d[1]
                self.has_double_jump = False
                self.state = "ARIAL"

        if self.state == "STAND":
            self.X_VEL = 0
            self.Y_VEL = 0
        elif self.state == "WALK":
            self.X_VEL = self.walk_speed * d[0]
        elif self.state == "DASH":
            self.X_VEL = self.dash_speed * d[0]

        elif self.state == "ARIAL":
            pass
            if abs(self.Y_VEL + self.grav) <= self.floaty:
                self.Y_VEL += self.grav
            elif self.Y_VEL > 0:
                self.Y_VEL =  0 - self.floaty
            elif self.Y_VEL < 0:
                self.Y_VEL = self.floaty

    def update(self):
        self.update_state()
        self.apply_state()

        self.X += self.X_VEL
        self.Y += self.Y_VEL

        self.update_boxes()

        self.frame += 1

    def DEBUG(self):
        print("-------")
        print(self.state, self.frame)
        print("input")
        for key in self.inp:
            print("    ", key, self.inp[key])
        print("move data")
        move_data = self.get_move_data()
        for key in move_data:
            print("    ", key, move_data[key])
        print("fighter data")
        print("    ", "X", self.X)
        print("    ", "Y", self.Y)
        print("    ", "X_VEL", self.X_VEL)
        print("    ", "Y_VEL", self.Y_VEL)
        print("    ", "DJ", self.has_double_jump)
