#! /usr/bin/python3

from typing import *
from random import random

import pygame
from pygame.locals import *

from constants import *
from objects import Object
from vector import vector

pygame.init()


class Effect(Object):

    def __init__(self, *args, solid=False, transparent=True, **kwargs):
        kwargs.update({'solid': solid, 'transparent': transparent})
        super().__init__(*args, **kwargs)

    def draw(self, surface: pygame.Surface):
        position = self.position - self.player.position
        blit_at = (position + GAME_CENTER) * OBJECT_SIZE
        rect = self.character.get_rect(center=blit_at + OBJECT_SIZE // 2)
        surface.blit(self.character, rect)

    def update(self):
        self.position += self.velocity


class HitMarker(Effect):
    def __init__(self, *args, character='*', color=RED, **kwargs):
        kwargs.update({'character': character, 'color': color})
        super().__init__(*args, **kwargs)
        self.position += vector([random() - 0.5, random() - 0.5])
        self.velocity = vector([0, -1/3])
        self.lifespan = 3

    def draw(self, surface: pygame.Surface):
        self.character.set_alpha(255 * self.lifespan  / 3)
        super().draw(surface)
        self.lifespan -= 1
        if self.lifespan <= 0:
            del self.map.objects[self.map.objects.index(self)]
