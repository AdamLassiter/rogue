#! /usr/bin/python3

from random import randrange

import pygame
from pygame.locals import *

from constants import *
from vector import vector

pygame.init()


class Object(object):
    FONT = pygame.font.Font('./DejaVuSansMono.ttf', OBJECT_SIZE)

    def __init__(self, player_ref, map_ref, position: vector, character: str = '',
                 color: tuple = WHITE, solid: bool = True, transparent: bool = None) -> None:
         self.player = player_ref
         self.map = map_ref
         self.char = character
         self.character = Object.FONT.render(character, False, color).convert()
         self.position = position
         self.solid = solid
         self.transparent = not solid if transparent is None else transparent
         self.velocity = vector([0, 0])

    def __repr__(self):
        return self.character

    @staticmethod
    def dist(objA: tuple, objB: tuple) -> float:
         x1, y1 = objA
         x2, y2 = objB
         return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

    def draw(self, surface: pygame.Surface):
        position = self.position - self.player.position
        alpha = 255 / (Object.dist((0, 0), position) / OBJECT_SHADOW + 1) ** 2
        self.character.set_alpha(alpha)
        blit_at = (position + GAME_CENTER) * OBJECT_SIZE
        rect = self.character.get_rect(center=blit_at + OBJECT_SIZE // 2)
        surface.blit(self.character, rect)

    @staticmethod
    def bresenham(start: vector, end: vector) -> list:
        x1, y1 = start
        x2, y2 = end
        dx = x2 - x1
        dy = y2 - y1
        is_steep = abs(dy) > abs(dx)
        if is_steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
        swapped = x1 > x2
        if swapped:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        dx = x2 - x1
        dy = y2 - y1
        error = int(dx / 2.0)
        ystep = 1 if y1 < y2 else -1
        y = y1
        points = []
        for x in range(x1, x2 + 1):
            coord = vector([y, x]) if is_steep else vector([x, y])
            points.append(coord)
            error -= abs(dy)
            if error < 0:
                y += ystep
                error += dx
        return list(reversed(points)) if swapped else points

    def visible(self, other_position: vector) -> int:
        line_of_sight = self.bresenham(self.position, other_position)[1:-1]
        if all([self.map[x].transparent for x in line_of_sight]):
            return Object.dist(self.position, other_position)
        return False

    def update(self):
        if not self.map[self.position + self.velocity].solid:
            self.position += self.velocity
        self.velocity = vector([0, 0])
