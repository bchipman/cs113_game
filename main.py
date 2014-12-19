# python standard library modules
import os
import random
import sys
from collections import deque

# pygame
import pygame
from pygame.locals import *

# psutil  (download here:  http://www.lfd.uci.edu/~gohlke/pythonlibs/#psutil)
try:
    import psutil
    psutil_found = True
except ImportError:
    psutil_found = False

# our modules
import globals as GL
from classes import *
from debug import *
from globals import *
from pages import *
from skills import *
from pygbutton import PygButton

# ----------------------------------------------------------------------------
# noinspection PyUnusedLocal
class Application:
    def __init__(self):
        _start = StartPage()
        _options = OptionsPage()
        _help = HelpPage()
        _pause = PausePage()
        _game_over = GameOverPage()
        current_page = '_start'
        while True:
            eval(current_page + '()')
            current_page = GL.NEXT_PAGE

# ----------------------------------------------------------------------------
class GameLoop:
    def __init__(self):
        def _setup_time():
            pygame.time.set_timer(TIME_TICK_EVENT, 250)
            pygame.time.set_timer(REGENERATION_EVENT, 1000)
            self.game_time = GameTime()

        def _setup_ui():
            self.bkg_image = pygame.image.load('data/backgrounds/bkg_menus.png')
            self.return_button = pygbutton.PygButton((490, 550, 300, 50), 'Main Menu')
            self.window_border = Rect2(left=0, top=0, width=1280, height=600)
            self.play_area_border = Rect2(left=60, top=0, width=1160, height=485)
            self.left_grey_fill = Rect2(left=0, top=0, width=65, height=600)
            self.right_grey_fill = Rect2(left=1215, top=0, width=60, height=600)
            self.bottom_grey_fill = Rect2(left=0, top=475, width=1280, height=125)
            self.skill_boxes = [
                # player 1 skill boxes
                Rect2(topleft=(90, 500), size=(40, 40), color=BLACK),
                Rect2(topleft=(140, 500), size=(40, 40), color=BLACK),
                Rect2(topleft=(190, 500), size=(40, 40), color=BLACK),
                Rect2(topleft=(240, 500), size=(40, 40), color=BLACK),
                Rect2(topleft=(290, 500), size=(40, 40), color=BLACK),
                # player 2 skill boxes
                Rect2(topleft=(950, 500), size=(40, 40), color=BLACK),
                Rect2(topleft=(1000, 500), size=(40, 40), color=BLACK),
                Rect2(topleft=(1050, 500), size=(40, 40), color=BLACK),
                Rect2(topleft=(1100, 500), size=(40, 40), color=BLACK),
                Rect2(topleft=(1150, 500), size=(40, 40), color=BLACK), ]
            self.health_bar_outline = pygame.image.load('data/backgrounds/health_bar_outline.png')
            self.health_bar_outline2 = pygame.image.load('data/backgrounds/health_bar_outline2.png')
            self.energy_bar_outline = pygame.image.load('data/backgrounds/energy_bar_outline.png')
            self.energy_bar_outline2 = pygame.image.load('data/backgrounds/energy_bar_outline2.png')

        def _setup_arena():
            # self.arena = random.choice(( arena3, arena4, arena5)))
            self.arena = Arena(GL.get_selected_level())
            GL.arena_in_use = self.arena  # used for out_of_arena_fix within global.py
            self.arena_image = pygame.image.load(self.arena.background)

        def _setup_fonts():
            # main_font = 'data/viner-hand-itc.ttf'
            main_font = 'data/fonts/Kremlin.ttf'
            self.timer_font = pygame.font.Font(main_font, 36)
            self.timer_font_xy = 605, 500
            self.health_font = pygame.font.Font(main_font, 55)
            self.health_font_xy = 60, 490
            self.energy_font = pygame.font.Font(main_font, 55)
            self.energy_font_xy = 80, 535
            self.debug_font_small = pygame.font.SysFont('consolas', 12)  # monospace
            self.debug_font_small_2 = pygame.font.SysFont('lucidasans', 12)  # monospace
            self.debug_font = pygame.font.SysFont('consolas', 20)  # monospace
            self.debug_font_xy1 = 1075, 505
            self.debug_font_xy2 = 1075, 520
            self.debug_font_xy3 = 1075, 540
            self.debug_font_xy4 = 1075, 560
            self.debug_font_xy5 = 800, 505
            self.debug_font_xy6 = 800, 520
            self.debug_font_xy7 = 800, 540
            self.cpu_avg = 0.0
            self.cpu_deque = deque((0,), maxlen=5)

            # Scrolling text stuff
            self.st_dmg_font = pygame.font.Font(main_font, 12)
            self.st_energy_font = pygame.font.Font(main_font, 12)
            self.st_condition_font = pygame.font.Font(main_font, 15)
            self.st_level_up_font = pygame.font.Font(main_font, 30)

            # Icon text
            self.icon_energy_font = pygame

            # Other text
            self.oor_font = pygame.font.Font(main_font, 20)

        def _setup_particles():
            self.active_particles = []

        def _setup_monsters():
            self.active_monsters = []
            self.ultimate_monster_active = False
            self.dropped_skills = []
            self.spawn_monsters = False
            pygame.event.post(pygame.event.Event(MONSTER_SPAWN_EVENT))

            self.weak_monster_image = pygame.image.load('data/sprites+portraits/monster_weak.png')
            self.medium_monster_image = pygame.image.load('data/sprites+portraits/monster_medium.png')
            self.ultimate_monster_image = pygame.image.load('data/sprites+portraits/monster_ultimate.png')

        def _setup_music():
            if AUDIO.music_on:
                AUDIO.play_next_random_song()

        def _setup_rain():
            self.rain_particles = []
            self.rain = Rect2(left=0, top=0, width=1, height=3)
            self.make_rain = False
            pygame.event.post(pygame.event.Event(MORE_RAIN_EVENT))

        def _setup_players():

            def _setup_player_sprites(spritesheet):
                try:
                    spritesheet1 = pygame.image.load(spritesheet)
                    spritesheet1.convert()
                except pygame.error:
                    return None

                m1 = []
                # Put spritesheet into list, each sprite is 64x64 pixels large, except for death
                for num in range(1, 8):  # Standing
                    m1.append(spritesheet1.subsurface((64 * (num - 1), 0, 64, 64)))
                for num in range(8, 16):  # Walk Transition
                    m1.append(spritesheet1.subsurface((64 * (num - 8), 64, 64, 64)))
                for num in range(16, 24):  # Walk Part 1
                    m1.append(spritesheet1.subsurface((64 * (num - 16), 128, 64, 64)))
                for num in range(24, 32):  # Walk Part 2
                    m1.append(spritesheet1.subsurface((64 * (num - 24), 192, 64, 64)))
                for num in range(32, 40):  # Jump and Fall
                    m1.append(spritesheet1.subsurface((64 * (num - 32), 256, 64, 64)))
                for num in range(40, 48):
                    m1.append(spritesheet1.subsurface((64 * (num - 40), 320, 64, 64)))
                for num in range(48, 56):
                    m1.append(spritesheet1.subsurface((64 * (num - 48), 384, 64, 64)))
                for num in range(56, 64):
                    m1.append(spritesheet1.subsurface((64 * (num - 56), 448, 64, 64)))
                for num in range(64, 71):
                    m1.append(spritesheet1.subsurface((64 * (num - 64), 512, 64, 64)))
                for num in range(71, 75):
                    m1.append(spritesheet1.subsurface((128 * (num - 71), 576, 128, 64)))

                for num in range(len(m1)):
                    m1[num].set_colorkey((0, 0, 0))  # sprite bg rgb is (0,0,0)
                    m1[num] = m1[num].convert_alpha()

                return m1

            self.player1 = Player(id=1, topleft=self.arena.p1_spawn, sprite=_setup_player_sprites(GL.P1_SPRITESHEET))
            self.player2 = Player(id=2, topleft=self.arena.p2_spawn, sprite=_setup_player_sprites(GL.P2_SPRITESHEET))

            self.player1.opposite = self.player2  # Makes things a lot easier
            self.player2.opposite = self.player1  # Makes things a lot easier

        _setup_time()
        _setup_ui()
        _setup_arena()
        initialize_skill_table()
        _setup_monsters()
        _setup_fonts()
        _setup_particles()
        _setup_music()
        _setup_rain()
        _setup_players()

    # ------------------------------------------------------------------------
    def __call__(self):
        self.return_now = False
        while not self.return_now:
            self.handle_players_inputs()
            self.handle_monsters(self.game_time.msec)
            self.handle_particles()
            self.draw_screen()
            self.draw_debug()
            self.handle_event_queue()
            self.check_if_game_over()
            pygame.display.update()
            GL.CLOCK.tick(GL.FPS)

    # -------------------------------------------------------------------------
    def handle_players_inputs(self):

        def _refresh_inputs():
            GL.INPUT1.refresh()
            GL.INPUT2.refresh()

        def _handle_players_inputs():
            self.player1(self.arena)
            self.player2(self.arena)

        def _handle_special_input():
            if GL.INPUT1.PAUSE_MODE_TOGGLED:
                self.return_now = True
                GL.CURR_GAME = self
                GL.NEXT_PAGE = '_pause'

            if GL.INPUT1.RESPAWN_EVENT:
                self.player1.topleft = self.player1.topleft_initial
                self.player1.dx = self.player1.dx_initial
                self.player1.facing_direction = self.player1.facing_direction_initial
                self.player2.topleft = self.player2.topleft_initial
                self.player2.dx = self.player2.dx_initial
                self.player2.facing_direction = self.player2.facing_direction_initial

            if GL.INPUT1.KILLALL_EVENT:
                for m in self.active_monsters:
                    m.hit_points = 0

        _refresh_inputs()
        _handle_players_inputs()
        _handle_special_input()

    # -------------------------------------------------------------------------
    def handle_particles(self):

        def _update_active_particles():
            if self.player1.new_particle:
                if isinstance(self.player1.new_particle, list):
                    for p in self.player1.new_particle:
                        if isinstance(p, Particle):
                            self.active_particles.append(p)
                        else:
                            self.arena.rects.append(Rect2(tuple(p)[0:4], color=p.color, hits_to_destroy=p.hits_to_destroy, spawn_point=p.spawn_point))
                else:
                    if isinstance(self.player1.new_particle, Particle):
                        self.active_particles.append(self.player1.new_particle)
                    else:
                        p = self.player1.new_particle
                        self.arena.rects.append(Rect2(tuple(p)[0:4], color=p.color, hits_to_destroy=p.hits_to_destroy, spawn_point=p.spawn_point))
                self.player1.new_particle = None

            if self.player2.new_particle:
                if isinstance(self.player2.new_particle, list):
                    for p in self.player2.new_particle:
                        if isinstance(p, Particle):
                            self.active_particles.append(p)
                        else:
                            self.arena.rects.append(Rect2(tuple(p)[0:4], color=p.color, hits_to_destroy=p.hits_to_destroy, spawn_point=p.spawn_point))
                else:
                    if isinstance(self.player2.new_particle, Particle):
                        self.active_particles.append(self.player2.new_particle)
                    else:
                        p = self.player2.new_particle
                        self.arena.rects.append(Rect2(tuple(p)[0:4], color=p.color, hits_to_destroy=p.hits_to_destroy, spawn_point=p.spawn_point))
                self.player2.new_particle = None

        def _update_particles():
            for p in self.active_particles:
                if p.expired:
                    if p.on_expire_f:
                        p.on_expire_f(p)
                    self.active_particles.remove(p)
                else:
                    p.update(self.game_time.msec)

        def _check_particle_collisions():
            for p in self.active_particles:
                opposite = self.player2 if p.belongs_to == self.player1 else self.player1

                # Ranged Particle
                if isinstance(p, RangeParticle):
                    # Check Terrains
                    all_terrain_hit_i = p.p_collidelistall(self.arena.rects)
                    if all_terrain_hit_i:  # False if empty list
                        if p.on_terrain_f:
                            p.on_terrain_f(p)
                        self.active_particles.remove(p)
                        for i in all_terrain_hit_i:
                            if i in range(0, len(self.arena.rects)):
                                self.arena.rects[i].hits_to_destroy -= 1
                                if self.arena.rects[i].hits_to_destroy == 0:
                                    self.arena.rects.pop(i)
                    # Check Monsters
                    else:
                        first_hit = p.collidelist(self.active_monsters)
                        if first_hit != -1:  # If hit a monsters
                            p.on_hit(self.active_monsters[first_hit], self.game_time.msec)
                            self.active_particles.remove(p)
                    # If didn't hit a monster, check player
                        else:
                            if p.colliderect(opposite):
                                p.on_hit(opposite, self.game_time.msec)
                                self.active_particles.remove(p)
                # Melee Particle
                elif isinstance(p, MeleeParticle):
                    # Check Monsters
                    all_monsters_hit_i = p.collidelistall(self.active_monsters)
                    for i in all_monsters_hit_i:
                        p.on_hit(self.active_monsters[i], self.game_time.msec)

                    first_terrain_hit_i = p.collidelist(self.arena.rects)
                    if first_terrain_hit_i != -1:
                        self.arena.rects[first_terrain_hit_i].hits_to_destroy -= 1
                        if self.arena.rects[first_terrain_hit_i].hits_to_destroy == 0:
                            self.arena.rects.pop(first_terrain_hit_i)
                    # Check Player
                    if p.colliderect(opposite):
                        p.on_hit(opposite, self.game_time.msec)
                # Field Particle
                else:
                    # Check Monsters and players
                    for t in self.active_monsters + [self.player1, self.player2]:
                        if p.is_in_field(t):
                            p.on_hit(t, self.game_time.msec)

        _update_active_particles()
        _update_particles()
        _check_particle_collisions()

    # -------------------------------------------------------------------------
    def handle_monsters(self, time):

        def _handle_monster_spawning():
            if self.spawn_monsters and len(self.active_monsters) < self.arena.max_monsters:
                spawn_point = self.arena.random_spawn_point  # pick a random spawn point
                color = random.choice((LLBLUE, DKYELLOW, DKPURPLE, DKORANGE))  # pick a random color
                monster_info = MONSTER_TABLE[random.choice(self.arena.possible_monsters)]  # pick a random monster
                self.active_monsters.append(Monster(monster_info, spawn_point.topleft, self.player1, self.player2, color))
            if not self.ultimate_monster_active:
                if self.game_time.msec != 0 and (self.game_time.msec % ULTIMATE_SPAWN_RATE) == 0:
                    spawn_point = self.arena.random_spawn_point  # pick a random spawn point
                    color = random.choice((LLBLUE, DKYELLOW, DKPURPLE, DKORANGE))  # pick a random color
                    self.ultimate_monster_active = True
                    self.active_monsters.append(Monster(MONSTER_TABLE[ULTIMATE], spawn_point.topleft, self.player1, self.player2, color))
            self.spawn_monsters = False

        def _handle_dead_monsters():
            for m in self.active_monsters:
                if m.is_dead():
                    dropped_skill_id = get_dropped_skill(m)
                    col = RED
                    if 100 <= dropped_skill_id < 1000:
                        col = BLUE
                    elif dropped_skill_id >= 1000:
                        col = YELLOW

                    dropped_skill_rect = Rect2(topleft=m.topleft, size=(25, 25), id=dropped_skill_id, color=col)
                    self.arena.dropped_skills.append(dropped_skill_rect)
                    if m.kind == ULTIMATE:
                        self.ultimate_monster_active = False
                    if m.last_hit_by is not None:
                        m.last_hit_by.handle_exp(m.exp_value,self.game_time.msec)

                    # Debugging: kill button used
                    else:
                        self.player1.handle_exp(m.exp_value,self.game_time.msec)
                    self.active_monsters.remove(m)

        def _update_monsters(time):
            for m in self.active_monsters:
                m(self.game_time.msec, self.arena)
                if m.colliderect(self.player1):
                    m.on_hit(self.player1, time)
                if m.colliderect(self.player2):
                    m.on_hit(self.player2, time)

        _handle_monster_spawning()
        _handle_dead_monsters()
        _update_monsters(time)

    # -------------------------------------------------------------------------
    def draw_screen(self):

        def _draw_ui1():
            GL.SCREEN.blit(self.bkg_image, (0, 0))
            if self.arena.background is not None:
                GL.SCREEN.blit(self.arena_image, (self.arena.play_area_rect.left, 0))

        def _draw_ui2():
            # font for player's health and energy
            # health_display = self.health_font.render(str(self.player1.hit_points), True, RED)
            # energy_display = self.energy_font.render(str(int(self.player1.energy)), True, YELLOW)
            # GL.SCREEN.blit(health_display, self.health_font_xy)
            # GL.SCREEN.blit(energy_display, self.energy_font_xy)

            # health bars
            GL.SCREEN.blit(self.health_bar_outline, (5, 20))
            GL.SCREEN.blit(self.health_bar_outline2, (1239, 20))

            # dynamic health bars
            self.damage_taken1 = self.player1.hit_points_max - self.player1.hit_points
            self.damage_taken2 = self.player2.hit_points_max - self.player2.hit_points
            self.health_bar1 = Rect((20, (21 + (2 * self.damage_taken1))), (20, (200 - (2 * self.damage_taken1))))
            self.health_bar2 = Rect((1241, (21 + (2 * self.damage_taken2))), (20, (200 - (2 * self.damage_taken2))))
            pygame.draw.rect(GL.SCREEN, YELLOW, self.health_bar1)
            pygame.draw.rect(GL.SCREEN, YELLOW, self.health_bar2)

            # energy bars
            GL.SCREEN.blit(self.energy_bar_outline, (5, 280))
            GL.SCREEN.blit(self.energy_bar_outline2, (1239, 280))

            # dynamic energy bars
            self.energy_used1 = 10 - self.player1.energy
            self.energy_used2 = 10 - self.player2.energy
            self.energy_bar1 = Rect((20, 281 + (20 * self.energy_used1)), (20, 200 - (20 * self.energy_used1)))
            self.energy_bar2 = Rect((1241, 281 + (20 * self.energy_used2)), (20, 200 - (20 * self.energy_used2)))
            pygame.draw.rect(GL.SCREEN, GREEN, self.energy_bar1)
            pygame.draw.rect(GL.SCREEN, GREEN, self.energy_bar2)

            skill_ids = self.player1.skills + self.player2.skills
            for i, skill_box in enumerate(self.skill_boxes):
                pygame.draw.rect(GL.SCREEN, skill_box.color, skill_box)

                # If icon picture exists
                if skill_ids[i] in ICONS_TABLE.keys():
                    # Draw picture
                    GL.SCREEN.blit(GL.WHITE_BACKGROUND, (skill_box.left, skill_box.top))
                    GL.SCREEN.blit(ICONS_TABLE[skill_ids[i]], (skill_box.left, skill_box.top))
                    # Draw energy text
                # otherwise
                else:
                    skill_text = str(SKILLS_TABLE[skill_ids[i]]['name'])
                    skill_font = self.debug_font_small_2.render(skill_text, True, WHITE)
                    skill_text_xy = font_position_center(skill_box, self.debug_font_small_2, skill_text)
                    GL.SCREEN.blit(skill_font, skill_text_xy)

                if i < 5:
                    if self.player1.energy < SKILLS_TABLE[skill_ids[i]]['energy']:
                        GL.SCREEN.blit(GL.RED_MASK, (skill_box.left, skill_box.top))
                else:
                    if self.player2.energy < SKILLS_TABLE[skill_ids[i]]['energy']:
                        GL.SCREEN.blit(GL.RED_MASK, (skill_box.left, skill_box.top))

            self.return_button.draw(GL.SCREEN)

        def _draw_timer():
            time_display = self.timer_font.render(str(self.game_time), True, BLUE)
            GL.SCREEN.blit(time_display, self.timer_font_xy)

        def _draw_arena():
            for rect in self.arena:
                if rect.color is not None:
                    pygame.draw.rect(GL.SCREEN, rect.color, rect)

        def _draw_players():
            def _draw_player(p):
                # Draw player using wait_frames and animation_key
                # wait_frames = frames waited before key is incremented
                # animation_key = index for the sprite list

                # Draw player 1
                if p.state != p.previous_state:
                    p.wait_frames = 0
                    p.animation_key = -1
                    # -1 because it will always get incremented at the start of each check
                flip = False  # value for flipping sprite

                if p.state == DEATH:
                    if p.facing_direction == LEFT:
                        flip = True
                    if p.wait_frames <= 0:
                        p.wait_frames = 3
                        if p.animation_key < 3:
                            p.animation_key += 1
                    if flip:
                        GL.SCREEN.blit(pygame.transform.flip(p.sprite[p.animation_key + 70], flip, False), (p.left - 17 - 64, p.top - 22))
                    else:
                        GL.SCREEN.blit(pygame.transform.flip(p.sprite[p.animation_key + 70], flip, False), (p.left - 17, p.top - 22))

                # elif p.state = WIN:

                elif p.state == ATTACK or p.state == RESET:
                    # Starting Indexes and how much sprites for each attack state are as follows
                    # ONEHAND = 28, 4
                    # TWOHAND = 32, 4
                    # CAST1 = 36, 3
                    # CAST2 = 39, 4
                    # CAST3 = 43, 1
                    # THROW = 44, 4
                    # MACHGUN = 52, 2
                    # BREATH = 54, 3
                    # POKE = 57, 4
                    # BULLET = 61, 4
                    # DASH = 7, 1
                    # RUN = 8, 16

                    if p.facing_direction == LEFT:
                        flip = True

                    if p.attack_state == 'RUN':
                        if p.wait_frames <= 0:
                            p.wait_frames = 2
                            p.animation_key = (p.animation_key + 1) % 16
                        GL.SCREEN.blit(pygame.transform.flip(p.sprite[p.animation_key + 8], flip, False), (p.left - 17, p.top - 22))
                    elif p.attack_state == 'none':
                        p.wait_frames = 1
                    else:
                        if p.wait_frames <= 0:
                            p.wait_frames = p.attack_frame
                            if p.animation_key < \
                                    PL_ATTACK_TABLE[p.attack_state][1]:
                                p.animation_key += 1
                        GL.SCREEN.blit(pygame.transform.flip(p.sprite[p.animation_key + PL_ATTACK_TABLE[p.attack_state][0]], flip, False), (p.left - 17, p.top - 22))

                # JUMP
                elif p.state == JUMP:
                    if p.facing_direction == LEFT:
                        flip = True
                    if p.wait_frames <= 0:
                        p.wait_frames = 5
                        if p.animation_key <= 0:
                            p.animation_key += 1
                    GL.SCREEN.blit(pygame.transform.flip(p.sprite[p.animation_key + 24], flip, False), (p.left - 17, p.top - 22))

                # FALL
                elif p.state == FALL:
                    if p.facing_direction == LEFT:
                        flip = True
                    if p.wait_frames <= 0:
                        p.wait_frames = 5
                        if p.animation_key <= 0:
                            p.animation_key += 1
                    GL.SCREEN.blit(pygame.transform.flip(p.sprite[p.animation_key + 26], flip, False), (p.left - 17, p.top - 22))

                # WALK
                elif p.state == RWALK or p.state == LWALK:
                    if p.facing_direction == LEFT:
                        flip = True
                    if p.state == RWALK and p.previous_state != RWALK:
                        p.animation_key = -8  # Transition sprites loaded before walk
                    elif p.state == LWALK and p.previous_state != LWALK:
                        p.animation_key = -8
                    if p.wait_frames <= 0:
                        p.wait_frames = 2
                        p.animation_key += 1
                        if p.animation_key > 0:
                            p.animation_key %= 16  # Loops the key
                    GL.SCREEN.blit(pygame.transform.flip(p.sprite[p.animation_key + 8], flip, False), (p.left - 17, p.top - 22))

                # STAND (default animation)
                else:
                    if p.facing_direction == LEFT:
                        flip = True
                    # Currently only have 1 standing sprite
                    GL.SCREEN.blit(pygame.transform.flip(p.sprite[p.animation_key + 1], flip, False), (p.left - 17, p.top - 22))
                p.wait_frames += -1

            if self.player1.sprite is not None:
                _draw_player(self.player1)
            if self.player2.sprite is not None:
                _draw_player(self.player2)

            # If player is above screen
            for p in [self.player1, self.player2]:
                if p.bottom < 0:
                    text = 'P1: ' if p.id == 1 else 'P2: '
                    text2 = str(p.bottom)
                    color = BLUE if p.id == 1 else GREEN
                    v1 = (p.centerx, 5)
                    v2 = (p.centerx - 10, 30)
                    v3 = (p.centerx + 10, 30)
                    vlist = [v1, v2, v3]

                    GL.SCREEN.blit(self.oor_font.render(text, True, color), (p.centerx - 20, 40))
                    GL.SCREEN.blit(self.st_dmg_font.render(text2, True, color), (p.centerx + 10, 40))
                    pygame.draw.polygon(GL.SCREEN, color, vlist)

        def _draw_monsters():
            for m in self.active_monsters:
                if m.kind == WEAK:
                    GL.SCREEN.blit(self.weak_monster_image, m.topleft)
                elif m.kind == MEDIUM:
                    GL.SCREEN.blit(self.medium_monster_image, m.topleft)
                elif m.kind == ULTIMATE:
                    GL.SCREEN.blit(self.ultimate_monster_image, m.topleft)
                health_bar = Rect2(left=m.left, top=m.top - 8, width=m.width, height=6)
                health_bar_width = round(m.width * (m.hit_points / m.hit_points_max))
                health_bar_life = Rect2(left=m.left, top=m.top - 8, width=health_bar_width, height=6)

                pygame.draw.rect(GL.SCREEN, WHITE, health_bar)
                pygame.draw.rect(GL.SCREEN, RED, health_bar_life)
                pygame.draw.rect(GL.SCREEN, BLACK, health_bar, 1)

        def _draw_dropped_skills():
            for skill in self.arena.dropped_skills:
                pygame.draw.rect(GL.SCREEN, skill.color, skill)
                if skill.id not in ICONS_TABLE.keys():
                    skill_text = str(skill.id)
                    skill_font = self.debug_font_small_2.render(skill_text, True, WHITE)
                    skill_text_xy = font_position_center(skill, self.debug_font_small_2, skill_text)
                    GL.SCREEN.blit(skill_font, skill_text_xy)
                else:
                    icon = ICONS_TABLE[skill.id]
                    icon = pygame.transform.scale(icon, (20, 20))
                    GL.SCREEN.blit(icon, (skill[0] + 2.5, skill[1] + 2.5))

        def _draw_particles():
            for p in self.active_particles:
                if isinstance(p, FieldParticle):
                    pygame.draw.circle(GL.SCREEN, p.color, (p.centerx, p.centery), p.radius, 1)
                else:
                    # If icon art exists
                    if p.sid in PARTICLES_TABLE.keys():
                        pimg = PARTICLES_TABLE[p.sid]
                        if p.direction == LEFT:
                            pimg = pygame.transform.flip(pimg, True, False)

                        # melee rotate
                        if isinstance(p, MeleeParticle):
                            if p.direction == LEFT:
                                pimg = pygame.transform.rotate(pimg, math.degrees(-1 * p.progress))
                            else:
                                pimg = pygame.transform.rotate(pimg, math.degrees(p.progress))

                        # Special rotate cases
                        elif p.sid in [5, 112, 123, 125, 'beehive']:
                            if 'rotator' not in p.__dict__.keys():
                                p.rotator = 0
                            else:
                                p.rotator += 10
                            pimg = pygame.transform.rotate(pimg, p.rotator)
                        GL.SCREEN.blit(pimg, (p.left, p.top))

                    # no particle
                    else:
                        pygame.draw.rect(GL.SCREEN, p.color, p)

        def _draw_scrolling_text():
            for unit in self.active_monsters + [self.player1, self.player2]:
                for i, t in enumerate(unit.st_buffer):
                    if t[2] < 0:
                        unit.st_buffer.append((t[0], t[1], t[2] + self.game_time.msec + 2000))
                        unit.st_buffer.remove(t)
                        continue
                    # Damage scrolling text
                    if t[0] == ST_DMG:
                        text = '-' + str(int(t[1]))
                        color = RED

                        GL.SCREEN.blit(self.st_dmg_font.render(text, True, color),
                                       (unit.centerx + 30, unit.top - (3000 - t[2] + self.game_time.msec) / 50))
                    # Health Gain text
                    elif t[0] == ST_HP:
                        text = '+' + str(int(t[1]))
                        color = GREEN
                        GL.SCREEN.blit(self.st_dmg_font.render(text, True, color),
                                       (unit.centerx + 30, unit.top - (3000 - t[2] + self.game_time.msec) / 50))
                    # Level up scrolling text
                    elif t[0] == ST_LEVEL_UP:
                        text = t[1]
                        color = YELLOW
                        GL.SCREEN.blit(self.st_level_up_font.render(text, True, color),
                                       (unit.centerx - 50, unit.top - (4000 - t[2] + self.game_time.msec) / 50))
                    # Energy gain text
                    elif t[0] == ST_ENERGY:
                        text = str(t[1])
                        color = PURPLE
                        GL.SCREEN.blit(self.st_energy_font.render(text, True, color),
                                       (unit.centerx, unit.top - (3000 - t[2] + self.game_time.msec) / 50))
                    if t[2] <= self.game_time.msec:
                        unit.st_buffer.remove(t)

                # Condition scrolling text
                # Process list
                print_list = []
                for k, vl in unit.conditions.items():
                    # ignore dot
                    if k != DOT:
                        if unit.conditions[k] and k == SHIELD:
                            sum_mag = 0
                            max_duration = 0
                            for sh in unit.conditions[k]:
                                sum_mag += sh.magnitude
                                max_duration = max(max_duration, int((sh.duration - self.game_time.msec + sh.start) / 1000))
                            print_list.append((GREEN, SHIELD + '(' + str(sum_mag) + '):' + str(max_duration)))
                        elif unit.conditions[k]:
                            max_duration = 0
                            for c in unit.conditions[k]:
                                max_duration = max(max_duration, int((c.duration - self.game_time.msec + c.start) / 1000))
                            color = GREEN if k in BUFFS else RED
                            print_list.append((color, k + ':' + str(max_duration)))
                # Print list
                for i, v in enumerate(print_list):
                    GL.SCREEN.blit(self.st_condition_font.render(v[1], True, v[0]), (unit.centerx - 70, unit.top - 20 - (15 * i)))

        def _draw_rain():
            if self.make_rain:
                for i in range(5, self.arena.play_area_rect.width, 10):
                    rain_copy = self.rain.copy()
                    rain_copy.left = i + self.arena.play_area_rect.left
                    self.rain_particles.append(rain_copy)

            for r in self.rain_particles:
                r.move_ip((0, 5))
                pygame.draw.rect(GL.SCREEN, BLUE, r)

            for r in self.rain_particles[:]:
                if r.top > self.arena.play_area_rect.height:
                    self.rain_particles.remove(r)
            self.make_rain = False

        _draw_ui1()
        _draw_arena()
        _draw_monsters()
        _draw_dropped_skills()
        if not GL.INPUT1.DEBUG_MODE_ON:
            _draw_players()
        _draw_particles()
        _draw_scrolling_text()
        _draw_ui2()
        _draw_timer()
        # _draw_rain()

    # -------------------------------------------------------------------------
    def draw_debug(self):

        def _draw_spawn_point_rects():
            for rect in self.arena.spawn_points:
                pygame.draw.rect(GL.SCREEN, RED, rect)

        def _draw_play_area_debug_border():
            old_play_area = Rect2(65, 0, 1150, 475)
            pygame.draw.rect(GL.SCREEN, YELLOW, old_play_area, 1)
            pygame.draw.rect(GL.SCREEN, GREEN, self.arena.play_area_rect, 1)
            pygame.draw.rect(GL.SCREEN, RED, self.arena.left_wall, 1)
            pygame.draw.rect(GL.SCREEN, RED, self.arena.floor, 1)
            pygame.draw.rect(GL.SCREEN, RED, self.arena.right_wall, 1)

        def _draw_debug_text():
            x = '| x:{:>8.2f}|'.format(self.player1.x)
            y = '| y:{:>8.2f}|'.format(self.player1.y)
            dx = '|dx:{:>8.2f}|'.format(self.player1.dx)
            dy = '|dy:{:>8.2f}|'.format(self.player1.dy)
            debug_font_1 = self.debug_font.render(x, True, GREEN)
            debug_font_2 = self.debug_font.render(y, True, GREEN)
            debug_font_3 = self.debug_font.render(dx, True, GREEN)
            debug_font_4 = self.debug_font.render(dy, True, GREEN)
            GL.SCREEN.blit(debug_font_1, self.debug_font_xy1)
            GL.SCREEN.blit(debug_font_2, self.debug_font_xy2)
            GL.SCREEN.blit(debug_font_3, self.debug_font_xy3)
            GL.SCREEN.blit(debug_font_4, self.debug_font_xy4)

            num_monsters = '|curr num monsters:{:>4}|'.format(len(self.active_monsters))
            max_monsters = '| max num monsters:{:>4}|'.format(self.arena.max_monsters)
            debug_font_m1 = self.debug_font.render(num_monsters, True, GREEN)
            debug_font_m2 = self.debug_font.render(max_monsters, True, GREEN)
            GL.SCREEN.blit(debug_font_m1, self.debug_font_xy5)
            GL.SCREEN.blit(debug_font_m2, self.debug_font_xy6)

        def _draw_cpu_usage():
            cpu_text = '|CPU Utilization:{:>5.1f}%|'.format(self.cpu_avg) if psutil_found else '|CPU Utilization:  ????|'
            cpu_font = self.debug_font.render(cpu_text, True, RED)
            GL.SCREEN.blit(cpu_font, self.debug_font_xy7)

        def _draw_destructible_terrain_debug_text():
            for rect in self.arena.destructible_terrain:
                rendered_debug_font = self.debug_font_small_2.render(str(rect.hits_to_destroy), True, BLACK)
                pos = font_position_center(rect, self.debug_font_small_2, str(rect.hits_to_destroy))
                GL.SCREEN.blit(rendered_debug_font, pos)

        def _draw_mouse_text():
            mouse_pos = pygame.mouse.get_pos()
            play_area_mouse_pos = mouse_pos[0] - self.arena.play_area_rect.left, mouse_pos[1]
            pygame.draw.circle(GL.SCREEN, WHITE, mouse_pos, 2, 0)
            pygame.draw.circle(GL.SCREEN, BLACK, mouse_pos, 2, 1)
            if 0 <= play_area_mouse_pos[0] <= self.arena.play_area_rect.width and 0 <= play_area_mouse_pos[1] <= self.arena.play_area_rect.height:
                offset_pos_mouse_font = self.debug_font_small.render(str(play_area_mouse_pos), True, DGREY)
                GL.SCREEN.blit(offset_pos_mouse_font, mouse_pos)
            real_pos_mouse_font = self.debug_font_small.render(str(mouse_pos), True, DKYELLOW)
            GL.SCREEN.blit(real_pos_mouse_font, (mouse_pos[0] + 3, mouse_pos[1] + 10))

        def _draw_players_debug(draw_p1=True, draw_p2=True):

            def _draw_player_debug(p, c1, c2):
                pygame.draw.rect(GL.SCREEN, c1, p)
                eye = Rect2(topleft=p.topleft, size=(5, 5))
                if p.facing_direction == LEFT:
                    eye.topleft = p.topleft
                    eye.move_ip((+3, 3))
                else:
                    eye.topright = p.topright
                    eye.move_ip((-3, 3))
                pygame.draw.rect(GL.SCREEN, c2, eye)

            if draw_p1:
                _draw_player_debug(self.player1, DKRED, LBLUE)
            if draw_p2:
                _draw_player_debug(self.player2, LBLUE, DKRED)

        def _draw_player_collision_points_for_debugging():
            coll_data = get_collision_data(self.player1, self.arena)
            locs = []
            for terr, pt, side in coll_data:
                if pt.L: locs.append(self.player1.midleft)
                if pt.R: locs.append(self.player1.midright)
                if pt.T: locs.append(self.player1.midtop)
                if pt.B: locs.append(self.player1.midbottom)
                if pt.TL: locs.append(self.player1.topleft)
                if pt.TR: locs.append(self.player1.topright)
                if pt.BR: locs.append(self.player1.bottomright)
                if pt.BL: locs.append(self.player1.bottomleft)
                if locs:  # True if not empty list
                    pygame.draw.circle(GL.SCREEN, ORANGE, self.player1.center, 5, 0)
                for l in locs:
                    pygame.draw.circle(GL.SCREEN, ORANGE, l, 3, 0)

        if GL.INPUT1.DEBUG_MODE_ON:
            _draw_spawn_point_rects()
            _draw_play_area_debug_border()
            _draw_debug_text()
            _draw_cpu_usage()
            _draw_destructible_terrain_debug_text()
            _draw_players_debug()
            _draw_player_collision_points_for_debugging()
            _draw_mouse_text()
        elif not GL.INPUT1.DEBUG_MODE_ON:
            if self.player1.sprite is None:
                _draw_players_debug(draw_p1=True, draw_p2=False)
            if self.player2.sprite is None:
                _draw_players_debug(draw_p1=False, draw_p2=True)

    # -------------------------------------------------------------------------
    def handle_event_queue(self):

        def _handle_song_end_event():
            for event in pygame.event.get(SONG_END_EVENT):
                if event.type == SONG_END_EVENT:
                    print('the song ended!')
                    AUDIO.play_next_random_song()

        def _handle_return_to_main_menu_from_click():
            for event in pygame.event.get():
                if 'click' in self.return_button.handleEvent(event):
                    self.return_now = True
                    GL.NEXT_PAGE = '_start'

        def _handle_time_tick_event():
            for event in pygame.event.get(TIME_TICK_EVENT):
                if event.type == TIME_TICK_EVENT:
                    self.game_time.inc()

                    # for CPU usage debug text
                    if psutil_found and GL.INPUT1.DEBUG_MODE_ON:
                        new_cpu = psutil.cpu_percent(interval=None)
                        self.cpu_deque.append(new_cpu)
                        self.cpu_avg = sum(self.cpu_deque) / len(self.cpu_deque)

                    # Player 1 conditions
                    for k, v in self.player1.conditions.items():
                        for e in v:
                            if e.is_expired(self.game_time.msec):
                                self.player1.conditions[k].remove(e)

                    # Player 2 conditions
                    for k, v in self.player2.conditions.items():
                        for e in v:
                            if e.is_expired(self.game_time.msec):
                                self.player2.conditions[k].remove(e)

                    # Monster conditions
                    for m in self.active_monsters:
                        for k, v in m.conditions.items():
                            for e in v:
                                if e.is_expired(self.game_time.msec):
                                    m.conditions[k].remove(e)

        def _handle_regeneration_event():
            for event in pygame.event.get(REGENERATION_EVENT):
                if event.type == REGENERATION_EVENT:
                    # Player 1
                    if self.player1.hit_points > 0:
                        if self.player1.conditions[WOUNDED] and not self.player1.conditions[INVIGORATED]:
                            self.player1.hit_points += self.player1.level / 20
                        elif not self.player1.conditions[WOUNDED] and self.player1.conditions[INVIGORATED]:
                            self.player1.hit_points += self.player1.level / 5
                        else:
                            self.player1.hit_points += self.player1.level / 10
                        if self.player1.hit_points > 100:
                            self.player1.hit_points = 100

                        if self.player1.conditions[WEAKENED] and not self.player1.conditions[EMPOWERED]:
                            self.player1.energy += self.player1.level / 10
                        elif not self.player1.conditions[WEAKENED] and self.player1.conditions[EMPOWERED]:
                            self.player1.energy += self.player1.level / 2.5
                        else:
                            self.player1.energy += self.player1.level / 5
                        if self.player1.energy > 10:
                            self.player1.energy = 10
                    # Player 2
                    if self.player2.hit_points > 0:
                        if self.player2.conditions[WOUNDED] and not self.player2.conditions[INVIGORATED]:
                            self.player2.hit_points += self.player2.level / 20
                        elif not self.player2.conditions[WOUNDED] and self.player2.conditions[INVIGORATED]:
                            self.player2.hit_points += self.player2.level / 5
                        else:
                            self.player2.hit_points += self.player2.level / 10
                        if self.player2.hit_points > 100:
                            self.player2.hit_points = 100

                        if self.player2.conditions[WEAKENED] and not self.player2.conditions[EMPOWERED]:
                            self.player2.energy += self.player2.level / 10
                        elif not self.player2.conditions[WEAKENED] and self.player2.conditions[EMPOWERED]:
                            self.player2.energy += self.player2.level / 2.5
                        else:
                            self.player2.energy += self.player2.level / 5
                        if self.player2.energy > 10:
                            self.player2.energy = 10

        def _handle_player_lock_events():
            # player 1 skill lock timer
            for event in pygame.event.get(PLAYER1_LOCK_EVENT):
                if event.type == PLAYER1_LOCK_EVENT:
                    self.player1.attack_cooldown_expired = True
                    pygame.time.set_timer(PLAYER1_LOCK_EVENT, 0)
            # player 2 skill lock timer
            for event in pygame.event.get(PLAYER2_LOCK_EVENT):
                if event.type == PLAYER2_LOCK_EVENT:
                    self.player2.attack_cooldown_expired = True
                    pygame.time.set_timer(PLAYER2_LOCK_EVENT, 0)

        def _handle_player_pickup_skill_events():
            for event in pygame.event.get(PLAYER1_PICKUP_EVENT):
                if event.type == PLAYER1_PICKUP_EVENT:
                    self.player1.pickup_time += 1
                    pygame.time.set_timer(PLAYER1_PICKUP_EVENT, 0)

            for event in pygame.event.get(PLAYER2_PICKUP_EVENT):
                if event.type == PLAYER2_PICKUP_EVENT:
                    self.player2.pickup_time += 1
                    pygame.time.set_timer(PLAYER2_PICKUP_EVENT, 0)

        def _handle_rain_event():
            for event in pygame.event.get(MORE_RAIN_EVENT):
                if event.type == MORE_RAIN_EVENT:
                    self.make_rain = True
                    pygame.time.set_timer(MORE_RAIN_EVENT, 150)

        def _handle_monster_spawn_event():
            for event in pygame.event.get(MONSTER_SPAWN_EVENT):
                if event.type == MONSTER_SPAWN_EVENT:
                    self.spawn_monsters = True
                    pygame.time.set_timer(MONSTER_SPAWN_EVENT, 10000)

        def _handle_quit_event():
            for event in pygame.event.get(QUIT):
                if event.type == QUIT:
                    EXIT_GAME()

        if not GL.INPUT1.START_EVENT:
            _handle_song_end_event()
            _handle_time_tick_event()
            _handle_regeneration_event()
            _handle_player_lock_events()
            _handle_player_pickup_skill_events()
            _handle_rain_event()
            _handle_monster_spawn_event()
            _handle_quit_event()
            _handle_return_to_main_menu_from_click()
        else:
            _handle_quit_event()
            GL.INPUT1.refresh_during_pause()
            pygame.event.clear()

    # ----------------------------------------------------------------------------
    def check_if_game_over(self):
        if self.player1.is_dead() or self.player2.is_dead():
            self.return_now = True
            GL.NEXT_PAGE = '_game_over'

# ----------------------------------------------------------------------------

if __name__ == '__main__':
    Application()
