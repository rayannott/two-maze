import random
from string import ascii_lowercase

import numpy as np

import mazes
from utils.constants import *
from utils.utils import get_english_words, split_word_into

class Game:
    def __init__(self, room_id: int, is_second_player: bool) -> None:
        self.seed = room_id
        self.is_second_player = is_second_player # 1st: False, 2nd: True

        random.seed(self.seed)
        self.deceptive_letters = ''.join((random.choice(ascii_lowercase) for _ in range(NUM_OF_MAZES)))
        self.word_to_win = random.choice(get_english_words())
        letters_doubled = list(self.word_to_win + self.deceptive_letters)
        random.shuffle(letters_doubled)
        word_to_win_new = ''.join(letters_doubled)

        self.word_parts = split_word_into(word_to_win_new, n_parts=NUM_OF_MAZES)
        self.mazes: list[mazes.MyMaze] = []
        for maze_idx in range(NUM_OF_MAZES):
            self.mazes.append(
                mazes.MyMaze(seed=self.seed, letters=self.word_parts[maze_idx], maze_index=maze_idx)
            )
        self.info_key_map: dict[int, str] = {}
        for maze_idx in range(NUM_OF_MAZES):
            self.info_key_map[self.mazes[maze_idx].info_key] = f'{self.deceptive_letters[maze_idx].upper()} is deceptive!'
        self.grid_shape = self.mazes[0].grid_shape

        self.revealed_exit: bool = False

        
        # visual clues
        self._generate_color_marks_to_show()
        self._generate_somethings_to_show()
        self._generate_checkpoint_codes()
        self._generate_random_starting_position()
        self._generate_exit()

        self.__print_info()

    def __print_info(self):
        print(f'{self.word_to_win=}\n{self.deceptive_letters=}\n{self.starting_position=}\n{self.word_parts=}\n{self.info_key_map=}\n{self.checkpoint_codes=}\n{self.seed=}')

    def _generate_color_marks_to_show(self):
        self.color_marks_to_show = np.zeros((NUM_OF_MAZES, *self.grid_shape), dtype=int)
        random.seed(self.seed)
        for maze_id, maze in enumerate(self.mazes):
            marks = maze.get_all_color_marks()
            random.shuffle(marks)
            marks_to_show = marks[:PER_MAP_COLOR_MARKS_SHOWN]
            deceptive_mark_id = random.randrange(PER_MAP_COLOR_MARKS_SHOWN) # this one lies
            for idx, ((i, j), tc) in enumerate(marks_to_show):
                if idx != deceptive_mark_id:
                    self.color_marks_to_show[maze_id, i, j] = tc.value
                else:
                    self.color_marks_to_show[maze_id, i, j] = tc.value+1 if tc.value != 3 else 1
    
    def _generate_somethings_to_show(self):
        self.somethings_to_show = np.zeros((NUM_OF_MAZES, *self.grid_shape), dtype=int)
        random.seed(self.seed)
        for maze_id, maze in enumerate(self.mazes):
            hints = maze.get_all_things()
            random.shuffle(hints)
            hints_to_show = hints[:SOMETHING_HINTS_SHOWN]
            for ((i, j), _) in hints_to_show:
                self.somethings_to_show[maze_id, i, j] = 1

    def _generate_checkpoint_codes(self):
        self.checkpoint_codes: dict[tuple[int, int, int], int] = {}
        for maze_id, maze in enumerate(self.mazes):
            self.checkpoint_codes.update(maze.checkpoint_codes)
        self.checkpoint_codes_backw = dict(zip(self.checkpoint_codes.values(), self.checkpoint_codes.keys()))

    def _generate_random_starting_position(self):
        random.seed(self.seed + 10)
        maze_index = np.random.randint(NUM_OF_MAZES)
        all_empty_passes = self.mazes[maze_index].get_all_empty_passes()
        chosen_tile_pos = random.choice(all_empty_passes)
        self.starting_position = (maze_index, *chosen_tile_pos)

    def _generate_exit(self):
        random.seed(self.seed + 11)
        maze_index = np.random.randint(NUM_OF_MAZES)
        all_empty_passes = self.mazes[maze_index].get_all_empty_passes()
        chosen_tile_pos = random.choice(all_empty_passes)
        self.exit_position = (maze_index, *chosen_tile_pos)
