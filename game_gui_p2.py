import pygame

from game import Game
from gui.gui_utils import *


class GameGUI2:
    '''GUI for the second player (P2)'''
    def __init__(self, game: Game, surface: pygame.Surface) -> None:
        self.game = game
        pygame.init()
        self.surface = surface
        self.clock = pygame.time.Clock()
        self.is_running = True

    def run(self):
        while self.is_running:
            self.clock.tick(FRAMERATE)
            self.surface.fill(BLACK)
            pos = pygame.mouse.get_pos()

            # update gui
            # self.update_gui(pos)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.is_running = False
            pygame.display.update()
