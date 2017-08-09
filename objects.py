from random import randrange
from typing import *

import pygame
from pygame.locals import *
pygame.init()

from constants import *
from vector import vector


class Object:
    FONT = pygame.font.SysFont('Monospace Regular', int(OBJECT_SIZE * 1.4))

    def __init__(self, player_ref, map_ref, position: vector, character: str = '',
                 color: Iterable[int] = WHITE, solid: bool = True,
                 transparent: bool = None) -> None:
        self.player = player_ref
        self.map = map_ref
        self.character = Object.FONT.render(character, False, color, BLACK).convert()
        self.position = position
        self.solid = solid
        self.transparent = not solid if transparent is None else transparent
        self.velocity = vector([0, 0])

    def draw(self, surface: pygame.Surface):
        def dist(objA: tuple, objB: tuple) -> float:
            x1, y1 = objA
            x2, y2 = objB
            return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
        position = self.position - self.player.position
        alpha = 255 / (dist((0, 0), position) / OBJECT_SHADOW + 1) ** 2
        self.character.set_alpha(alpha)
        blit_at = (position + GAME_CENTER) * OBJECT_SIZE
        rect = self.character.get_rect(center=blit_at + OBJECT_SIZE // 2)
        surface.blit(self.character, rect)

    def visible(self, other_position: vector) -> bool:
        def bresenham(start: vector, end: vector):
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
            return points
        line_of_sight = bresenham(self.position, other_position)[1:-1]
        return all([self.map[x].transparent for x in line_of_sight])

    def update(self):
        if not self.map.blocked(self.position + self.velocity):
            self.position = self.position + self.velocity


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

    def __init__(self, *args, character: str = 'H', color: tuple = YELLOW, **kwargs) -> None:
        kwargs.update({'character': character, 'color': color})
        super().__init__(*args, **kwargs)

    def update(self):
        if self.player.position == self.position:
            pygame.event.post(pygame.event.Event(LADDER_EVENT, {'ladder': self}))


class Fighter(Object):

    def __init__(self, *args, stats=(0, 0, 0), **kwargs) -> None:
        self.max_hp, self.attack, self.defense = stats
        self.hp = self.max_hp
        super().__init__(*args, **kwargs)


class Troll(Object):

    def __init__(self, *args, character: str = 'T', color: tuple = GREEN, **kwargs) -> None:
        kwargs.update({'character': character, 'color': color})
        super().__init__(*args, **kwargs)

    def draw(self, surface: pygame.Surface):
        if self.visible(self.player.position):
            super().draw(surface)

    def update(self):
        if randrange(3) == 0:
            self.velocity = vector([randrange(-1, 2) for _ in range(2)])
        else:
            self.velocity = vector([0, 0])
        super().update()


class Player(Fighter):

    def __init__(self, *args, character: str = '@', **kwargs) -> None:
        kwargs.update({'character': character})
        super().__init__(*args, **kwargs)

    def update(self):
        keypresses = list(map(int, pygame.key.get_pressed()))
        self.velocity = vector([keypresses[K_d] - keypresses[K_a],
                                keypresses[K_s] - keypresses[K_w]])
        super().update()
