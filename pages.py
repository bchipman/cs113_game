# python standard library modules
import os
import sys
import textwrap
import pygbutton
from collections import deque

# pygame
import pygame
from pygame.locals import *

# our modules
import globals as GL
from globals import *
from pygbutton import *
from classes import *

SELECTION_BOX_WIDTH = 4
SELECTION_BOX_COLOR = BLUE

class StartPage:
    def __init__(self):
        self.bg_image = pygame.image.load('data/backgrounds/bkg_start_page.png')
        self.start_button = PygButton((325, 395, 140, 40), 'Start')
        self.help_button = PygButton((485, 395, 110, 40), 'Help')
        self.options_button = PygButton((615, 395, 175, 40), 'Options')
        self.exit_button = PygButton((810, 395, 105, 40), 'Exit')
        AUDIO.turn_on_music()
        title_font = pygame.font.Font('data/fonts/Kremlin.ttf', 50)
        self.title_font1 = title_font.render('Famished', True, DKRED)
        self.title_font2 = title_font.render('Tournament', True, DKRED)
        self.selection_box = deque([self.start_button, self.help_button, self.options_button, self.exit_button])

    def __call__(self):
        self.return_now = False
        while not self.return_now:
            self.draw()
            self.input()
            self.events()
            GL.CLOCK.tick(GL.FPS)

    def draw(self):
        GL.SCREEN.blit(self.bg_image, (0, 0))
        self.start_button.draw(GL.SCREEN)
        self.help_button.draw(GL.SCREEN)
        self.options_button.draw(GL.SCREEN)
        self.exit_button.draw(GL.SCREEN)
        GL.SCREEN.blit(self.title_font1, (495, 120))
        GL.SCREEN.blit(self.title_font2, (450, 175))
        pygame.draw.rect(GL.SCREEN, SELECTION_BOX_COLOR, self.selection_box[0].rect, SELECTION_BOX_WIDTH)
        pygame.display.update()

    def input(self):
        GL.INPUT1.refresh()
        if GL.INPUT1.QUICK_START:
            all_sprites = ['data/sprites+portraits/human_p1.png',
                           'data/sprites+portraits/elf_p1.png',
                           'data/sprites+portraits/human_p2.png',
                           'data/sprites+portraits/elf_p2.png']
            p1_sprite = random.choice(all_sprites)
            p2_sprite = random.choice([s for s in all_sprites if s != p1_sprite])
            GL.set_player1_spritesheet(p1_sprite)
            GL.set_player2_spritesheet(p2_sprite)

            arena = random.choice([GL.arena3, GL.arena4, GL.arena5])
            GL.set_level(arena)

            self.return_now = True
            GL.NEXT_PAGE = 'GameLoop()'

        if GL.INPUT1.CONFIRM:

            if self.selection_box[0] == self.start_button:
                self.return_now = True
                GL.NEXT_PAGE = 'PlayerSelectPage()'

            elif self.selection_box[0] == self.help_button:
                self.return_now = True
                GL.NEXT_PAGE = '_help'

            elif self.selection_box[0] == self.options_button:
                self.return_now = True
                GL.NEXT_PAGE = '_options'

            elif self.selection_box[0] == self.exit_button:
                EXIT_GAME()

        if GL.INPUT1.LEFT_EVENT:
            self.selection_box.rotate()

        if GL.INPUT1.RIGHT_EVENT:
            self.selection_box.rotate(-1)

        if GL.INPUT1.CANCEL:
            EXIT_GAME()

    def events(self):
        for event in pygame.event.get():
            if 'click' in self.start_button.handleEvent(event):
                while self.selection_box[0] != self.start_button:
                    self.selection_box.rotate()
                self.return_now = True
                GL.NEXT_PAGE = 'PlayerSelectPage()'

            if 'click' in self.help_button.handleEvent(event):
                while self.selection_box[0] != self.help_button:
                    self.selection_box.rotate()
                self.return_now = True
                GL.NEXT_PAGE = '_help'

            if 'click' in self.options_button.handleEvent(event):
                while self.selection_box[0] != self.options_button:
                    self.selection_box.rotate()
                self.return_now = True
                GL.NEXT_PAGE = '_options'

            if 'click' in self.exit_button.handleEvent(event):
                while self.selection_box[0] != self.exit_button:
                    self.selection_box.rotate()
                EXIT_GAME()

            if event.type == pygame.QUIT:
                EXIT_GAME()

# ----------------------------------------------------------------------------
class HelpPage:
    def __init__(self):
        self.return_button = pygbutton.PygButton((0, 550, 300, 50), 'Main Menu')
        self.section_font = pygame.font.Font('data/fonts/Kremlin.ttf', 40)
        self.font = pygame.font.Font('data/fonts/arial_narrow_7.ttf', 20)
        self.bg_image = pygame.image.load('data/backgrounds/bkg_help.png')
        self.bg_title = self.section_font.render('Background', True, WHITE)
        self.bg_text = textwrap.wrap('Under the tyranny of the dark overlord, the world ' +
                                     'is in chaos and all the resources are nearly depleted.  ' +
                                     'Entire populations have been subjugated to life in labor ' +
                                     'camps, brutally policed by the overlord\'s military forces.  ' +
                                     'As your people\'s champion, you must fight to the death in the ' +
                                     'battle arena to win much needed resources.', width=50)
        self.goals_title = self.section_font.render('Goals', True, WHITE)
        self.goals_text = textwrap.wrap('Ultimately, you want to slay your opponent.  ' +
                                        'To become a better fighter, kill the monsters, gain ' +
                                        'experience, and pick up skills.  The player to land ' +
                                        'the last hit on the monster will receives the experience ' +
                                        'points.  An ultimate boss will spawn every few ' +
                                        'minutes.  These bosses drop ultimate skills which ' +
                                        'will help you humiliate and destroy your opponent.  ' +
                                        'Muah Hah Hah!!', width=50)
        self.selection_box = deque([self.return_button])

    def __call__(self):
        self.return_now = False
        while not self.return_now:
            self.draw()
            self.input()
            self.events()
            GL.CLOCK.tick(GL.FPS)

    def draw(self):
        GL.SCREEN.fill(BLACK)
        GL.SCREEN.blit(self.bg_image, (0, 0))

        GL.SCREEN.blit(self.bg_title, (800, 40))
        for num, text in enumerate(self.bg_text):
            line = self.font.render(text, True, DKRED)
            GL.SCREEN.blit(line, (800, 90 + (num * 20)))

        GL.SCREEN.blit(self.goals_title, (800, 250))
        for num, text in enumerate(self.goals_text):
            line = self.font.render(text, True, DKRED)
            GL.SCREEN.blit(line, (800, 300 + (num * 20)))

        self.return_button.draw(GL.SCREEN)
        pygame.draw.rect(GL.SCREEN, SELECTION_BOX_COLOR, self.selection_box[0].rect, SELECTION_BOX_WIDTH)
        pygame.display.update()

    def input(self):
        GL.INPUT1.refresh()

        if GL.INPUT1.CONFIRM or GL.INPUT1.CANCEL:
            self.return_now = True
            GL.NEXT_PAGE = '_start'

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                EXIT_GAME()
            if 'click' in self.return_button.handleEvent(event):
                self.return_now = True
                GL.NEXT_PAGE = '_start'

# ----------------------------------------------------------------------------
class PlayerSelectPage:

    def __init__(self):
        def _setup_display():
            self.return_button = pygbutton.PygButton((0, 550, 300, 50), 'Main Menu')
            self.player1_spritesheet = None
            self.player2_spritesheet = None

        def _load_images():
            self.bg_image = pygame.image.load('data/backgrounds/bkg_player_select.png')
            self.humanPortrait = pygame.image.load('data/sprites+portraits/human_portrait.png')
            self.elfPortrait = pygame.image.load('data/sprites+portraits/elf_portrait.png')

            self.portraits = [self.humanPortrait, self.elfPortrait]
            self.portraits2 = [self.humanPortrait, self.elfPortrait]

            # show human portrait by default
            self.index = 0
            self.index2 = 0

        def _setup_fonts():
            self.start_font = pygame.font.Font('data/fonts/Kremlin.ttf', 50)
            self.start_font_xy = font_position_center(GL.SCREEN.get_rect(), self.start_font, '---------------Press Start when ready---------------')
            self.start_font_rendered = self.start_font.render('---------------Press Start when ready---------------', True, YELLOW)

        def _setup_flags():
            self.ready1 = False
            self.ready2 = False
            self.start = False

            # if there is a second gamepad, there is a second player
            # set ready to false if second player exists
            # if no second player, set ready to true
            if not GL.INPUT2.gamepad_found:
                self.ready2 = True

        _setup_display()
        _setup_fonts()
        _setup_flags()
        _load_images()

    def __call__(self):
        self.return_now = False
        while not self.return_now:
            self.draw()
            self.input()
            self.events()
            GL.CLOCK.tick(GL.FPS)

    def draw(self):
        GL.SCREEN.blit(self.bg_image, (0, 0))
        self.return_button.draw(GL.SCREEN)
        GL.SCREEN.blit(self.portraits[self.index], (167, 106))
        GL.SCREEN.blit(self.portraits2[self.index2], (810, 106))
        if self.ready1 and self.ready2:
            GL.SCREEN.blit(self.start_font_rendered, self.start_font_xy)
        pygame.display.update()

    def input(self):

        def refresh_inputs():
            GL.INPUT1.refresh()
            GL.INPUT2.refresh()

        def player_select_inputs():

            def check_left_right(player):
                if player == 'player1':
                    if GL.INPUT1.LEFT_EVENT:
                        self.index -= 1
                        if self.index < 0:
                            self.index = len(self.portraits) - 1

                        check_other_player('player1')

                    elif GL.INPUT1.RIGHT_EVENT:
                        self.index += 1
                        if self.index >= len(self.portraits):
                            self.index = 0

                        check_other_player('player1')

                elif player == 'player2':
                    if GL.INPUT2.LEFT_EVENT:
                        self.index2 -= 1
                        if self.index2 < 0:
                            self.index2 = len(self.portraits2) - 1

                        check_other_player('player2')

                    elif GL.INPUT2.RIGHT_EVENT:
                        self.index2 += 1
                        if self.index2 >= len(self.portraits2):
                            self.index2 = 0

                        check_other_player('player2')

            def check_other_player(player):
                if player == 'player1':
                    if self.index == self.index2 and self.ready2:  # player 2 is using character, skip index
                        self.index += 1
                        if self.index >= len(self.portraits):
                            self.index = 0
                else:
                    if self.index == self.index2 and self.ready1:  # player 2 is using character, skip index
                        self.index2 += 1
                        if self.index2 >= len(self.portraits2):
                            self.index2 = 0

            # if player 1/2 is not ready, let them select character
            if not self.ready1:
                check_left_right('player1')
            if not self.ready2:
                check_left_right('player2')

        def player_done_selecting():
            # if player presses A
            # they selected sprite
            # set sprite to player
            # if they pressed select
            # they want to select a different sprite or return to start screen
            if GL.INPUT1.CONFIRM:
                if self.ready2 and self.index2 == self.index:
                    print('Player 2 is using this character. Select a different one.')
                else:
                    print('player 1 ready')
                    self.ready1 = True

            if GL.INPUT2.CONFIRM:
                if self.ready1 and self.index2 == self.index:
                    print('Player 1 is using this character. Select a different one.')
                else:
                    print('player 2 ready')
                    self.ready2 = True

            # if player presses back when previously stated they were ready
            # allow them to reselect player
            if self.ready1 and GL.INPUT1.CANCEL:
                print('player 1 not ready anymore')
                self.ready1 = False

            elif not self.ready1 and GL.INPUT1.CANCEL:
                print('player 1 requested to go back to start')
                self.return_now = True
                GL.NEXT_PAGE = '_start'

            if self.ready2 and GL.INPUT2.CANCEL:
                print('player 2 not ready anymore')
                self.ready2 = False

            elif not self.ready2 and GL.INPUT2.CANCEL:
                print('player 2 requested to go back to start')
                self.return_now = True
                GL.NEXT_PAGE = '_start'

        def ready_for_start():
            if self.ready1 and self.ready2:

                # if player 1 or player 2 presses start when both players are ready
                # go to level select
                # if using a keyboard - only one player
                # if keyboard user presses 'A' when he is ready
                # go to level select
                if GL.INPUT1.CONFIRM or GL.INPUT2.CONFIRM:
                    self.start = True
                    print('setting sprites')
                    set_sprites()
                    print('set sprites')
                    print('going to level select screen')
                    GL.NEXT_PAGE = 'LevelSelectPage()'
                    self.return_now = True

        def set_sprites():
            # set spritesheet for player1
            if self.index == 0:  # human
                self.player1_spritesheet = 'data/sprites+portraits/human_p1.png'
            elif self.index == 1:  # elf
                self.player1_spritesheet = 'data/sprites+portraits/elf_p1.png'

            # set spritesheet for player2
            if self.index2 == 0:  # human
                self.player2_spritesheet = 'data/sprites+portraits/human_p2.png'
            elif self.index2 == 1:  # elf
                self.player2_spritesheet = 'data/sprites+portraits/elf_p2.png'

            GL.set_player1_spritesheet(self.player1_spritesheet)
            GL.set_player2_spritesheet(self.player2_spritesheet)

        refresh_inputs()
        player_select_inputs()
        player_done_selecting()
        ready_for_start()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                EXIT_GAME()
            if 'click' in self.return_button.handleEvent(event):
                self.return_now = True
                GL.NEXT_PAGE = '_start'

# ----------------------------------------------------------------------------
class LevelSelectPage:
    def __init__(self):
        def _setup_display():
            self.return_button = pygbutton.PygButton((0, 550, 300, 50), 'Main Menu')
            self.ready = False

        def _load_images():
            self.bg_image = pygame.image.load('data/backgrounds/bkg_level_select.png')
            self.bg_image2 = pygame.image.load('data/backgrounds/bkg_level_select2.png')
            self.humanLevel = pygame.image.load('data/backgrounds/arena_human.png')
            self.elfLevel = pygame.image.load('data/backgrounds/arena_vines.png')
            self.androidLevel = pygame.image.load('data/backgrounds/arena_android.png')
            self.levels = [self.humanLevel, self.elfLevel, self.androidLevel]
            self.outerX = [19, 444, 874]
            self.innerX = [24, 450, 878]
            self.index = 0

        _setup_display()
        _load_images()

    def __call__(self):
        self.return_now = False
        while not self.return_now:
            self.input()
            self.draw()
            self.events()
            GL.CLOCK.tick(GL.FPS)

    def draw(self):
        GL.SCREEN.blit(self.bg_image, (0, 0))
        outer_highlight = Rect2(topleft=(self.outerX[self.index], 184), size = (389, 173), color=(20, 118, 128))
        inner_highlight = Rect2(topleft=(self.innerX[self.index], 190), size=(379, 162), color=(80, 191, 201))
        pygame.draw.rect(GL.SCREEN, outer_highlight.color, outer_highlight)
        pygame.draw.rect(GL.SCREEN, inner_highlight.color, inner_highlight)
        GL.SCREEN.blit(self.bg_image2, (0, 0))
        self.return_button.draw(GL.SCREEN)
        pygame.display.update()

    def input(self):
        GL.INPUT1.refresh()  # only player 1 can select level

        if GL.INPUT1.LEFT_EVENT:
            self.index -= 1
            if self.index < 0:
                self.index = len(self.levels) - 1

        if GL.INPUT1.RIGHT_EVENT:
            self.index += 1
            if self.index >= len(self.levels):
                self.index = 0

        if GL.INPUT1.CANCEL:
            GL.NEXT_PAGE = 'PlayerSelectPage()'
            self.return_now = True

        def ready_check():
            if GL.INPUT1.CONFIRM:
                print('ready to load')
                self.ready = True
                set_level()
                GL.NEXT_PAGE = 'GameLoop()'
                self.return_now = True

        def set_level():
            print('setting level')
            if self.index == 0:
                arena = arena4
            elif self.index == 1:
                arena = arena3
            elif self.index == 2:
                arena = arena5

            GL.set_level(arena)
            print('set level')

        ready_check()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                EXIT_GAME()
            if 'click' in self.return_button.handleEvent(event):
                self.return_now = True
                GL.NEXT_PAGE = '_start'

# ----------------------------------------------------------------------------
class OptionsPage:
    def __init__(self):
        self.bg_image = pygame.image.load('data/backgrounds/bkg_start_page.png')
        self.active_colors = BLACK, DKRED
        self.inactive_colors = DKRED, BLACK

        self.main_menu_button = pygbutton.PygButton((0, 550, 300, 50), 'Main Menu')
        self.music_on_button = pygbutton.PygButton((650, 200, 60, 50), 'ON')
        self.sound_on_button = pygbutton.PygButton((650, 260, 60, 50), 'ON')
        self.music_off_button = pygbutton.PygButton((730, 200, 80, 50), 'OFF')
        self.sound_off_button = pygbutton.PygButton((730, 260, 80, 50), 'OFF')

        font = pygame.font.Font('data/fonts/Kremlin.ttf', 40)
        self.bg_font = font.render('Music:', True, DKRED)
        self.se_font = font.render('Sound:', True, DKRED)

        self.selection_box = deque([
            deque([self.main_menu_button]),
            deque([self.sound_on_button, self.sound_off_button]),
            deque([self.music_on_button, self.music_off_button]),
        ])

        if not AUDIO.music_on:
            self.selection_box[0].rotate()
        if not AUDIO.sound_on:
            self.selection_box[1].rotate()

    def __call__(self):
        self.return_now = False
        while not self.return_now:
            self.draw()
            self.input()
            self.events()
            GL.CLOCK.tick(GL.FPS)

    def draw(self):
        if AUDIO.music_on:
            self.music_on_button.fgcolor, self.music_on_button.bgcolor = self.active_colors
            self.music_off_button.fgcolor, self.music_off_button.bgcolor = self.inactive_colors
        else:
            self.music_on_button.fgcolor, self.music_on_button.bgcolor = self.inactive_colors
            self.music_off_button.fgcolor, self.music_off_button.bgcolor = self.active_colors

        if AUDIO.sound_on:
            self.sound_on_button.fgcolor, self.sound_on_button.bgcolor = self.active_colors
            self.sound_off_button.fgcolor, self.sound_off_button.bgcolor = self.inactive_colors
        else:
            self.sound_on_button.fgcolor, self.sound_on_button.bgcolor = self.inactive_colors
            self.sound_off_button.fgcolor, self.sound_off_button.bgcolor = self.active_colors

        GL.SCREEN.blit(self.bg_image, (0, 0))
        GL.SCREEN.blit(self.bg_font, (450, 200))
        GL.SCREEN.blit(self.se_font, (450, 260))
        self.music_on_button.draw(GL.SCREEN)
        self.music_off_button.draw(GL.SCREEN)
        self.sound_on_button.draw(GL.SCREEN)
        self.sound_off_button.draw(GL.SCREEN)
        self.main_menu_button.draw(GL.SCREEN)

        pygame.draw.rect(GL.SCREEN, SELECTION_BOX_COLOR, self.selection_box[0][0].rect, SELECTION_BOX_WIDTH)
        pygame.display.update()

    def input(self):
        GL.INPUT1.refresh()

        if GL.INPUT1.CONFIRM:
            if self.selection_box[0][0] == self.main_menu_button:
                self.return_now = True
                GL.NEXT_PAGE = '_start'

        if GL.INPUT1.CANCEL:
            if self.selection_box[0][0] == self.main_menu_button:  # if already on main menu button when hit select / b ..
                self.return_now = True  # .. then return
                GL.NEXT_PAGE = '_start'
            else:  # if not on main menu button when hit select / b ..
                while self.selection_box[0][0] != self.main_menu_button:  # .. then go to return button
                    self.selection_box.rotate()

        if GL.INPUT1.UP_EVENT:
            self.selection_box.rotate(-1)

        if GL.INPUT1.DOWN_EVENT:
            self.selection_box.rotate()

        if GL.INPUT1.LEFT_EVENT or GL.INPUT1.RIGHT_EVENT:
            if GL.INPUT1.LEFT_EVENT:
                self.selection_box[0].rotate()
            if GL.INPUT1.RIGHT_EVENT:
                self.selection_box[0].rotate(-1)

            if self.selection_box[0][0] == self.sound_on_button:
                AUDIO.turn_on_effects()
            elif self.selection_box[0][0] == self.sound_off_button:
                AUDIO.turn_off_effects()
            elif self.selection_box[0][0] == self.music_on_button:
                AUDIO.turn_on_music()
            elif self.selection_box[0][0] == self.music_off_button:
                AUDIO.turn_off_music()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                EXIT_GAME()

            if 'click' in self.music_on_button.handleEvent(event):
                while self.selection_box[0][0] not in (self.music_on_button, self.music_off_button):
                    self.selection_box.rotate()
                while self.selection_box[0][0] != self.music_on_button:
                    self.selection_box[0].rotate()
                AUDIO.turn_on_music()

            if 'click' in self.music_off_button.handleEvent(event):
                while self.selection_box[0][0] not in (self.music_on_button, self.music_off_button):
                    self.selection_box.rotate()
                while self.selection_box[0][0] != self.music_off_button:
                    self.selection_box[0].rotate()
                AUDIO.turn_off_music()

            if 'click' in self.sound_on_button.handleEvent(event):
                while self.selection_box[0][0] not in (self.sound_on_button, self.sound_off_button):
                    self.selection_box.rotate()
                while self.selection_box[0][0] != self.sound_on_button:
                    self.selection_box[0].rotate()
                AUDIO.turn_on_effects()

            if 'click' in self.sound_off_button.handleEvent(event):
                while self.selection_box[0][0] not in (self.sound_on_button, self.sound_off_button):
                    self.selection_box.rotate()
                while self.selection_box[0][0] != self.sound_off_button:
                    self.selection_box[0].rotate()
                AUDIO.turn_off_effects()

            if 'click' in self.main_menu_button.handleEvent(event):
                while self.selection_box[0][0] != self.main_menu_button:
                    self.selection_box.rotate()
                self.return_now = True
                GL.NEXT_PAGE = '_start'

# ----------------------------------------------------------------------------
class PausePage:
    def __init__(self):
        self.bg_image = pygame.image.load('data/backgrounds/bkg_menus_dim.png')
        self.menu_box = Rect2(topleft=(320, 120), size=(640, 240), border_color=BLACK, fill_color=DGREY)
        main_font = 'data/fonts/Kremlin.ttf'
        pause_font = pygame.font.Font(main_font, 100)
        self.pause_font_xy = font_position_center(self.menu_box, pause_font, '-PAUSE-')
        self.pause_font_rendered = pause_font.render('-PAUSE-', True, RED)
        self.continue_button = pygbutton.PygButton((395, 270, 200, 50), 'Continue')
        self.quit_button = pygbutton.PygButton((730, 270, 100, 50), 'Quit')
        self.selection_box = deque([self.continue_button, self.quit_button])

    def __call__(self):
        self.return_now = False
        while not self.return_now:
            self.draw()
            self.input()
            self.events()
            GL.CLOCK.tick(GL.FPS)
        while self.selection_box[0] != self.continue_button:  # reset selection box to 'continue'
            self.selection_box.rotate()

    def draw(self):
        scaled_bg = pygame.transform.scale(self.bg_image, self.menu_box.size)
        GL.SCREEN.blit(scaled_bg, self.menu_box.topleft)
        pygame.draw.rect(GL.SCREEN, self.menu_box.border_color, self.menu_box, 4)
        GL.SCREEN.blit(self.pause_font_rendered, (self.pause_font_xy[0], self.menu_box.top))
        self.continue_button.draw(GL.SCREEN)
        self.quit_button.draw(GL.SCREEN)
        pygame.draw.rect(GL.SCREEN, SELECTION_BOX_COLOR, self.selection_box[0].rect, SELECTION_BOX_WIDTH)
        pygame.display.update()

    def input(self):
        GL.INPUT1.refresh_during_pause()

        if GL.INPUT1.CONFIRM:
            self.return_now = True

            if self.selection_box[0] == self.continue_button:
                GL.NEXT_PAGE = 'GL.CURR_GAME'

            elif self.selection_box[0] == self.quit_button:
                GL.NEXT_PAGE = '_start'

        if GL.INPUT1.LEFT_EVENT:
            self.selection_box.rotate()

        if GL.INPUT1.RIGHT_EVENT:
            self.selection_box.rotate(-1)

        if GL.INPUT1.CANCEL:
            self.return_now = True
            GL.NEXT_PAGE = 'GL.CURR_GAME'

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                EXIT_GAME()

            if 'click' in self.continue_button.handleEvent(event):
                self.return_now = True
                GL.NEXT_PAGE = 'GL.CURR_GAME'

            if 'click' in self.quit_button.handleEvent(event):
                self.return_now = True
                GL.NEXT_PAGE = '_start'

# ----------------------------------------------------------------------------
class GameOverPage:
    def __init__(self):
        self.bg_image = pygame.image.load('data/backgrounds/bkg_menus_dim.png')
        self.menu_box = Rect2(topleft=(320, 120), size=(640, 240), border_color=BLACK, fill_color=DGREY)
        main_font = 'data/fonts/Kremlin.ttf'
        game_over_font = pygame.font.Font(main_font, 95)
        self.game_over_xy = font_position_center(self.menu_box, game_over_font, '-Game Over-')
        self.game_over_rendered = game_over_font.render('-Game Over-', True, RED)
        self.main_menu_button = pygbutton.PygButton((395, 270, 200, 50), 'Main Menu')
        self.exit_button = pygbutton.PygButton((730, 270, 100, 50), 'Exit')
        self.selection_box = deque([self.main_menu_button, self.exit_button])

    def __call__(self):
        self.return_now = False
        while not self.return_now:
            self.draw()
            self.input()
            self.events()
            GL.CLOCK.tick(GL.FPS)

    def draw(self):
        scaled_bg = pygame.transform.scale(self.bg_image, self.menu_box.size)
        GL.SCREEN.blit(scaled_bg, self.menu_box.topleft)
        pygame.draw.rect(GL.SCREEN, self.menu_box.border_color, self.menu_box, 4)
        GL.SCREEN.blit(self.game_over_rendered, (self.game_over_xy[0], self.menu_box.top))
        self.main_menu_button.draw(GL.SCREEN)
        self.exit_button.draw(GL.SCREEN)
        pygame.draw.rect(GL.SCREEN, SELECTION_BOX_COLOR, self.selection_box[0].rect, SELECTION_BOX_WIDTH)
        pygame.display.update()

    def input(self):
        GL.INPUT1.refresh_during_pause()

        if GL.INPUT1.CANCEL:
            self.return_now = True
            GL.NEXT_PAGE = '_start'

        if GL.INPUT1.CONFIRM:

            if self.selection_box[0] == self.main_menu_button:
                self.return_now = True
                GL.NEXT_PAGE = '_start'

            elif self.selection_box[0] == self.exit_button:
                EXIT_GAME()

        if GL.INPUT1.LEFT_EVENT:
            self.selection_box.rotate()

        if GL.INPUT1.RIGHT_EVENT:
            self.selection_box.rotate(-1)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                EXIT_GAME()

            if 'click' in self.main_menu_button.handleEvent(event):
                while self.selection_box[0] != self.main_menu_button:
                    self.selection_box.rotate()
                self.return_now = True
                GL.NEXT_PAGE = '_start'

            if 'click' in self.exit_button.handleEvent(event):
                while self.selection_box[0] != self.exit_button:
                    self.selection_box.rotate()
                EXIT_GAME()
