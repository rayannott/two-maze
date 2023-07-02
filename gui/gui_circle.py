'''
All curcilar gui objects
'''

from abc import ABC, abstractmethod
import math
from typing import Optional

import pygame

from gui.gui_rect import Label, Panel
from gui.gui_utils import FONT_NORM, FONT_SMALL, WHITE, WINDOW_SIZE


class GUICircle(ABC):
    def __init__(
            self,
            center: tuple[float, float],
            radius: float,
            surface: pygame.Surface,
            text: str = '',
            hoverhint: str = '',
            text_font: pygame.font.Font = FONT_NORM,
            parent: Optional[Panel] = None
        ) -> None:
        super().__init__()
        self.center = center
        self.radius = radius
        self.surface = surface
        self.text = text
        self.hoverhint = hoverhint
        self.text_font = text_font
        self.parent = parent
        self.active = True
        self.visible = True
        self.hovering = False # boolean flag updated every frame
        self.depth = 1 if parent else 0

        self.color_frame = WHITE

        self.text_label = Label(self.text, self.surface, self.text_font, WHITE, center=self.center)
        self.hint_label = Label(self.hoverhint, self.surface, FONT_SMALL, WHITE, bottomleft=(3, WINDOW_SIZE[1] - 3))
    
    def set_visible(self, set_to: bool) -> None:
        self.visible = set_to

    def set_active(self, set_to: bool) -> None:
        self.active = set_to

    def set_frame_color(self, set_to: str):
        self.color_frame = set_to
    
    def set_text(self, set_to: str) -> None:
        self.text_label.set_text(set_to)

    def clicked(self) -> bool:
        return self.active and self.hovering

    @abstractmethod
    def draw(self) -> None:
        if self.visible:
            pygame.draw.circle(self.surface, self.color_frame, self.center, self.radius, width=2 if self.hovering else 1)

    @abstractmethod
    def update(self, current_mouse_pos: tuple[int, int]):
        self.hovering = (current_mouse_pos[0] - self.center[0])**2 + (current_mouse_pos[1] - self.center[1])**2 < self.radius**2
        if self.hoverhint and self.hovering:
            self.hint_label.update()
        self.draw()
        self.text_label.update()


class DummyCircle(GUICircle):
    def __init__(self, center: tuple[float, float], radius: float, surface: pygame.Surface, text: str = '', hoverhint: str = '', text_font: pygame.font.Font = FONT_NORM, parent: Panel | None = None) -> None:
        super().__init__(center, radius, surface, text, hoverhint, text_font, parent)

    def draw(self) -> None:
        return super().draw()
    
    def update(self, current_mouse_pos: tuple[int, int]):
        return super().update(current_mouse_pos)


class ProgressCircle(GUICircle):
    def __init__(self, 
                center: tuple[float, float], 
                radius: float, surface: pygame.Surface,
                progress: float = 0.3,
                text: str = '', hoverhint: str = '',
                text_font: pygame.font.Font = FONT_NORM, 
                parent: Panel | None = None
        ) -> None:
        super().__init__(center, radius, surface, text, hoverhint, text_font, parent)
        self.progress = progress
        self.RESOLUTION = 100
        self.k = int(self.progress * self.RESOLUTION)

    def draw(self) -> None:
        for i in range(self.k):
            theta = 2 * math.pi * i / self.RESOLUTION - math.pi * 0.5
            pygame.draw.line(
                self.surface, WHITE, self.center,
                (self.center[0] + self.radius * math.cos(theta) * 0.8, self.center[1] + self.radius * math.sin(theta) * 0.8),
                width=3
            )
        return super().draw()
    
    def update(self, current_mouse_pos: tuple[int, int]):
        self.k = int(self.progress * self.RESOLUTION)
        return super().update(current_mouse_pos)
    
    def set_progress(self, set_to: float) -> None:
        if set_to <= 1.009:
            self.progress = set_to
    
    def change_progress(self, delta: float) -> None:
        if 0 <= self.progress + delta <= 1.009:
            self.progress += delta
