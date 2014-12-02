# python standard library modules
import os
import random
import sys

# pygame
import pygame
from pygame.locals import *

# our modules
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
            turn_on_music()

        def _setup_time():
            self.clock = pygame.time.Clock()
            self.fps = 5

        def _setup_input():
            self.input = Input()

        pygame.init()
        _setup_display()
        _setup_music()
        _setup_time()
        _setup_input()

    def __call__(self):
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

        #text for transparent buttons
        #self.button_font = pygame.font.Font('data/Kremlin.ttf', 30)
        #self.b_start = self.button_font.render('Start', True, DKRED)
        #self.b_help = self.button_font.render('Help', True, DKRED)
        #self.b_options = self.button_font.render('Options', True, DKRED)
        #self.b_exit = self. button_font.render('Exit', True, DKRED)
        #self.screen.blit(self.b_start, (340, 400))
        #self.screen.blit(self.b_help, (500, 400))
        #self.screen.blit(self.b_options, (630, 400))
        #self.screen.blit(self.b_exit, (845, 400))

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

        def _setup_time():
            self.clock = pygame.time.Clock()
            self.fps = 30
            pygame.time.set_timer(TIME_TICK_EVENT, 250)
            pygame.time.set_timer(REGENERATION_EVENT, 1000)
            self.game_time = GameTime()

        def _setup_input():
            self.start_menu = start_menu
            self.input = Input()

        def _setup_Rects():
            self.window = self.surface.get_rect()
            self.window_border = Rect2(left=0, top=0, width=1280, height=600)
            self.play_area_border = Rect2(left=60, top=0, width=1160, height=485)
            self.player1 = Player(id=1, left=200, top=150, width=30, height=40)
            self.player1_eyeball = Rect2(left=200, top=150, width=5, height=5)
            self.player2 = Player(id=2, left=1080, top=150, width=30, height=40)
            self.player1.hit_points = 20  # FOR TESTING/DEBUGGING, REMOVE LATER
            self.player2_eyeball = Rect2(left=1080, top=150, width=5, height=5)
            self.player1.opposite = self.player2  # Makes things a lot easier
            self.player2.opposite = self.player1  # Makes things a lot easier
            self.arena = Arena(random.choice((arena1, arena2)))

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
            self.debug_font_xy1 = 1000, 505
            self.debug_font_xy2 = 1000, 520
            self.debug_font_xy3 = 1000, 540
            self.debug_font_xy4 = 1000, 560
            self.debug_font_xy5 = 725, 505
            self.debug_font_xy6 = 725, 520
            self.debug_font_xy7 = 725, 535
            # Scrolling text font
            self.st_font = pygame.font.Font(main_font, 30)

        def _setup_particles():
            self.active_particles = []

        def _setup_monsters():
            self.active_monsters = []
            self.spawn_monsters = False
            pygame.event.post(pygame.event.Event(MONSTER_SPAWN_EVENT))

        def _setup_music():
            self.music_flag = get_music_on()
            if self.music_flag:
                self.songs = ['data/pneumatic_driller.mp3', 'data/euglena_zielona.mp3',
                              'data/drilldance.mp3', 'data/running_emu.mp3', 'data/wooboodoo.mp3',
                              'data/accident.mp3']
                self.curr_song = None
                self.play_next_random_song()

        def _setup_rain():
            self.rain_particles = []
            self.rain = Rect2(left=0, top=0, width=1, height=3)
            self.make_rain = False
            pygame.event.post(pygame.event.Event(MORE_RAIN_EVENT))

        def _setup_mouse():
            pygame.mouse.set_visible(False)

        def _setup_player_sprites():  # load player sprites here
            # Will later need some value to tell the game what sprite
            # to load based on player choice, since we don't want to
            # just load everything possible

            # Load sprites for player 1
            try:
                spritesheet1 = pygame.image.load("data/pl_human.png")
            except:
                raise (UserWarning, "Unable to load sprites")  # error msg and exit
            spritesheet1.convert()
            m1 = []

            # Put spritesheet into list, each sprite is 64x64 pixels large
            for num in range(1, 7, 1):  # Standing
                m1.append(spritesheet1.subsurface((64 * (num - 1), 0, 64, 64)))
            for num in range(7, 15, 1):  # Walk Transition
                m1.append(spritesheet1.subsurface((64 * (num - 7), 64, 64, 64)))
            for num in range(15, 23, 1):  # Walk Part 1
                m1.append(spritesheet1.subsurface((64 * (num - 15), 128, 64, 64)))
            for num in range(23, 31, 1):  # Walk Part 2
                m1.append(spritesheet1.subsurface((64 * (num - 23), 192, 64, 64)))
            for num in range(31, 35, 1):  # Jump and Fall
                m1.append(spritesheet1.subsurface((64 * (num - 31), 256, 64, 64)))

            for num in range(len(m1)):
                m1[num].set_colorkey((0, 0, 0))  # sprite bg rgb is (0,0,0)
                m1[num] = m1[num].convert_alpha()

            self.p1_sprite = m1
            self.p1_wait_frames = 0
            self.p1_animation_key = -1

            # Player 2 will be the same thing with a different spritesheet

        pygame.init()
        _setup_display()
        _setup_time()
        _setup_input()
        _setup_Rects()
        initialize_skill_table()
        _setup_monsters()
        _setup_fonts()
        _setup_particles()
        _setup_music()
        _setup_rain()
        _setup_mouse()
        _setup_player_sprites()

    # ------------------------------------------------------------------------
    def __call__(self):
        while True:
            if not self.input.PAUSED:
                self.handle_input()
                self.handle_monsters()
                self.handle_particles()
                self.draw_screen()
                self.draw_debug()
                pygame.display.update()
                self.handle_event_queue()
                self.clock.tick(self.fps)
            else:
                self.handle_input()
                self.handle_event_queue()

    # -------------------------------------------------------------------------
    def handle_input(self):

        def _handle_special_input():
            if self.input.PAUSED:
                rendered_font = self.pause_font.render('-PAUSE-', True, RED)
                self.surface.blit(rendered_font, self.pause_font_xy)
                pygame.display.update()

            if self.input.RESPAWN and not self.input.PAUSED:
                self.player1.topleft = self.player1.topleft_initial

            if self.input.EXIT:
                # Add the QUIT event to the pygame event queue to be handled
                # later, at the same time the QUIT event from clicking the
                # window X is handled
                pygame.event.post(pygame.event.Event(QUIT))

        def _handle_player_input():
            if not self.input.PAUSED:
                self.player1(self.input, self.arena)

        self.input.refresh()
        _handle_player_input()
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
                # Added this part into player inputs; causing bugs if skill doesn't create particle
                # pygame.time.set_timer(USEREVENT + 2, self.player1.new_particle.cooldown)

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
                if isinstance(p, RangeParticle):
                    all_terrain_hit_i = p.p_collidelistall(self.arena.rects)
                    if all_terrain_hit_i:  # False if empty list
                        if p.on_terrain_f:
                            p.on_terrain_f(p)
                        self.active_particles.remove(p)
                        for i in all_terrain_hit_i:
                            self.arena.rects[i].hits_to_destroy -= 1
                            if self.arena.rects[i].hits_to_destroy == 0:
                                self.arena.rects.pop(i)
                    else:
                        first_hit = p.collidelist(self.active_monsters)
                        if first_hit != -1:  # If hit a monsters
                            p.on_hit(self.active_monsters[first_hit], self.game_time.msec)
                            self.active_particles.remove(p)
                        else:  # If didn't hit a monster, check player
                            if p.colliderect(opposite):
                                p.on_hit(opposite, self.game_time.msec)
                                self.active_particles.remove(p)
                else:  # if MeleeParticle
                    all_monsters_hit_i = p.collidelistall(self.active_monsters)
                    for i in all_monsters_hit_i:
                        p.on_hit(self.active_monsters[i], self.game_time.msec)

                    first_terrain_hit_i = p.collidelist(self.arena.rects)
                    if first_terrain_hit_i != -1:
                        self.arena.rects[first_terrain_hit_i].hits_to_destroy -= 1
                        if self.arena.rects[first_terrain_hit_i].hits_to_destroy == 0:
                            self.arena.rects.pop(first_terrain_hit_i)
                    if p.colliderect(opposite):
                        p.on_hit(opposite, self.game_time.msec)

        _update_active_particles()
        _update_particles()
        _check_particle_collisions()

    # -------------------------------------------------------------------------
    def handle_monsters(self):
        if self.spawn_monsters and len(self.active_monsters) < self.arena.max_monsters:
            spawn_point = random.choice(list(filter(lambda x: x.spawn_point, self.arena)))  # pick a random spawn point
            monster_info = MONSTER_TABLE[random.choice(self.arena.possible_monsters)]
            self.active_monsters.append(Monster(monster_info, spawn_point.left, spawn_point.top, self.player1, self.player1))

        for m in self.active_monsters:
            if m.is_dead():
                self.active_monsters.remove(m)
            else:
                m(self.game_time.msec, self.arena)

        self.spawn_monsters = False

    # -------------------------------------------------------------------------
    def draw_screen(self):
        def _draw_ui():
            self.surface.fill(DGREY)  # fill background dark grey

            #font for player's health and energy
            #health_display = self.health_font.render(str(self.player1.hit_points), True, RED)
            #energy_display = self.energy_font.render(str(int(self.player1.energy)), True, YELLOW)
            #self.surface.blit(health_display, self.health_font_xy)
            #self.surface.blit(energy_display, self.energy_font_xy)

            #health bars
            #currently only goes off of one player's health
            #left health bar outline image
            self.health_bar_outline = pygame.image.load('data/health_bar_outline.png')
            self.surface.blit(self.health_bar_outline, (5, 20))
            self.health_bar_outline2 = pygame.image.load('data/health_bar_outline2.png')
            self.surface.blit(self.health_bar_outline2, (1239, 20))
            #right health bar outline image
            #dynamic health bars
            self.damage_taken1 = self.player1.hit_points_max - self.player1.hit_points
            self.damage_taken2 = self.player2.hit_points_max - self.player2.hit_points
            self.health_bar1 = Rect((20, (21 + (2 * self.damage_taken1))), (20, (200 - (2 * self.damage_taken1))))
            self.health_bar2 = Rect((1241, (21 + (2 * self.damage_taken2))), (20, (200 - (2 * self.damage_taken2))))
            pygame.draw.rect(self.surface, YELLOW, self.health_bar1)
            pygame.draw.rect(self.surface, YELLOW, self.health_bar2)

            # need to add dynamic aspect of energy bars
            #left energy bar outline image
            self.energy_bar_outline = pygame.image.load('data/energy_bar_outline.png')
            self.surface.blit(self.energy_bar_outline, (5, 280))
            #right energy bar outline image
            self.energy_bar_outline2 = pygame.image.load('data/energy_bar_outline2.png')
            self.surface.blit(self.energy_bar_outline2, (1239, 280))
            #dynamic energy bars
            self.energy_used1 = 10 - self.player1.energy
            self.energy_used2 = 10 - self.player2.energy
            self.energy_bar1 = Rect((20, 281 + (20 * self.energy_used1)), (20, 200 - (20 * self.energy_used1)))
            self.energy_bar2 = Rect((1241, 281 + (20 * self.energy_used2)), (20, 200 - (20 * self.energy_used2)))
            pygame.draw.rect(self.surface, GREEN, self.energy_bar1)
            pygame.draw.rect(self.surface, GREEN, self.energy_bar2)

            #player 1 skill boxes
            #each skill will have an image associated with it - stored in skill table?
            self.skill_box1 = Rect((90, 500), (40, 40))
            pygame.draw.rect(self.surface, BLACK, self.skill_box1)

            self.skill_box2 = Rect((140, 500), (40, 40))
            pygame.draw.rect(self.surface, BLACK, self.skill_box2)
            #self.image_box2 = pygame.image.load('assets/temp_skill.PNG')
            #self.surface.blit(self.image_box2, (150,510))

            self.skill_box3 = Rect((190, 500), (40, 40))
            pygame.draw.rect(self.surface, BLACK, self.skill_box3)

            self.skill_box4 = Rect((240, 500), (40, 40))
            pygame.draw.rect(self.surface, BLACK, self.skill_box4)

            self.skill_box5 = Rect((290, 500), (40, 40))
            pygame.draw.rect(self.surface, BLACK, self.skill_box5)

            #player 2 skill boxes
            self.skill_box6 = Rect((950, 500), (40, 40))
            pygame.draw.rect(self.surface, DKRED, self.skill_box6)

            self.skill_box7 = Rect((1000, 500), (40, 40))
            pygame.draw.rect(self.surface, DKRED, self.skill_box7)
            #self.image_box2 = pygame.image.load('assets/temp_skill.PNG')
            #self.surface.blit(self.image_box2, (150,510))

            self.skill_box8 = Rect((1050, 500), (40, 40))
            pygame.draw.rect(self.surface, DKRED, self.skill_box8)

            self.skill_box9 = Rect((1100, 500), (40, 40))
            pygame.draw.rect(self.surface, DKRED, self.skill_box9)

            self.skill_box10 = Rect((1150, 500), (40, 40))
            pygame.draw.rect(self.surface, DKRED, self.skill_box10)

            #main menu button at bottom middle of screen
            self.return_button = pygbutton.PygButton((490, 550, 300, 50), 'Main Menu')
            self.return_button.draw(self.surface)

        def _draw_timer():
            time_display = self.timer_font.render(str(self.game_time), True, BLUE)
            self.surface.blit(time_display, self.timer_font_xy)

        def _draw_map():
            for rect in self.arena:
                if rect.color is not None:
                    pygame.draw.rect(self.surface, rect.color, rect)

        def _draw_players():
            # Draw player using wait_frames and animation_key
            # wait_frames = frames waited before key is incremented
            # animation_key = index for the sprite list

            # Draw player 1
            if self.player1.state != self.player1.previous_state:
                self.p1_wait_frames = 0
                self.p1_animation_key = -1  # -1 because it will always get
                                            # incremented at the start of each check
            flip = False  # value for flipping sprite

            # Draw player 2
            pygame.draw.rect(self.surface, BLUE, self.player2)


            # Animations that still need to be implemented
            # if (self.player1.state == DEATH):
            # if (self.player1.state == ATTACK):
            # if (self.player1.state == CAST):
            # if (self.player1.state == SLIDE):

            # JUMP
            if self.player1.state == JUMP:
                if self.player1.facing_direction == LEFT:
                    flip = True
                if self.p1_wait_frames <= 0:
                    self.p1_wait_frames = 5
                    if self.p1_animation_key <= 0:
                        self.p1_animation_key += 1
                self.screen.blit(pygame.transform.flip(self.p1_sprite[self.p1_animation_key + 30], flip, False), (self.player1.left-17,self.player1.top-22))
            # FALL
            elif self.player1.state == FALL:
                if self.player1.facing_direction == LEFT:
                    flip = True
                if self.p1_wait_frames <= 0:
                    self.p1_wait_frames = 5
                    if self.p1_animation_key <= 0:
                        self.p1_animation_key += 1
                self.screen.blit(pygame.transform.flip(self.p1_sprite[self.p1_animation_key + 32], flip, False), (self.player1.left-17,self.player1.top-22))
            # WALK
            elif self.player1.state == RWALK or self.player1.state == LWALK:
                if self.player1.facing_direction == LEFT:
                    flip = True
                if self.player1.state == RWALK and self.player1.previous_state != RWALK:
                    self.p1_animation_key = -8  # Transition sprites loaded before walk
                elif self.player1.state == LWALK and self.player1.previous_state != LWALK:
                    self.p1_animation_key = -8
                if self.p1_wait_frames <= 0:
                    self.p1_wait_frames = 2
                    self.p1_animation_key += 1
                    if self.p1_animation_key > 0:
                        self.p1_animation_key %= 16  # Loops the key
                self.screen.blit(pygame.transform.flip(self.p1_sprite[self.p1_animation_key + 14], flip, False), (self.player1.left - 17, self.player1.top - 22))
            # STAND (default animation)
            else:
                if self.player1.facing_direction == LEFT:
                    flip = True
                # Currently only have 1 standing sprite
                self.screen.blit(
                    pygame.transform.flip(self.p1_sprite[self.p1_animation_key + 1], flip, False), (self.player1.left - 17, self.player1.top - 22))
            self.p1_wait_frames += -1
            # Draw player 2 here

        def _draw_players():
            # Draw player using wait_frames and animation_key
            # wait_frames = frames waited before key is incremented
            # animation_key = index for the sprite list

            # Draw player 1
            if self.player1.state != self.player1.previous_state:
                self.p1_wait_frames = 0
                self.p1_animation_key = -1  # -1 because it will always get
                                            # incremented at the start of each check
            flip = False  # value for flipping sprite
            
            # Draw player 2
            pygame.draw.rect(self.surface, LBLUE, self.player2)
            

            # Animations that still need to be implemented
            # if (self.player1.state == DEATH):
            # if (self.player1.state == ATTACK):
            # if (self.player1.state == CAST):
            # if (self.player1.state == SLIDE):

            # JUMP
            if self.player1.state == JUMP:
                if self.player1.facing_direction == LEFT:
                    flip = True
                if self.p1_wait_frames <= 0:
                    self.p1_wait_frames = 5
                    if self.p1_animation_key <= 0:
                        self.p1_animation_key += 1
                self.screen.blit(pygame.transform.flip(self.p1_sprite[self.p1_animation_key + 30], flip, False), (self.player1.left-17,self.player1.top-22))
            # FALL
            elif self.player1.state == FALL:
                if self.player1.facing_direction == LEFT:
                    flip = True
                if self.p1_wait_frames <= 0:
                    self.p1_wait_frames = 5
                    if self.p1_animation_key <= 0:
                        self.p1_animation_key += 1
                self.screen.blit(pygame.transform.flip(self.p1_sprite[self.p1_animation_key + 32], flip, False), (self.player1.left-17,self.player1.top-22))
            # WALK
            elif self.player1.state == RWALK or self.player1.state == LWALK:
                if self.player1.facing_direction == LEFT:
                    flip = True
                if self.player1.state == RWALK and self.player1.previous_state != RWALK:
                    self.p1_animation_key = -8  # Transition sprites loaded before walk
                elif self.player1.state == LWALK and self.player1.previous_state != LWALK:
                    self.p1_animation_key = -8
                if self.p1_wait_frames <= 0:
                    self.p1_wait_frames = 2
                    self.p1_animation_key += 1
                    if self.p1_animation_key > 0:
                        self.p1_animation_key %= 16  # Loops the key
                self.screen.blit(pygame.transform.flip(self.p1_sprite[self.p1_animation_key + 14], flip, False), (self.player1.left - 17, self.player1.top - 22))
            # STAND (default animation)
            else:
                if self.player1.facing_direction == LEFT:
                    flip = True
                # Currently only have 1 standing sprite
                self.screen.blit(
                    pygame.transform.flip(self.p1_sprite[self.p1_animation_key + 1], flip, False), (self.player1.left - 17, self.player1.top - 22))
            self.p1_wait_frames += -1
            # Draw player 2 here

        def _draw_monsters():
            for m in self.active_monsters:
                pygame.draw.rect(self.surface, ORANGE, m)
                health_bar = Rect2(left=m.left, top=m.top - 8, width=m.width, height=6)
                health_bar_width = round(m.width * (m.hit_points / m.hit_points_max))
                health_bar_life = Rect2(left=m.left, top=m.top - 8, width=health_bar_width, height=6)

                pygame.draw.rect(self.surface, WHITE, health_bar)
                pygame.draw.rect(self.surface, RED, health_bar_life)
                pygame.draw.rect(self.surface, BLACK, health_bar, 1)

        def _draw_particles():
            for p in self.active_particles:
                pygame.draw.rect(self.surface, p.color, p)

        def _draw_scrolling_text():
            for t in self.player1.st_buffer:
                self.surface.blit(self.st_font.render('-' + str(int(t[0])), True, RED),
                (self.player1.centerx, self.player1.top - (3000 - t[1] + self.game_time.msec) / 50))
                if t[1] <= self.game_time.msec:
                    self.player1.st_buffer.remove(t)
            for t in self.player2.st_buffer:
                self.surface.blit(self.st_font.render("-"+str(int(t[0])), True, RED), \
                (self.player2.centerx, self.player2.top - (3000 - t[1] + self.game_time.msec)/50))
                if t[1] <= self.game_time.msec:
                    self.player2.st_buffer.remove(t)
            for m in self.active_monsters:
                for t in m.st_buffer:
                    self.surface.blit(self.st_font.render('-' + str(int(t[0])), True, RED),
                    (m.centerx, m.top - (3000 - t[1] + self.game_time.msec) / 50))
                    if t[1] <= self.game_time.msec:
                        m.st_buffer.remove(t)

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

        _draw_ui()
        _draw_timer()
        _draw_map()
        _draw_monsters()
        if not self.input.DEBUG_VIEW:
            _draw_players()
        _draw_particles()
        _draw_scrolling_text()
        # _draw_rain()

    # -------------------------------------------------------------------------
    def draw_debug(self):

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

            num_monsters = '|curr num monsters:{:>2}|'.format(len(self.active_monsters))
            max_monsters = '| max num monsters:{:>2}|'.format(self.arena.max_monsters)
            debug_font_m1 = self.debug_font.render(num_monsters, True, GREEN)
            debug_font_m2 = self.debug_font.render(max_monsters, True, GREEN)
            self.surface.blit(debug_font_m1, self.debug_font_xy5)
            self.surface.blit(debug_font_m2, self.debug_font_xy6)

        def _draw_destructible_terrain_debug_text():
            for rect in filter(lambda x: x.hits_to_destroy > 0, self.arena):
                rendered_debug_font = self.debug_font_small_2.render(str(rect.hits_to_destroy), True, BLACK)
                pos = font_position_center(rect, self.debug_font_small_2, str(rect.hits_to_destroy))
                self.surface.blit(rendered_debug_font, pos)

        def _draw_mouse_text():
            mouse_pos = pygame.mouse.get_pos()
            play_area_mouse_pos = mouse_pos[0] - self.arena.play_area_rect.left, mouse_pos[1]
            if 0 <= play_area_mouse_pos[0] <= self.arena.play_area_rect.width and \
                    0 <= play_area_mouse_pos[1] <= self.arena.play_area_rect.height:
                pygame.draw.circle(self.surface, BLACK, mouse_pos, 2, 1)
                rendered_debug_font = self.debug_font_small.render(str(play_area_mouse_pos), True, BLACK)
                self.surface.blit(rendered_debug_font, mouse_pos)

        def _draw_players_debug():
            pygame.draw.rect(self.surface, LBLUE, self.player1)
            pygame.draw.rect(self.surface, LBLUE, self.player2)
            if self.player1.facing_direction == LEFT:
                self.player1_eyeball.topleft = self.player1.topleft
                self.player1_eyeball.move_ip((+3, 3))
            else:
                self.player1_eyeball.topright = self.player1.topright
                self.player1_eyeball.move_ip((-3, 3))
            pygame.draw.rect(self.surface, DKRED, self.player1_eyeball)

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

        if self.input.DEBUG_VIEW:
            _draw_debug_text()
            _draw_destructible_terrain_debug_text()
            _draw_players_debug()
            _draw_player_collision_points_for_debugging()
            _draw_mouse_text()

    # -------------------------------------------------------------------------
    def handle_event_queue(self):

        def _handle_song_end_event():
            for event in pygame.event.get(SONG_END_EVENT):
                if event.type == SONG_END_EVENT:
                    print("the song ended!")
                    self.play_next_random_song()

        def _handle_return_to_main_menu():
            for event in pygame.event.get():
                if 'click' in self.return_button.handleEvent(event):
                    start_menu()
            if self.input.ENTER_LEAVE:
                self.input.ENTER_LEAVE = False
                self.start_menu()

        def _handle_time_tick_event():
            for event in pygame.event.get(TIME_TICK_EVENT):
                if event.type == TIME_TICK_EVENT:
                    self.game_time.inc()

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
                        for k,v in m.conditions.items():
                            for e in v:
                                if e.is_expired(self.game_time.msec):
                                    m.conditions[k].remove(e)

        def _handle_regeneration_event():
            for event in pygame.event.get(REGENERATION_EVENT):
                if event.type == REGENERATION_EVENT:
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

        def _handle_player_lock_events():
            for event in pygame.event.get(PLAYER1_LOCK_EVENT):
                # player 1 skill lock timer
                if event.type == PLAYER1_LOCK_EVENT:
                    self.player1.attack_cooldown_expired = True
                    pygame.time.set_timer(PLAYER1_LOCK_EVENT, 0)

        def _handle_player_meditate_events():
            for event in pygame.event.get(PLAYER1_MEDITATE_EVENT):
                if event.type == PLAYER1_MEDITATE_EVENT:
                    self.player1.energy += 5
                    if self.player1.energy > 10:
                        self.player1.energy = 10
                    pygame.time.set_timer(PLAYER1_MEDITATE_EVENT, 0)

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
                # QUIT event occurs when click X on window bar
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

        if not self.input.PAUSED:
            _handle_song_end_event()
            _handle_time_tick_event()
            _handle_regeneration_event()
            _handle_player_lock_events()
            _handle_player_meditate_events()
            _handle_rain_event()
            _handle_monster_spawn_event()
            _handle_quit_event()
            _handle_return_to_main_menu()
            pygame.event.clear()
        else:
            _handle_quit_event()
            self.input._handle_keyboard_updown_events()
            self.input._handle_gamepad_updown_events()
            pygame.event.clear()

# -------------------------------------------------------------------------
    def play_next_random_song(self):
        print('self.songs', self.songs)
        print('self.curr_song', self.curr_song)
        self.next_song = random.choice([s for s in self.songs if s != self.curr_song])
        self.curr_song = self.next_song
        print('self.next_song', self.next_song)
        pygame.mixer.music.load(self.next_song)
        pygame.mixer.music.play()
        pygame.mixer.music.set_endevent(SONG_END_EVENT)

# -------------------------------------------------------------------------
if __name__ == '__main__':
    StartMenu()()
