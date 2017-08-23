#! /usr/bin/python3

import pygame
from pygame.locals import *

from constants import *
from objects import Object
from vector import vector

pygame.init()


class Tile(Object):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.explored = False

    def draw(self, surface: pygame.Surface):
        if self.visible(self.player.position):
            self.explored = True
        if self.explored:
            super().draw(surface)


class Dirt(Tile):

    def __init__(self, *args, character: str = '.', color: tuple = BROWN,
                 solid: bool = False, **kwargs) -> None:
        kwargs.update({'character': character, 'color': color, 'solid': solid})
        super().__init__(*args, **kwargs)


class Wall(Tile):

    def __init__(self, *args, character: str = '#', color: tuple = GREY,
                 solid: bool = True, **kwargs) -> None:
        kwargs.update({'character': character, 'color': color, 'solid': solid})
        super().__init__(*args, **kwargs)


class Ladder(Tile):

    def __init__(self, *args, character: str = 'H', color: tuple = YELLOW,
                 solid: bool = False, **kwargs) -> None:
        kwargs.update({'character': character, 'color': color, 'solid': solid})
        super().__init__(*args, **kwargs)

    def update(self):
        if self.player.position == self.position:
            pygame.event.post(pygame.event.Event(LADDER_EVENT, {'ladder': self}))
