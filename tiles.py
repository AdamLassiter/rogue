#! /usr/bin/env python3

import pygame
from pygame.locals import *

from constants import *
from effects import BonfireFlame
from objects import Object

pygame.init()


class Tile(Object):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.explored = False

    def draw(self, surface: pygame.Surface):
        if self.visible(self.game.player.position):
            super().draw(surface)
        elif self.explored:
            self.alpha = 64
            super().draw(surface)

    def update(self):
        if self.visible(self.game.player.position):
            self.explored = True


class Dirt(Tile):

    def __init__(self, *args, character: str = '.', color: tuple = BROWN,
                 solid: bool = False, **kwargs):
        kwargs.update({'character': character, 'color': color, 'solid': solid})
        super().__init__(*args, **kwargs)


class Wall(Tile):

    def __init__(self, *args, character: str = '#', color: tuple = GREY,
                 solid: bool = True, **kwargs):
        kwargs.update({'character': character, 'color': color, 'solid': solid})
        super().__init__(*args, **kwargs)


class Bonfire(Tile):

    def __init__(self, *args, character: str = 'x', color: tuple = DARK_BROWN,
                 solid: bool = False, **kwargs):
        kwargs.update({'character': character, 'color': color, 'solid': solid})
        super().__init__(*args, **kwargs)

    def draw(self, surface: pygame.Surface):
        self.alpha = 255
        super().draw(surface)

    def update(self):
        if self.position == self.game.player.position:
            pygame.event.post(pygame.event.Event(BONFIRE_EVENT, {}))
        for _ in range(3):
            BonfireFlame(self.game, self.position).spawn()
        super().update()
