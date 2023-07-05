from typing import Literal
import numpy as np
import pygame

from game import Game
from gui.gui_rect import Panel, Button, Label
from gui.gui_utils import *
from mazes import TC, Tile, TT, TileItemType

CONTROL_PANEL_SIZE = (900, 900)
CURRENT_TILE_PANEL_SIZE = (450, 450)
MOVE_BTN_SIZE = (300, 100)
ACT_BTN_SIZE = (400, 110)


class ButtonThickBorders(Button):
    def draw(self) -> None:
        if self.visible:
            pygame.draw.rect(self.surface, self.color_frame, self.rect, width=16 if self.hovering else 8, border_radius=3)


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

        self.tile_and_neigh_cache: tuple[Tile, Tile, Tile, Tile, Tile] | None = self.get_this_tile_and_neigh()
        self.closest_something_cache: int | None = None
        self.chosen_checkpoint_code_idx: int | None = None

        self._create_control_panel()
        self._create_left_panel()

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
        self.current_tile_panel.populate_one(
            'act_btn',
            Button(
                (CURRENT_TILE_PANEL_SIZE[0]//2-ACT_BTN_SIZE[0]//2, CURRENT_TILE_PANEL_SIZE[1] - ACT_BTN_SIZE[1] - 20), ACT_BTN_SIZE, 
                self.surface, 'ACT BUTTON', 'do something', FONT_BIG, parent=self.current_tile_panel
            )
        )
        self.current_tile_panel.add_labels([
            Label('checkpoint', self.surface, FONT_BIG, WHITE, center=(CURRENT_TILE_PANEL_SIZE[0]//2, 25)),
            Label('info on the subject above', self.surface, FONT_NORM, WHITE, center=(CURRENT_TILE_PANEL_SIZE[0]//2, 70))
        ])
        self.control_panel.populate_one(
            'current_tile_panel',
            self.current_tile_panel
        )
        self.control_panel.populate_many({
            'up': ButtonThickBorders(
                (CONTROL_PANEL_SIZE[0]//2 - MOVE_BTN_SIZE[0]//2, (CONTROL_PANEL_SIZE[1] - CURRENT_TILE_PANEL_SIZE[1])//4 - MOVE_BTN_SIZE[1]//2),
                MOVE_BTN_SIZE, self.surface, 'UP', 'move up', parent=self.control_panel
            ),
            'down': ButtonThickBorders(
                (CONTROL_PANEL_SIZE[0]//2 - MOVE_BTN_SIZE[0]//2, CONTROL_PANEL_SIZE[1] - (CONTROL_PANEL_SIZE[1] - CURRENT_TILE_PANEL_SIZE[1])//4 - MOVE_BTN_SIZE[1]//2),
                MOVE_BTN_SIZE, self.surface, 'DOWN', 'move down', parent=self.control_panel
            ),
            'right': ButtonThickBorders(
                (CONTROL_PANEL_SIZE[0] - (CONTROL_PANEL_SIZE[0] - CURRENT_TILE_PANEL_SIZE[0])//4 - MOVE_BTN_SIZE[1]//2, CONTROL_PANEL_SIZE[1]//2 - MOVE_BTN_SIZE[0]//2),
                (MOVE_BTN_SIZE[1], MOVE_BTN_SIZE[0]), self.surface, 'RIGHT', 'move right', parent=self.control_panel
            ),
            'left': ButtonThickBorders(
                ((CONTROL_PANEL_SIZE[0] - CURRENT_TILE_PANEL_SIZE[0])//4 - MOVE_BTN_SIZE[1]//2, CONTROL_PANEL_SIZE[1]//2 - MOVE_BTN_SIZE[0]//2),
                (MOVE_BTN_SIZE[1], MOVE_BTN_SIZE[0]), self.surface, 'LEFT', 'move left', parent=self.control_panel
            )
        })
        self.control_panel.add_labels([
            Label('**', self.surface, FONT_HUGE, color=WHITE, 
                center=((CONTROL_PANEL_SIZE[0] - CURRENT_TILE_PANEL_SIZE[0])//4, 
                        (CONTROL_PANEL_SIZE[1] - CURRENT_TILE_PANEL_SIZE[1])//4))
        ])

    def _create_left_panel(self):
        self.left_panel = Panel(
            (20, 20), (self.control_panel.rect.topleft[0] - 40, WINDOW_SIZE[1]-40),
            self.surface
        )

    def _choose_color(self, tile: Tile):
        if tile._type == TT.WALL: return LIGHT_GREY
        if tile.has is None: return COLORS_HEX[tile.color.value]
        if tile.has.tile_item_type == TileItemType.CHECKPOINT:
            return '#0000FF'
        elif tile.has.tile_item_type == TileItemType.PIT:
            return '#FF0000'
        elif tile.has.tile_item_type == TileItemType.LETTER:
            return '#00FF00'

    def update_control_btns_colors(self):
        if self.tile_and_neigh_cache is None:
            self.tile_and_neigh_cache = self.get_this_tile_and_neigh()
        this_tile, up_tile, down_tile, right_tile, left_tile = self.tile_and_neigh_cache
        self.control_panel.gui_objects['current_tile_panel'].set_frame_color(
            self._choose_color(this_tile)
        )
        self.control_panel.gui_objects['up'].set_frame_color(
            self._choose_color(up_tile)
        )
        self.control_panel.gui_objects['down'].set_frame_color(
            self._choose_color(down_tile)
        )
        self.control_panel.gui_objects['right'].set_frame_color(
            self._choose_color(right_tile)
        )
        self.control_panel.gui_objects['left'].set_frame_color(
            self._choose_color(left_tile)
        )
    
    def update_this_tile(self):
        this_tile = self.tile_and_neigh_cache[0]
        color = self._choose_color(this_tile)
        if this_tile.has is None:
            main_label = 'nothing'
            act_button_text = ''
            info_label = ''
            self.current_tile_panel.gui_objects['act_btn'].hint_label.set_text('do something')
        else:
            tile_item = this_tile.has
            if tile_item.tile_item_type == TileItemType.CHECKPOINT:
                main_label = 'CHECKPOINT'
                info_label = f'with code {tile_item.code}'
                if tile_item.code not in self.revealed_checkpoints:
                    act_button_text = f' REGISTER'
                elif self.chosen_checkpoint_code_idx is not None:
                    act_button_text = f'GO TO {self.revealed_checkpoints[self.chosen_checkpoint_code_idx]}'
                    self.current_tile_panel.gui_objects['act_btn'].hint_label.set_text(' '.join(map(str, self.revealed_checkpoints)))
                else:
                    act_button_text = ''
            elif tile_item.tile_item_type == TileItemType.PIT:
                main_label = 'PIT'
                info_label = f'leading to maze #{tile_item.index}'
                act_button_text = 'FALL'
            elif tile_item.tile_item_type == TileItemType.LETTER:
                main_label = 'LETTER'
                info_label = f'letter {tile_item.letter.upper()}'
                act_button_text = 'COLLECT'
        self.control_panel.labels[0].set_color(COLORS_HEX[this_tile.color.value])
        self.current_tile_panel.labels[0].set_text(main_label)
        # self.current_tile_panel.labels[0].rect.center = (CURRENT_TILE_PANEL_SIZE[0]//2, 25)
        self.current_tile_panel.labels[1].set_text(info_label)
        self.current_tile_panel.labels[0].set_color(color)
        self.current_tile_panel.gui_objects['act_btn'].set_text(act_button_text)

    def update_gui(self, pos):
        self.control_panel.update(pos)
        self.left_panel.update(pos)
        self.update_control_btns_colors()
        self.update_this_tile()
        self.control_panel.labels[0].set_text(
            f'[{self.closest_something_cache}]' if self.tile_and_neigh_cache[0].color != TC.BLANK else '[?]'
        )
    
    def _update_closest_something_cache(self):
        if self.closest_something_cache is None:
            maze_id, i, j = self.position
            path = self.game.mazes[maze_id].bfs((i, j))
            self.closest_something_cache = len(path) - 1 if path else -1
    
    def update(self):
        self._update_closest_something_cache()

    def process_act_btn_press(self):
        print('act btn pressed')
        this_tile = self.tile_and_neigh_cache[0]
        if this_tile.has is None: return
        print('this tile:', this_tile)
        if this_tile.has.tile_item_type == TileItemType.PIT:
            things = self.game.mazes[this_tile.has.index].get_all_things()
            for thing in things:
                if thing[1].tile_item_type == TileItemType.PIT and thing[1].index == self.position[0]:
                    break
            self.set_position((this_tile.has.index, *thing[0]))
            print('fell to', self.position)
        elif this_tile.has.tile_item_type == TileItemType.CHECKPOINT:
            code = this_tile.has.code
            if code not in self.revealed_checkpoints:
                self.revealed_checkpoints.append(code)
                if len(self.revealed_checkpoints) == 2:
                    self.chosen_checkpoint_code_idx = 0
            elif self.chosen_checkpoint_code_idx is not None:
                teleport_to = self.game.checkpoint_codes_backw[self.revealed_checkpoints[self.chosen_checkpoint_code_idx]]
                if teleport_to != self.position:
                    self.set_position(teleport_to)
                    print('teleported character to', teleport_to)
        elif this_tile.has.tile_item_type == TileItemType.LETTER:
            maze_id, i, j = self.position
            collected_letter = this_tile.has.letter
            self.game.mazes[maze_id].maze[i][j].has = None
            self.letters_collected.append(collected_letter)
            self.closest_something_cache = None
            print('collected letter', self.letters_collected)
        
    
    def get_this_tile_and_neigh(self) -> tuple[Tile, Tile, Tile, Tile, Tile]:
        maze_id, i, j = self.position
        this_tile = self.game.mazes[maze_id].maze[i][j]
        up_tile = self.game.mazes[maze_id].maze[i-1][j]
        down_tile = self.game.mazes[maze_id].maze[i+1][j]
        left_tile = self.game.mazes[maze_id].maze[i][j-1]
        right_tile = self.game.mazes[maze_id].maze[i][j+1]
        return this_tile, up_tile, down_tile, right_tile, left_tile
    
    def set_position(self, set_to: tuple[int, int, int]):
        self.position = set_to
        self.tile_and_neigh_cache = None
        self.closest_something_cache = None

    def move_character_to(self, direction: Literal['up', 'down', 'right', 'left']):
        this_tile, up_tile, down_tile, right_tile, left_tile = self.tile_and_neigh_cache
        if direction == 'up' and up_tile._type == TT.PASS:
            self.set_position((self.position[0], self.position[1]-1, self.position[2]))
        elif direction == 'down' and down_tile._type == TT.PASS:
            self.set_position((self.position[0], self.position[1]+1, self.position[2]))
        elif direction == 'right' and right_tile._type == TT.PASS:
            self.set_position((self.position[0], self.position[1], self.position[2]+1))
        elif direction == 'left' and left_tile._type == TT.PASS:
            self.set_position((self.position[0], self.position[1], self.position[2]-1))
        else:
            print('cannot move!')

    def run(self):
        while self.is_running:
            self.clock.tick(FRAMERATE)
            self.surface.fill(BLACK)
            pos = pygame.mouse.get_pos()

            # update brains
            self.update()

            # update gui
            self.update_gui(pos)

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.is_running = False
                    elif event.key == pygame.K_LEFT:
                        self.move_character_to(direction='left')
                    elif event.key == pygame.K_RIGHT:
                        self.move_character_to(direction='right')
                    elif event.key == pygame.K_UP:
                        self.move_character_to(direction='up')
                    elif event.key == pygame.K_DOWN:
                        self.move_character_to(direction='down')
                    elif event.key == pygame.K_d:
                        #? debug
                        print('debug')
                        self.set_position((0, 1, 29))
                    elif event.key == pygame.K_RETURN:
                        self.process_act_btn_press()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button in {4, 5}:
                        if self.current_tile_panel.gui_objects['act_btn'].clicked():
                            # scrolling over the act button
                            if len(self.revealed_checkpoints) > 1:
                                delt = 1 if event.button == 4 else -1
                                self.chosen_checkpoint_code_idx = (self.chosen_checkpoint_code_idx + delt) % len(self.revealed_checkpoints)
                        continue
                    if self.control_panel.clicked():
                        obj_clicked = self.control_panel.object_clicked()
                        if obj_clicked in {'up', 'down', 'right', 'left'}:
                            self.move_character_to(direction=obj_clicked)
                        elif obj_clicked == 'current_tile_panel':
                            curr_tile_panel_obj_clicked = self.current_tile_panel.object_clicked()
                            if curr_tile_panel_obj_clicked == 'act_btn':
                                self.process_act_btn_press()
                            
                    print('current pos:', self.position)
            pygame.display.update()
