from os import environb
import pygame
from pygame import Surface, Rect

from src.utils import shift_angle
from src.sprites import load_spritesheet

HEL16 = pygame.font.SysFont("Helvetica", 16)

fighter_map = {
    "SWORDIE": {
        "MAXHP": 100,
        "W": 192,
        "H": 192,
        "WALKSPEED": 4,
        "DASHSPEED": 8,
        "JUMPSTRENGTH": -16,
        "BASELANDINGLAG": 3,
        "DOUBLEJUMPSTRENGTH": 16,
        "GRAV": 0.6,
        "TRACTION": 0.9,
        "SPRITESHEET": {
            "STAND": ((0, 0), (192, 192)),
            "DASH": ((192, 0), (192, 192)),
            "WALK": ((384, 0), (192, 192)),
            "JUMPSQUAT": ((576, 0), (192, 192)),
            "ARIAL": ((768, 0), (192, 192)),
            "LANDING": ((960, 0), (192, 192)),
            "GROUNDATK0:1": ((1152, 0), (192, 192)),
            "GROUNDATK0:4": ((1344, 0), (192, 192)),
            "GROUNDATK0:12": ((1536, 0), (192, 192)),
            "GROUNDATK0:18": ((1728, 0), (192, 192)),
            "HITLAG": ((1920, 0), (192, 192)),
            "HITSTUN" :((2112, 0), (192, 192)),
            "HITLAND": ((2304, 0), (192, 192)),
        },
        "SSFILENAME": "swordie.png",
        "MSFILENAME": "swordie"
    },
    "BRAWLER": {
        "MAXHP": 100,
        "W": 128,
        "H": 128,
        "WALKSPEED": 3,
        "DASHSPEED": 10,
        "JUMPSTRENGTH": -16,
        "BASELANDINGLAG": 3,
        "DOUBLEJUMPSTRENGTH": 16,
        "GRAV": 0.8,
        "TRACTION": 0.6,
        "SPRITESHEET": {
            "STAND": ((0, 0), (128, 128)),
            "DASH": ((128, 0), (128, 128)),
            "WALK": ((256, 0), (128, 128)),
            "JUMPSQUAT": ((384, 0), (128, 128)),
            "ARIAL": ((512, 0), (128, 128)),
            "LANDING": ((640, 0), (128, 128)),
        },
        "SSFILENAME": "brawler.png",
        "MSFILENAME": "brawler"
    },
    "SPEEDLE": {
        "MAXHP": 100,
        "W": 128,
        "H": 128,
        "WALKSPEED": 5,
        "DASHSPEED": 10,
        "JUMPSTRENGTH": -20,
        "BASELANDINGLAG": 3,
        "DOUBLEJUMPSTRENGTH": 20,
        "GRAV": 1,
        "TRACTION": 0.8,
        "SPRITESHEET": {
            "STAND": ((0, 0), (128, 128)),
            "DASH": ((128, 0), (128, 128)),
            "WALK": ((256, 0), (128, 128)),
            "JUMPSQUAT": ((384, 0), (128, 128)),
            "ARIAL": ((512, 0), (128, 128)),
            "LANDING": ((640, 0), (128, 128)),
        },
        "SSFILENAME": "speedle.png",
        "MSFILENAME": "speedle"
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
        self.dash = None

        self.jump_strength = template["JUMPSTRENGTH"]
        self.double_jump_strength = template["DOUBLEJUMPSTRENGTH"]
        self.has_double_jump = True
        self.can_double_jump = False
        self.platform_drop = False

        self.landing_lag = 0
        self.base_landing_lag = template["BASELANDINGLAG"]

        self.grav = template["GRAV"]
        self.traction = template["TRACTION"]

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
        self.X_DI = 0
        self.Y_DI = 0
        self.DI_cap = 0

        self.strikelag = 0
        self.hitlag = 0
        self.hitstun = 0
        self.knockback_angle = (0, 0) # velocity mod
        self.knockback_strength = 0
        
        self.combo = 0

        self.spritesheet = load_spritesheet(template["SSFILENAME"], template["SPRITESHEET"])

        self.state = "STAND"
        self.frame = 0
        self.direction = 1

        self.frame_data_filename = template["MSFILENAME"]
        self._load_moves()

        self.hitboxes = []
        self.hitbox_data = []
        self.hurtboxes = []
        self.ECB = []

        self.update_boxes()

    def _load_moves(self):
        try:
            with open("src/bin/"+self.frame_data_filename) as f:
                self.data = eval(f.read())
            return self.data
        except IOError:
            print("Missing file: "+self.frame_data_filename)
            return None

    def _get_move_identifier(self):
        if self.state in self.data: return self.state
        x = self.frame
        while x >= 0:
            name = self.state + ":" + str(x)
            if name in self.data: return name
            x -= 1
        return None

    def get_move_data(self):
        name = self._get_move_identifier()
        return self.data[name] if name is not None else {
            "ACTIONABLE":[],"HITBOXES":[],"HURTBOXES":[],"ECB":[]
        }

    def flip_rect(self, rect_style):
        pos, dim = rect_style
        x, y = pos
        w, h = dim

        r = self.W
        r -= x + w
        return (r, y), dim

    def get_hitbox_data(self, box):
        x, y, w, h = box.x, box.y, box.w, box.h
        for hitbox in self.hitbox_data:
            if ((x-self.X, y-self.Y), (w, h)) in hitbox["RECTS"]: return hitbox
            if self.flip_rect(((x-self.X, y-self.Y), (w, h))) in hitbox["RECTS"]: return hitbox
        return None

    def update_boxes(self):
        move_data = self.get_move_data()
        self.hitboxes = []
        self.hitbox_data = []
        self.ECB = []
        self.hurtboxes = []
        
        self.hitbox_data = move_data["HITBOXES"]

        for hitbox in move_data["HITBOXES"]:
            for rect in hitbox["RECTS"]:
                box = self.flip_rect(rect) if self.direction < 0 else rect
                self.hitboxes.append(Rect(box[0][0] + self.X, box[0][1] + self.Y, box[1][0], box[1][1]))

        for hurtbox in move_data["HURTBOXES"]:
            if self.direction < 0:
                hurtbox = self.flip_rect(hurtbox)
            self.hurtboxes.append(Rect(hurtbox[0][0] + self.X, hurtbox[0][1] + self.Y, hurtbox[1][0], hurtbox[1][1]))

        for ecb in move_data["ECB"]:
            if self.direction < 0:
                ecb = self.flip_rect(ecb)
            self.ECB.append(Rect(ecb[0][0] + self.X, ecb[0][1] + self.Y, ecb[1][0], ecb[1][1]))

    def check_collision(self, enemy):
        priority_hitbox = None
        for hurtbox in self.hurtboxes:
            for hitbox in hurtbox.collidelistall(enemy.hitboxes):
                data = enemy.get_hitbox_data(enemy.hitboxes[hitbox])
                priority_hitbox = data if priority_hitbox is None or data["PRIO"] > priority_hitbox["PRIO"] else priority_hitbox

        if priority_hitbox is not None:
            self.hitstun = priority_hitbox["HITSTUN"]
            self.hitlag = priority_hitbox["HITLAG"]
            self.knockback_angle = priority_hitbox["ANGLE"][0] * enemy.direction, priority_hitbox["ANGLE"][1]
            self.knockback_strength = priority_hitbox["STRENGTH"]
            enemy.strikelag = priority_hitbox["HITLAG"]
            self.DI_cap = priority_hitbox["DI"]

    def _check_floor(self, floor):
        lowest = None
        for rect in self.ECB:
            if lowest is None or lowest.bottom > rect.bottom:
                lowest = rect
        if lowest is not None and lowest.bottom > floor:
            return True, floor
        return False, 0

    def _check_plats(self, plats):
        if self.Y_VEL >= 0:
            for plat in plats:
                for ecbox in self.ECB:
                    if plat.colliderect(ecbox):
                        return True, plat.top
        return False
    
    def update_DI(self):
        x, y = self._dir_as_tuple()
        if abs(self.X_DI + 0.1 * x) < 1:
            self.X_DI += 0.1 * x
        if abs(self.Y_DI + 0.1 * y) < 1:
            self.Y_DI += 0.1 * y
    
    def ecb_collision(self, G):
        move_data = self.get_move_data()
        stage = G["STAGE"]
        plats = stage["PLAT"]
        floor = stage["HEIGHT"]

        collision, offset = self._check_plats(plats) or self._check_floor(floor)
        if collision and self.state in ["ARIAL", "ARIALATK0", "ARIALATK1", "HITSTUN"]:
            self.has_double_jump = True
            self.Y = offset - self.H
            if self.state == "HITSTUN":
                self.state = "HITLAND"
                self.landing_lag = self.hitstun
            elif "LANDINGLAG" in move_data["ACTIONABLE"]:
                self.state = "LANDINGLAG"
                self.landing_lag = move_data["LANDINGLAG"]
            else:
                self.state = "LANDING"
                self.landing_lag = self.base_landing_lag

    def draw_boxes(self, G, surf):
        for ecbox in self.ECB:
            pygame.draw.rect(surf, (0, 0, 255), G["SCROLL"](ecbox), width=1)
        for hitbox in self.hitboxes:
            pygame.draw.rect(surf, (255, 0, 0), G["SCROLL"](hitbox), width=1)
        for hurtbox in self.hurtboxes:
            pygame.draw.rect(surf, (0, 155, 0), G["SCROLL"](hurtbox), width=1)

    def get_sprite(self, G):
        sprite = self._get_sprite() if not self.direction > 0 else pygame.transform.flip(self._get_sprite(), 1, 0)
        if G["DEBUG"]:
            self.draw_boxes(G, G["SCREEN"])
        return sprite
            
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
        surf.blit(HEL16.render(self.state, 0, (0, 0, 0)), (0, 0))
        return surf
        
    def update_state(self):
        move_data = self.get_move_data()
        state = self.state

        if self.strikelag: return
        if self.hitlag:
            self.state = "HITLAG"
        elif self.state != "HITLAND" and self.hitstun:
            self.state = "HITSTUN"
        # JUMP FUNCTIONALITY
        elif self.inp["BTN2"] and "JUMPSQUAT" in move_data["ACTIONABLE"]:
            self.state = "JUMPSQUAT"
        elif self.inp["BTN2"] and "DOUBLEJUMP" in move_data["ACTIONABLE"] and self.has_double_jump and self.can_double_jump:
            self.state = "DOUBLEJUMP"
        elif self.state == "JUMPSQUAT" and "JUMP" in move_data["ACTIONABLE"]:
            self.state = "JUMP"

        # DASH FUNCTIONALITY
        elif self.inp["BTN3"] and self.dash is None and "DASH" in move_data["ACTIONABLE"] and (self.inp["LEFT"] != self.inp["RIGHT"]):
                self.state = "DASH"
        elif self.dash is not None:
            if not self.inp["BTN3"]:
                self.dash = None
                self.state = "STAND"
        elif not self.inp["BTN3"] and "WALK" in move_data["ACTIONABLE"] and (self.inp["LEFT"] or self.inp["RIGHT"]):
                self.state = "WALK"

        # GROUNDED ATTACK FUNCTIONALITY
        elif self.inp["BTN0"] and "GROUNDATK0" in move_data["ACTIONABLE"]:
            self.state = "GROUNDATK0"
        elif self.inp["BTN1"] and "GROUNDATK1" in move_data["ACTIONABLE"]:
            self.state = "GROUNDATK1"

        # ARIAL ATTACK FUNCTIONALITY
        elif self.inp["BTN0"] and "ARIALATK0" in move_data["ACTIONABLE"]:
            self.state = "ARIALATK0"
        elif self.inp["BTN1"] and "ARIALATK1" in move_data["ACTIONABLE"]:
            self.state = "ARIALATK1"

        # DASH ATTACK FUNCTIONALITY
        elif self.inp["BTN0"] and "DASHATK0" in move_data["ACTIONABLE"]:
            self.state = "DASHATK0"
        elif self.inp["BTN1"] and "DASHATK1" in move_data["ACTIONABLE"]:
            self.state = "DASHATK1"

        elif self.state in ["LANDING", "LANDINGLAG" , "HITLAND"]:
            if self.landing_lag == 0:
                self.state = "STAND"
            self.landing_lag -= 1
        # DEFAULT BACK TO STAND
        elif "STAND" in move_data["ACTIONABLE"]:
            self.state = "STAND"

        if state != self.state:
            self.frame = 0

    def _dir_as_tuple(self):
        x = self.inp["LEFT"] * -1 + self.inp["RIGHT"] * 1
        y = self.inp["UP"] * -1 + self.inp["DOWN"] * 1
        return (x, y)
        
    def apply_state(self, G):
        d = self._dir_as_tuple()
        if self.strikelag:
            self.strikelag -= 1
            return
        if self.state == "HITLAG":
            if self.frame == 0:
                self.HP -= self.knockback_strength
                self.X_VEL, self.Y_VEL = 0, 0
            self.hitlag -= 1
            return
        if self.state in ["HITSTUN", "HITLAND"]:
            self.hitstun -= 1
            if self.frame == 0:
                if self.state == "HITSTUN":
                    kbangle = shift_angle(self.knockback_angle, self.DI_cap * ((self.X_DI + self.Y_DI)/2))
                    self.X_VEL = self.knockback_strength * kbangle[0] * (self.combo + 1)
                    self.Y_VEL = 0 - self.knockback_strength * kbangle[1] * (self.combo + 1)
            if self.state == "HITSTUN":
                self.Y_VEL += self.grav
            else:
                self.Y_VEL = 0
            if self.hitstun == 0:
                self.state = "ARIAL" if self.state == "HITSTUN" else "STAND"
            return
        if self.state in ["STAND", "WALK"]:
            self.platform_drop = self.inp["DOWN"] and self.inp["BTN2"]
            self.direction = d[0] if d[0] else self.direction

        if self.frame == 0:
            if self.state == "JUMP":
                self.Y_VEL = self.jump_strength
                self.state = "ARIAL"
                self.can_double_jump = False
            if self.state == "DOUBLEJUMP":
                self.X_VEL = self.double_jump_strength * d[0]
                self.Y_VEL = self.double_jump_strength * d[1]
                if all(d):
                    self.X_VEL *= 0.7
                    self.Y_VEL *= 0.7
                self.has_double_jump = False
                self.state = "ARIAL"
            if self.state == "DASH":
                self.dash = self.direction
        
        if self.state == "ARIAL" and not self.inp["BTN2"]:
            self.can_double_jump = True

        if self.state in ["STAND", "WALK", "DASH", "GROUNDATK0", "GROUNDATK1", "DASHATK0", "DASHATK1"]:
            self.X_VEL *= self.traction if abs(self.X_VEL) > 1 else 0
        if self.state in ["STAND", "LANDING", "LANDINGLAG"]:
            self.Y_VEL = 0

        if self.state == "WALK":
            if not abs(self.X_VEL) > self.walk_speed:
                self.X_VEL = self.walk_speed * d[0]

        if self.state == "DASH":
            self.X_VEL = self.dash_speed * self.dash
        else:
            self.dash = None

        if self.state == "ARIAL":
            self.Y_VEL += self.grav

        if self.state not in ["ARIAL", "ARIALATK0", "ARIALATK1"] and not self._on_land(G):
            self.state = "ARIAL"
            

    def _on_land(self, G):
        self.ECB = [Rect(ecbox.x, ecbox.y+8, ecbox.w, ecbox.h) for ecbox in self.ECB]
        collisions, offset = self._check_plats(G["STAGE"]["PLAT"]) or self._check_floor(G["STAGE"]["HEIGHT"])
        self.update_boxes()
        return collisions

    def update(self, G):
        opponent = G["P2"]["ACTIVE"] if G["P1"]["ACTIVE"] is self else G["P1"]["ACTIVE"]
        self.check_collision(opponent)
        self.ecb_collision(G)

        self.update_boxes()

        self.update_state()
        self.apply_state(G)

        if not self.strikelag:
            self.X += self.X_VEL
            self.Y += self.Y_VEL
            self.X = int(self.X)
            self.Y = int(self.Y)
            self.update_boxes()
            self.frame = min(self.frame + 1, 500)
        else:
            self.update_DI()

    def DEBUG(self, G):
        x = 0 if G["P1"]["ACTIVE"] is self else 512
        y = 256
        G["SCREEN"].blit(G["HEL16"].render("STATE:{}".format(self.state), 0, (80, 0, 0)), (x, y))
        y += 16
        G["SCREEN"].blit(G["HEL16"].render("FRAME:{}".format(self.frame), 0, (80, 0, 0)), (x, y))
        y += 16
        G["SCREEN"].blit(G["HEL16"].render("POSITION: ({}, {})".format(self.X, self.Y), 0, (80, 0, 0)), (x, y))
        y += 16
        G["SCREEN"].blit(G["HEL16"].render("X VEL:{} Y VEL: {}".format(self.X_VEL, self.Y_VEL), 0, (80, 0, 0)), (x, y))
        y += 16
        G["SCREEN"].blit(G["HEL16"].render("HITLAG: {}".format(self.hitlag), 0, (80, 0, 0)), (x, y))
        y += 16
        G["SCREEN"].blit(G["HEL16"].render("STRIKELAG: {}".format(self.strikelag), 0, (80, 0, 0)), (x, y))
        y += 16
        G["SCREEN"].blit(G["HEL16"].render("HITSTUN: {}".format(self.hitstun), 0, (80, 0, 0)), (x, y))
        y += 16
        G["SCREEN"].blit(G["HEL16"].render("KB ANGLE: {}".format(self.knockback_angle), 0, (80, 0, 0)), (x, y))
        y += 16
        G["SCREEN"].blit(G["HEL16"].render("KB STR: {}".format(self.knockback_strength), 0, (80, 0, 0)), (x, y))
        y += 16
        G["SCREEN"].blit(G["HEL16"].render("PLAT DROP: {}".format(self.platform_drop), 0, (80, 0, 0)), (x, y))
        y += 16
        G["SCREEN"].blit(G["HEL16"].render("ON LAND: {}".format(self._on_land(G)), 0, (80, 0, 0)), (x, y))
        y += 16
        G["SCREEN"].blit(G["HEL16"].render("--INPUTS--", 0, (80, 0, 0)), (x, y))
        y += 16
        G["SCREEN"].blit(G["HEL16"].render("L:{LEFT} U:{UP} R:{RIGHT} D:{DOWN}".format(**self.inp), 0, (80, 0, 0)), (x, y))
        y += 16
        G["SCREEN"].blit(G["HEL16"].render("A:{BTN0} B:{BTN1} X:{BTN2} Y:{BTN3}".format(**self.inp), 0, (80, 0, 0)), (x, y))
