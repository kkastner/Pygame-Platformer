#!/usr/bin/env python

"""
level_editor.py: Basic level editor to be used with platformer.py.
Original code provided by Coding with Russ (codingwithruss.com), modified to be used with my platformer.
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
import pickle
import math
from os import path


pygame.init()

clock = pygame.time.Clock()
fps = 60

#game window
tile_size = 32
cols = 30
margin = 100
SCREEN_WIDTH = tile_size * cols
SCREEN_HEIGHT = (tile_size * cols) + margin

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Level Editor')

def populateBackground(img, img_size):
    numWidthTiles = math.ceil(SCREEN_WIDTH / img_size)
    numHeightTiles = math.ceil(SCREEN_WIDTH / img_size)
    for i in range(numHeightTiles):
        for j in range(numWidthTiles):
            screen.blit(img, (j * img_size, i * img_size))

#load images
bg_img = [None for _ in range(7)]
bg_img[1] = pygame.image.load("img/Pixel Adventure/Background/Blue.png")
bg_img[2] = pygame.image.load("img/Pixel Adventure/Background/Brown.png")
bg_img[3] = pygame.image.load("img/Pixel Adventure/Background/Gray.png")
bg_img[4] = pygame.image.load("img/Pixel Adventure/Background/Green.png")
bg_img[5] = pygame.image.load("img/Pixel Adventure/Background/Pink.png")
bg_img[6] = pygame.image.load("img/Pixel Adventure/Background/Purple.png")
bg_img[0] = pygame.image.load("img/Pixel Adventure/Background/Yellow.png")
dirt_img = pygame.image.load('img/Platform Tiles/dirt_32x32.png')
grass_img = pygame.image.load('img/Platform Tiles/grass_32x32.png')
enemy_img = pygame.image.load('img/Rock2 (32x28).png')
platform_x_img = pygame.image.load('img/platform_x.png')
platform_y_img = pygame.image.load('img/platform_y.png')
spikes_img = pygame.image.load('img/Pixel Adventure/Traps/Spikes/Idle.png')
apple_img = pygame.image.load('img/Apple.png')
end_img = pygame.image.load('img/Pixel Adventure/Items/Checkpoints/End/End (Idle).png')
save_img = pygame.image.load('img/save_btn.png')
save_img = pygame.transform.scale(save_img, (tile_size * 4, tile_size))
load_img = pygame.image.load('img/load_btn.png')
load_img = pygame.transform.scale(load_img, (tile_size * 4, tile_size))


#define game variables
clicked = False
level = 1

#define colours
white = (255, 255, 255)
black = (0, 0, 0)
green = (144, 201, 120)

font = pygame.font.SysFont('Futura', 24)

#create empty tile list
world_data = []
for row in range(cols):
	r = [0] * cols
	world_data.append(r)

#create boundary
for tile in range(0, cols):
	world_data[cols-1][tile] = 2
	world_data[0][tile] = 1
	world_data[tile][0] = 1
	world_data[tile][cols-1] = 1

#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

def draw_grid():
	for c in range(cols+1):
		#vertical lines
		pygame.draw.line(screen, white, (c * tile_size, 0), (c * tile_size, SCREEN_HEIGHT - margin))
		#horizontal lines
		pygame.draw.line(screen, white, (0, c * tile_size), (SCREEN_WIDTH, c * tile_size))


def draw_world():
	for row in range(cols):
		for col in range(cols):
			if world_data[row][col] > 0:
				if world_data[row][col] == 1:
					#dirt blocks
					img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 2:
					#grass blocks
					img = pygame.transform.scale(grass_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 3:
					#enemy blocks
					img = pygame.transform.scale(enemy_img, (tile_size, int(tile_size * 0.75)))
					screen.blit(img, (col * tile_size, row * tile_size + (tile_size * 0.25)))
				if world_data[row][col] == 4:
					#horizontally moving platform
					img = pygame.transform.scale(platform_x_img, (tile_size, tile_size // 2))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 5:
					#vertically moving platform
					img = pygame.transform.scale(platform_y_img, (tile_size, tile_size // 2))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 6:
					#spikes
					img = pygame.transform.scale(spikes_img, (tile_size, tile_size // 2))
					screen.blit(img, (col * tile_size, row * tile_size + (tile_size // 2)))
				if world_data[row][col] == 7:
					#apple
					img = pygame.transform.scale(apple_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size + (tile_size // 16), row * tile_size + (tile_size // 16)))
				if world_data[row][col] == 8:
					#exit
					img = pygame.transform.scale(end_img, (tile_size, int(tile_size * 1.5)))
					screen.blit(img, (col * tile_size, row * tile_size - (tile_size // 2)))



class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button
		screen.blit(self.image, (self.rect.x, self.rect.y))

		return action

#create load and save buttons
save_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 80, save_img)
load_button = Button(SCREEN_WIDTH // 2 + 50, SCREEN_HEIGHT - 80, load_img)

#main game loop
run = True
while run:

	clock.tick(fps)

	#draw background
	screen.fill(green)
	populateBackground(bg_img[level % 7], 64)

	#load and save level
	if save_button.draw():
		#save level data
		pickle_out = open(f'level{level}_data', 'wb')
		pickle.dump(world_data, pickle_out)
		pickle_out.close()
	if load_button.draw():
		#load in level data
		if path.exists(f'level{level}_data'):
			pickle_in = open(f'level{level}_data', 'rb')
			world_data = pickle.load(pickle_in)


	#show the grid and draw the level tiles
	draw_grid()
	draw_world()


	#text showing current level
	draw_text(f'Level: {level}', font, black, tile_size, SCREEN_HEIGHT - 80)
	draw_text('Press UP or DOWN to change level', font, black, tile_size, SCREEN_HEIGHT - 60)

	#event handler
	for event in pygame.event.get():
		#quit game
		if event.type == pygame.QUIT:
			run = False
		#mouseclicks to change tiles
		if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
			clicked = True
			pos = pygame.mouse.get_pos()
			x = pos[0] // tile_size
			y = pos[1] // tile_size
			#check that the coordinates are within the tile area
			if x < cols and y < cols:
				#update tile value
				if pygame.mouse.get_pressed()[0] == 1:
					world_data[y][x] += 1
					if world_data[y][x] > 8:
						world_data[y][x] = 0
				elif pygame.mouse.get_pressed()[2] == 1:
					world_data[y][x] -= 1
					if world_data[y][x] < 0:
						world_data[y][x] = 8
		if event.type == pygame.MOUSEBUTTONUP:
			clicked = False
		#up and down key presses to change level number
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP:
				level += 1
			elif event.key == pygame.K_DOWN and level > 1:
				level -= 1

	#update game display window
	pygame.display.update()

pygame.quit()