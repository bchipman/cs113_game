import datetime
import os
import random
import sys
from collections import namedtuple
from collections import defaultdict

import pygame
from pygame import Color
from pygame.locals import *  # for event timers

if os.environ['COMPUTERNAME'] == 'BRIAN-DESKTOP':
    os.environ['SDL_VIDEO_WINDOW_POS'] = '{},{}'.format(1920, 90)
if os.environ['COMPUTERNAME'] in ('MAX-LT', 'BRIAN-LAPTOP'):
    os.environ['SDL_VIDEO_WINDOW_POS'] = '{},{}'.format(50, 30)

pygame.init()
pygame.display.set_caption('Famished Tournament')
SCREEN = pygame.display.set_mode((1280, 600))
WINDOW = SCREEN.get_rect()
RED_MASK = pygame.Surface((40, 40))
RED_MASK.fill((255, 0, 0))
RED_MASK.set_alpha(100)
WHITE_BACKGROUND = pygame.Surface((40, 40))
WHITE_BACKGROUND.fill((100, 100, 100))
CLOCK = pygame.time.Clock()
FPS = 30
NEXT_PAGE = 'start'

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
TRANSPARENT = Color(235, 0, 255)

# Music
SONGS = ['data/pneumatic_driller.mp3', 'data/euglena_zielona.mp3',
         'data/drilldance.mp3', 'data/running_emu.mp3', 'data/wooboodoo.mp3',
         'data/accident.mp3']

SOUNDS = {}

# Monster Types and Globals
ALL = 'ALL'
WEAK = 'WEAK'
MEDIUM = 'MEDIUM'
ULTIMATE = 'ULTIMATE'
CHASING = 'CHASING'
IDLE = 'IDLE'
ULTIMATE_SPAWN_RATE = 5000
WEAK_EXP_VALUE = 10
MEDIUM_EXP_VALUE = 25
ULTIMATE_EXP_VALUE = 50

# Player exp level-up thresholds
#                   1  2   3    4    5    6    7    8    9    10
LEVEL_THRESHOLDS = [0, 50, 100, 150, 200, 250, 300, 350, 400, 450]

# Player States (for animation)
STAND = 'STAND'
LWALK = 'LWALK'
RWALK = 'RWALK'
JUMP = 'JUMP'
FALL = 'FALL'
WIN = 'WIN'
DEATH = 'DEATH'
RESET = 'RESET'
ATTACK = 'ATTACK'  # Rest is attacks
ONEHAND = 'ONEHAND'
TWOHAND = 'TWOHAND'
CAST1 = 'CAST1'
CAST2 = 'CAST2'
CAST3 = 'CAST3'
THROW = 'THROW'
MACHGUN = 'MACHGUN'
BREATH = 'BREATH'
POKE = 'POKE'
BULLET = 'BULLET'
DASH = 'DASH'
RUN = 'RUN'

# Player Attack State Info Table [index, max value]
PL_ATTACK_TABLE = {'ONEHAND': [28, 3],
                   'TWOHAND': [32, 3],
                   'CAST1': [36, 2],
                   'CAST2': [39, 3],
                   'CAST3': [43, 0],
                   'THROW': [44, 3],
                   'MACHGUN': [48, 1],
                   'BREATH': [50, 2],
                   'POKE': [53, 3],
                   'BULLET': [57, 3],
                   'DASH': [7, 0],
                   'RUN': [8, 15]}

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
ATTACKBUTTON = 'attack_id'
SKILL1BUTTON = 'skill1_id'
SKILL2BUTTON = 'skill2_id'
SKILL3BUTTON = 'skill3_id'
ULTBUTTON = 'ult_id'

# Scrolling texts
ST_DMG = 'ST_DMG'
ST_HP = 'ST_HP'
ST_ENERGY = 'ST_ENERGY'
ST_LEVEL_UP = 'ST_LEVEL_UP'

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

# -----------------------------Global Functions-------------------------------
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
        if target.hit_points < 0:
            target.hit_points = 0
        if time >= 0:
            target.st_buffer.append((ST_DMG, value, time + 2000))
        else:
            target.st_buffer.append((ST_DMG, value, time))

def handle_hp_gain(target, value, time):
    if value != 0:
        if target.hit_points > 0:
            target.hit_points += value
        if target.hit_points > target.hit_points_max:
            target.hit_points = target.hit_points_max
        if time >= 0:
            target.st_buffer.append((ST_HP, value, time + 2000))
        else:
            target.st_buffer.append((ST_HP, value, time))

def handle_energy(target, value, time):
    if value != 0:
        target.energy += value
        if time >= 0:
            target.st_buffer.append((ST_ENERGY, value, time + 2000))
        else:
            target.st_buffer.append((ST_ENERGY, value, time))

def condition_string(cond, value):
    st = cond + ': '
    left = 0 + int(value / 1000)
    right = 0 + int((value % 1000) / 100)
    st += str(left)
    st += '.'
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

def EXIT_GAME():
    pygame.quit()
    sys.exit()


# ---------Getters and Setters for Player Sprites and Level Select------------
def set_player1_spritesheet(spritesheet):
    global P1_SPRITESHEET
    P1_SPRITESHEET = spritesheet

def set_player2_spritesheet(spritesheet):
    global P2_SPRITESHEET
    P2_SPRITESHEET = spritesheet

def set_level(arena):
    global SELECTED_ARENA
    SELECTED_ARENA = arena

def get_spritesheet(player):
    if player == 'player1':
        global P1_SPRITESHEET
        return P1_SPRITESHEET
    elif player == 'player2':
        global P2_SPRITESHEET
        return P2_SPRITESHEET

def get_selected_level():
    global SELECTED_ARENA
    return SELECTED_ARENA

# -----------------------------Music and Sound--------------------------------
class Audio:
    def __init__(self):
        try:
            pygame.mixer.init(44100)
            self.audio_device_found = True
        except pygame.error:
            self.audio_device_found = False
        self.menu_song = self.curr_song = 'data/404error.mp3'
        self.music_on = self.sound_on = True

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
            print('music turned on', end='    ')
            print(self)

    def turn_off_music(self):
        if self.audio_device_found:
            self.music_on = False
            pygame.mixer.music.stop()
            print('music turned off')

    def turn_on_effects(self):
        if self.audio_device_found:
            self.sound_on = True
            print('sound effects turned on')

    def turn_off_effects(self):
        if self.audio_device_found:
            self.sound_on = False
            print('sound effects turned off')

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

# ----------------------------------Input-------------------------------------
class Input:
    def __init__(self, player_id=1):
        self.gp_input = defaultdict(bool)
        self.kb_input = defaultdict(bool)
        self.player_id = player_id
        try:
            self.gamepad = pygame.joystick.Joystick(player_id - 1)
            self.gamepad.init()
            self.gamepad_found = True
            print('p{} uses "{}"'.format(str(self.player_id), self.gamepad.get_name()))
            self.__setup_gamepad_buttons__()
        except pygame.error:
            pass

    def __setup_gamepad_buttons__(self):
        input_nt = namedtuple('input_nt', 'kind, number, value1, value2')

        #  L2                                  R2
        #     L1                            R1
        #         U                      Y
        #       L   R   SELCT  START   X   B
        #         D                      A

        if self.gamepad.get_name() == 'Gioteck PS3 Wired Controller':  # Max's gamepad
            di = {'GP_LEFT': input_nt(kind='hat', number=0, value1=-1, value2=0),
                  'GP_RIGHT': input_nt(kind='hat', number=0, value1=1, value2=0),
                  'GP_UP': input_nt(kind='hat', number=0, value1=1, value2=-1),
                  'GP_DOWN': input_nt(kind='hat', number=0, value1=-1, value2=+1),
                  'GP_Y': input_nt(kind='button', number=0, value1=None, value2=None),
                  'GP_X': input_nt(kind='button', number=3, value1=None, value2=None),
                  'GP_B': input_nt(kind='button', number=1, value1=None, value2=None),
                  'GP_A': input_nt(kind='button', number=2, value1=None, value2=None),
                  'GP_SELECT': input_nt(kind='button', number=8, value1=None, value2=None),
                  'GP_START': input_nt(kind='button', number=9, value1=None, value2=None),
                  'GP_L1': input_nt(kind='button', number=4, value1=None, value2=None),
                  'GP_R1': input_nt(kind='button', number=5, value1=None, value2=None),
                  'GP_L2': input_nt(kind='button', number=6, value1=None, value2=None),
                  'GP_R2': input_nt(kind='button', number=7, value1=None, value2=None)}

        elif self.gamepad.get_name() == 'Logitech Cordless RumblePad 2 USB':  # Brian's gamepad if switched to "D"
            di = {'GP_LEFT': input_nt(kind='hat', number=0, value1=-1, value2=0),  # works but seems backwards to me (value1 and value2)
                  'GP_RIGHT': input_nt(kind='hat', number=0, value1=+1, value2=0),  # works but seems backwards to me (value1 and value2)
                  'GP_UP': input_nt(kind='hat', number=0, value1=0, value2=+1),
                  'GP_DOWN': input_nt(kind='hat', number=0, value1=0, value2=-1),
                  'GP_Y': input_nt(kind='button', number=3, value1=None, value2=None),
                  'GP_X': input_nt(kind='button', number=0, value1=None, value2=None),
                  'GP_B': input_nt(kind='button', number=2, value1=None, value2=None),
                  'GP_A': input_nt(kind='button', number=1, value1=None, value2=None),
                  'GP_SELECT': input_nt(kind='button', number=8, value1=None, value2=None),
                  'GP_START': input_nt(kind='button', number=9, value1=None, value2=None),
                  'GP_L1': input_nt(kind='button', number=4, value1=None, value2=None),
                  'GP_R1': input_nt(kind='button', number=5, value1=None, value2=None),
                  'GP_L2': input_nt(kind='button', number=6, value1=None, value2=None),
                  'GP_R2': input_nt(kind='button', number=7, value1=None, value2=None)}

        elif self.gamepad.get_name() in ('Wireless Gamepad F710 (Controller)', 'Controller (XBOX 360 For Windows)'):  # Brian's gamepad if switched to "X"
            di = {'GP_LEFT': input_nt(kind='hat', number=0, value1=-1, value2=0),  # works but seems backwards to me (value1 and value2)
                  'GP_RIGHT': input_nt(kind='hat', number=0, value1=+1, value2=0),  # works but seems backwards to me (value1 and value2)
                  'GP_UP': input_nt(kind='hat', number=0, value1=0, value2=+1),
                  'GP_DOWN': input_nt(kind='hat', number=0, value1=0, value2=-1),
                  'GP_Y': input_nt(kind='button', number=3, value1=None, value2=None),
                  'GP_X': input_nt(kind='button', number=2, value1=None, value2=None),
                  'GP_B': input_nt(kind='button', number=1, value1=None, value2=None),
                  'GP_A': input_nt(kind='button', number=0, value1=None, value2=None),
                  'GP_SELECT': input_nt(kind='button', number=6, value1=None, value2=None),
                  'GP_START': input_nt(kind='button', number=7, value1=None, value2=None),
                  'GP_L1': input_nt(kind='button', number=4, value1=None, value2=None),
                  'GP_R1': input_nt(kind='button', number=5, value1=None, value2=None),
                  'GP_L2': input_nt(kind='axis', number=2, value1=+1, value2=None),
                  'GP_R2': input_nt(kind='axis', number=2, value1=-1, value2=None)}

        self.GP_INPUTS_DICT = di

    def get_gamepad(self):
        return self.gamepad_found

    def refresh(self):
        self._reset_all_event_flags()
        if self.player_id == 1:
            self._get_keyboard_pressed()
            self._get_keyboard_events()
        self._get_gamepad_pressed2()
        self._combine_all_pressed()
        if self.player_id == 1:
            self._handle_mouse_visibility()

    def refresh_during_pause(self):
        self._reset_all_event_flags()
        self.refreshing_during_pause = True
        if self.player_id == 1:
            self._get_keyboard_pressed()
            self._get_keyboard_events()
            self._get_gamepad_pressed2()
            self._combine_all_pressed()
            self._handle_mouse_visibility()
        self.refreshing_during_pause = False

    def _get_keyboard_pressed(self):
        sucky_kb_input = pygame.key.get_pressed()
        self.kb_input['K_RETURN'] = sucky_kb_input[K_RETURN]
        self.kb_input['K_ESCAPE'] = sucky_kb_input[K_ESCAPE]
        self.kb_input['K_BACKQUOTE'] = sucky_kb_input[K_BACKQUOTE]
        self.kb_input['K_F12'] = sucky_kb_input[K_F12]
        self.kb_input['K_LEFT'] = sucky_kb_input[K_LEFT]
        self.kb_input['K_RIGHT'] = sucky_kb_input[K_RIGHT]
        self.kb_input['K_UP'] = sucky_kb_input[K_UP]
        self.kb_input['K_DOWN'] = sucky_kb_input[K_DOWN]
        self.kb_input['K_SPACE'] = sucky_kb_input[K_SPACE]
        self.kb_input['K_a'] = sucky_kb_input[K_a]
        self.kb_input['K_s'] = sucky_kb_input[K_s]
        self.kb_input['K_d'] = sucky_kb_input[K_d]
        self.kb_input['K_f'] = sucky_kb_input[K_f]
        self.kb_input['K_g'] = sucky_kb_input[K_g]
        self.kb_input['K_q'] = sucky_kb_input[K_q]
        self.kb_input['K_r'] = sucky_kb_input[K_r]
        self.kb_input['K_k'] = sucky_kb_input[K_k]

    def _get_keyboard_events(self):
        for event in pygame.event.get(KEYDOWN):
            if event.key == K_RETURN:
                self.START_PRESS_EVENT = not self.START_PRESS_EVENT

            if event.key == K_ESCAPE:
                self.SELECT_PRESS_EVENT = not self.SELECT_PRESS_EVENT

            if event.key == K_BACKQUOTE:
                self.DEBUG_VIEW = not self.DEBUG_VIEW

            if event.key == K_F12:
                self.F12DEBUG_VIEW = not self.DEBUG_VIEW

            if event.key == K_LEFT:
                self.LEFT_PRESS_EVENT = not self.LEFT_PRESS_EVENT

            if event.key == K_RIGHT:
                self.RIGHT_PRESS_EVENT = not self.RIGHT_PRESS_EVENT

            if event.key == K_UP:
                self.UP_PRESS_EVENT = not self.UP_PRESS_EVENT

            if event.key == K_DOWN:
                self.DOWN_PRESS_EVENT = not self.DOWN_PRESS_EVENT

    def _get_gamepad_pressed2(self):
        if self.gamepad_found:
            if self.player_id == 1:
                Input.joy_button_events = [e for e in pygame.event.get(JOYBUTTONDOWN)]
                Input.joy_axis_events = [e for e in pygame.event.get(JOYAXISMOTION)]
                Input.joy_hat_events = [e for e in pygame.event.get(JOYHATMOTION)]

            joy_button_events = list(filter(lambda x: x.joy == self.player_id - 1, Input.joy_button_events))
            joy_axis_events = list(filter(lambda x: x.joy == self.player_id - 1, Input.joy_axis_events))
            joy_hat_events = list(filter(lambda x: x.joy == self.player_id - 1, Input.joy_hat_events))

            for name, info in self.GP_INPUTS_DICT.items():  # these are all the inputs that we care about
                if info.kind == 'button':
                    self.gp_input[name] = self.gamepad.get_button(info.number)
                    if info.number in [e.button for e in joy_button_events]:
                        self.gp_input[name + '_PRESS_EVENT'] = not self.gp_input[name + '_PRESS_EVENT']
                        # print('button', name + '_PRESS_EVENT', self.gp_input[name + '_PRESS_EVENT'])

                elif info.kind == 'axis':
                    self.gp_input[name] = round(self.gamepad.get_axis(info.number)) == info.value1
                    if (info.number, info.value1) in [(e.axis, e.value) for e in joy_axis_events]:
                        self.gp_input[name + '_PRESS_EVENT'] = not self.gp_input[name + '_PRESS_EVENT']
                        # print('axis  ', name + '_PRESS_EVENT', self.gp_input[name + '_PRESS_EVENT'])

                elif info.kind == 'hat':
                    self.gp_input[name] = self.gamepad.get_hat(info.number)[info.value2] == info.value1  # ITS FUCKING BACKWARDS??? THE TWO WAYS TO LOOK UP HAT DATA DONT RETURN THE SAME DATA IN THE SAME FUCKING WAY?  WHAT THE FUCK FUCK YOU PYGAME.
                    if (info.number, info.value1, info.value2) in [(e.hat, e.value[0], e.value[1]) for e in joy_hat_events]:
                        self.gp_input[name + '_PRESS_EVENT'] = not self.gp_input[name + '_PRESS_EVENT']
                        # print('hat   ', name + '_PRESS_EVENT', self.gp_input[name + '_PRESS_EVENT'])

    def _combine_all_pressed(self):
        self.LEFT = self.kb_input['K_LEFT'] or self.gp_input['GP_LEFT']
        self.RIGHT = self.kb_input['K_RIGHT'] or self.gp_input['GP_RIGHT']
        self.UP = self.kb_input['K_UP'] or self.gp_input['GP_UP']
        self.DOWN = self.kb_input['K_DOWN'] or self.gp_input['GP_DOWN']
        self.JUMP = self.kb_input['K_SPACE'] or self.gp_input['GP_A']
        self.ATTACK = self.kb_input['K_a'] or self.gp_input['GP_X']
        self.SKILL1 = self.kb_input['K_s'] or self.gp_input['GP_B']
        self.SKILL2 = self.kb_input['K_d'] or self.gp_input['GP_Y']
        self.SKILL3 = self.kb_input['K_f'] or self.gp_input['GP_R1']
        self.ULT = self.kb_input['K_g'] or self.gp_input['GP_R2']
        self.DROP_SKILL = self.kb_input['K_q'] or self.gp_input['GP_L1']
        self.RESPAWN = self.kb_input['K_r']
        self.KILLALL = self.kb_input['K_k']

        self.LEFT_PRESS_EVENT = self.gp_input['GP_LEFT_PRESS_EVENT']
        self.RIGHT_PRESS_EVENT = self.gp_input['GP_RIGHT_PRESS_EVENT']
        self.UP_PRESS_EVENT = self.gp_input['GP_UP_PRESS_EVENT']
        self.DOWN_PRESS_EVENT = self.gp_input['GP_DOWN_PRESS_EVENT']
        self.START_PRESS_EVENT = self.gp_input['GP_START_PRESS_EVENT']
        self.SELECT_PRESS_EVENT = self.gp_input['GP_SELECT_PRESS_EVENT']

        self.A_PRESS_EVENT = self.gp_input['GP_A_PRESS_EVENT']
        self.B_PRESS_EVENT = self.gp_input['GP_B_PRESS_EVENT']

    def __setattr__(self, name, value):
        if name == 'refreshing_during_pause':
            self.__dict__[name] = value  # update like normal (otherwise infinite recursion)

        if self.refreshing_during_pause:  # if paused
            if name not in 'LEFT, RIGHT, UP, DOWN, JUMP, ATTACK, SKILL1, SKILL2, SKILL3, ULT, DROP_SKILL, RESPAWN, KILLALL, DEBUG_VIEW'.split(', '):  # and NOT one of these
                if 'EVENT' in name:  # and if one of these
                    self.__dict__['gp_input']['GP_' + name] = value  # sync [X]_PRESS_EVENT with self.gp_input[GP_[X]_PRESS_EVENT]
                self.__dict__[name] = value  # update like normal

        elif not self.refreshing_during_pause:
            if 'EVENT' in name:  # and if one of these
                self.__dict__['gp_input']['GP_' + name] = value  # sync [X]_PRESS_EVENT with self.gp_input[GP_[X]_PRESS_EVENT]
            self.__dict__[name] = value  # update like normal

    def _reset_all_event_flags(self):
        for name in 'LEFT_PRESS_EVENT, RIGHT_PRESS_EVENT, UP_PRESS_EVENT, DOWN_PRESS_EVENT, START_PRESS_EVENT, SELECT_PRESS_EVENT, A_PRESS_EVENT, B_PRESS_EVENT'.split(', '):
            exec('self.{} = False'.format(name))

    def _handle_mouse_visibility(self):
        global NEXT_PAGE
        if self.DEBUG_VIEW and NEXT_PAGE not in ('start, options, help'.split(', ')):
            pygame.mouse.set_visible(False)
        else:
            pygame.mouse.set_visible(True)

    def __getattr__(self, name):
        # initializes any missing variables to False
        exec('self.{} = False'.format(name))
        return eval('self.{}'.format(name))
INPUT1 = Input(player_id=1)
INPUT2 = Input(player_id=2)

# ----------------------------------Arenas------------------------------------
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
    max_monsters=3, possible_monsters=(WEAK, MEDIUM),
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
    max_monsters=3, possible_monsters=(WEAK, MEDIUM),  # ALL
    background=None, p1_spawn=(135, 150), p2_spawn=(985, 150))

arena3 = arena_nt(
    left_wall_x=65, right_wall_x=1215, floor_y=458,
    platforms=[
        terrain_nt(401, 80, 112, 37, None, -1, False),
        terrain_nt(557, 80, 112, 37, None, -1, False),
        terrain_nt(85, 140, 228, 40, None, -1, False),
        terrain_nt(85, 180, 40, 142, None, -1, False),
        terrain_nt(85, 322, 95, 40, None, -1, False),
        terrain_nt(332, 241, 220, 40, None, -1, False),
        terrain_nt(595, 319, 417, 40, None, -1, False),
        terrain_nt(972, 156, 40, 163, None, -1, False),
        terrain_nt(785, 120, 227, 40, None, -1, False),
        terrain_nt(150, 465, -5, 5, None, -1, True),
        terrain_nt(930, 465, -5, 5, None, -1, True), ],
    max_monsters=3, possible_monsters=(WEAK, MEDIUM),  # ALL
    background='data/vinesLevel.png', p1_spawn=(75, 50), p2_spawn=(992, 50))

arena4 = arena_nt(
    left_wall_x=65, right_wall_x=1215, floor_y=458,
    platforms=[
        terrain_nt(546, 51, 229, 37, None, -1, False),
        terrain_nt(0, 114, 110, 37, None, -1, False),
        terrain_nt(338, 114, 112, 37, None, -1, False),
        terrain_nt(823, 152, 229, 37, None, -1, False),
        terrain_nt(594, 164, 18, 194, None, -1, False),
        terrain_nt(702, 181, 18, 194, None, -1, False),
        terrain_nt(134, 190, 113, 37, None, -1, False),
        terrain_nt(268, 286, 229, 37, None, -1, False),
        terrain_nt(802, 316, 348, 37, None, -1, False),
        terrain_nt(72, 351, 112, 37, None, -1, False),
        terrain_nt(150, 450, -5, 5, None, -1, True),
        terrain_nt(930, 450, -5, 5, None, -1, True), ],
    max_monsters=3, possible_monsters=(WEAK, MEDIUM),  # ALL
    background='data/humanLevel.png', p1_spawn=(75, 50), p2_spawn=(992, 50))

arena5 = arena_nt(
    left_wall_x=65, right_wall_x=1215, floor_y=458,
    platforms=[
        terrain_nt(59, 70, 40, 298, None, -1, False),
        terrain_nt(236, 44, 40, 298, None, -1, False),
        terrain_nt(498, 119, 112, 37, None, -1, False),
        terrain_nt(953, 47, 112, 37, None, -1, False),
        terrain_nt(1031, 335, 112, 37, None, -1, False),
        terrain_nt(673, 208, 229, 37, None, -1, False),
        terrain_nt(496, 348, 263, 56, None, -1, False),
        terrain_nt(381, 402, 350, 56, None, -1, False),
        terrain_nt(150, 450, -5, 5, None, -1, True),
        terrain_nt(930, 450, -5, 5, None, -1, True), ],
    max_monsters=3, possible_monsters=(WEAK, MEDIUM),  # ALL
    background='data/androidLevel.png', p1_spawn=(75, 50), p2_spawn=(985, 150))

# ---------------------------------Monsters-----------------------------------
monster_info_nt = namedtuple('monster_info_nt', 'kind, w, h, dx, dy, hp, chase, idle, exp_value, dmg')
MONSTER_TABLE = {
    WEAK: monster_info_nt(WEAK, 30, 40, 2, 10, 50, 5000, 5000, WEAK_EXP_VALUE, 3),
    MEDIUM: monster_info_nt(MEDIUM, 50, 60, 3, 12, 100, 7000, 5000, MEDIUM_EXP_VALUE, 5),
    ULTIMATE: monster_info_nt(ULTIMATE, 80, 80, 4, 13, 150, 10000, 5000, ULTIMATE_EXP_VALUE, 8)}

# ------------Spritesheet and Arena Globals with Default Values---------------
P1_SPRITESHEET = 'data/p1_human_8bit.png'
P2_SPRITESHEET = 'data/p1_human_8bit.png'
SELECTED_ARENA = arena3
