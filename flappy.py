import pygame
import sys
import random
import os
import time
from queue import Queue
import logging

logging.basicConfig(level=logging.DEBUG)

def draw_floor():
	screen.blit(floor_surface,(floor_x_position,900))
	screen.blit(floor_surface,(floor_x_position + 576,900))

def create_pipe():
	random_pipe_position = random.choice(pipe_height)
	bottom_pipe = pipe_surface.get_rect(midtop = (700,random_pipe_position))
	top_pipe = pipe_surface.get_rect(midbottom = (700,random_pipe_position-300))
	return bottom_pipe, top_pipe

def move_pipes(pipes):
	for pipe in pipes:
		pipe.centerx -= 5
	return pipes

def draw_pipes(pipes):
	for pipe in pipes:
		if pipe.bottom >= 1024:
			screen.blit(pipe_surface, pipe)
		else:
			flip_pipe = pygame.transform.flip(pipe_surface, False, True)
			screen.blit(flip_pipe, pipe)

def check_collision(pipes):
	for pipe in pipes:
		if bird_rectangle.colliderect(pipe):
			death_sound.play()
			return False


	if bird_rectangle.top <= -100 or bird_rectangle.bottom >= 900:
		return False

	return True

def rotate_bird(bird):
	new_bird = pygame.transform.rotozoom(bird, -bird_movement*3, 1)
	return new_bird

def bird_animation():
	new_bird = bird_frames[bird_index]
	new_bird_rectangle = new_bird.get_rect(center = (100, bird_rectangle.centery))
	return new_bird, new_bird_rectangle

def score_display(game_state):
	base_heigh = 320

	if game_state == 'main_game':
		score_surface = game_font.render(str(int(score)), True, (255,255,255))
		score_rectangle = score_surface.get_rect(center = (288, base_heigh))
		screen.blit(score_surface, score_rectangle)

	if game_state == 'game_over':
		score_surface = game_font.render(f'Score: {int(score)}', True, (255,255,255))
		score_rectangle = score_surface.get_rect(center = (288, base_heigh))
		screen.blit(score_surface, score_rectangle)

		high_score_surface = game_font.render(f'High Score: {int(high_score)}', True, (255,255,255))
		high_score_rectangle = high_score_surface.get_rect(center = (288, base_heigh+85))
		screen.blit(high_score_surface, high_score_rectangle)

def update_score(score, high_score):
	if score > high_score:
		high_score = score
	return high_score


#function to initialize (init()) pygame
pygame.mixer.pre_init(frequency = 44100, size = 16, channels = 1, buffer = 512)
pygame.init()
screen = pygame.display.set_mode((576,1024))
clock = pygame.time.Clock()
game_font = pygame.font.Font('./assets/04B_19.TTF',40)

# variables for the game
gravity = 0.25
bird_movement = 0
game_active = False
score = 0
high_score = 0

# this one would also work
# background_surface = pygame.transform.scale2x(pygame.image.load('assets/background-day.png'))

obliverati_faces = [ pygame.image.load(f'assets/oblive_{i}.png').convert_alpha() for i in range(4) ]
obliverati_faces = [pygame.transform.scale(img, (400,400)) for img in obliverati_faces]
current_image_index = 0
last_switch_time = time.time()

background_surface = pygame.image.load('assets/background-night.png').convert()
background_surface = pygame.transform.scale2x(background_surface)

floor_surface = pygame.image.load('assets/base.png').convert()
floor_surface = pygame.transform.scale2x(floor_surface)
floor_x_position = 0

bird_downflap = pygame.transform.scale2x(pygame.image.load('assets/bluebird-downflap_v1_2.png').convert_alpha())
bird_midflap = pygame.transform.scale2x(pygame.image.load('assets/bluebird-midflap_v1.png').convert_alpha())
bird_upflap = pygame.transform.scale2x(pygame.image.load('assets/bluebird-upflap_v1.png').convert_alpha())
bird_frames = [bird_downflap, bird_midflap, bird_upflap]
bird_index = 0
bird_surface = bird_frames[bird_index]
bird_rectangle = bird_surface.get_rect(center = (100,512))

BIRDFLAP = pygame.USEREVENT + 1
pygame.time.set_timer(BIRDFLAP, 200)

# bird_surface = pygame.image.load('assets/bluebird-midflap.png').convert_alpha()
# bird_surface = pygame.transform.scale2x(bird_surface)
# bird_rectangle = bird_surface.get_rect(center = (100,512))

pipe_surface = pygame.image.load('assets/pipe-green.png')
pipe_surface = pygame.transform.scale2x(pipe_surface)
pipe_list = []
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1200) # event triggered every 1.2 seconds
pipe_height = [400, 600, 800]

game_over_surface = pygame.transform.scale2x(pygame.image.load('assets/message.png').convert_alpha())
game_over_rectangle = game_over_surface.get_rect(center = (288,-40))

pygame.mixer.init()
pygame.mixer.music.load('sound/instrumental.wav')
pygame.mixer.music.play()

flap_sound = pygame.mixer.Sound('sound/sfx_wing.wav')
death_sound = pygame.mixer.Sound('sound/sfx_hit.wav')

rap_effects_path = 'sound/obli/'
obli_sounds_files = [file for file in os.listdir(rap_effects_path) if os.path.isfile(os.path.join(rap_effects_path, file))]

obli_sounds = [ pygame.mixer.Sound(f'sound/obli/{sound_file}') for sound_file in obli_sounds_files ]

MAX_SCORE_SOUND_COUNTDOWN = 105
score_sound = pygame.mixer.Sound('sound/sfx_point.wav')
score_sound_countdown = MAX_SCORE_SOUND_COUNTDOWN

MAX_RAP_QUEUE_SIZE = 7
rap_queue = Queue()

def get_random_obli_sound():
	rap_effect = random.choice(obli_sounds)
	obli_sounds.remove(rap_effect)
	rap_queue.put(rap_effect)

	if rap_queue.qsize() > MAX_RAP_QUEUE_SIZE:
		rap_effect_used = rap_queue.get()
		obli_sounds.append(rap_effect_used)
	
	return rap_effect


while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE and game_active:
				bird_movement = 0
				bird_movement -= 8     # changed from 12 to 8 to reduce jumping speed....
				#flap_sound.play()
 
			if event.key == pygame.K_SPACE and game_active == False:
				game_active = True
				pipe_list.clear()
				bird_rectangle.center = (100, 512)
				bird_movement = 0
				score = 0


		if event.type == SPAWNPIPE:
			pipe_list.extend(create_pipe())

		if event.type == BIRDFLAP:
			if bird_index < 2:
				bird_index += 1
			else:
				bird_index = 0

			bird_surface, bird_rectangle = bird_animation()

	if not pygame.mixer.music.get_busy():
		pygame.mixer.music.play()

	screen.blit(background_surface,(0,0))

	if game_active:
		# bird movement
		bird_movement += gravity
		rotated_bird = rotate_bird(bird_surface)
		bird_rectangle.centery += bird_movement
		screen.blit(rotated_bird, bird_rectangle)
		game_active = check_collision(pipe_list)


		# pipes
		pipe_list = move_pipes(pipe_list)
		draw_pipes(pipe_list)

		score += 0.01
		score_display('main_game')
		score_sound_countdown -= 1
		if score_sound_countdown <= 0:
			get_random_obli_sound().play()
			#score_sound.play()
			score_sound_countdown = MAX_SCORE_SOUND_COUNTDOWN

	else:
		if time.time() - last_switch_time >= 0.5:
			current_image_index = (current_image_index + 1) % len(obliverati_faces)
			last_switch_time = time.time()
		
		screen.blit(obliverati_faces[current_image_index], (88, 480))

		screen.blit(game_over_surface, game_over_rectangle)
		high_score = update_score(score, high_score)
		score_display('game_over')


	#Floor
	floor_x_position -= 1
	draw_floor()
	if floor_x_position <= -576:
		floor_x_position = 0


	pygame.display.update()
	clock.tick(120)  