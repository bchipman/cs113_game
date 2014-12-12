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

# set window starting position for my desktop which has multiple monitors, this
# is a convenience thing for me.  You guys can add your own setting here if
# it's useful for you
if os.environ['COMPUTERNAME'] == 'BRIAN-DESKTOP':
    os.environ['SDL_VIDEO_WINDOW_POS'] = '{},{}'.format(1920, 90)
if os.environ['COMPUTERNAME'] == 'MAX-LT':
    os.environ['SDL_VIDEO_WINDOW_POS'] = '{},{}'.format(50, 30)

# -------------------------------------------------------------------------
class StartMenu:
    def __init__(self):
        def _setup_display():
            pygame.display.set_mode((1280, 600))
            pygame.display.set_caption('Famished Tournament')
            self.screen = pygame.display.get_surface()
            self.start_button = PygButton((325, 395, 140, 40), 'Start')
            self.help_button = PygButton((485, 395, 110, 40), 'Help')
            self.options_button = PygButton((615, 395, 175, 40), 'Options')
            self.exit_button = PygButton((810, 395, 105, 40), 'Exit')

        def _setup_music():
            AUDIO.turn_on_music()

        def _setup_time():
            self.clock = pygame.time.Clock()
            self.fps = 5

        def _setup_input():
            self.input = Input(inside_menu=True)

        pygame.init()
        _setup_display()
        _setup_music()
        _setup_time()
        _setup_input()

    def __call__(self, restart_music=False):
        if restart_music:
            AUDIO.restart_music()
        while True:
            self.input.refresh()
            self.draw_UI()
            self.handle_events()
            self.clock.tick(self.fps)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if 'click' in self.start_button.handleEvent(event):
                GameLoop(self)()
            if 'click' in self.exit_button.handleEvent(event):
                pygame.quit()
                sys.exit()
            if 'click' in self.help_button.handleEvent(event):
                HelpPage(self)()
            if 'click' in self.options_button.handleEvent(event):
                OptionsPage(self)()
            if self.input.ENTER_LEAVE:
                self.input.ENTER_LEAVE = False
                GameLoop(self)()

    def draw_UI(self):
        self.image = pygame.image.load('data/temp_start_bkg.png')
        self.screen.blit(self.image, (0, 0))

        self.start_button.draw(self.screen)
        self.help_button.draw(self.screen)
        self.options_button.draw(self.screen)
        self.exit_button.draw(self.screen)

        self.title_font = pygame.font.Font('data/Kremlin.ttf', 50)
        self.title1 = self.title_font.render('Famished', True, DKRED)
        self.title2 = self.title_font.render('Tournament', True, DKRED)
        self.screen.blit(self.title1, (495, 120))
        self.screen.blit(self.title2, (450, 175))

        # text for transparent buttons
        # self.button_font = pygame.font.Font('data/Kremlin.ttf', 30)
        # self.b_start = self.button_font.render('Start', True, DKRED)
        # self.b_help = self.button_font.render('Help', True, DKRED)
        # self.b_options = self.button_font.render('Options', True, DKRED)
        # self.b_exit = self. button_font.render('Exit', True, DKRED)
        # self.screen.blit(self.b_start, (340, 400))
        # self.screen.blit(self.b_help, (500, 400))
        # self.screen.blit(self.b_options, (630, 400))
        # self.screen.blit(self.b_exit, (845, 400))

        pygame.display.flip()

# -------------------------------------------------------------------------
class GameLoop:
    def __init__(self, start_menu):
        def _setup_display():
            # set the window size - can add the NOFRAME arg if we don't want a
            # window frame but then we have to figure out how to move the
            # window since it won't have a menu bar to grab
            self.screen = pygame.display.set_mode((1280, 600))
            pygame.display.set_caption('Famished Tournament')
            self.surface = pygame.display.get_surface()
            # main menu button at bottom middle of screen
            self.return_button = pygbutton.PygButton((490, 550, 300, 50), 'Main Menu')

        def _setup_time():
            self.clock = pygame.time.Clock()
            self.fps = 30
            pygame.time.set_timer(TIME_TICK_EVENT, 250)
            pygame.time.set_timer(REGENERATION_EVENT, 1000)
            self.game_time = GameTime()

        def _setup_ui():
            self.start_menu = start_menu
            self.window = self.surface.get_rect()
            self.window_border = Rect2(left=0, top=0, width=1280, height=600)
            self.play_area_border = Rect2(left=60, top=0, width=1160, height=485)
            self.left_grey_fill = Rect2(left=0, top=0, width=65, height=600)
            self.right_grey_fill = Rect2(left=1215, top=0, width=60, height=600)
            self.bottom_grey_fill = Rect2(left=0, top=475, width=1280, height=115)

        def _setup_arena():
            self.arena = Arena(random.choice((arena3, arena4, arena5)))
            GL.arena_in_use = self.arena  # used for out_of_arena_fix within global.py

        def _setup_fonts():
            # main_font = 'data/viner-hand-itc.ttf'
            main_font = 'data/Kremlin.ttf'
            self.timer_font = pygame.font.Font(main_font, 36)
            self.timer_font_xy = 605, 500
            self.health_font = pygame.font.Font(main_font, 55)
            self.health_font_xy = 60, 490
            self.energy_font = pygame.font.Font(main_font, 55)
            self.energy_font_xy = 80, 535
            self.pause_font = pygame.font.Font(main_font, 200)
            self.pause_font_xy = font_position_center(self.window, self.pause_font, '-PAUSE-')
            self.debug_font_small = pygame.font.SysFont('consolas', 10)  # monospace
            self.debug_font_small_2 = pygame.font.SysFont('lucidasans', 12)  # monospace
            self.debug_font = pygame.font.SysFont('consolas', 20)  # monospace
            self.debug_font_xy1 = 1075, 505
            self.debug_font_xy2 = 1075, 520
            self.debug_font_xy3 = 1075, 540
            self.debug_font_xy4 = 1075, 560
            self.debug_font_xy5 = 800, 505
            self.debug_font_xy6 = 800, 520
            self.debug_font_xy7 = 800, 540
            self.st_font = pygame.font.Font(main_font, 18)  # Scrolling text font
            self.cpu_avg = 0.0
            self.cpu_deque = deque((0,), maxlen=5)

        def _setup_particles():
            self.active_particles = []

        def _setup_monsters():
            self.active_monsters = []
            self.dropped_skills = []
            self.spawn_monsters = False
            pygame.event.post(pygame.event.Event(MONSTER_SPAWN_EVENT))

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
                # Put spritesheet into list, each sprite is 64x64 pixels large
                for num in range(1, 7):  # Standing
                    m1.append(spritesheet1.subsurface((64 * (num - 1), 0, 64, 64)))
                for num in range(7, 15):  # Walk Transition
                    m1.append(spritesheet1.subsurface((64 * (num - 7), 64, 64, 64)))
                for num in range(15, 23):  # Walk Part 1
                    m1.append(spritesheet1.subsurface((64 * (num - 15), 128, 64, 64)))
                for num in range(23, 31):  # Walk Part 2
                    m1.append(spritesheet1.subsurface((64 * (num - 23), 192, 64, 64)))
                for num in range(31, 35):  # Jump and Fall
                    m1.append(spritesheet1.subsurface((64 * (num - 31), 256, 64, 64)))

                for num in range(len(m1)):
                    m1[num].set_colorkey((0, 0, 0))  # sprite bg rgb is (0,0,0)
                    m1[num] = m1[num].convert_alpha()

                return m1

            p1_sprite = _setup_player_sprites('data/p1_human_8bit.png')
            p2_sprite = _setup_player_sprites('data/p2_human_8bit.png')

            self.player1 = Player(id=1, topleft=self.arena.p1_spawn, size=(30, 40), sprite=p1_sprite)
            self.player2 = Player(id=2, topleft=self.arena.p2_spawn, size=(30, 40), sprite=p2_sprite)

            self.player1.hit_points = 20  # FOR TESTING/DEBUGGING, REMOVE LATER

            self.player1.opposite = self.player2  # Makes things a lot easier
            self.player2.opposite = self.player1  # Makes things a lot easier

        def _setup_skill_boxes():
            self.skill_boxes = [
                # player 1 skill boxes
                Rect2(topleft=(90, 500), size=(40, 40), color=BLACK),
                Rect2(topleft=(140, 500), size=(40, 40), color=BLACK),
                Rect2(topleft=(190, 500), size=(40, 40), color=BLACK),
                Rect2(topleft=(240, 500), size=(40, 40), color=BLACK),
                Rect2(topleft=(290, 500), size=(40, 40), color=BLACK),
                # player 2 skill boxes
                Rect2(topleft=(950, 500), size=(40, 40), color=DKRED),
                Rect2(topleft=(1000, 500), size=(40, 40), color=DKRED),
                Rect2(topleft=(1050, 500), size=(40, 40), color=DKRED),
                Rect2(topleft=(1100, 500), size=(40, 40), color=DKRED),
                Rect2(topleft=(1150, 500), size=(40, 40), color=DKRED), ]

        pygame.init()
        _setup_display()
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
        _setup_skill_boxes()

    # ------------------------------------------------------------------------
    def __call__(self):
        while True:
            if not self.player1.input.PAUSED:
                self.handle_players_inputs()
                self.handle_monsters()
                self.handle_particles()
                self.draw_screen()
                self.draw_debug()
                pygame.display.update()
                self.handle_event_queue()
                self.clock.tick(self.fps)
            else:
                self.handle_players_inputs()
                self.handle_event_queue()

    # -------------------------------------------------------------------------
    def handle_players_inputs(self):

        def _refresh_inputs():
            self.player1.input.refresh()
            self.player2.input.refresh()

        def _handle_players_inputs():
            if not self.player1.input.PAUSED:
                self.player1(self.arena)
                self.player2(self.arena, self.player1.input)

        def _handle_special_input():
            if self.player1.input.PAUSED:
                rendered_font = self.pause_font.render('-PAUSE-', True, RED)
                self.surface.blit(rendered_font, self.pause_font_xy)
                pygame.display.update()

            if self.player1.input.RESPAWN and not self.player1.input.PAUSED:
                self.player1.topleft = self.player1.topleft_initial
                self.player1.dx = self.player1.dx_initial
                self.player1.facing_direction = self.player1.facing_direction_initial
                self.player2.topleft = self.player2.topleft_initial
                self.player2.dx = self.player2.dx_initial
                self.player2.facing_direction = self.player2.facing_direction_initial

            if self.player1.input.KILLALL and not self.player1.input.PAUSED:
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
                        self.active_particles.append(p)
                else:
                    self.active_particles.append(self.player1.new_particle)
                self.player1.new_particle = None

            if self.player2.new_particle:
                if isinstance(self.player2.new_particle, list):
                    for p in self.player2.new_particle:
                        self.active_particles.append(p)
                else:
                    self.active_particles.append(self.player2.new_particle)
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
    def handle_monsters(self):

        def _handle_monster_spawning():
            if self.spawn_monsters and len(self.active_monsters) < self.arena.max_monsters:
                spawn_point = self.arena.random_spawn_point  # pick a random spawn point
                color = random.choice((LLBLUE, DKYELLOW, DKPURPLE, DKORANGE))  # pick a random color
                monster_info = MONSTER_TABLE[random.choice(self.arena.possible_monsters)]  # pick a random monster
                self.active_monsters.append(Monster(monster_info, spawn_point.topleft, self.player1, self.player2, color))
            self.spawn_monsters = False

        def _handle_dead_monsters():
            for m in self.active_monsters:
                if m.is_dead():
                    dropped_skill_id = get_dropped_skill(m)
                    dropped_skill_rect = Rect2(topleft=m.topleft, size=(25, 25), id=dropped_skill_id, color=BLACK)
                    self.arena.dropped_skills.append(dropped_skill_rect)
                    self.active_monsters.remove(m)

        def _update_monsters():
            for m in self.active_monsters:
                m(self.game_time.msec, self.arena)

        _handle_monster_spawning()
        _handle_dead_monsters()
        _update_monsters()

    # -------------------------------------------------------------------------
    def draw_screen(self):
    
        def _draw_ui1():
            self.surface.fill(DGREY)
            if self.arena.background is not None:
                self.image = pygame.image.load(self.arena.background)
                self.screen.blit(self.image, (self.arena.play_area_rect.left, 0))
            

        def _draw_ui2():
            pygame.draw.rect(self.surface, DGREY, self.left_grey_fill)
            pygame.draw.rect(self.surface, DGREY, self.right_grey_fill)
            pygame.draw.rect(self.surface, DGREY, self.bottom_grey_fill)


            # font for player's health and energy
            # health_display = self.health_font.render(str(self.player1.hit_points), True, RED)
            # energy_display = self.energy_font.render(str(int(self.player1.energy)), True, YELLOW)
            # self.surface.blit(health_display, self.health_font_xy)
            # self.surface.blit(energy_display, self.energy_font_xy)

            # health bars
            # currently only goes off of one player's health
            # left health bar outline image
            self.health_bar_outline = pygame.image.load('data/health_bar_outline.png')
            self.surface.blit(self.health_bar_outline, (5, 20))
            self.health_bar_outline2 = pygame.image.load('data/health_bar_outline2.png')
            self.surface.blit(self.health_bar_outline2, (1239, 20))
            # right health bar outline image
            # dynamic health bars
            self.damage_taken1 = self.player1.hit_points_max - self.player1.hit_points
            self.damage_taken2 = self.player2.hit_points_max - self.player2.hit_points
            self.health_bar1 = Rect((20, (21 + (2 * self.damage_taken1))), (20, (200 - (2 * self.damage_taken1))))
            self.health_bar2 = Rect((1241, (21 + (2 * self.damage_taken2))), (20, (200 - (2 * self.damage_taken2))))
            pygame.draw.rect(self.surface, YELLOW, self.health_bar1)
            pygame.draw.rect(self.surface, YELLOW, self.health_bar2)

            # need to add dynamic aspect of energy bars
            # left energy bar outline image
            self.energy_bar_outline = pygame.image.load('data/energy_bar_outline.png')
            self.surface.blit(self.energy_bar_outline, (5, 280))
            # right energy bar outline image
            self.energy_bar_outline2 = pygame.image.load('data/energy_bar_outline2.png')
            self.surface.blit(self.energy_bar_outline2, (1239, 280))
            # dynamic energy bars
            self.energy_used1 = 10 - self.player1.energy
            self.energy_used2 = 10 - self.player2.energy
            self.energy_bar1 = Rect((20, 281 + (20 * self.energy_used1)), (20, 200 - (20 * self.energy_used1)))
            self.energy_bar2 = Rect((1241, 281 + (20 * self.energy_used2)), (20, 200 - (20 * self.energy_used2)))
            pygame.draw.rect(self.surface, GREEN, self.energy_bar1)
            pygame.draw.rect(self.surface, GREEN, self.energy_bar2)

            skill_ids = self.player1.skills + self.player2.skills
            for i, skill_box in enumerate(self.skill_boxes):
                pygame.draw.rect(self.surface, skill_box.color, skill_box)
                skill_text = str(skill_ids[i])
                skill_font = self.debug_font_small_2.render(skill_text, True, WHITE)
                skill_text_xy = font_position_center(skill_box, self.debug_font_small_2, skill_text)
                self.surface.blit(skill_font, skill_text_xy)

            self.return_button.draw(self.surface)

        def _draw_timer():
            time_display = self.timer_font.render(str(self.game_time), True, BLUE)
            self.surface.blit(time_display, self.timer_font_xy)

        def _draw_arena():
            for rect in self.arena:
                if rect.color is not None:
                    pygame.draw.rect(self.surface, rect.color, rect)

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

                # Animations that still need to be implemented
                # if (p.state == DEATH):
                # if (p.state == ATTACK):
                # if (p.state == CAST):
                # if (p.state == SLIDE):

                # JUMP
                if p.state == JUMP:
                    if p.facing_direction == LEFT:
                        flip = True
                    if p.wait_frames <= 0:
                        p.wait_frames = 5
                        if p.animation_key <= 0:
                            p.animation_key += 1
                    self.screen.blit(pygame.transform.flip(p.sprite[p.animation_key + 30], flip, False), (p.left-17,p.top-22))
                # FALL
                elif p.state == FALL:
                    if p.facing_direction == LEFT:
                        flip = True
                    if p.wait_frames <= 0:
                        p.wait_frames = 5
                        if p.animation_key <= 0:
                            p.animation_key += 1
                    self.screen.blit(pygame.transform.flip(p.sprite[p.animation_key + 32], flip, False), (p.left-17,p.top-22))
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
                    self.screen.blit(pygame.transform.flip(p.sprite[p.animation_key + 14], flip, False), (p.left - 17, p.top - 22))
                # STAND (default animation)
                else:
                    if p.facing_direction == LEFT:
                        flip = True
                    # Currently only have 1 standing sprite
                    self.screen.blit(
                        pygame.transform.flip(p.sprite[p.animation_key + 1], flip, False), (p.left - 17, p.top - 22))
                p.wait_frames += -1

            if self.player1.sprite is not None:
                _draw_player(self.player1)
            if self.player2.sprite is not None:
                _draw_player(self.player2)

        def _draw_monsters():
            for m in self.active_monsters:
                pygame.draw.rect(self.surface, m.color, m)
                health_bar = Rect2(left=m.left, top=m.top - 8, width=m.width, height=6)
                health_bar_width = round(m.width * (m.hit_points / m.hit_points_max))
                health_bar_life = Rect2(left=m.left, top=m.top - 8, width=health_bar_width, height=6)

                pygame.draw.rect(self.surface, WHITE, health_bar)
                pygame.draw.rect(self.surface, RED, health_bar_life)
                pygame.draw.rect(self.surface, BLACK, health_bar, 1)

        def _draw_dropped_skills():
            for skill in self.arena.dropped_skills:
                pygame.draw.rect(self.surface, skill.color, skill)
                skill_text = str(skill.id)
                skill_font = self.debug_font_small_2.render(skill_text, True, WHITE)
                skill_text_xy = font_position_center(skill, self.debug_font_small_2, skill_text)
                self.surface.blit(skill_font, skill_text_xy)

        def _draw_particles():
            for p in self.active_particles:
                if isinstance(p, FieldParticle):
                    pygame.draw.circle(self.surface, p.color, (p.centerx, p.centery), p.radius, 1)
                else:
                    pygame.draw.rect(self.surface, p.color, p)

        def _draw_scrolling_text():
            for unit in self.active_monsters + [self.player1, self.player2]:
                for t in unit.st_buffer:
                    text = t[0] if isinstance(t[0],str) else ("-" + str(int(t[0])))
                    color = RED
                    if isinstance(t[0],str) and t[0] in BUFFS:
                        color = GREEN
                    self.surface.blit(self.st_font.render(text, True, color),
                    (unit.centerx, unit.top - (3000 - t[1] + self.game_time.msec)/50))
                    if t[1] <= self.game_time.msec:
                        unit.st_buffer.remove(t)

        def _draw_rain():
            if self.make_rain:
                for i in range(5, self.arena.play_area_rect.width, 10):
                    rain_copy = self.rain.copy()
                    rain_copy.left = i + self.arena.play_area_rect.left
                    self.rain_particles.append(rain_copy)

            for r in self.rain_particles:
                r.move_ip((0, 5))
                pygame.draw.rect(self.surface, BLUE, r)

            for r in self.rain_particles[:]:
                if r.top > self.arena.play_area_rect.height:
                    self.rain_particles.remove(r)
            self.make_rain = False

        _draw_ui1()
        _draw_timer()
        _draw_arena()
        _draw_monsters()
        _draw_dropped_skills()
        if not self.player1.input.DEBUG_VIEW:
            _draw_players()
        _draw_particles()
        _draw_scrolling_text()
        _draw_ui2()
        # _draw_rain()

    # -------------------------------------------------------------------------
    def draw_debug(self):

        def _draw_spawn_point_rects():
            for rect in self.arena.spawn_points:
                pygame.draw.rect(self.surface, RED, rect)

        def _draw_play_area_debug_border():
            old_play_area = Rect2(65, 0, 1150, 475)
            pygame.draw.rect(self.surface, YELLOW, old_play_area, 1)
            pygame.draw.rect(self.surface, GREEN, self.arena.play_area_rect, 1)
            pygame.draw.rect(self.surface, RED, self.arena.left_wall, 1)
            pygame.draw.rect(self.surface, RED, self.arena.floor, 1)
            pygame.draw.rect(self.surface, RED, self.arena.right_wall, 1)

        def _draw_debug_text():
            x = '| x:{:>8.2f}|'.format(self.player1.x)
            y = '| y:{:>8.2f}|'.format(self.player1.y)
            dx = '|dx:{:>8.2f}|'.format(self.player1.dx)
            dy = '|dy:{:>8.2f}|'.format(self.player1.dy)
            debug_font_1 = self.debug_font.render(x, True, GREEN)
            debug_font_2 = self.debug_font.render(y, True, GREEN)
            debug_font_3 = self.debug_font.render(dx, True, GREEN)
            debug_font_4 = self.debug_font.render(dy, True, GREEN)
            self.surface.blit(debug_font_1, self.debug_font_xy1)
            self.surface.blit(debug_font_2, self.debug_font_xy2)
            self.surface.blit(debug_font_3, self.debug_font_xy3)
            self.surface.blit(debug_font_4, self.debug_font_xy4)

            num_monsters = '|curr num monsters:{:>4}|'.format(len(self.active_monsters))
            max_monsters = '| max num monsters:{:>4}|'.format(self.arena.max_monsters)
            debug_font_m1 = self.debug_font.render(num_monsters, True, GREEN)
            debug_font_m2 = self.debug_font.render(max_monsters, True, GREEN)
            self.surface.blit(debug_font_m1, self.debug_font_xy5)
            self.surface.blit(debug_font_m2, self.debug_font_xy6)

        def _draw_cpu_usage():
            cpu_text = '|CPU Utilization:{:>5.1f}%|'.format(self.cpu_avg) if psutil_found else '|CPU Utilization:  ????|'
            cpu_font = self.debug_font.render(cpu_text, True, RED)
            self.surface.blit(cpu_font, self.debug_font_xy7)

        def _draw_destructible_terrain_debug_text():
            for rect in self.arena.destructible_terrain:
                rendered_debug_font = self.debug_font_small_2.render(str(rect.hits_to_destroy), True, BLACK)
                pos = font_position_center(rect, self.debug_font_small_2, str(rect.hits_to_destroy))
                self.surface.blit(rendered_debug_font, pos)

        def _draw_mouse_text():
            mouse_pos = pygame.mouse.get_pos()
            play_area_mouse_pos = mouse_pos[0] - self.arena.play_area_rect.left, mouse_pos[1]
            pygame.draw.circle(self.surface, WHITE, mouse_pos, 2, 0)
            pygame.draw.circle(self.surface, BLACK, mouse_pos, 2, 1)
            if 0 <= play_area_mouse_pos[0] <= self.arena.play_area_rect.width and 0 <= play_area_mouse_pos[1] <= self.arena.play_area_rect.height:
                offset_pos_mouse_font = self.debug_font_small.render(str(play_area_mouse_pos), True, DGREY)
                self.surface.blit(offset_pos_mouse_font, mouse_pos)
            real_pos_mouse_font = self.debug_font_small.render(str(mouse_pos), True, DKYELLOW)
            self.surface.blit(real_pos_mouse_font, (mouse_pos[0] + 3, mouse_pos[1] + 10))

        def _draw_players_debug(draw_p1=True, draw_p2=True):

            def _draw_player_debug(p, c1, c2):
                pygame.draw.rect(self.surface, c1, p)
                eye = Rect2(topleft=p.topleft, size=(5, 5))
                if p.facing_direction == LEFT:
                    eye.topleft = p.topleft
                    eye.move_ip((+3, 3))
                else:
                    eye.topright = p.topright
                    eye.move_ip((-3, 3))
                pygame.draw.rect(self.surface, c2, eye)

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
                    pygame.draw.circle(self.surface, ORANGE, self.player1.center, 5, 0)
                for l in locs:
                    pygame.draw.circle(self.surface, ORANGE, l, 3, 0)

        if self.player1.input.DEBUG_VIEW:
            _draw_spawn_point_rects()
            _draw_play_area_debug_border()
            _draw_debug_text()
            _draw_cpu_usage()
            _draw_destructible_terrain_debug_text()
            _draw_players_debug()
            _draw_player_collision_points_for_debugging()
            _draw_mouse_text()
        elif not self.player1.input.DEBUG_VIEW:
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

        def _handle_return_to_main_menu():
            for event in pygame.event.get():
                if 'click' in self.return_button.handleEvent(event):
                    self.start_menu(restart_music=True)
            if self.player1.input.ENTER_LEAVE:
                self.player1.input.ENTER_LEAVE = False
                self.start_menu(restart_music=True)

        def _handle_time_tick_event():
            for event in pygame.event.get(TIME_TICK_EVENT):
                if event.type == TIME_TICK_EVENT:

                    self.game_time.inc()

                    # for CPU usage debug text
                    if psutil_found and self.player1.input.DEBUG_VIEW:
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
            for event in pygame.event.get(PLAYER1_LOCK_EVENT):
                # player 1 skill lock timer
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
                    print("FOUND")
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
                    pygame.time.set_timer(MONSTER_SPAWN_EVENT, 1000)

        def _handle_quit_event():
            for event in pygame.event.get(QUIT):
                # QUIT event occurs when click X on window bar
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

        if not self.player1.input.PAUSED:
            _handle_song_end_event()
            _handle_time_tick_event()
            _handle_regeneration_event()
            _handle_player_lock_events()
            _handle_player_pickup_skill_events()
            _handle_rain_event()
            _handle_monster_spawn_event()
            _handle_quit_event()
            _handle_return_to_main_menu()
        else:
            _handle_quit_event()
            self.player1.input._handle_keyboard_updown_events()
            self.player1.input._handle_gamepad_updown_events()
            pygame.event.clear()

# -------------------------------------------------------------------------
if __name__ == '__main__':
    StartMenu()()
