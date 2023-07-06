import pathlib

import pygame

FRAMERATE = 60

WHITE = '#FFFFFF'
BLACK = '#000000'
GREY = '#333333'
LIGHT_GREY = '#646464'
GREEN = '#00FF00'
RED = '#FF0000'
CP0 = ('#DB5294', '#52DB9A') # cool color pair number 0
CP1 = ('#AE5DDA', '#89DA5D')

COLORS_INTS = [
    [255, 255, 255],
    [ 50, 200, 190],
    [200,  40, 210],
    [200, 220,  30]
]

# white cyan magenta yellow
COLORS_HEX = [
    '#FFFFFF',
    '#32C8BE',
    '#C828D2',
    '#C8DC1E'
]

pygame.font.init()
# TODO add new fonts
assets_dir = pathlib.Path('assets'); dir_name = pathlib.Path('main_font.ttf')
FONT_SMALL = pygame.font.Font(assets_dir/dir_name, 14)
FONT_NORM = pygame.font.Font(assets_dir/dir_name, 20)
FONT_BIG = pygame.font.Font(assets_dir/dir_name, 34)
FONT_HUGE = pygame.font.Font(assets_dir/dir_name, 50)

WINDOW_SIZE = pygame.display.set_mode((0, 0), pygame.FULLSCREEN).get_size()

def shift(tup1: tuple, tup2: tuple) -> tuple:
    return tup1[0] + tup2[0], tup1[1] + tup2[1]
