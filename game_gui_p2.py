from typing import Literal
import numpy as np
import pygame

from game import Game
from gui.gui_rect import Draggable, Panel, Button, Label
from gui.gui_utils import *
from mazes import TC, Tile, TT, TileItemType
from sfx_tools import play_sfx, play_sfx_warning

CONTROL_PANEL_SIZE = (900, 900)
CURRENT_TILE_PANEL_SIZE = (450, 450)
MOVE_BTN_SIZE = (CURRENT_TILE_PANEL_SIZE[0]-10, (CONTROL_PANEL_SIZE[1]-CURRENT_TILE_PANEL_SIZE[1])//2-10)
ACT_BTN_SIZE = (400, 110)
DRAGGABLE_LETTER_SIZE = (100, 100)
EXIT_BTN_SIZE = (60, 60)


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
        self.letters_collected: list[str] = []
        self.revealed_checkpoints: list[int] = [] # only their codes

        self.tile_and_neigh_cache: tuple[Tile, Tile, Tile, Tile, Tile] | None = self.get_this_tile_and_neigh()
        self.closest_something_cache: int | None = None
        self.chosen_checkpoint_code_idx: int | None = None
        
        self.act_btn_clicked_on_exit = 0 # should be clicked 5 times

        self.exit_btn = Button((WINDOW_SIZE[0]-20-EXIT_BTN_SIZE[0], 20), EXIT_BTN_SIZE, self.surface, 'EXIT', 'exit the game')
        self._create_control_panel()
        self._create_left_panel()

        self.victory_sound_played = False

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
        self.left_panel.add_labels([
            Label('__/__', self.surface, FONT_NORM, color=WHITE, topright=shift(self.left_panel.rect.topright, (-5, 0)))
        ])

    def _choose_color(self, tile: Tile):
        if tile._type == TT.WALL: return GREY
        if tile.has is None: return COLORS_HEX[tile.color.value]
        if tile.has.tile_item_type == TileItemType.CHECKPOINT:
            return '#0000FF'
        elif tile.has.tile_item_type == TileItemType.PIT:
            return '#FF0000'
        elif tile.has.tile_item_type == TileItemType.LETTER:
            return '#00FF00'
        elif tile.has.tile_item_type == TileItemType.INFO_HINT:
            return '#E1950F'

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
            if self.act_btn_clicked_on_exit >= 5 and self.position == self.game.exit_position:
                main_label = 'VICTORY!'
                info_label = 'well done :)'
                color = GREEN
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
            elif tile_item.tile_item_type == TileItemType.INFO_HINT:
                main_label = 'INFO HINT'
                info_label = f'info key {tile_item.key}'
                act_button_text = ''

        self.control_panel.labels[0].set_color(COLORS_HEX[this_tile.color.value])
        self.current_tile_panel.labels[0].set_text(main_label)
        self.current_tile_panel.labels[1].set_text(info_label)
        self.current_tile_panel.labels[0].set_color(color)
        self.current_tile_panel.gui_objects['act_btn'].set_text(act_button_text)

    def update_gui(self, pos):
        self.exit_btn.update(pos)
        self.control_panel.update(pos)
        self.left_panel.update(pos)
        self.update_control_btns_colors()
        self.update_this_tile()
        self.control_panel.labels[0].set_text(
            f'[{self.closest_something_cache}]' if self.tile_and_neigh_cache[0].color != TC.BLANK else '[?]'
        )
        self.left_panel.labels[0].set_text(f'{len(self.letters_collected)}/{len(self.game.letters_with_deceptive)}')
    
    def _update_closest_something_cache(self):
        if self.closest_something_cache is None:
            maze_id, i, j = self.position
            path = self.game.mazes[maze_id].bfs((i, j))
            self.closest_something_cache = len(path) - 1 if path else -1
    
    def update(self):
        self._update_closest_something_cache()
        if not self.victory_sound_played and self.act_btn_clicked_on_exit >= 5:
            play_sfx('victory')
            self.victory_sound_played = True

    def collected_new_letter(self, letter: str):
        maze_id, i, j = self.position
        self.game.mazes[maze_id].maze[i][j].has = None
        self.left_panel.populate_one(
            str(len(self.letters_collected)),
            Draggable((60, 60), DRAGGABLE_LETTER_SIZE, self.surface, letter.upper(), text_font=FONT_BIG, parent=self.left_panel)
        )
        self.letters_collected.append(letter)
        self.closest_something_cache = None
        print('collected letter', letter)

    def process_act_btn_press(self):
        print('act btn pressed', 'current pos: ', self.position)
        this_tile = self.tile_and_neigh_cache[0]
        if self.position == self.game.exit_position:
            print('this is the exit!')
            self.act_btn_clicked_on_exit += 1
            return
        self.act_btn_clicked_on_exit = 0 # no abusing
        if this_tile.has is None:
            play_sfx_warning()
            return
        if this_tile.has.tile_item_type == TileItemType.PIT:
            things = self.game.mazes[this_tile.has.index].get_all_things()
            for thing in things:
                if thing[1].tile_item_type == TileItemType.PIT and thing[1].index == self.position[0]:
                    break
            self.set_position((this_tile.has.index, *thing[0]))
            print('fell to', self.position)
            play_sfx('teleport')
        elif this_tile.has.tile_item_type == TileItemType.CHECKPOINT:
            code = this_tile.has.code
            if code not in self.revealed_checkpoints:
                self.revealed_checkpoints.append(code)
                if len(self.revealed_checkpoints) == 2:
                    self.chosen_checkpoint_code_idx = 0
                play_sfx('switch')
            elif self.chosen_checkpoint_code_idx is not None:
                teleport_to = self.game.checkpoint_codes_backw[self.revealed_checkpoints[self.chosen_checkpoint_code_idx]]
                if teleport_to != self.position:
                    self.set_position(teleport_to)
                    print('teleported character to', teleport_to)
                play_sfx('teleport')
        elif this_tile.has.tile_item_type == TileItemType.LETTER:
            collected_letter = this_tile.has.letter
            self.collected_new_letter(collected_letter)
            play_sfx('success')
        
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
        if self.tile_and_neigh_cache is None: self.tile_and_neigh_cache = self.get_this_tile_and_neigh()
        this_tile, up_tile, down_tile, right_tile, left_tile = self.tile_and_neigh_cache
        if direction == 'up' and up_tile._type == TT.PASS:
            self.set_position((self.position[0], self.position[1]-1, self.position[2]))
            play_sfx('click')
        elif direction == 'down' and down_tile._type == TT.PASS:
            self.set_position((self.position[0], self.position[1]+1, self.position[2]))
            play_sfx('click')
        elif direction == 'right' and right_tile._type == TT.PASS:
            self.set_position((self.position[0], self.position[1], self.position[2]+1))
            play_sfx('click')
        elif direction == 'left' and left_tile._type == TT.PASS:
            self.set_position((self.position[0], self.position[1], self.position[2]-1))
            play_sfx('click')
        else:
            print('cannot move!')
            play_sfx_warning()

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
                        pass
                    elif event.key == pygame.K_LEFT:
                        self.move_character_to(direction='left')
                    elif event.key == pygame.K_RIGHT:
                        self.move_character_to(direction='right')
                    elif event.key == pygame.K_UP:
                        self.move_character_to(direction='up')
                    elif event.key == pygame.K_DOWN:
                        self.move_character_to(direction='down')
                    elif event.key == pygame.K_d:
                        pass
                    elif event.key == pygame.K_RETURN:
                        self.process_act_btn_press()
                    elif event.key == pygame.K_SPACE:
                        # scrolling through the checkpoints with the keyboard
                        if len(self.revealed_checkpoints) > 1:
                            self.chosen_checkpoint_code_idx = (self.chosen_checkpoint_code_idx + 1) % len(self.revealed_checkpoints)
                            play_sfx('short_click')
                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.left_panel.clicked() and event.button == 1:
                        obj_clicked = self.left_panel.object_clicked()
                        if obj_clicked:
                            self.left_panel.gui_objects[obj_clicked].hold(False)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button in {4, 5}:
                        if self.current_tile_panel.gui_objects['act_btn'].clicked():
                            # scrolling over the act button
                            if len(self.revealed_checkpoints) > 1:
                                delt = 1 if event.button == 4 else -1
                                self.chosen_checkpoint_code_idx = (self.chosen_checkpoint_code_idx + delt) % len(self.revealed_checkpoints)
                                play_sfx('short_click')
                        continue
                    if self.control_panel.clicked():
                        obj_clicked = self.control_panel.object_clicked()
                        if obj_clicked in {'up', 'down', 'right', 'left'}:
                            self.move_character_to(direction=obj_clicked)
                        elif obj_clicked == 'current_tile_panel':
                            curr_tile_panel_obj_clicked = self.current_tile_panel.object_clicked()
                            if curr_tile_panel_obj_clicked == 'act_btn':
                                self.process_act_btn_press()
                    elif self.left_panel.clicked() and event.button == 1:
                        obj_clicked = self.left_panel.object_clicked()
                        if obj_clicked:
                            self.left_panel.gui_objects[obj_clicked].hold(True)
                            play_sfx('short_click')
                    elif self.exit_btn.clicked():
                        play_sfx('click')
                        self.is_running = False
            pygame.display.update()
