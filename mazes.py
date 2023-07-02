from dataclasses import dataclass
from enum import Enum, auto

import numpy as np
import matplotlib.pyplot as plt

from mazelib import Maze
from mazelib.generate.Prims import Prims

NUM_OF_CHECKPOINTS = 4
NUM_OF_MARKS = 30
NUM_OF_MAZES = 3


COLORS = [
    np.array([1., 1., 1.]),
    np.array([0.19140625, 0.8046875 , 0.74609375]),
    np.array([0.78125   , 0.16796875, 0.828125  ]),
    np.array([0.8046875 , 0.875     , 0.12109375])
]

class TT(Enum):
    '''TT = TileType'''
    WALL = 0
    PASS = 1


class TC(Enum):
    '''TC = TileColor'''
    BLANK = 0
    CYAN = 1
    MAGENTA = 2
    YELLOW = 3


class TileItemType(Enum):
    LETTER = auto()
    CHECKPOINT = auto()
    PIT = auto()


class TileItem:
    def __init__(self, tile_item_type: TileItemType) -> None:
        self.tile_item_type = tile_item_type

class LetterTI(TileItem):
    def __init__(self, letter: str) -> None:
        super().__init__(tile_item_type=TileItemType.LETTER)
        self.letter = letter
    def __repr__(self) -> str:
        return f'Letter({self.letter})'

class CheckpointTI(TileItem):
    def __init__(self, code: int) -> None:
        super().__init__(tile_item_type=TileItemType.CHECKPOINT)
        self.code = code
    
    def __repr__(self) -> str:
        return f'Checkpoint({self.code})'

class PitTI(TileItem):
    def __init__(self, index: int) -> None:
        super().__init__(tile_item_type=TileItemType.PIT)
        self.index = index
    
    def __repr__(self):
        return f'Pit({self.index})'

@dataclass
class Tile:
    _type: TT
    has: TileItem | None = None
    color: TC = TC.BLANK
    visible: bool = True # True if not under fog


class MyMaze:
    def __init__(self, seed: int, letters: str, maze_index: int) -> None:
        self.seed = seed * (1 + maze_index) # so that NUM_OF_MAZES are all different
        self.maze_index = maze_index
        self.letters_in_this_maze = letters
        self.checkpoint_codes = [np.random.randint(2**16) for _ in range(NUM_OF_CHECKPOINTS)]

        self._maze_generated = Maze(self.seed)
        self._maze_generated.generator = Prims(10, 15)
        self._maze_generated.generate()
        self.m_grid = 1 - self._maze_generated.grid # 1 is pass, 0 is wall
        self.grid_shape: tuple[int, int] = self.m_grid.shape
        

        self._create_maze()
        self._add_colors()
        self._add_pits()
        self._add_letters()
        self._add_checkpoints()
        self._add_fog()

    def _create_maze(self):
        self.maze: list[list[Tile]] = []
        for i in range(self.grid_shape[0]):
            _row = []
            for j in range(self.grid_shape[1]):
                _row.append(Tile(TT.PASS if self.m_grid[i, j] else TT.WALL))
            self.maze.append(_row)
    
    def _add_fog(self):
        np.random.seed(self.seed+1)
        h, w = self.grid_shape
        N_BLOBS = 3 + (1 if np.random.random() < 0.25 else 0)
        for _ in range(N_BLOBS):
            epicenter = (np.random.randint(1, h-1), np.random.randint(1, w-1))
            for dh in range(-3, 4):
                for dw in range(-3, 4):
                    point = epicenter[0] + dh, epicenter[1] + dw
                    if not (0 <= point[0] < h and 0 <= point[1] < w):
                        continue 
                    r = np.random.random()
                    if r < np.sqrt(1./(abs(dh) + abs(dw) + 1)):
                        self.maze[point[0]][point[1]].visible = False
    
    def _get_n_unoccupied_points(self, n: int, seed: int) -> list[tuple[int, int]]:
        np.random.seed(seed)
        h, w = self.grid_shape
        points = []
        while len(points) < n:
            pt = (np.random.randint(1, h-1), np.random.randint(1, w-1))
            if self.maze[pt[0]][pt[1]]._type == TT.PASS and self.maze[pt[0]][pt[1]].has is None:
                points.append(pt)
        return points

    def _add_colors(self):
        np.random.seed(self.seed+2)
        points = self._get_n_unoccupied_points(NUM_OF_MARKS, self.seed+2)
        COLOR_MAP = [TC.CYAN, TC.MAGENTA, TC.YELLOW]
        for p in points:
            self.maze[p[0]][p[1]].color = COLOR_MAP[np.random.randint(3)]
    
    def _add_letters(self):
        points = self._get_n_unoccupied_points(len(self.letters_in_this_maze), self.seed+3)
        for letter, p in zip(self.letters_in_this_maze, points):
            self.maze[p[0]][p[1]].has = LetterTI(letter=letter)

    def _add_checkpoints(self):
        points = self._get_n_unoccupied_points(NUM_OF_CHECKPOINTS, self.seed+4)
        for cp_code, p in zip(self.checkpoint_codes, points):
            self.maze[p[0]][p[1]].has = CheckpointTI(code=cp_code)
    
    def _add_pits(self):
        NUM_OF_PITS = NUM_OF_MAZES - 1
        points = self._get_n_unoccupied_points(NUM_OF_PITS, self.seed+5)
        points_iter = iter(points)
        for pit_idx in range(NUM_OF_MAZES):
            if pit_idx != self.maze_index:
                p = next(points_iter)
                self.maze[p[0]][p[1]].has = PitTI(index=pit_idx)
    
    def __str__(self) -> str:
        res = ''
        for i in range(self.grid_shape[0]):
            for j in range(self.grid_shape[1]):
                if not self.maze[i][j].visible:
                    res += '?'
                    continue
                if self.maze[i][j]._type == TT.WALL:
                    res += '#'
                    continue
                if self.maze[i][j].has is None:
                    res += '.'
                    continue
                if self.maze[i][j].has.tile_item_type == TileItemType.PIT:
                    res += '!'
                    continue
                if self.maze[i][j].has.tile_item_type == TileItemType.CHECKPOINT:
                    res += '*'
                    continue
                if self.maze[i][j].has.tile_item_type == TileItemType.LETTER:
                    res += self.maze[i][j].has.letter
                    continue
            res += '\n'
        return res

    def plot_mpl(self, fog: bool = True):
        maze_img = np.zeros((*self.grid_shape, 3), dtype=float)
        for i in range(self.grid_shape[0]):
            for j in range(self.grid_shape[1]):
                if fog and not self.maze[i][j].visible:
                    maze_img[i, j, :] = 0.5
                    continue
                if self.maze[i][j]._type == TT.WALL:
                    maze_img[i, j, :] = 0.
                    continue
                # this is PASS:
                maze_img[i, j, :] = COLORS[self.maze[i][j].color.value]
                if self.maze[i][j].has is None:
                    continue
                if self.maze[i][j].has.tile_item_type == TileItemType.PIT:
                    maze_img[i, j, :] = np.array([1., 0., 0.]) # red
                    continue
                if self.maze[i][j].has.tile_item_type == TileItemType.CHECKPOINT:
                    maze_img[i, j, :] = np.array([0., 0., 1.]) # blue
                    continue
                if self.maze[i][j].has.tile_item_type == TileItemType.LETTER:
                    maze_img[i, j, :] = np.array([0., 1., 0.]) # green
                    continue
        plt.imshow(maze_img)
        plt.show()
