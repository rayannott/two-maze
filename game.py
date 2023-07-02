import random

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
