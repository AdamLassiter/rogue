#! /usr/bin/python3

import pygame

from constants import *
from objects import Object
from vector import vector

pygame.init()


class Label:
    FONT = Object.FONT

    def __init__(self, position: vector, label: str, value, color: tuple = WHITE) -> None:
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


class Inventory:
    FONT = Object.FONT

    def __init__(self, player_ref, position: vector):
        self.player = player_ref
        self.position = position
        self.items = [x for x in player_ref.inventory]

    def draw(self, surface: pygame.Surface):
        if self.items != self.player.inventory:
            self.items = [x for x in self.player.inventory]
        for n, item in enumerate(self.items):
            surface.blit(item.character, (self.position + vector([0, n])) * OBJECT_SIZE)

    def update(self):
        pass


class Hud(Object):

    def __init__(self, player_ref):
        self.player_ref = pr = player_ref
        self.position = p = vector([0, 0])
        self.labels = [Label(p + vector([0, 0]), ' HP', lambda: str(pr.hp)),
                       Label(p + vector([0, 1]), 'ATK', lambda: str(pr.attack)),
                       Label(p + vector([0, 2]), 'DEF', lambda: str(pr.defense)),
                       Label(p + vector([0, 3]), 'SPD', lambda: str(pr.speed))]
        self.inventory = Inventory(player_ref, p + vector([0, 5]))
        self.solid = False

    def draw(self, surface: pygame.Surface):
        self.inventory.draw(surface)
        for label in self.labels:
            label.draw(surface)

    def update(self):
        self.inventory.update()
        for label in self.labels:
            label.update()
