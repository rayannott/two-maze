import pygame

from game import Game
from mazes import TC, TT, TileItemType
from gui.gui_rect import Button, Panel
from gui.gui_utils import *
from utils.constants import NUM_OF_MAZES

TILE_SIZE = 40
SKIP_SIZE = 2
BIG_SKIP_SIZE = 5
CHOOSE_MAZE_BTN_SIZE = 50

class GameGUI1:
    '''GUI for the first player (P1)'''
    def __init__(self, game: Game, surface: pygame.Surface) -> None:
        self.game = game
        self.chosen_maze_idx = 0
        self.grid_shape = self.game.mazes[0].grid_shape
        pygame.init()
        self.surface = surface
        self.clock = pygame.time.Clock()
        self.is_running = True

        self._create_mazes_panel()
        self._create_maze_control_panel()
    
    def _create_mazes_panel(self):
        self.mazes_panel = Panel(
            (20, 20), 
            (self.grid_shape[1]*(TILE_SIZE + SKIP_SIZE) + SKIP_SIZE, 
                    self.grid_shape[0]*(TILE_SIZE + SKIP_SIZE) + SKIP_SIZE),
            self.surface
        )
    
    def _create_maze_control_panel(self):
        self.maze_control_panel = Panel(
            (self.mazes_panel.rect.topright[0] + 2 * SKIP_SIZE, 20),
            (4*CHOOSE_MAZE_BTN_SIZE + 5 * BIG_SKIP_SIZE, 400),
            self.surface,
        )
        for i in range(len(self.game.mazes)):
            self.maze_control_panel.populate_one(
                str(i),
                Button(
                    (BIG_SKIP_SIZE + (CHOOSE_MAZE_BTN_SIZE + BIG_SKIP_SIZE) * i, BIG_SKIP_SIZE), 
                    (CHOOSE_MAZE_BTN_SIZE, CHOOSE_MAZE_BTN_SIZE), self.surface, f'M{i}', f'choose maze {i}',
                    parent=self.maze_control_panel
                )
            )

    def draw_maze(self, maze_index: int):
        for i in range(self.grid_shape[0]):
            for j in range(self.grid_shape[1]):
                this_tile = self.game.mazes[maze_index].maze[i][j]
                if this_tile.visible:
                    fill_color = (10, 10, 10) if this_tile._type == TT.WALL else (255, 255, 255)
                else:
                    fill_color = (120, 120, 120)
                pygame.draw.rect(self.surface, fill_color, 
                    pygame.rect.Rect(20 + SKIP_SIZE + (SKIP_SIZE + TILE_SIZE)*j, 
                                    SKIP_SIZE + 20 + (SKIP_SIZE + TILE_SIZE)*i, TILE_SIZE, TILE_SIZE),
                    border_radius=2
                )

    def maze_tile_hovering(self, pos):
        '''Returns the coordinates of the Tile hovering'''
        x = pos[0] - 20; y = pos[1] - 20
        j = x // (TILE_SIZE + SKIP_SIZE)
        i = y // (TILE_SIZE + SKIP_SIZE)
        return i, j

    def update_gui(self, pos):
        self.mazes_panel.update(pos)
        self.maze_control_panel.update(pos)
        self.draw_maze(self.chosen_maze_idx)

    def run(self):
        while self.is_running:
            self.clock.tick(FRAMERATE)
            self.surface.fill(BLACK)
            pos = pygame.mouse.get_pos()

            # update gui
            self.update_gui(pos)

            # process events
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.is_running = False
                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.maze_control_panel.clicked():
                        obj_clicked = self.maze_control_panel.object_clicked()
                        if not obj_clicked: continue
                        if int(obj_clicked) in range(len(self.game.mazes)):
                            self.chosen_maze_idx = int(obj_clicked)
                    elif self.mazes_panel.clicked():
                        coord = self.maze_tile_hovering(pos)
                        print(coord, self.game.mazes[self.chosen_maze_idx].maze[coord[0]][coord[1]])
            pygame.display.update()
