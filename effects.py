#! /usr/bin/python3

from random import random, randrange

import pygame
from pygame.locals import *

from constants import *
from objects import Object
from vector import vector

pygame.init()


class Effect(Object):

    def __init__(self, *args, solid: bool = False, transparent: bool = True, **kwargs):
        kwargs.update({'solid': solid, 'transparent': transparent})
        super().__init__(*args, **kwargs)

    def draw(self, surface: pygame.Surface):
        super().draw(surface)

    def update(self):
        self.position += self.velocity

    def spawn(self):
        self.map.effects.append(self)

    def destroy(self):
        if self in self.map.effects:
            del self.map.effects[self.map.effects.index(self)]


class HitMarker(Effect):

    def __init__(self, *args, character: str = '*', color: tuple = RED, **kwargs):
        kwargs.update({'character': character, 'color': color})
        super().__init__(*args, **kwargs)
        self.position += vector([random() - 0.5, random() - 0.5])
        self.velocity = vector([0, -1/3])
        self.lifespan = 3

    def draw(self, surface: pygame.Surface):
        self.alpha = 255 * self.lifespan  / 3
        super().draw(surface)

    def update(self):
        if self.lifespan <= 0:
            self.destroy()
        self.lifespan -= 1
        super().update()


class BonfireFlame(HitMarker):

    def __init__(self, *args, character: str = '*', **kwargs):
        y, r, b = vector(YELLOW), vector(RED), random()
        flame_color = tuple(((y * b) ** 2 + (r * (1 - b)) ** 2) ** 0.5)
        kwargs.update({'character': character, 'color': flame_color})
        super().__init__(*args, **kwargs)


class StoneGlare(Effect):

    def __init__(self, *args, character: str = '\N{FULL BLOCK}',
                 color: tuple = GREY, **kwargs):
        kwargs.update({'character': character, 'color': color})
        super().__init__(*args, **kwargs)
        if self.player.speed > 0:
            self.player.speed -= 1
            self.dv = 1
        else:
            self.dv = 0
        self.lifespan = 5

    def draw(self, surface: pygame.Surface):
        self.alpha = 128
        super().draw(surface)

    def update(self):
        self.lifespan -= 1
        if self.lifespan <= 0:
            self.player.speed += self.dv
            self.destroy()
        self.position = self.player.position + self.player.velocity


class Fireball(Effect):

    def __init__(self, *args, parent: Object = None, character: str = 'o',
                 color: tuple = RED, **kwargs):
        kwargs.update({'character': character, 'color': color})
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.path = Object.bresenham(parent.position, self.player.position)
        self.distance = 0

    def update(self):
        self.distance += 1
        self.distance %= len(self.path)
        self.distance += self.distance == 0
        d_pos = self.path[self.distance] - self.path[self.distance - 1]
        next_obj = self.map[self.position + d_pos]
        if next_obj.solid:
            if hasattr(next_obj, 'take_damage') and next_obj is not self.parent:
                self.parent.deal_damage(next_obj)
            self.destroy()
        else:
            self.velocity = d_pos
        super().update()
