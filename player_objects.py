# load PyGame from main file
from my_shooter import *


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)  # can use super().init as well --> update: NOOOT
        self.image = pygame.image.load("ship.png")
        self.rect = self.image.get_rect()
        self.speed = 10
        self.size = 24
        self.rect.centerx = int(WIDTH / 2)
        self.rect.bottom = HEIGHT - 10
        self.shield = 0
        self.lives = 3
        self.invulnerable = False
        self.timer = None
        self.multi_shoot = False
        self.multi_shoot_timer = None
        self.multi_shoot_points = 50

    def update(self):
        now = pygame.time.get_ticks()
        key_state = pygame.key.get_pressed()
        if key_state[pygame.K_LEFT]:
            self.rect.x -= self.speed
        elif key_state[pygame.K_RIGHT]:
            self.rect.x += self.speed

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

        # detect if player is invulnerable and start ticking two seconds
        if self.invulnerable and now - self.timer > 2000:
            self.invulnerable = False

        # disable multi shoot after 5 seconds
        if self.multi_shoot and now - self.multi_shoot_timer > 5000:
            self.multi_shoot = False

    def shoot(self):
        if not self.multi_shoot:  # multi shoot is off... normal situation so conditioned first
            bullet = Bullet(self.rect.centerx, self.rect.top, 0)
            return bullet
        else:  # multi shoot is on!
            bullet_1 = Bullet(self.rect.centerx, self.rect.top, 0)
            bullet_2 = Bullet(self.rect.centerx, self.rect.top, -2)
            bullet_3 = Bullet(self.rect.centerx, self.rect.top, 2)
            bullets = [bullet_1, bullet_2, bullet_3]
            return bullets

    def damage(self):
        if not self.invulnerable:  # without invulnerability player loses life and enables invulnerability
            self.lives -= 1
            self.invulnerable = True
            self.timer = pygame.time.get_ticks()
        if self.lives == 0:
            self.kill()
            return True
        return False

    def enable_multi_shoot(self):
        self.multi_shoot = True
        self.multi_shoot_timer = pygame.time.get_ticks()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, x_speed):  # pass location where to spawn bullet and x_speed for multi shoot
        pygame.sprite.Sprite.__init__(self)
        self.height = 15
        self.width = 5
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(DEEP_PINK)
        self.rect = self.image.get_rect()
        self.speed_x = x_speed
        self.speed_y = -12
        self.rect.centerx = x
        self.rect.bottom = y

    def update(self):
        self.rect.bottom = self.rect.bottom + self.speed_y
        self.rect.x += self.speed_x
        if self.rect.right > WIDTH:
            self.kill()
        elif self.rect.left < 0:
            self.kill()
        elif self.rect.bottom < 0:
            self.kill()


# multi shoot enables player's ship to shoot in three directions
class MultiShootBonus(pygame.sprite.Sprite):
    def __init__(self, img_file):
        pygame.sprite.Sprite.__init__(self)
        self.image = img_file
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randint(10, WIDTH - 10)
        self.rect.bottom = -50
        self.speed_y = random.randint(6, 10)

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT:
            self.kill()
