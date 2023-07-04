import random

import numpy as np

import mazes
from utils.constants import *
from utils.utils import get_english_words, split_word_into

class Game:
    def __init__(self, room_id: int, is_second_player: bool) -> None:
        self.seed = room_id
        self.is_second_player = is_second_player # 1st: False, 2nd: True
        random.seed(self.seed)
        self.word_to_win = random.choice(get_english_words())
        letters_doubled = list(random.choice(get_english_words()) * 2)
        random.shuffle(letters_doubled)
        word_to_win_doubled = ''.join(letters_doubled)

        self.word_parts = split_word_into(word_to_win_doubled, n_parts=NUM_OF_MAZES)
        self.mazes: list[mazes.MyMaze] = []
        for maze_idx in range(NUM_OF_MAZES):
            self.mazes.append(
                mazes.MyMaze(seed=self.seed, letters=self.word_parts[maze_idx], maze_index=maze_idx)
            )
        self.grid_shape = self.mazes[0].grid_shape
        
        # visual clues
        self._generate_color_marks_to_show()
        self._generate_somethings_to_show()
        self._generate_checkpoint_codes()

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
        all_checkpoints_coordinates = []
        np.random.seed(self.seed + 9)
        for maze_id, maze in enumerate(self.mazes):
            all_things = maze.get_all_things()
            all_checkpoints_coordinates.extend([(maze_id, *el[0]) for el in all_things if el[1].tile_item_type == mazes.TileItemType.CHECKPOINT])
        self.checkpoint_codes: dict[tuple[int, int, int], int] = {}
        codes = []
        while len(codes) < len(all_checkpoints_coordinates):
            this_code = np.random.randint(1000, 10000)
            if this_code not in codes: codes.append(this_code)
        for code, chp_coord in zip(codes, all_checkpoints_coordinates):
            self.checkpoint_codes[chp_coord] = code
        self.checkpoint_codes_backw = dict(zip(self.checkpoint_codes.values(), self.checkpoint_codes.keys()))
