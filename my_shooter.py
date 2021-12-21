# pygame for game engine, time for measuring actions etc. and random to create random objects
import pygame
import random
from datetime import datetime
import time

# set up constants:
HEIGHT = 900
WIDTH = 1300
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
DEEP_PINK = (255, 20, 147)

# import modules
import player_objects
import enemy_objects


class MyShooter:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.running = True
        self.display_surf = pygame.display.set_mode([WIDTH, HEIGHT])
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.trumps = pygame.sprite.Group()
        self.rogers = pygame.sprite.Group()
        self.kimojis = pygame.sprite.Group()
        self.trump_img = pygame.image.load("trump.png").convert_alpha()
        self.roger_img = pygame.image.load("roger.png").convert_alpha()
        self.bg_img = pygame.image.load("space_background.jpg")
        self.star_img = pygame.image.load("star_bonus.png").convert_alpha()
        self.kimoji_img = pygame.image.load("kimoji.png").convert_alpha()
        self.stars = pygame.sprite.Group()
        self.points_font = pygame.font.Font('freesansbold.ttf', 32)
        self.lives_font = pygame.font.Font('freesansbold.ttf', 24)
        self.max_trumps = 10
        self.max_rogers = 6
        self.clock = pygame.time.Clock()
        self.points = 990
        self.shoot_basic_sound = pygame.mixer.Sound("shoot_basic.wav")
        self.shoot_enemy_sound = pygame.mixer.Sound("shoot_enemy.wav")
        self.hurt_sound = pygame.mixer.Sound("auch.ogg")
        self.background_music = pygame.mixer.music.load("heroes_moon_music.mp3")
        self.star_sound = pygame.mixer.Sound("star_sound.wav")
        self.high_score = None
        self.boss_on = False

    def on_init(self):
        pygame.display.set_caption("Laser Space Shooter 0.4")
        pygame.display.set_icon(pygame.image.load("shooter_icon.jpg"))
        self.all_sprites.add(ship)
        pygame.mixer.music.play(-1)
        self.high_score = self.get_high_score()

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.on_cleanup()
            elif event.key == pygame.K_SPACE:
                new_bullet = ship.shoot()
                self.shoot_basic_sound.play()
                if type(new_bullet) == list:
                    for bullet in new_bullet:
                        self.bullets.add(bullet)
                        self.all_sprites.add(bullet)
                else:
                    self.bullets.add(new_bullet)
                    self.all_sprites.add(new_bullet)
                self.points -= 3

    @staticmethod
    def get_high_score():
        # read file and parse top score will break with bad file data
        points = []
        file = open("scores.txt", "r")
        i = 0
        for line in file:
            if i == 0:
                i += 1
                continue
            points.append(int(line.split(",")[0]))
            i += 1
        file.close()
        if points:
            points.sort()
            return points[-1]
        else:
            return "NA"

    def create_trumps(self):
        # create new trumps until max limit is reached
        while len(self.trumps) < self.max_trumps:
            new_trump = enemy_objects.Trump(self.trump_img)
            self.trumps.add(new_trump)
            self.all_sprites.add(new_trump)

    def create_rogers(self):
        # create roger stones
        while len(self.rogers) < self.max_rogers:
            new_roger = enemy_objects.Henchman(self.roger_img)
            self.rogers.add(new_roger)
            self.all_sprites.add(new_roger)

    def create_star(self):
        new_star = player_objects.MultiShootBonus(self.star_img)
        self.stars.add(new_star)
        self.all_sprites.add(new_star)

    def create_kimoji(self):
        new_kimoji = enemy_objects.Kimoji(self.kimoji_img)
        self.kimojis.add(new_kimoji)
        self.all_sprites.add(new_kimoji)

    def check_collisions(self):
        # checks if player's ship is hit by trump
        for trump in self.trumps:
            if trump.rect.colliderect(ship):
                self.hurt_sound.play()
                if ship.damage():
                    self.on_cleanup()

        # checks if trump or roger gets hit by bullet
        for bullet in self.bullets:
            for trump in self.trumps:
                if trump.rect.colliderect(bullet):
                    bullet.kill()
                    self.points += random.randint(6, 15)
                    trump.kill()
            for roger in self.rogers:
                if roger.rect.colliderect(bullet):
                    bullet.kill()
                    self.points += random.randint(12, 25)
                    roger.kill()
        # checks if player is hit by flying enemy
        for roger in self.rogers:
            if roger.rect.colliderect(ship):
                self.hurt_sound.play()
                if ship.damage():
                    self.on_cleanup()
        # checks if player is hit by enemies' bullets
        for e_bullet in self.enemy_bullets:
            if e_bullet.rect.colliderect(ship):
                self.hurt_sound.play()
                if ship.damage():
                    self.on_cleanup()

        # check bonus star collision
        for star in self.stars:
            if star.rect.colliderect(ship):
                self.star_sound.play()
                ship.enable_multi_shoot()
                ship.lives += 1
                star.kill()

        # boss fight only
        if self.boss_on:
            for bullet in self.bullets:
                for kimoji in self.kimojis:
                    if kimoji.rect.colliderect(bullet):
                        kimoji.damage()
                        self.points += 25
                        bullet.kill()

    def on_loop(self):
        # initiate boss fight! (kill mobs and spawn KIMOJI)
        if self.points > 1000 and not self.boss_on:
            pygame.mixer.music.stop()
            boss_music = pygame.mixer.music.load("boss_music.mp3")
            pygame.mixer.music.play()
            self.boss_on = True
            self.max_rogers = 0
            self.max_trumps = 0
            for roger in self.rogers:
                roger.kill()
            for trump in self.trumps:
                trump.kill()
            self.create_kimoji()
        # spawn star based on point limit
        if self.points > ship.multi_shoot_points:
            ship.multi_shoot_points *= 2
            self.create_star()
        # spawn enemies
        self.create_trumps()
        self.create_rogers()
        # check collisions
        self.check_collisions()
        # move objects
        self.all_sprites.update()
        # check if roger stone can shoot
        for roger in self.rogers:
            if roger.can_shoot():
                self.shoot_enemy_sound.play()
                new_enemy_bullet = roger.shoot()
                self.enemy_bullets.add(new_enemy_bullet)
                self.all_sprites.add(new_enemy_bullet)

        for kimoji in self.kimojis:
            if kimoji.can_shoot():
                new_kimoji_bullets = kimoji.shoot()
                for bullet in new_kimoji_bullets:
                    self.enemy_bullets.add(bullet)
                    self.all_sprites.add(bullet)

    def on_render(self):
        self.display_surf.fill(BLACK)
        self.display_surf.blit(self.bg_img, [0, 0])
        self.all_sprites.draw(self.display_surf)
        # needs to be set to real hit rect pygame.draw.circle(self.display_surf, RED, ship.rect.center, ship.size, 1)

        # text rendering for points
        points_string = 'Points: ' + str(self.points) + ' (HIGH: ' + str(self.high_score) + ')'
        points_text = self.points_font.render(points_string, True, WHITE)
        points_rect = points_text.get_rect()
        points_rect.left = 10
        points_rect.top = 10
        self.display_surf.blit(points_text, points_rect)

        # text rendering for lives
        lives_text = self.lives_font.render('Lives: ' + str(ship.lives), True, RED)
        lives_rect = points_text.get_rect()
        lives_rect.left = 10
        lives_rect.top = points_rect.bottom
        self.display_surf.blit(lives_text, lives_rect)

        pygame.display.flip()
        self.clock.tick(FPS)

    def record_points(self):
        file = open("scores.txt", "a+")
        to_write = ",".join([("\n" + str(self.points)), "xxx", str(datetime.now())])
        file.write(to_write)
        file.close()

    def on_cleanup(self):
        # write scores to file here
        print("you scored: " + str(self.points))
        self.record_points()
        pygame.quit()
        quit()

    def on_execute(self):
        self.on_init()
        while self.running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()


if __name__ == "__main__":
    ship = player_objects.Player()
    gameApp = MyShooter()
    gameApp.on_execute()
