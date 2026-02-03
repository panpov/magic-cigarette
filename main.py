# title: Magic Cigarette
# author: Panharith Pov
# desc: smoke a magic cigarette to destroy two lungs!
# license: MIT
# version: 1.0

import pyxel
import time

# Game setup
TITLE = "Magic Cigarette"
SCRN_CLR = 4
SCRN_W = 128
SCRN_H = 128
FPS = 30

# Player
PLYR_W = 24
PLYR_H = 4
BUTT_W = 8
PLYR_PRM_CLR = 7
PLYR_SEC_CLR = 9
PLYR_TER_CLR = 13

PLYR_SPD = 1
MAX_CHRG = 16
CHRG_STR = 1
CHRG_SPD = 4
CLDWN_SPD = 8

INIT_X = 52
INIT_Y = 118

# Misc
SMK_CLR = 10
LUNG_BCLR = 14
LUNG_SCLR = 2
WALL_FIZZLE_AMT = 1
LUNG_FIZZLE_AMT = 0.5

smoke_particles = []

def power_cutoff(power):
    match power:
        case x if x < 4:
            return 1
        case x if x < 8:
            return 2
        case x if x < 12:
            return 3
        case _:
            return 4

class Smoke:
    def __init__(self, x, y, r, dx, dy):
        self.x = x
        self.y = y
        self.r = r
        
        self.dx = dx
        self.dy = dy
        
        smoke_particles.append(self)
    
    def bounce(self, direction, fizzle_amount):
        if direction == "h":
            self.dx *= -1
        else:
            self.dy *= -1
        self.r -= fizzle_amount
    
    def within_bounds(self):
        if self.x >= pyxel.width or self.x < 0:
            pyxel.play(1, 2)
            self.bounce("h", 1)
        elif self.y < 0:
            pyxel.play(1, 2)
            self.bounce("v", 1)
    
    def explode(self):
        pyxel.images[1].circ(self.x, self.y, self.r + 1, SCRN_CLR)
    
    def collision(self):
        # vertical
        if (pyxel.images[1].pget(self.x, self.y + (self.dy * self.r)) == LUNG_BCLR
            or pyxel.images[1].pget(self.x, self.y + (self.dy * self.r)) == LUNG_SCLR):
            pyxel.play(1, 1)
            self.explode()
            self.bounce("v", 0.5)
        # horizontal
        elif (pyxel.images[1].pget(self.x + (self.dx * self.r), self.y) == LUNG_BCLR
              or pyxel.images[1].pget(self.x + (self.dx * self.r), self.y) == LUNG_SCLR):
            pyxel.play(1, 1)
            self.explode()
            self.bounce("h", 0.5)
        
    def update(self):
        if self.r <= 0 or self.y >= pyxel.height:
            smoke_particles.remove(self)
            
        self.collision()
        self.within_bounds()
        
        self.x += self.dx
        self.y += self.dy
    
    def draw(self):
        pyxel.circ(self.x, self.y, self.r, SMK_CLR)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # 1 = right, -1 = left
        self.dir = 1
        self.arrow_x_offset = 0
        
        self.power = 0
        self.charge = 0
        self.charge_timer = 0
        self.cooldown_timer = -1
    
    def shoot(self):
        smoke_radius = power_cutoff(self.power)
        if self.dir == 1:
            dx = 1
        else:
            dx = -1
        
        pyxel.play(1, 3)
        Smoke((self.x + PLYR_W) - self.charge, self.y - 1, smoke_radius, dx, -1)
        self.power = 0
    
    def smoke(self):
        self.cooldown_timer = -1
        if self.charge < MAX_CHRG:
            if self.charge_timer == CHRG_SPD:
                self.power += 1
                self.charge += 1
                self.charge_timer = 0
            else:
                self.charge_timer += 1

    def cooldown(self):
        self.charge_timer = 0
        if self.charge > 0:
            if self.cooldown_timer == CLDWN_SPD:
                self.charge -= 1
                self.cooldown_timer = 0
            else:
                self.cooldown_timer += 1
        else:
            self.cooldown_timer = -1

    def controls(self):
        if pyxel.btnr(pyxel.KEY_SPACE) and self.power != 0:
            self.shoot()
        elif pyxel.btn(pyxel.KEY_SPACE):
            self.smoke()
        else:
            self.cooldown()
        
        if pyxel.btn(pyxel.KEY_LEFT) and self.x > 0:
            self.x -= PLYR_SPD
            self.dir = -1
            self.arrow_x_offset = 4
        if pyxel.btn(pyxel.KEY_RIGHT) and self.x < pyxel.width - (PLYR_W - self.charge):
            self.x += PLYR_SPD
            self.dir = 1
            self.arrow_x_offset = 0
    
    def draw(self):
        # base
        pyxel.rect(self.x, self.y, PLYR_W - self.charge, PLYR_H, PLYR_PRM_CLR)
        
        # butt
        pyxel.rect(self.x, self.y, BUTT_W, PLYR_H, PLYR_SEC_CLR)
        
        # charge
        pyxel.rect((self.x + PLYR_W) - self.charge, self.y, self.power, PLYR_H, PLYR_TER_CLR)
        
        # recharge (black)
        if self.charge > 0:
            pyxel.rect((self.x + PLYR_W) - self.charge, self.y, 1, PLYR_H, PLYR_TER_CLR)
        
        # direction arrow
        pyxel.blt(self.x + (PLYR_W - self.charge) - self.arrow_x_offset,
                  self.y - PLYR_H, 2, 0, 0, 4 * self.dir, 4, 0)

class Game:
    def __init__(self):
        pyxel.init(SCRN_W, SCRN_H, title=TITLE, fps=FPS)
        pyxel.load("resources.pyxres")
        
        self.player = Player(INIT_X, INIT_Y)
        self.start = True
        self.start_time = 0
        self.min = 0
        self.sec = 0
        
        pyxel.playm(0, loop=True)
        pyxel.run(self.update, self.draw)

    def deflect_smoke(self, smoke):
        if (smoke.x >= self.player.x
            and smoke.x <= self.player.x + PLYR_W - self.player.charge
            and smoke.y >= self.player.y
            and smoke.y <= self.player.y + PLYR_H):
            pyxel.play(1, 4)
            smoke.bounce("v", 0)

    def update(self):
        if self.start:
            if pyxel.btn(pyxel.KEY_SPACE):
                pyxel.play(1, 5)
                self.start = False
                self.start_time = time.time()
        else:
            self.player.controls()
            for smoke in smoke_particles:
                self.deflect_smoke(smoke)
                smoke.update()
            
            self.min, self.sec = divmod(time.time() - self.start_time, 59)

    def draw(self):
        pyxel.cls(SCRN_CLR)
        pyxel.blt(0, 0, 1, 0, 0, SCRN_W, SCRN_H)
        
        self.player.draw()
        for smoke in smoke_particles:
            smoke.draw()
        
        if self.start:
            pyxel.text(25, 60, "<- ->", 8)
            pyxel.text(20, 66, "to move", 7)
            pyxel.text(84, 60, "SPACE", 8)
            pyxel.text(78, 66, "to shoot", 7)
            pyxel.text(24, 100, "Press SPACE to start", 7)
            pyxel.text(48, 100, "SPACE", 8)
        else:
            # timer
            pyxel.text(4, 4, "{:02.0f}:{:02.0f}".format(self.min, self.sec), 7)

Game()