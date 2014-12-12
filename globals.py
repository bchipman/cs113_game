import datetime
import random
from collections import namedtuple

import pygame
from pygame import Color
from pygame.locals import *  # for event timers

# Colors
BLACK = Color(0, 0, 0)
DGREY = Color(64, 64, 64)
WHITE = Color(255, 255, 255)
BROWN = Color(139, 69, 19)
RED = Color(255, 0, 0)
DKRED = Color(128, 0, 0)
DKGREEN = Color(0, 128, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)
LLBLUE = Color(0, 0, 128)
LBLUE = Color(0, 128, 255)
SKYBLUE = Color(128, 223, 223)
YELLOW = Color(255, 255, 0)
DKYELLOW = Color(153, 153, 0)
DKDKYELLOW = Color(128, 128, 0)
PURPLE = Color(255, 0, 255)
DKPURPLE = Color(153, 0, 153)
ORANGE = Color(255, 153, 0)
DKORANGE = Color(153, 92, 0)

# Music
SONGS = ['data/pneumatic_driller.mp3', 'data/euglena_zielona.mp3',
         'data/drilldance.mp3', 'data/running_emu.mp3', 'data/wooboodoo.mp3',
         'data/accident.mp3']

# Monster Types and Globals
ALL = 'ALL'
WEAK = 'WEAK'
MEDIUM = 'MEDIUM'
ULTIMATE = 'ULTIMATE'
CHASING = 'CHASING'
IDLE = 'IDLE'

# Player States (for animation)
STAND = 'STAND'
LWALK = 'LWALK'
RWALK = 'RWALK'
JUMP = 'JUMP'
FALL = 'FALL'
DEATH = 'DEATH'
ATTACK = 'ATTACK'
CAST = 'CAST'

# Gamepad Buttons
GP_LEFT = 'GP_LEFT'
GP_RIGHT = 'GP_RIGHT'
GP_UP = 'GP_UP'
GP_DOWN = 'GP_DOWN'
GP_Y = 3
GP_X = 0
GP_B = 2
GP_A = 1
GP_START = 9
GP_BACK = 8

# Inputs
LEFT = 'LEFT'
RIGHT = 'RIGHT'
UP = 'UP'
DOWN = 'DOWN'
JUMP = 'JUMP'
ATTACK = 'ATTACK'
DEBUG = 'DEBUG'
EXIT = 'EXIT'
RESET = 'RESET'
MELEE = 'MELEE'
RANGE = 'RANGED'
FIELD = 'FIELD'

# Conditions
STUN = 'STUN'
SLOW = 'SLOW'
SNARE = 'SNARE'
DOT = 'DOT'
SILENCE = 'SILENCE'
WOUNDED = 'WOUNDED'
WEAKENED = 'WEAKENED'
SPEED = 'SPEED'
SHIELD = 'SHIELD'
INVIGORATED = 'INVIGORATED'
EMPOWERED = 'EMPOWERED'
BUFFS = [SPEED, SHIELD, INVIGORATED, EMPOWERED]
DEBUFFS = [STUN, SLOW, SNARE, DOT, SILENCE, WOUNDED, WEAKENED]

# Buttons
ATTACKBUTTON = "attack_id"
SKILL1BUTTON = "skill1_id"
SKILL2BUTTON = "skill2_id"
SKILL3BUTTON = "skill3_id"
ULTBUTTON    = "ult_id"


# Events
TIME_TICK_EVENT = USEREVENT + 0
PLAYER1_LOCK_EVENT = USEREVENT + 1
PLAYER2_LOCK_EVENT = USEREVENT + 2
PLAYER1_PICKUP_EVENT = USEREVENT + 3
PLAYER2_PICKUP_EVENT = USEREVENT + 4
REGENERATION_EVENT = USEREVENT + 5
MONSTER_SPAWN_EVENT = USEREVENT + 6
SONG_END_EVENT = USEREVENT + 7
MORE_RAIN_EVENT = USEREVENT + 8

# Global Functions
def all_in(items_want_inside, container_being_checked):
    for thing in items_want_inside:
        if thing not in container_being_checked:
            return False
    return True

def all_isinstance(items_checking, instance_wanted):
    for thing in items_checking:
        if isinstance(thing, instance_wanted) is False:
            return False
    return True

def font_position_center(rect, font, text):
    x = (rect.width - font.size(text)[0]) // 2
    y = (rect.height - font.size(text)[1]) // 2
    return rect.left + x, rect.top + y

def out_of_arena_fix(player):
    """Global to handle players from reaching out of arena."""
    global arena_in_use  # set in GameLoop._setup_arena of main.py
    play_area = arena_in_use.play_area_rect
    fixed = False  # Can be used for out-of-bounds checking since it returns true
    if player.left < play_area.left:
        player.left = play_area.left
        fixed = True
    if player.bottom > play_area.bottom:
        player.bottom = play_area.bottom
        fixed = True
    if player.right > play_area.right:
        player.right = play_area.right
        fixed = True
    return fixed

def handle_damage(target, value, time):
    if value != 0:
        target.hit_points -= value
        target.shield_trigger(value)
        target.st_buffer.append((value, time + 2000))

def condition_string(cond, value):
    st = cond + ": "
    left = 0 + int(value/1000)
    right = 0 + int( (value%1000) / 100)
    st += str(left)
    st += "."
    st += str(right)
    return st

def force_add_particle_to_player(particle,player):
    if isinstance(particle,list):
        if player.new_particle is None:
            player.new_particle = particle
        elif isinstance(player.new_particle, list):
            player.new_particle += particle
        else:
            player.new_particle = [player.new_particle] + particle

    else:
        if player.new_particle is None:
            player.new_particle = particle
        elif isinstance(player.new_particle, list):
            player.new_particle.append(particle)
        else:
            player.new_particle = [player.new_particle, particle]


# Music and Sound
class Audio:
    def __init__(self):
        try:
            pygame.mixer.init(44100)
            self.audio_device_found = True
        except pygame.error:
            self.audio_device_found = False
        self.menu_song = self.curr_song = 'data/404error.mp3'
        self.music_on = self.sound_on = False

    def restart_music(self):
        if self.audio_device_found:
            self.turn_off_music()
            self.turn_on_music()

    def turn_on_music(self):
        if self.audio_device_found:
            self.music_on = True
            self.curr_song = self.menu_song
            pygame.mixer.music.load(self.curr_song)
            pygame.mixer.music.play(-1)
            print(self)

    def turn_off_music(self):
        if self.audio_device_found:
            self.music_on = False
            pygame.mixer.music.stop()

    def turn_on_effects(self):
        if self.audio_device_found:
            self.sound_on = True

    def turn_off_effects(self):
        if self.audio_device_found:
            self.sound_on = False

    def play_next_random_song(self):
        if self.audio_device_found:
            self.curr_song = random.choice([s for s in SONGS if s != self.curr_song])
            pygame.mixer.music.load(self.curr_song)
            pygame.mixer.music.play()
            pygame.mixer.music.set_endevent(SONG_END_EVENT)
            print(self)

    def __str__(self):
        t = datetime.datetime.now().strftime('%H:%M:%S')
        return 'new song: "{}"    started at: {}'.format(self.curr_song.replace('data/', '').replace('.mp3', ''), t)

AUDIO = Audio()

# Arenas
arena_nt = namedtuple('arena_nt', 'left_wall_x, right_wall_x, floor_y, platforms, max_monsters, possible_monsters, background, p1_spawn, p2_spawn')
terrain_nt = namedtuple('terrain_nt', 'left, top, width, height, color, hits_to_destroy, spawn_point')

arena1 = arena_nt(
    left_wall_x=65, right_wall_x=1215, floor_y=475,
    platforms=[
        terrain_nt(0, 270, 300, 60, DKGREEN, -1, False),
        terrain_nt(850, 270, 300, 60, DKGREEN, -1, False),
        terrain_nt(545, 150, 60, 230, DKGREEN, -1, False),
        terrain_nt(140, 100, 150, 20, DKGREEN, -1, False),
        terrain_nt(860, 100, 150, 20, DKGREEN, -1, False),
        terrain_nt(30, 240, 40, 20, WHITE, 5, False),
        terrain_nt(1145, 465, -5, 5, None, -1, True),
        terrain_nt(15, 465, -5, 5, None, -1, True), ],
    max_monsters=5, possible_monsters=(WEAK, MEDIUM),
    background=None, p1_spawn=(135, 150), p2_spawn=(985, 150))

arena2 = arena_nt(
    left_wall_x=65, right_wall_x=1215, floor_y=475,
    platforms=[
        terrain_nt(50, 100, 50, 300, DKGREEN, -1, False),
        terrain_nt(240, 40, 50, 300, DKGREEN, -1, False),
        terrain_nt(500, 135, 100, 25, DKGREEN, -1, False),
        terrain_nt(725, 255, 175, 25, DKGREEN, -1, False),
        terrain_nt(1050, 375, 100, 25, DKGREEN, -1, False),
        terrain_nt(400, 434, 300, 41, DKGREEN, -1, False),
        terrain_nt(485, 394, 300, 41, DKGREEN, -1, False),
        terrain_nt(970, 65, 80, 10, DKGREEN, -1, False),
        terrain_nt(150, 465, -5, 5, None, -1, True),
        terrain_nt(930, 465, -5, 5, None, -1, True), ],
    max_monsters=5, possible_monsters=ALL,
    background=None, p1_spawn=(135, 150), p2_spawn=(985, 150))

arena3 = arena_nt(
    left_wall_x=65, right_wall_x=1215, floor_y=458,
    platforms=[
        terrain_nt(425, 80, 73, 40, None, -1, False),
        terrain_nt(555, 80, 100, 40, None, -1, False),
        terrain_nt(85, 140, 228, 40, None, -1, False),
        terrain_nt(85, 180, 40, 142, None, -1, False),
        terrain_nt(85, 322, 95, 40, None, -1, False),
        terrain_nt(332, 241, 220, 40, None, -1, False),
        terrain_nt(595, 319, 417, 40, None, -1, False),
        terrain_nt(972, 156, 40, 163, None, -1, False),
        terrain_nt(785, 120, 227, 40, None, -1, False),
        terrain_nt(150, 465, -5, 5, None, -1, True),
        terrain_nt(930, 465, -5, 5, None, -1, True), ],
    max_monsters=5, possible_monsters=ALL,
    background='data/vines-copy2.png', p1_spawn=(75, 50), p2_spawn=(992, 50))

arena4 = arena_nt(
     left_wall_x=65, right_wall_x=1215, floor_y=458,
    platforms=[
        terrain_nt(546, 51, 229, 37, None, -1, False),
        terrain_nt(0, 114, 110, 37, None, -1, False),
        terrain_nt(338, 114, 112, 37, None, -1, False),
        terrain_nt(823, 152, 229, 37, None, -1, False),
        terrain_nt(594, 164, 18, 194, None, -1, False),
        terrain_nt(702, 204, 18, 194, None, -1, False),
        terrain_nt(134, 190, 113, 37, None, -1, False),
        terrain_nt(268, 286, 229, 37, None, -1, False),
        terrain_nt(802, 316, 348, 37, None, -1, False),
        terrain_nt(72, 351, 112, 37, None, -1, False),
        terrain_nt(150, 450, -5, 5, RED, -1, True),
        terrain_nt(930, 450, -5, 5, RED, -1, True), ],
    max_monsters=5,
    possible_monsters=ALL,
    background='data/tree.png', p1_spawn=(75,50), p2_spawn=(992, 50))

arena5 = arena_nt(
     left_wall_x=65, right_wall_x=1215, floor_y=458,
    platforms=[
        terrain_nt(59, 87, 40, 298, None, -1, False),
        terrain_nt(236, 44, 40, 298, None, -1, False),
        terrain_nt(498, 119, 112, 37, None, -1, False),
        terrain_nt(953, 47, 112, 37, None, -1, False),
        terrain_nt(1031, 359, 112, 37, None, -1, False),
        terrain_nt(673, 241, 229, 37, None, -1, False),
        terrain_nt(496, 348, 263, 56, None, -1, False),
        terrain_nt(381, 402, 350, 56, None, -1, False),
        terrain_nt(150, 450, -5, 5, RED, -1, True),
        terrain_nt(930, 450, -5, 5, RED, -1, True), ],
    max_monsters=5,
    possible_monsters=ALL,
    background='data/cyborg.png', p1_spawn=(75,50), p2_spawn=(985, 150))



# Monsters
monster_info_nt = namedtuple('monster_info_nt', 'kind, w, h, dx, dy, hp, chase, idle')
MONSTER_TABLE = {
    WEAK: monster_info_nt(WEAK, 30, 40, 2, 10, 100, 5000, 5000),
    MEDIUM: monster_info_nt(MEDIUM, 50, 60, 3, 12, 250, 7000, 5000),
    ULTIMATE: monster_info_nt(ULTIMATE, 80, 80, 4, 13, 500, 10000, 5000)}
