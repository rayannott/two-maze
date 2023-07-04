from typing import Literal
import numpy as np
import pygame

from game import Game
from gui.gui_rect import Panel, Button, Label
from gui.gui_utils import *
from mazes import TC, Tile, TT

CONTROL_PANEL_SIZE = (900, 900)
CURRENT_TILE_PANEL_SIZE = (450, 450)
MOVE_BTN_SIZE = (300, 100)


class GameGUI2:
    '''GUI for the second player (P2)'''
    def __init__(self, game: Game, surface: pygame.Surface) -> None:
        self.game = game
        pygame.init()
        self.surface = surface
        self.clock = pygame.time.Clock()
        self.is_running = True

        self.position: tuple[int, int, int] = self.game.starting_position
        print('init position', self.position)
        self.letters_collected: list[str] = []
        self.revealed_checkpoints: list[int] = [] # only their codes

        self.tile_and_neigh_cache: tuple[Tile, Tile, Tile, Tile, Tile] | None = None

        self._create_control_panel()

    def _create_control_panel(self):
        self.control_panel = Panel(
            ((WINDOW_SIZE[0] - CONTROL_PANEL_SIZE[0])//2, (WINDOW_SIZE[1] - CONTROL_PANEL_SIZE[1])//2),
            CONTROL_PANEL_SIZE,
            self.surface,
        )
        self.current_tile_panel = Panel(
            ((CONTROL_PANEL_SIZE[0] - CURRENT_TILE_PANEL_SIZE[0])//2, (CONTROL_PANEL_SIZE[1] - CURRENT_TILE_PANEL_SIZE[1])//2),
            CURRENT_TILE_PANEL_SIZE,
            self.surface,
            parent=self.control_panel
        )
        # TODO: add button ACT and label INFO
        self.control_panel.populate_one(
            'current_tile_panel',
            self.current_tile_panel
        )
        self.control_panel.populate_many({
            'up': Button(
                (CONTROL_PANEL_SIZE[0]//2 - MOVE_BTN_SIZE[0]//2, (CONTROL_PANEL_SIZE[1] - CURRENT_TILE_PANEL_SIZE[1])//4 - MOVE_BTN_SIZE[1]//2),
                MOVE_BTN_SIZE, self.surface, 'UP', 'move up', parent=self.control_panel
            ),
            'down': Button(
                (CONTROL_PANEL_SIZE[0]//2 - MOVE_BTN_SIZE[0]//2, CONTROL_PANEL_SIZE[1] - (CONTROL_PANEL_SIZE[1] - CURRENT_TILE_PANEL_SIZE[1])//4 - MOVE_BTN_SIZE[1]//2),
                MOVE_BTN_SIZE, self.surface, 'DOWN', 'move down', parent=self.control_panel
            ),
            'right': Button(
                (CONTROL_PANEL_SIZE[0] - (CONTROL_PANEL_SIZE[0] - CURRENT_TILE_PANEL_SIZE[0])//4 - MOVE_BTN_SIZE[1]//2, CONTROL_PANEL_SIZE[1]//2 - MOVE_BTN_SIZE[0]//2),
                (MOVE_BTN_SIZE[1], MOVE_BTN_SIZE[0]), self.surface, 'RIGHT', 'move right', parent=self.control_panel
            ),
            'left': Button(
                ((CONTROL_PANEL_SIZE[0] - CURRENT_TILE_PANEL_SIZE[0])//4 - MOVE_BTN_SIZE[1]//2, CONTROL_PANEL_SIZE[1]//2 - MOVE_BTN_SIZE[0]//2),
                (MOVE_BTN_SIZE[1], MOVE_BTN_SIZE[0]), self.surface, 'LEFT', 'move left', parent=self.control_panel
            )
        })

    def _choose_btn_border_color(self, tile: Tile):
        if tile._type == TT.WALL: return LIGHT_GREY
        return COLORS_HEX[tile.color.value]

    def update_control_btns_colors(self):
        if self.tile_and_neigh_cache is None:
            self.tile_and_neigh_cache = self.get_this_tile_and_neigh()
            print('new cache', self.tile_and_neigh_cache)
        this_tile, up_tile, down_tile, right_tile, left_tile = self.tile_and_neigh_cache
        self.control_panel.gui_objects['current_tile_panel'].set_frame_color(
            self._choose_btn_border_color(this_tile)
        )
        self.control_panel.gui_objects['up'].set_frame_color(
            self._choose_btn_border_color(up_tile)
        )
        self.control_panel.gui_objects['down'].set_frame_color(
            self._choose_btn_border_color(down_tile)
        )
        self.control_panel.gui_objects['right'].set_frame_color(
            self._choose_btn_border_color(right_tile)
        )
        self.control_panel.gui_objects['left'].set_frame_color(
            self._choose_btn_border_color(left_tile)
        )

    def update_gui(self, pos):
        self.control_panel.update(pos)
        self.update_control_btns_colors()
    
    def get_this_tile_and_neigh(self) -> tuple[Tile, Tile, Tile, Tile, Tile]:
        maze_id, i, j = self.position
        this_tile = self.game.mazes[maze_id].maze[i][j]
        up_tile = self.game.mazes[maze_id].maze[i-1][j]
        down_tile = self.game.mazes[maze_id].maze[i+1][j]
        left_tile = self.game.mazes[maze_id].maze[i][j-1]
        right_tile = self.game.mazes[maze_id].maze[i][j+1]
        return this_tile, up_tile, down_tile, right_tile, left_tile
    
    def move_character_to(self, direction: Literal['up', 'down', 'right', 'left']):
        this_tile, up_tile, down_tile, right_tile, left_tile = self.tile_and_neigh_cache
        if direction == 'up' and up_tile._type == TT.PASS:
            self.position = (self.position[0], self.position[1]-1, self.position[2])
            self.tile_and_neigh_cache = None
        elif direction == 'down' and down_tile._type == TT.PASS:
            self.position = (self.position[0], self.position[1]+1, self.position[2])
            self.tile_and_neigh_cache = None
        elif direction == 'right' and right_tile._type == TT.PASS:
            self.position = (self.position[0], self.position[1], self.position[2]+1)
            self.tile_and_neigh_cache = None
        elif direction == 'left' and left_tile._type == TT.PASS:
            self.position = (self.position[0], self.position[1], self.position[2]-1)
            self.tile_and_neigh_cache = None
        else:
            print('cannot move!')

    def run(self):
        while self.is_running:
            self.clock.tick(FRAMERATE)
            self.surface.fill(BLACK)
            pos = pygame.mouse.get_pos()

            # update gui
            self.update_gui(pos)

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.is_running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.control_panel.clicked():
                        obj_clicked = self.control_panel.object_clicked()
                        print(obj_clicked)
                        if obj_clicked in {'up', 'down', 'right', 'left'}:
                            self.move_character_to(direction=obj_clicked)
                        else:
                            pass
                        # if obj_clicked == 'up':
                        #     print('up')
                        # elif obj_clicked == 'down':
                        #     print('down')
                        # elif obj_clicked == 'right':
                        #     print('right')
                        # elif obj_clicked == 'left':
                        #     print('left')
                        # else:
                        #     ...
                    print('current pos:', self.position)
            pygame.display.update()
