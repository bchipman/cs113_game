# python standard library modules
import os
import sys
import textwrap
import pygbutton

# pygame
import pygame
from pygame.locals import *

# our modules
from classes import *
from globals import *
from skills import *
from main import *

class HelpPage:
    def __init__(self, start_menu=None):
        def _setup_display():
            pygame.display.set_mode((1280, 600))
            pygame.display.set_caption('Famished Tournament')
            self.screen = pygame.display.get_surface()
            self.return_button = pygbutton.PygButton((0, 550, 300, 50), 'Main Menu')

        def _setup_time():
            self.clock = pygame.time.Clock()
            self.fps = 5

        self.section_font = pygame.font.Font('data/Kremlin.ttf', 40)
        self.font = pygame.font.Font('data/arial_narrow_7.ttf', 20)
        self.start_menu = start_menu
        _setup_display()
        _setup_time()

    def __call__(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if 'click' in self.return_button.handleEvent(event):
                    self.start_menu()

            self.draw_screen()
            self.clock.tick(self.fps)

    def draw_screen(self):
        self.image = pygame.image.load('data/Evil_Eyes.png')
        self.screen.blit(self.image, (0,245))
        self.add_text()
        self.return_button.draw(self.screen)

        pygame.display.flip()

    def add_text(self):
        # text wrapper creates a list of text
        # for each item in the list
        # print the line
        self.bkg_title = self.section_font.render('Background', True, WHITE)
        self.screen.blit(self.bkg_title, (800, 40))

        self.bkg_text = textwrap.wrap('Under the tyranny of the dark overlord, the world' +
                                      'is in chaos and all the resources are nearly depleted. ' +
                                      'Entire populations have been subjugated to life in labor ' +
                                      'camps, brutally policed by the overlord\'s military forces. ' +
                                      'As your people\'s champion, you must fight to the death in the ' +
                                      'battle arena to win much needed resources.', width=50)
        i = 0
        for t in self.bkg_text:
            self.line = self.font.render(t, True, DKRED)
            self.screen.blit(self.line, (800, 90 + (i * 20)))
            i += 1

        self.goals_title = self.section_font.render('Goals', True, WHITE)
        self.screen.blit(self.goals_title, (800, 250))

        self.goals_text = textwrap.wrap('Ultimately, you want to slay your opponent. ' +
                                        'To become a better fighter, kill the monsters, gain ' +
                                        'experience, and pick up skills. The player to land ' +
                                        'the last hit on the monster will receives the experience ' +
                                        'points. An ultimate boss will spawn every few ' +
                                        'minutes. These bosses drop ultimate skills which ' +
                                        'will help you humiliate and destroy your opponent.', width=50)

        j = 0
        for t in self.goals_text:
            self.line = self.font.render(t, True, DKRED)
            self.screen.blit(self.line, (800, 300 + (j * 20)))
            j += 1

# -------------------------------------------------------------------------
class OptionsPage:
    def __init__(self, start_menu=None):
        def _setup_display():
            pygame.display.set_mode((1280, 600))
            pygame.display.set_caption('Famished Tournament')
            self.screen = pygame.display.get_surface()
            self.bkg_image = pygame.image.load('data/temp_start_bkg.png')
            self.screen.blit(self.bkg_image, (0, 0))

            self.active_colors = BLACK, DKRED
            self.inactive_colors = DKRED, BLACK

            m_on = s_on = self.inactive_colors
            m_off = s_off = self.active_colors

            if AUDIO.music_on:
                m_on, m_off = self.active_colors, self.inactive_colors

            if AUDIO.sound_on:
                s_on, s_off = self.active_colors, self.inactive_colors

            self.music_on_button = pygbutton.PygButton((650, 200, 60, 50), 'ON', fgcolor=m_on[0], bgcolor=m_on[1])
            self.music_off_button = pygbutton.PygButton((730, 200, 80, 50), 'OFF', fgcolor=m_off[0], bgcolor=m_off[1])
            self.effects_on_button = pygbutton.PygButton((770, 260, 60, 50), 'ON', fgcolor=s_on[0], bgcolor=s_on[1])
            self.effects_off_button = pygbutton.PygButton((850, 260, 80, 50), 'OFF', fgcolor=s_off[0], bgcolor=s_off[1])
            self.return_button = pygbutton.PygButton((0, 550, 300, 50), 'Main Menu')

            self.draw_screen()


        def _setup_time():
            self.clock = pygame.time.Clock()
            self.fps = 5

        self.font = pygame.font.Font('data/Kremlin.ttf', 40)
        self.start_menu = start_menu
        _setup_display()
        _setup_time()

    def __call__(self):
        while True:
            self.draw_screen()
            self.handle_events()
            self.clock.tick(self.fps)

    def draw_screen(self):
        self.bkg_music_font = self.font.render('Music:', True, DKRED)
        self.se_font = self.font.render('Sound Effects:', True, DKRED)
        self.screen.blit(self.bkg_music_font, (500, 200))
        self.screen.blit(self.se_font, (400, 260))
        self.music_on_button.draw(self.screen)
        self.music_off_button.draw(self.screen)
        self.effects_on_button.draw(self.screen)
        self.effects_off_button.draw(self.screen)
        self.return_button.draw(self.screen)
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # button click event handling
            if 'click' in self.music_on_button.handleEvent(event):
                self.music_on_button.fgcolor, self.music_on_button.bgcolor = self.active_colors
                self.music_off_button.fgcolor, self.music_off_button.bgcolor = self.inactive_colors
                AUDIO.turn_on_music()

            if 'click' in self.music_off_button.handleEvent(event):
                self.music_on_button.fgcolor, self.music_on_button.bgcolor = self.inactive_colors
                self.music_off_button.fgcolor, self.music_off_button.bgcolor = self.active_colors
                AUDIO.turn_off_music()

            if 'click' in self.effects_on_button.handleEvent(event):
                self.effects_on_button.fgcolor, self.effects_on_button.bgcolor = self.active_colors
                self.effects_off_button.fgcolor, self.effects_off_button.bgcolor = self.inactive_colors
                AUDIO.turn_on_effects()

            if 'click' in self.effects_off_button.handleEvent(event):
                self.effects_on_button.fgcolor, self.effects_on_button.bgcolor = self.inactive_colors
                self.effects_off_button.fgcolor, self.effects_off_button.bgcolor = self.active_colors
                AUDIO.turn_off_effects()

            if 'click' in self.return_button.handleEvent(event):
                self.start_menu()
