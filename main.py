# title: Magic Cigarette
# author: Pan Pov
# last modified: 04/25/2026
# desc: smoke a magic cigarette to destroy your lungs!
# license: MIT
# version: 1.1

import pyxel
import time

# Game setup
TITLE = "Magic Cigarette"
SCRN_CLR = 4
SCRN_W = 128
SCRN_H = 128
FPS = 30

# Player appearance
PLYR_W = 24
PLYR_H = 4
BUTT_W = 8
PLYR_PRM_CLR = 7
PLYR_SEC_CLR = 9
PLYR_TER_CLR = 13
ARROW_U_OFFSET = 3
ARROW_L_OFFSET = 4

# Player logic
PLYR_SPD = 1
MAX_CHRG = 16
CHRG_STR = 1
CHRG_SPD = 1
CLDWN_SPD = 2
EXPLSN_STR = 3

INIT_X = 52
INIT_Y = 118

# Misc.
SMK_CLR = 10
LUNG_BCLR = 14
LUNG_SCLR = 2
WALL_FIZZLE_AMT = 1
LUNG_FIZZLE_AMT = 0.5

# used for game_over
# lung pixels are bounded by these
MIN_X = 10
MAX_X = 118
MAX_Y = 92

# Sound
SND_BOUNCE = 2
SND_SHOOT = 3
SND_DEFLECT = 4
SND_START = 5

########################################################################################

smoke_particles = []
is_game_over = False

def power_cutoff(power):
    """Rounds given power (charge amount)"""
    match power:
        case x if x < 4:
            return 2
        case x if x < 8:
            return 3
        case x if x < 12:
            return 4
        case _:
            return 5

def game_over():
    """If all pixels in image bank 1 (which is the stage) are SCRN_CLR, game over."""
    for y in range(MAX_Y):
        for x in range(MIN_X, MAX_X):
            if pyxel.images[1].pget(x, y) != SCRN_CLR:
                return False
    return True

########################################################################################

class Smoke:
    def __init__(self, x, y, r, dx, dy):
        self.x = x
        self.y = y
        self.r = r
        
        self.dx = dx
        self.dy = dy
        
        smoke_particles.append(self)
    
    def bounce(self, direction, fizzle_amount):
        """Bounces smoke in the opposite of given direction and reduces size of smoke by
        fizzle_amount"""
        if direction == "h":
            self.dx *= -1
        else:
            self.dy *= -1
        self.r -= fizzle_amount
        global is_game_over
        is_game_over = game_over()
    
    def within_bounds(self):
        """Checks if smoke is within game screen, bouncing it if not"""
        if self.x >= pyxel.width or self.x < 0:
            pyxel.play(1, SND_BOUNCE)
            self.bounce("h", 1)
        elif self.y < 0:
            pyxel.play(1, SND_BOUNCE)
            self.bounce("v", 1)
    
    def explode(self):
        """Replaces pixels of lungs with color of screen, mimicking explosion"""
        pyxel.images[1].circ(self.x, self.y, self.r + EXPLSN_STR, SCRN_CLR)
    
    def collision(self):
        """Checks if pixel of background at smoke's coordinates is color of lungs or
        lungs' border, calling self.explode() and self.bounce() if so"""
        # vertical check
        if (pyxel.images[1].pget(self.x, self.y + (self.dy * self.r)) == LUNG_BCLR
            or pyxel.images[1].pget(self.x, self.y + (self.dy * self.r)) == LUNG_SCLR):
            pyxel.play(1, 1)
            self.explode()
            self.bounce("v", 0.5)
        # horizontal check
        elif (pyxel.images[1].pget(self.x + (self.dx * self.r), self.y) == LUNG_BCLR
              or pyxel.images[1].pget(self.x + (self.dx * self.r), self.y) == LUNG_SCLR):
            pyxel.play(1, 1)
            self.explode()
            self.bounce("h", 0.5)
        
    def update(self):
        """Smoke instance is deleted if radius is 0 or is under screen bottom. Otherwise,
        move smoke in direction of attack"""
        if self.r <= 0 or self.y >= pyxel.height:
            smoke_particles.remove(self)
            
        self.collision()
        self.within_bounds()
        
        self.x += self.dx
        self.y += self.dy
    
    def draw(self):
        pyxel.circ(self.x, self.y, self.r, SMK_CLR)

########################################################################################

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
        # used for arrow indicator. -1 = left, 0 = up, 1 = right
        self.dir = 1
        self.arrow_x_offset = 0
        
        self.power = 0
        self.charge = 0
        self.charge_timer = 0
        self.cooldown_timer = -1
    
    def shoot(self):
        """Spawns smoke going in direction of arrow"""
        smoke_radius = power_cutoff(self.power)
        dx = self.dir
        
        pyxel.play(1, SND_SHOOT)
        # spawn smoke at the end of "smoked" part
        Smoke((self.x + PLYR_W) - self.charge, self.y - 1, smoke_radius, dx, -1)
        self.power = 0
    
    def smoke(self):
        """Charge up attack, increasing size of smoke up until MAX_CHRG. While charging,
        smoked part does not recover (via cooldown_timer). charge is used to draw smoked
        part correctly, while power is what is actually used for size of smoke."""
        self.cooldown_timer = -1
        if self.charge < MAX_CHRG:
            if self.charge_timer == CHRG_SPD:
                self.power += 1
                self.charge += 1
                self.charge_timer = 0
            else:
                self.charge_timer += 1

    def cooldown(self):
        """While not charging attack, recover smoked part to allow for bigger attacks."""
        self.charge_timer = 0
        if self.charge > 0:
            if self.cooldown_timer == CLDWN_SPD:
                # reduce length of smoked part box
                self.charge -= 1
                self.cooldown_timer = 0
            else:
                self.cooldown_timer += 1
        else:
            self.cooldown_timer = -1

    def controls(self):
        """Controls for the magic cigarette (the player)"""
        # shoot smoke if player has charged up at least 1 point of power
        if pyxel.btnr(pyxel.KEY_SPACE) and self.power != 0:
            self.shoot()
        elif pyxel.btn(pyxel.KEY_SPACE):
            self.smoke()
        else:
            self.cooldown()
        
        # update location/direction of arrow depending direction of movement
        if pyxel.btn(pyxel.KEY_UP):
            self.dir = 0
            self.arrow_x_offset = ARROW_U_OFFSET
        if pyxel.btn(pyxel.KEY_LEFT) and self.x > 0:
            self.x -= PLYR_SPD
            self.dir = -1
            self.arrow_x_offset = ARROW_L_OFFSET
        if pyxel.btn(pyxel.KEY_RIGHT) and self.x < pyxel.width - (PLYR_W - self.charge):
            self.x += PLYR_SPD
            self.dir = 1
            self.arrow_x_offset = 0
    
    def draw(self):
        """Draw player on the screen"""
        # base rectangle
        pyxel.rect(self.x, self.y, PLYR_W - self.charge, PLYR_H, PLYR_PRM_CLR)
        
        # cigarette butt
        pyxel.rect(self.x, self.y, BUTT_W, PLYR_H, PLYR_SEC_CLR)
        
        # charge (smoked part)
        pyxel.rect((self.x + PLYR_W) - self.charge, self.y, self.power, PLYR_H,
                   PLYR_TER_CLR)
        
        # recharge (black)
        if self.charge > 0:
            pyxel.rect((self.x + PLYR_W) - self.charge, self.y, 1, PLYR_H, PLYR_TER_CLR)
        
        # shooting direction indicator/arrow
        if self.dir == 0:
            pyxel.blt(self.x + (PLYR_W - self.charge) - self.arrow_x_offset,
                      self.y - PLYR_H - 1, 2, 0, 8, 5, 5, 0)
        else:
            pyxel.blt(self.x + (PLYR_W - self.charge) - self.arrow_x_offset,
                      self.y - PLYR_H, 2, 0, 0, 4 * self.dir, 4, 0)

########################################################################################

class Game:
    def __init__(self):
        pyxel.init(SCRN_W, SCRN_H, title=TITLE, fps=FPS)
        pyxel.load("resources.pyxres")
        
        self.player = Player(INIT_X, INIT_Y)
        self.start = True
        self.tut = True
        self.restart = False
        self.start_time = 0
        self.min = 0
        self.sec = 0
        
        # background music
        pyxel.playm(0, loop=True)
        pyxel.run(self.update, self.draw)

    def restart_game(self):
        self.start = False
        self.tut = False
        self.restart = False
        global smoke_particles, is_game_over
        smoke_particles = []
        is_game_over = False
        
        self.player.x = INIT_X
        self.player.y = INIT_Y
        self.start_time = time.time()
        self.min = 0
        self.sec = 0
        pyxel.images[1].blt(0, 0, 1, 128, 0, 128, 128)

    def deflect_smoke(self, smoke):
        """Allow player to deflect smoke without making it fizzle"""
        if (smoke.x >= self.player.x
            and smoke.x <= self.player.x + PLYR_W - self.player.charge
            and smoke.y >= self.player.y
            and smoke.y <= self.player.y + PLYR_H):
            pyxel.play(1, SND_DEFLECT)
            smoke.bounce("v", 0)

    def update(self):
        """Main gameplay updater"""
        if self.start:
            if pyxel.btnr(pyxel.KEY_SPACE):
                pyxel.play(1, SND_START)
                self.start = False
        elif self.tut:
            if pyxel.btnr(pyxel.KEY_SPACE):
                pyxel.play(1, SND_START)
                self.tut = False
                self.start_time = time.time()
        elif self.restart:
            if pyxel.btnr(pyxel.KEY_SPACE):
                pyxel.play(1, SND_START)
                self.restart_game()
        else:
            if not is_game_over:
                self.player.controls()
                for smoke in smoke_particles:
                    self.deflect_smoke(smoke)
                    smoke.update()
                
                # update timer
                self.min, self.sec = divmod(time.time() - self.start_time, 59)
            else:
                self.restart = True
                
    def draw(self):
        """Draw everything on the screen"""
        pyxel.cls(SCRN_CLR)
        
        if self.start:
            pyxel.blt(0, 0, 0, 0, 0, SCRN_W, SCRN_H)
            pyxel.text(103, 92, "v1.1", 7)
            pyxel.text(24, 111, "Press SPACE to start", 5)
            pyxel.text(48, 111, "SPACE", 8)
            pyxel.blt(46, 110, 2, 16, 0, 23, 8, 0)
        elif self.tut:
            pyxel.blt(0, 0, 0, 128, 0, SCRN_W, SCRN_H)
            pyxel.text(42, 10, "How to Play", 5)
            
            pyxel.blt(50, 24, 2, 16, 0, 23, 8, 0)
            pyxel.text(12, 35, "Hold to charge your attack", 5)
            pyxel.text(12, 35, "Hold", 8)
            pyxel.text(12, 43, "Let go to shoot!", 5)
            pyxel.text(12, 43, "Let go", 8)
            
            pyxel.blt(49, 52, 2, 0, 16, 26, 8, 0)
            pyxel.text(12, 63, "Press to move and aim", 5)
            pyxel.text(12, 63, "Press", 8)
            pyxel.text(12, 71, "Deflect your own attacks!", 5)
            pyxel.text(12, 71, "Deflect", 8)
            
            pyxel.blt(54, 80, 2, 16, 8, 15, 8, 0)
            pyxel.text(12, 91, "Press to exit the game", 5)
            pyxel.text(12, 91, "Press", 8)
            
            pyxel.text(24, 111, "Press SPACE to start", 5)
            pyxel.blt(46, 110, 2, 16, 0, 23, 8, 0)
        elif self.restart:
            pyxel.text(4, 4, "{:02.0f}:{:02.0f}".format(self.min, self.sec), 7)
            
            pyxel.text(42, 32, "You did it!", 7)
            pyxel.text(32, 42, "How does it", 7)
            pyxel.text(80, 42, "feel?", 9)
            pyxel.text(32, 52, "To have", 7)
            pyxel.text(64, 52, "no lungs?", 9)
            
            pyxel.text(16, 72, "Try again to see how much", 7)
            pyxel.text(24, 82, "faster you can smoke!", 7)
            pyxel.text(24, 82, "faster", 9)
            
            pyxel.text(22, 111, "Press SPACE to restart", 7)
            pyxel.blt(44, 110, 2, 16, 0, 23, 8, 0)
        else:
            pyxel.blt(0, 0, 1, 0, 0, SCRN_W, SCRN_H)
            self.player.draw()
            for smoke in smoke_particles:
                smoke.draw()
            
            # timer
            pyxel.text(4, 4, "{:02.0f}:{:02.0f}".format(self.min, self.sec), 7)

Game()
