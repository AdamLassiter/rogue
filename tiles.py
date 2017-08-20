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
        if self.explored:
            super().draw(surface)
        else:
            self.explored = self.visible(self.player.position)


class Ladder(Tile):

    def __init__(self, *args, character: str = 'H', color: tuple = YELLOW,
                 solid: bool = False, **kwargs) -> None:
        kwargs.update({'character': character, 'color': color, 'solid': solid})
        super().__init__(*args, **kwargs)

    def update(self):
        if self.player.position == self.position:
            pygame.event.post(pygame.event.Event(LADDER_EVENT, {'ladder': self}))
            self.player.inventory.append(self)
