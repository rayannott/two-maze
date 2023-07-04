import pygame
import numpy as np
import random

from game import Game
from mazes import TC, TT, TileItemType
from gui.gui_rect import Button, Label, Panel, TextEntry
from gui.gui_utils import *
from utils.constants import NUM_OF_MAZES, PER_MAP_COLOR_MARKS_SHOWN, SOMETHING_HINTS_SHOWN


COLORS_INTS = [
    [255, 255, 255],
    [ 50, 200, 190],
    [200,  40, 210],
    [200, 220,  30]
]

TILE_ITEM_TYPES_COLORS = [
    [],
    [250, 10, 10]
]

TILE_SIZE = 40
SKIP_SIZE = 2
BIG_SKIP_SIZE = 5
CHOOSE_MAZE_BTN_SIZE = 50


class GameGUI1:
    '''GUI for the first player (P1)'''
    def __init__(self, game: Game, surface: pygame.Surface) -> None:
        self.game = game
        self.chosen_maze_idx = 0
        self.grid_shape = self.game.grid_shape
        pygame.init()
        self.surface = surface
        self.clock = pygame.time.Clock()
        self.is_running = True
        self.feedback = ''; self.feedback_color = WHITE
        print(self.game.checkpoint_codes)

        # visual notes/marks:
        self.mazes_color_map = np.zeros((NUM_OF_MAZES, *self.grid_shape), dtype=int)
        self.mazes_markers_map = np.zeros((NUM_OF_MAZES, *self.grid_shape), dtype=int)
        self.mazes_boolean_map = np.zeros((NUM_OF_MAZES, *self.grid_shape), dtype=int)
        self.revealed_checkpoints: dict[tuple[int, int, int], int] = {}

        # creating the panels:
        self._create_mazes_panel()
        self._create_maze_control_panel()
        self._create_command_line_panel()

        # text entries:
        self.text_entries: list[TextEntry] = [
            self.command_line_panel.gui_objects['text_entry']
        ]

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
            (6*CHOOSE_MAZE_BTN_SIZE + 7 * BIG_SKIP_SIZE, 2*BIG_SKIP_SIZE+CHOOSE_MAZE_BTN_SIZE),
            self.surface, 'choose the maze'
        )
        for i in range(len(self.game.mazes)):
            self.maze_control_panel.populate_one(
                str(i),
                Button(
                    (BIG_SKIP_SIZE + (CHOOSE_MAZE_BTN_SIZE + BIG_SKIP_SIZE) * i, BIG_SKIP_SIZE), 
                    (CHOOSE_MAZE_BTN_SIZE, CHOOSE_MAZE_BTN_SIZE), self.surface, f'M{i}', f' #{i}',
                    parent=self.maze_control_panel
                )
            )
    
    def _create_command_line_panel(self):
        self.command_line_panel = Panel(
            (self.mazes_panel.rect.topright[0] + 2 * SKIP_SIZE, self.maze_control_panel.rect.bottomleft[1]+BIG_SKIP_SIZE),
            (self.maze_control_panel.rect.width, 2*CHOOSE_MAZE_BTN_SIZE+3*BIG_SKIP_SIZE),
            self.surface,
        )
        self.command_line_panel.populate_one(
            'text_entry',
            TextEntry(
                (BIG_SKIP_SIZE, BIG_SKIP_SIZE),
                (5 * CHOOSE_MAZE_BTN_SIZE + 4*BIG_SKIP_SIZE, 50),
                self.surface, 'command prompt', parent=self.command_line_panel
            )
        )
        self.command_line_panel.populate_one(
            'exec_cmd_btn',
            Button(
                (BIG_SKIP_SIZE*6 + 5*CHOOSE_MAZE_BTN_SIZE, BIG_SKIP_SIZE),
                (CHOOSE_MAZE_BTN_SIZE, 50),
                self.surface, 'Do', 'execute the command',
                parent=self.command_line_panel
            )
        )
        self.command_line_panel.add_labels([
            Label('*'*40, self.surface, FONT_SMALL, WHITE, topleft=(BIG_SKIP_SIZE, 2*BIG_SKIP_SIZE+CHOOSE_MAZE_BTN_SIZE))
        ])

    def draw_maze(self, maze_index: int):
        for i in range(self.grid_shape[0]):
            for j in range(self.grid_shape[1]):
                this_tile = self.game.mazes[maze_index].maze[i][j]
                if this_tile.visible:
                    if this_tile._type == TT.PASS:
                        fill_color = (255, 255, 255)
                    else:
                        fill_color = (10, 10, 10)
                else:
                    fill_color = (120, 120, 120)
                # tile itself:
                pygame.draw.rect(self.surface, fill_color, 
                    pygame.rect.Rect(20 + SKIP_SIZE + (SKIP_SIZE + TILE_SIZE)*j, 
                                    SKIP_SIZE + 20 + (SKIP_SIZE + TILE_SIZE)*i, TILE_SIZE, TILE_SIZE),
                    border_radius=2
                )
                # border rect:
                if (col_ind:=self.game.color_marks_to_show[self.chosen_maze_idx, i, j]) > 0:
                    pygame.draw.rect(self.surface, COLORS_INTS[col_ind],
                        pygame.rect.Rect(24 + SKIP_SIZE + (SKIP_SIZE + TILE_SIZE)*j, 
                                        SKIP_SIZE + 24 + (SKIP_SIZE + TILE_SIZE)*i, TILE_SIZE-8, TILE_SIZE-8),
                        width=5
                    )
                if self.mazes_boolean_map[self.chosen_maze_idx, i, j]:
                    self.game.somethings_to_show[self.chosen_maze_idx, i, j] = 0 # removes "!?" hint
                    pygame.draw.rect(self.surface, (150, 150, 150),
                        pygame.rect.Rect(21 + SKIP_SIZE + (SKIP_SIZE + TILE_SIZE)*j, 
                                        SKIP_SIZE + 21 + (SKIP_SIZE + TILE_SIZE)*i, TILE_SIZE-2, TILE_SIZE-2),
                        width=3,
                        border_radius=3
                    )
                if (col_ind:=self.mazes_color_map[self.chosen_maze_idx, i, j]) > 0:
                    pygame.draw.rect(self.surface, COLORS_INTS[col_ind],
                        pygame.rect.Rect(26 + SKIP_SIZE + (SKIP_SIZE + TILE_SIZE)*j, 
                                        SKIP_SIZE + 26 + (SKIP_SIZE + TILE_SIZE)*i, TILE_SIZE-12, TILE_SIZE-12),
                        width=3,
                        border_radius=3
                    )
                if (marker_ind:=self.mazes_markers_map[self.chosen_maze_idx, i, j]) > 0:
                    pygame.draw.rect(self.surface, TILE_ITEM_TYPES_COLORS[marker_ind],
                        pygame.rect.Rect(30 + SKIP_SIZE + (SKIP_SIZE + TILE_SIZE)*j, 
                                        SKIP_SIZE + 30 + (SKIP_SIZE + TILE_SIZE)*i, TILE_SIZE-20, TILE_SIZE-20),
                        border_radius=3
                    )
                if self.game.somethings_to_show[self.chosen_maze_idx, i, j]:
                    self.surface.blit(
                        FONT_NORM.render('?!', False, BLACK),
                        pygame.rect.Rect(30 + SKIP_SIZE + (SKIP_SIZE + TILE_SIZE)*j, 
                                        SKIP_SIZE + 30 + (SKIP_SIZE + TILE_SIZE)*i, TILE_SIZE-20, TILE_SIZE-20))
        for coords in self.revealed_checkpoints.keys():
            if coords[0] != self.chosen_maze_idx: continue
            _, i, j = coords
            pygame.draw.rect(self.surface, TILE_ITEM_TYPES_COLORS[2], 
                    pygame.rect.Rect(20 + SKIP_SIZE + (SKIP_SIZE + TILE_SIZE)*j, 
                                    SKIP_SIZE + 20 + (SKIP_SIZE + TILE_SIZE)*i, TILE_SIZE, TILE_SIZE),
                    border_radius=2
                )

    def set_feedback(self, msg, color=WHITE):
        self.feedback = msg
        self.feedback_color = color

    def maze_tile_hovering(self, pos):
        '''Returns the coordinates of the Tile hovering'''
        x = pos[0] - 20; y = pos[1] - 20
        j = x // (TILE_SIZE + SKIP_SIZE)
        i = y // (TILE_SIZE + SKIP_SIZE)
        return i, j

    def update_gui(self, pos):
        self.mazes_panel.update(pos)
        self.maze_control_panel.update(pos)
        for maze_id_str, choose_maze_btn in self.maze_control_panel.gui_objects.items():
            choose_maze_btn.set_frame_color('#00FF00' if int(maze_id_str) == self.chosen_maze_idx else '#FFFFFF')
        self.command_line_panel.update(pos)
        self.command_line_panel.labels[0].set_color(self.feedback_color)
        self.command_line_panel.labels[0].set_text(self.feedback)

        self.draw_maze(self.chosen_maze_idx)
    
    def process_cmd_prompt(self):
        cmd: str = self.command_line_panel.gui_objects['text_entry'].get_text()
        print('executed command:', cmd)
        match cmd.split():
            case ['code', code_str]:
                try:
                    code_int = int(code_str)
                except ValueError:
                    self.set_feedback(f'invalid code: {code_str}', color=RED)
                else:
                    coord_of_chp = self.game.checkpoint_codes_backw.get(code_int)
                    if coord_of_chp is not None:
                        if coord_of_chp in self.revealed_checkpoints:
                           self.set_feedback('this checkpoint is already open', color=RED)
                           return
                        self.revealed_checkpoints[coord_of_chp] = code_int
                        self.set_feedback(f'new checkpoint: {code_int}', color=GREEN)
                    else:
                        self.set_feedback('wrong code', color=RED)
            case ['sol', word_proposal]:
                if word_proposal == self.game.word_to_win:
                    self.set_feedback('victory!', color=GREEN)
                else:
                    self.set_feedback('wrong word', color=RED)
            case ['clear', what_to_clear]:
                if what_to_clear == 'bools': self.mazes_boolean_map = np.zeros((NUM_OF_MAZES, *self.grid_shape), dtype=int)
                elif what_to_clear == 'markers': self.mazes_markers_map = np.zeros((NUM_OF_MAZES, *self.grid_shape), dtype=int)
                elif what_to_clear == 'colors': self.mazes_color_map = np.zeros((NUM_OF_MAZES, *self.grid_shape), dtype=int)
                else: self.set_feedback(f'{what_to_clear}?: [bools, markers, colors]')

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
                    if any(te.focused for te in self.text_entries):
                        for te in self.text_entries:
                            if te.focused:
                                te.process_key_code_alphanum(event.key)
                                if event.key == pygame.K_BACKSPACE:
                                    if pygame.key.get_mods() & pygame.KMOD_CTRL: te.clear()
                                    else: te.pop_last_symbol()
                                elif event.key == pygame.K_RETURN:
                                    self.process_cmd_prompt()
                        continue
                    elif event.key == pygame.K_SPACE:
                        if self.mazes_panel.clicked():
                            coord = self.maze_tile_hovering(pos)
                            self.mazes_markers_map[self.chosen_maze_idx, coord[0], coord[1]] = \
                                (self.mazes_markers_map[self.chosen_maze_idx, coord[0], coord[1]] + 1) % 2
                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.maze_control_panel.clicked():
                        obj_clicked = self.maze_control_panel.object_clicked()
                        if not obj_clicked: continue
                        if int(obj_clicked) in range(len(self.game.mazes)):
                            self.chosen_maze_idx = int(obj_clicked)
                    elif self.command_line_panel.clicked():
                        obj_clicked = self.command_line_panel.object_clicked()
                        if obj_clicked == 'text_entry':
                            self.command_line_panel.gui_objects['text_entry'].toggle_focused()
                        elif obj_clicked == 'exec_cmd_btn':
                            self.process_cmd_prompt()
                    elif self.mazes_panel.clicked():
                        coord = self.maze_tile_hovering(pos)
                        if event.button in {4, 5}:
                            delt = 1 if event.button == 4 else -1
                            self.mazes_color_map[self.chosen_maze_idx, coord[0], coord[1]] = \
                                (self.mazes_color_map[self.chosen_maze_idx, coord[0], coord[1]] + delt) % 4
                        elif event.button == 1:
                            print('deb', coord, self.game.mazes[self.chosen_maze_idx][coord[0]][coord[1]])
                        elif event.button == 3:
                            coord = self.maze_tile_hovering(pos)
                            self.mazes_boolean_map[self.chosen_maze_idx, coord[0], coord[1]] = \
                                1 - self.mazes_boolean_map[self.chosen_maze_idx, coord[0], coord[1]]
                elif pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    coord_hovering = self.maze_tile_hovering(pos)
                    if not coord_hovering:
                        continue
                    code = self.revealed_checkpoints.get((self.chosen_maze_idx, *coord_hovering))
                    if code is not None:
                        self.set_feedback(f'{code} checkpoint', color=COLORS_INTS[3])
            pygame.display.update()
