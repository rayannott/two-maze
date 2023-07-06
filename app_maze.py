import random

import pygame

from gui.gui_utils import *
from gui.gui_rect import Button, Panel, TextEntry
from game import Game
from game_gui_p1 import GameGUI1
from game_gui_p2 import GameGUI2

class MazeApp:
    def __init__(self) -> None:
        pygame.init()
        self.surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.is_running = True

        self._create_buttons()
        self._create_create_room_panel()
        self._create_join_room_panel()
        
        self.menu_text_entries: list[TextEntry] = [
            self.create_room_panel.gui_objects['text_entry'],
            self.join_room_panel.gui_objects['text_entry']
        ]

    def _create_buttons(self):
        self.create_btn = Button((70, 40), (1000, 235), self.surface, 
                                'CREATE', 'create a new game room', FONT_BIG)
        self.join_btn = Button((70, 40+(235+20)), (1000, 235), self.surface, 
                                'JOIN', 'join an existing room', FONT_BIG)
        self.options_btn = Button((70, 40+(235+20)*2), (490, 235), self.surface, 
                                'OPTIONS', 'tweak the game settings', FONT_BIG)
        self.rules_btn = Button((580, 40+(235+20)*2), (490, 235), self.surface, 
                                'RULES', 'learn more', FONT_BIG)
        self.quit_btn = Button((70, 40+(235+20)*3), (1000, 235), self.surface, 
                                'EXIT', 'quit the game', FONT_BIG)

    def _create_create_room_panel(self):
        self.create_room_panel = Panel(
            (1090, 40), (WINDOW_SIZE[0]-1090-70, 235), 
            self.surface, 'create room')
        self.create_room_panel_flag = False
        self.create_room_panel.set_active_visible(self.create_room_panel_flag)
        self.create_room_panel.populate_one(
            'text_entry',
            TextEntry((30, 30), (500, 50), self.surface, 'enter the room code', parent=self.create_room_panel)
        )
        self.create_room_panel.populate_one(
            'rnd_btn',
            Button((550, 30), (190, 50), self.surface, 'RANDOM', 'insert a random code', parent=self.create_room_panel)
        )
        self.create_room_panel.populate_one(
            'start_btn',
            Button((30, 90), (300, 50), self.surface, 'START', 'enter the game with _ as the 1st player', parent=self.create_room_panel)
        )

    def _create_join_room_panel(self):
        self.join_room_panel = Panel(
            (1090, 40+(235+20)), (WINDOW_SIZE[0]-1090-70, 235),
            self.surface, 'join room')
        self.join_room_panel_flag = False
        self.join_room_panel.set_active_visible(self.join_room_panel_flag)
        self.join_room_panel.populate_one(
            'text_entry',
            TextEntry((30, 30), (500, 50), self.surface, 'enter the room code', parent=self.join_room_panel)
        )
        self.join_room_panel.populate_one(
            'start_btn',
            Button((30, 90), (300, 50), self.surface, 'START', 'enter the game with _ as the 2nd player', parent=self.join_room_panel)
        )

    def update_gui(self, pos):
        self.create_btn.update(pos)
        self.join_btn.update(pos)
        self.options_btn.update(pos)
        self.rules_btn.update(pos)
        self.quit_btn.update(pos)

        self.create_room_panel.update(pos)
        self.create_room_panel.gui_objects['start_btn'].hint_label.set_text(
            f'enter the game with {text_entry_text} as the 1st player'\
            if (text_entry_text:=self.create_room_panel.gui_objects["text_entry"].get_text()) else 'empty field!'
        )

        self.join_room_panel.update(pos)
        self.join_room_panel.gui_objects['start_btn'].hint_label.set_text(
            f'enter the game with {text_entry_text} as the 2nd player'\
            if (text_entry_text:=self.join_room_panel.gui_objects["text_entry"].get_text()) else 'empty field!'
        )

    def create_start_btn_pressed(self):
        try:
            room_id = int(self.create_room_panel.gui_objects["text_entry"].get_text())
        except ValueError:
            print('Error: empty room id entry')
        else:
            print(f'p1: game started with {room_id}')
            self.start_game_loop(room_id, is_second_player=False)
    
    def join_start_btn_pressed(self):
        try:
            room_id = int(self.join_room_panel.gui_objects["text_entry"].get_text())
        except ValueError:
            print('Error: empty room id entry')
        else:
            print(f'p2: game started with {room_id}')
            self.start_game_loop(room_id, is_second_player=True)

    def run_menu(self):
        '''
        Infinite game loop
        '''
        while self.is_running:
            self.clock.tick(FRAMERATE)
            self.surface.fill(BLACK)
            pos = pygame.mouse.get_pos()

            # update gui
            self.update_gui(pos)

            # process events
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    #* such a mess omg...
                    if any(te.focused for te in self.menu_text_entries):
                        for te in self.menu_text_entries:
                            if te.focused:
                                te.process_key_code_numeric(event.key)
                                if event.key == pygame.K_BACKSPACE:
                                    if pygame.key.get_mods() & pygame.KMOD_CTRL: te.clear()
                                    else: te.pop_last_symbol()
                                elif event.key == pygame.K_RETURN:
                                    if self.menu_text_entries[0].focused:
                                        self.create_start_btn_pressed()
                                    else:
                                        self.join_start_btn_pressed()
                    if event.key == pygame.K_ESCAPE:
                        for te in self.menu_text_entries: te.focused = False
                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.quit_btn.clicked():
                        self.is_running = False
                    elif self.join_btn.clicked():
                        print('join_btn')
                        self.join_room_panel_flag = not self.join_room_panel_flag
                        self.join_room_panel.set_active_visible(self.join_room_panel_flag)
                    elif self.create_btn.clicked():
                        print('create_btn')
                        self.create_room_panel_flag = not self.create_room_panel_flag
                        self.create_room_panel.set_active_visible(self.create_room_panel_flag)
                    elif self.options_btn.clicked():
                        print('options_btn')
                    elif self.rules_btn.clicked():
                        print('rules_btn')
                    elif self.create_room_panel.clicked():
                        obj_clicked = self.create_room_panel.object_clicked()
                        if obj_clicked == 'text_entry':
                            self.create_room_panel.gui_objects['text_entry'].toggle_focused()
                        elif obj_clicked == 'rnd_btn':
                            self.create_room_panel \
                                    .gui_objects['text_entry'] \
                                    .text_label.set_text(str(random.randint(100000, 999999)))
                        elif obj_clicked == 'start_btn':
                            self.create_start_btn_pressed()
                    elif self.join_room_panel.clicked():
                        obj_clicked = self.join_room_panel.object_clicked()
                        if obj_clicked == 'text_entry':
                            self.join_room_panel.gui_objects['text_entry'].toggle_focused()
                        elif obj_clicked == 'start_btn':
                            self.join_start_btn_pressed()
            pygame.display.update()
    
    def start_game_loop(self, room_id: int, is_second_player: bool):
        self.game = Game(room_id, is_second_player)
        print(room_id, self.game.word_to_win, self.game.exit_position)
        if is_second_player:
            self.game_gui = GameGUI2(self.game, self.surface)
        else:
            self.game_gui = GameGUI1(self.game, self.surface)
        
        self.game_gui.run()
