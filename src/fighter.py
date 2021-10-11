import json

import pygame
from pygame import Surface

from src.sprites import load_spritesheet

HEL16 = pygame.font.SysFont("Helvetica", 16)

fighter_map = {
    "SWORDIE": {
        "MAXHP": 100,
        "W": 128,
        "H": 96,
        "SPRITESHEET": {},
        "SSFILENAME": "swordie.png",
        "MSFILENAME": "swordie.json"
    },
    "BRAWLER": {
        "MAXHP": 100,
        "W": 128,
        "H": 96,
        "SPRITESHEET": {},
        "SSFILENAME": "brawler.png",
        "MSFILENAME": "brawler.json"
    },
    "SPEEDLE": {
        "MAXHP": 100,
        "W": 96,
        "H": 64,
        "SPRITESHEET": {},
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
                self.moves = json.load(f)
        except IOError:
            print("Missing file: " + template["MSFILENAME"])
            self.moves = {
                "STAND": {
                    "HITBOXES": [],
                    "HURTBOXES": []
                }
            }

        self.hitboxes = []
        self.hitbox_data = {}
        self.hurtboxes = []

    def update_boxes(self):
        self.hitboxes = [Rect(hitbox["POS"], hitbox["DIM"]) for hitbox in self.moves[self.state][self.frame]["HITBOXES"]]
        self.hitbox_data = [hitbox["DATA"] for hitbox in self.moves[self.state][self.frame]["HITBOXES"]]
        self.hurtboxes = [Rect(hurtbox["POS"], hurtbox["DIM"]) for hurtbox in self.moves[self.state][self.frame]["HURTBOXES"]]
                            
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
        
