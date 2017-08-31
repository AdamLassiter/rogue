#! /usr/bin/python3

from time import time

import pygame

from constants import *
from objects import Object
from vector import vector

pygame.init()


class Label:
    FONT = Object.FONT

    def __init__(self, position: vector, label: str, value, color: tuple = WHITE):
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

    def __init__(self, player_ref, ss):
        self.player_ref = pr = player_ref
        self.position = p = vector([0, 0])
        labels = [(' HP', lambda: str(pr.hp)),
                  ('ATK', lambda: str(pr.attack)),
                  ('DEF', lambda: str(pr.defense)),
                  ('SPD', lambda: str(pr.speed)),
                  ('SAV', ss)]
        self.labels = [Label(p + vector([0, i]), text, value)
                       for i, (text, value) in enumerate(labels)]
        self.inventory = Inventory(player_ref, p + vector([GAME_SPRITE_WIDTH - 1, 0]))
        self.solid = False

    def draw(self, surface: pygame.Surface):
        self.inventory.draw(surface)
        for label in self.labels:
            label.draw(surface)

    def update(self):
        self.inventory.update()
        for label in self.labels:
            label.update()
