#!/usr/bin/env python

"""
platformer.py: Basic platformer with some animations, music, and sound effects.
Made following the tutorial provided by Coding with Russ (codingwithruss.com),
altered to fit the open-source graphics chosen, with some additional functionality,
such as enemy/item/platform animations, and changing backgrounds.
"""

__author__  = "Kevin Kastner"
__copyright__ = "Copyright 2024, DragonWolf"
__credits__ = ["Kevin Kastner", "Ethan Kastner"]
__license__ = "None"
__version__ = "1.0"
__maintainer__ = "Kevin Kastner"
__email__ = "kkastner@alumni.nd.edu"
__status__ = "Prototype"

import pygame
from pygame.locals import *
from pygame import mixer
import math
import pickle
from os import path
from random import randint
import spritesheet


pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 960
STARTING_LEVEL = 1
MAX_LEVEL = 11

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Platformer")

#define font
font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)

#define game variables
tile_size = 32
game_over = 0
main_menu = True
level = STARTING_LEVEL
max_levels = MAX_LEVEL
score = 0

#define colors
black = (0, 0, 0)
white = (255, 255, 255)
blue = (0, 0, 255)

#load images
bg_img = [None for _ in range(7)]
bg_img[1] = pygame.image.load("img/Pixel Adventure/Background/Blue.png")
bg_img[2] = pygame.image.load("img/Pixel Adventure/Background/Brown.png")
bg_img[3] = pygame.image.load("img/Pixel Adventure/Background/Gray.png")
bg_img[4] = pygame.image.load("img/Pixel Adventure/Background/Green.png")
bg_img[5] = pygame.image.load("img/Pixel Adventure/Background/Pink.png")
bg_img[6] = pygame.image.load("img/Pixel Adventure/Background/Purple.png")
bg_img[0] = pygame.image.load("img/Pixel Adventure/Background/Yellow.png")
restart_img = pygame.image.load("img/Pixel Adventure/Menu/Buttons/Restart.png")
start_img = pygame.image.load("img/Pixel Adventure/Menu/Buttons/Play.png")
exit_img = pygame.image.load("img/Pixel Adventure/Menu/Buttons/Close.png")

#load sounds
pygame.mixer.music.load('sounds/ngini-ija.mp3')
pygame.mixer.music.play(-1, 0.0, 0)
apple_fx = pygame.mixer.Sound('sounds/apple-bite.mp3')
apple_fx.set_volume(0.3)
jump_fx = pygame.mixer.Sound('sounds/jump.mp3')
jump_fx.set_volume(0.2)
game_over_fx = pygame.mixer.Sound('sounds/game-over.mp3')

#function to draw background using tile image
def populateBackground(img, img_size):
    numWidthTiles = math.ceil(SCREEN_WIDTH / img_size)
    numHeightTiles = math.ceil(SCREEN_HEIGHT / img_size)
    for i in range(numHeightTiles):
        for j in range(numWidthTiles):
            screen.blit(img, (j * img_size, i * img_size))

#function to draw text onto screen
def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))

#function to reset level
def reset_level(level):
    player.reset(player_x, player_y)
    enemy_group.empty()
    platform_group.empty()
    spikes_group.empty()
    apple_group.empty()
    exit_group.empty()

    #create dummy apple for showing the score
    score_apple = Apple(tile_size // 2, tile_size // 2)
    apple_group.add(score_apple)

    #load in level data
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world


class Button():
    def __init__(self, x, y, image, scale=1) -> None:
        self.image = image
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * scale, self.image.get_height() * scale))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()

        #check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        #draw button
        screen.blit(self.image, self.rect)

        return action

class Player():
    def __init__(self, x, y) -> None:
        self.reset(x, y)
    
    def reset(self, x, y):
        sprite_sheet_image = pygame.image.load("img/Pixel Adventure/Main Characters/Pink Man/Idle (32x32).png").convert_alpha()
        sprite_sheet_idle = spritesheet.SpriteSheet(sprite_sheet_image)
        sprite_sheet_image = pygame.image.load("img/Pixel Adventure/Main Characters/Pink Man/Run (32x32).png").convert_alpha()
        sprite_sheet_running = spritesheet.SpriteSheet(sprite_sheet_image)
        sprite_sheet_image = pygame.image.load("img/Ghost/ghost-Sheet.png").convert_alpha()
        sprite_sheet_dead = spritesheet.SpriteSheet(sprite_sheet_image)
        #create animation list
        self.images_right = []
        self.images_left = []
        animation_steps = [11, 12, 4]
        self.action = 0
        self.index = 0
        self.counter = 0
        scale = 1
        width = 32
        height = 32
        self.x_offset = 6
        self.y_offset = 6

        for i, animation in enumerate(animation_steps):
            tmp_img_right = []
            tmp_img_left = []
            for step_counter in range(animation):
                if i == 0:
                    img_right = sprite_sheet_idle.get_image(step_counter, width, height, scale, black)
                elif i == 1:
                    img_right = sprite_sheet_running.get_image(step_counter, width, height, scale, black)
                elif i == 2:
                    img_right = sprite_sheet_dead.get_image(step_counter, width, height, scale, black)
                else:
                    #bad data entered
                    break
                img_left = spritesheet.SpriteSheet.get_x_flipped_image(img_right, black)
                tmp_img_right.append(img_right)
                tmp_img_left.append(img_left)
            self.images_right.append(tmp_img_right)
            self.images_left.append(tmp_img_left)
        self.image = self.images_right[self.action][self.index]
        self.rect = self.image.get_rect()
        self.rect.update(x + self.x_offset, y + self.y_offset, width - (2 * self.x_offset), height - self.y_offset)
        self.width = width - (2 * self.x_offset)
        self.height = height - self.y_offset
        self.vel_y = 0
        self.jumped = False
        self.direction = 1
        self.in_air = True
        

    def update(self, game_over):
        dx, dy = 0, 0
        animation_cooldown = 5
        col_thresh = 20
        moved = False

        if game_over == 0:
            #get keypresses
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and not self.jumped and not self.in_air:
                jump_fx.play()
                self.vel_y = -15
                self.jumped = True
                moved = True
            if not key[pygame.K_SPACE]:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.direction = -1
                moved = True
            if key[pygame.K_RIGHT]:
                dx += 5
                self.direction = 1
                moved = True
            if moved:
                if self.action != 1:
                    self.index = 0
                    self.counter = 0
                self.action = 1
            else:
                if self.action != 0:
                    self.index = 0
                    self.counter = 0
                self.action = 0

            #add gravity
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            #check for collision
            self.in_air = True
            for tile in world.tile_list:
                #check for collision in x direction
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0

                #check for collision in y direction
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #check if below the ground, i.e. jumping into block
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    #check if above the ground, i.e. falling on a block
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.in_air = False

            #check for collision with enemies
            if pygame.sprite.spritecollide(self, enemy_group, False):
                game_over = -1
                game_over_fx.play()
                self.died_y = self.rect.y
            
            #check for collision with spikes
            if pygame.sprite.spritecollide(self, spikes_group, False):
                game_over = -1
                game_over_fx.play()
                self.died_y = self.rect.y

            #check for collision with exit
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            #check for collision with platforms
            for platform in platform_group:
                #collision in the x direction
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0

                #collision in the y direction
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #check if below platform
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    #check if above platform
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    #move sideways with the platform
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction * platform.move_x

            #update player coordinates
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.action = 2
            draw_text('GAME OVER!', font, blue, (SCREEN_WIDTH // 2) - 200, (SCREEN_HEIGHT // 2) - 16)
            if self.died_y - self.rect.y < 200:
                self.rect.y -= 5
            else:
                self.counter = 0

        #handle animation
        self.counter += 1
        if self.counter > animation_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images_right[self.action]):
                self.index = 0
            if self.direction == 1:
                self.image = self.images_right[self.action][self.index]
            if self.direction == -1:
                self.image = self.images_left[self.action][self.index]

        #draw player onto screen
        screen.blit(self.image, (self.rect.x - self.x_offset, self.rect.y - self.y_offset))
        #pygame.draw.rect(screen, (255, 255, 255), self.rect, 2) #see rectangle outline

        return game_over

class World():
    def __init__(self, data) -> None:
        self.tile_list = []

        #load images
        dirt_img = pygame.image.load('img/Platform Tiles/dirt_32x32.png')
        grass_img = pygame.image.load('img/Platform Tiles/grass_32x32.png')

        for row_count, row in enumerate(data):
            for col_count, tile in enumerate(row):
                x, y = col_count * tile_size, row_count * tile_size
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = x
                    img_rect.y = y
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = x
                    img_rect.y = y
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    enemy = Enemy(x, y)
                    enemy_group.add(enemy)
                if tile == 4:
                    platform = Platform(x, y, 1, 0)
                    platform_group.add(platform)
                if tile == 5:
                    platform = Platform(x, y, 0, 1)
                    platform_group.add(platform)
                if tile == 6:
                    spikes = Spikes(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    spikes_group.add(spikes)
                if tile == 7:
                    apple = Apple(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    apple_group.add(apple)
                if tile == 8:
                    exit = Exit(x, y)
                    exit_group.add(exit)

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            #pygame.draw.rect(screen, (255, 255, 255), tile[1], 2) #see rectangle outline


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y) -> None:
        pygame.sprite.Sprite.__init__(self)
        sprite_sheet_image = pygame.image.load("img/Pixel Adventure/Enemies/Rocks/Rock2_Idle (32x28).png").convert_alpha()
        sprite_sheet_idle = spritesheet.SpriteSheet(sprite_sheet_image)
        sprite_sheet_image = pygame.image.load("img/Pixel Adventure/Enemies/Rocks/Rock2_Run (32x28).png").convert_alpha()
        sprite_sheet_running = spritesheet.SpriteSheet(sprite_sheet_image)
        #create animation list
        self.images_right = []
        self.images_left = []
        animation_steps = [13, 14]
        self.action = 1
        self.index = 0
        self.counter = 0
        scale = 1
        width = 32
        height = 32
        self.x_offset = 0
        self.y_offset = 10
        self.idle_time = 0

        for i, animation in enumerate(animation_steps):
            tmp_img_right = []
            tmp_img_left = []
            for step_counter in range(animation):
                if i == 0:
                    img_right = sprite_sheet_idle.get_image(step_counter, width, height, scale, black)
                elif i == 1:
                    img_right = sprite_sheet_running.get_image(step_counter, width, height, scale, black)
                #elif i == 2:
                #    img_right = sprite_sheet_dead.get_image(step_counter, width, height, scale, black)
                else:
                    #bad data entered
                    break
                img_left = spritesheet.SpriteSheet.get_x_flipped_image(img_right, black)
                tmp_img_right.append(img_right)
                tmp_img_left.append(img_left)
            self.images_right.append(tmp_img_right)
            self.images_left.append(tmp_img_left)
        self.image = self.images_right[self.action][self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        if self.idle_time > 0:
            self.action = 0
            self.idle_time -= 1
        else:
            self.action = 1
            self.rect.x += self.move_direction
            self.move_counter += 1
            idle_time = randint(0, 500)
            if idle_time >= 498:
                self.idle_time = idle_time // 5
        #handle animation
        animation_cooldown = 5
        self.counter += 1
        if self.counter > animation_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images_right[self.action]):
                self.index = 0
            if self.move_direction == -1:
                self.image = self.images_right[self.action][self.index]
            if self.move_direction == 1:
                self.image = self.images_left[self.action][self.index]
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1
        #pygame.draw.rect(screen, (255, 255, 255), self.rect, 2) #see rectangle outline

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y) -> None:
        pygame.sprite.Sprite.__init__(self)
        sprite_sheet_image = pygame.image.load("img/Pixel Adventure/Traps/Falling Platforms/On (32x10).png").convert_alpha()
        sprite_sheet = spritesheet.SpriteSheet(sprite_sheet_image)
        #create animation list
        self.images = []
        animation_steps = 4
        self.index = 0
        self.counter = 0
        scale = 1
        width = 32
        height = 10

        for step_counter in range(animation_steps):
            img = sprite_sheet.get_image(step_counter, width, height, scale, black)
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1
        #handle animation
        animation_cooldown = 5
        self.counter += 1
        if self.counter > animation_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images):
                self.index = 0
            self.image = self.images[self.index]

class Spikes(pygame.sprite.Sprite):
    def __init__(self, x, y) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/Pixel Adventure/Traps/Spikes/Idle.png")
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Apple(pygame.sprite.Sprite):
    def __init__(self, x, y) -> None:
        pygame.sprite.Sprite.__init__(self)
        sprite_sheet_image = pygame.image.load("img/Pixel Adventure/Items/Fruits/Apple.png").convert_alpha()
        sprite_sheet = spritesheet.SpriteSheet(sprite_sheet_image)
        #create animation list
        self.images = []
        animation_steps = 17
        self.index = 0
        self.counter = 0
        scale = 1
        width = 32
        height = 32

        for step_counter in range(animation_steps):
            img = sprite_sheet.get_image(step_counter, width, height, scale, black)
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        #handle animation
        animation_cooldown = 5
        self.counter += 1
        if self.counter > animation_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images):
                self.index = 0
            self.image = self.images[self.index]
        #pygame.draw.rect(screen, (255, 255, 255), self.rect, 2) #see rectangle outline

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/Pixel Adventure/Items/Checkpoints/End/End (Idle).png")
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

player_x, player_y = 100, SCREEN_HEIGHT - 64
player = Player(player_x, player_y)

enemy_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
spikes_group = pygame.sprite.Group()
apple_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

#create dummy apple for showing the score
score_apple = Apple(tile_size // 2, tile_size // 2)
apple_group.add(score_apple)

#load in level data
if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)


#create buttons
restart_button = Button(SCREEN_WIDTH // 2 - 32, SCREEN_HEIGHT // 2 + 64, restart_img, 2)
start_button = Button(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2, start_img, 4)
exit_button = Button(SCREEN_WIDTH // 2 + 130, SCREEN_HEIGHT // 2, exit_img, 6)

run = True
while run:

    clock.tick(fps)

    populateBackground(bg_img[level % 7], 64)

    if main_menu:
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
    else:
        world.draw()

        #player is playing the game
        if game_over == 0:
            enemy_group.update()
            platform_group.update()
            #update score
            #check if an apple has been collected
            if pygame.sprite.spritecollide(player, apple_group, True):
                score += 1
                apple_fx.play()
            apple_group.update()
        draw_text('X ' + str(score), font_score, white, tile_size - 5, 0)
        draw_text('Level ' + str(level), font_score, white, tile_size * 14, 0)

        enemy_group.draw(screen)
        platform_group.draw(screen)
        spikes_group.draw(screen)
        apple_group.draw(screen)
        exit_group.draw(screen)

        game_over = player.update(game_over)

        #if player has died
        if game_over == -1:
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0

        #if player has completed the level
        if game_over == 1:
            #reset game and go to next level
            level += 1
            if level <= max_levels:
                #reset level
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                draw_text('YOU WIN!', font, blue, (SCREEN_WIDTH // 2) - 152, (SCREEN_HEIGHT // 2) - 32)
                level = max_levels
                if restart_button.draw():
                    #restart game
                    level = STARTING_LEVEL
                    world_data = []
                    world = reset_level(level)
                    game_over = 0

    #event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()