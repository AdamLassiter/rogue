#! /usr/bin/python3

import pygame
from pygame.locals import *

from constants import *
from effects import Effect
from vector import vector

pygame.init()


class Pickup(Effect):

    def __init__(self, *args, solid: bool = False, **kwargs):
        kwargs.update({'solid': solid})
        super().__init__(*args, **kwargs)

    def pickup(self):
        self.player.inventory.append(self)
        self.destroy()

    def drop(self):
        self.spawn()

    def draw(self, surface: pygame.Surface):
        if self.visible(self.player.position):
            super().draw(surface)

    def update(self):
        if self.player.position == self.position:
            self.pickup()


class Ladder(Pickup):

    def __init__(self, *args, character: str = 'H', color: tuple = YELLOW, **kwargs):
        kwargs.update({'character': character, 'color': color})
        super().__init__(*args, **kwargs)

    def update(self):
        if self.player.position == self.position:
            pygame.event.post(pygame.event.Event(LADDER_EVENT, {'ladder': self}))
        super().update()


class Sword(Pickup):

    def __init__(self, *args, character: str = '/', color: tuple = GREY, **kwargs):
        kwargs.update({'character': character, 'color': color})
        super().__init__(*args, **kwargs)

    def pickup(self):
        self.player.attack += 1
        super().pickup()

    def drop(self):
        self.player.attack -= 1
        super().drop()
