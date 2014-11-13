#COLOR = (RRR, GGG, BBB)
from pygame import Color

BLACK = Color(0, 0, 0)
DGREY = Color(64, 64, 64)
WHITE = Color(255, 255, 255)

RED = Color(255, 0, 0)
DKRED = Color(128, 0, 0)
DKGREEN = Color(0, 128, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)
LBLUE = Color(0, 128, 255)
SKYBLUE = Color(128, 223, 223)

YELLOW = Color(255, 255, 0)
PURPLE = Color(255, 0, 255)
ORANGE = Color(255, 153, 0)

LEFT = 'LEFT'
RIGHT = 'RIGHT'
UP = 'UP'
DOWN = 'DOWN'
JUMP = 'JUMP'
ATTACK = 'ATTACK'
DEBUG = 'DEBUG'
EXIT = 'EXIT'
RESET = 'RESET'


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


def font_position_center(center_within_size, font, text):
    x = (center_within_size[0] - font.size(text)[0]) // 2
    y = (center_within_size[1] - font.size(text)[1]) // 2
    return x, y