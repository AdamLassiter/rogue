from typing import *

import pygame
pygame.init()

from constants import *
from objects import Object
from vector import vector


class Label:
    FONT = Object.FONT

    def __init__(self, position: vector, label: str, value: Callable[[], str],
                 color: tuple = WHITE) -> None:
        self.position = position
        self.label = label
        self.value = value
        self.color = color
        size = vector([len(label), 1])
        self.center = position + size / 2

    def draw(self, surface: pygame.Surface):
        surface.blit(self.surface, self.position * OBJECT_SIZE)

    def update(self):
        self.surface = Label.FONT.render(self.label + ' ' + self.value(),
                                         False, self.color).convert()


class Hud(Object):

    def __init__(self, player_ref):
        self.player_ref = pr = player_ref
        self.position = p = vector([0, 0])
        self.labels = [Label(p + vector([0, 0]), ' HP', lambda: str(pr.hp)),
                       Label(p + vector([0, 1]), 'ATK', lambda: str(pr.attack)),
                       Label(p + vector([0, 2]), 'DEF', lambda: str(pr.defense))]
        self.solid = False

    def draw(self, surface: pygame.Surface):
        for label in self.labels:
            label.draw(surface)

    def update(self):
        for label in self.labels:
            label.update()