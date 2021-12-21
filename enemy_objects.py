# load PyGame from main file
from my_shooter import *


class Trump(pygame.sprite.Sprite):
    def __init__(self, img_file):
        pygame.sprite.Sprite.__init__(self)
        self.image_original = img_file
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randint(WIDTH / 2 - 200, WIDTH / 2 + 200)
        self.rect.bottom = -300
        self.speed_x = random.randint(-3, 3)
        self.speed_y = random.randint(2, 5)
        self.size = 27
        self.rotation = 0
        self.rotation_speed = random.randint(-10, 10)
        self.last_rotate = pygame.time.get_ticks()

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        self.rotate()

        if self.rect.top > HEIGHT:
            self.kill()
        if self.rect.right > WIDTH:
            self.kill()
        if self.rect.left < 0:
            self.kill()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_rotate > 60:
            self.last_rotate = now
            self.rotation = (self.rotation + self.rotation_speed) % 360
            new_image = pygame.transform.rotate(self.image_original, self.rotation)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center


class Henchman(pygame.sprite.Sprite):
    def __init__(self, img_file):
        pygame.sprite.Sprite.__init__(self)
        self.image = img_file
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randint(WIDTH / 2 - 350, WIDTH / 2 + 350)
        self.rect.bottom = -200
        self.speed_x = 0
        self.speed_x_secondary = random.randint(-3, 3)
        self.speed_y = 0
        self.speed_y_secondary = random.randint(2, 5)
        self.speed_y_modifier = 0
        self.size = 27
        self.last_shoot = pygame.time.get_ticks()
        self.shooting_pace = random.randint(2500, 3500)
        self.last_pattern_change = pygame.time.get_ticks()
        self.pattern_change_speed = random.randint(1000, 2000)

    def update(self):
        # change flight pattern
        now = pygame.time.get_ticks()
        if now - self.last_pattern_change > self.pattern_change_speed:
            if self.speed_y_modifier % 2 == 0:
                self.speed_x_secondary = -self.speed_x_secondary
                self.speed_x = self.speed_x_secondary
                self.speed_y = 0
            else:
                self.speed_x = 0
                self.speed_y = self.speed_y_secondary
            self.speed_y_modifier += 1
            self.last_pattern_change = now

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.top > HEIGHT:
            self.kill()
        if self.rect.right > WIDTH:
            self.kill()
        if self.rect.left < 0:
            self.kill()

    def can_shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shoot > self.shooting_pace:
            self.last_shoot = now
            return True
        else:
            return False

    def shoot(self):
        new_enemy_bullet = EnemyBullet(self.rect.centerx, self.rect.bottom, 0)
        return new_enemy_bullet


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, x_speed):
        pygame.sprite.Sprite.__init__(self)
        self.height = 15
        self.width = 5
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.speed_y = 10
        self.speed_x = x_speed
        self.rect.centerx = x
        self.rect.bottom = y

    def update(self):
        self.rect.bottom += self.speed_y
        self.rect.x += self.speed_x
        if self.rect.top > HEIGHT:
            self.kill()
        elif self.rect.right < 0:
            self.kill()
        elif self.rect.left > WIDTH:
            self.kill()


class Kimoji(pygame.sprite.Sprite):
    def __init__(self, img_file):
        pygame.sprite.Sprite.__init__(self)
        self.image = img_file
        self.kimoji_dead_sound = pygame.mixer.Sound("kimoji_dead.wav")
        self.kimoji_hurt_sound = pygame.mixer.Sound("kimoji_hurt.wav")
        self.kimoji_roar = pygame.mixer.Sound("kimoji_roar.wav")
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.top = 20
        self.speed_x = 12
        self.speed_y = 2
        self.shooting_pace = 5000
        self.last_shoot = pygame.time.get_ticks()
        self.last_pattern_change = pygame.time.get_ticks()
        self.pattern_change_speed = 500
        self.lives = 50

    def update(self):
        now = pygame.time.get_ticks()
        if self.rect.left < 0:
            self.speed_x = -self.speed_x
        elif self.rect.right > WIDTH:
            self.speed_x = -self.speed_x

        if now - self.last_pattern_change > self.pattern_change_speed:
            self.speed_y = -self.speed_y
            self.last_pattern_change = now

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

    def damage(self):
        self.lives -= 1
        if self.lives <= 0:
            self.kimoji_dead_sound.play()
            self.kill()
        else:
            self.kimoji_hurt_sound.play()

    def can_shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shoot > self.shooting_pace:
            if self.shooting_pace == 5000:
                self.shooting_pace = 1000
            else:
                self.shooting_pace = 5000
            self.last_shoot = now
            return True
        else:
            return False

    def shoot(self):
        # spawn bullets
        bullets = []
        y = self.rect.bottom
        self.kimoji_roar.play()
        for i in range(12):
            x = random.randint(0, WIDTH)
            new_bullet = EnemyBullet(x, y, 0)
            bullets.append(new_bullet)
        return bullets
