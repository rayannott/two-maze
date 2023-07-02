import random
import mazes

from utils.constants import *
from utils.utils import get_english_words, split_word_into

class Game:
    def __init__(self, room_id: int, second_player: bool) -> None:
        self.seed = room_id
        self.second_player = second_player # 1st: False, 2nd: True
        random.seed(self.seed)
        self.word_to_win = random.choice(get_english_words())
        self.word_parts = split_word_into(self.word_to_win, n_parts=NUM_OF_MAZES)
        self.mazes: list[mazes.MyMaze] = []
        for maze_idx in range(NUM_OF_MAZES):
            self.mazes.append(
                mazes.MyMaze(seed=self.seed, letters=self.word_parts[maze_idx], maze_index=maze_idx)
            )
        