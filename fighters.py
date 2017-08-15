#! /usr/bin/python3

from typing import *
from random import randrange

import pygame
from pygame.locals import *

from constants import *
from objects import Object
from effects import HitMarker
from vector import vector

pygame.init()


class Fighter(Object):

    def __init__(self, *args, stats: tuple = (0, 0, 0), **kwargs) -> None:
        self.max_hp, self.attack, self.defense = stats
        self.hp = self.max_hp
        super().__init__(*args, **kwargs)

    def deal_damage(self, target):
        damage = max((self.attack - target.defense, 0))
        target.take_damage(damage)

    def take_damage(self, damage):
        hit = HitMarker(self.player, self.map, self.position)
        self.map.objects.append(hit)
        self.hp -= damage
        if self.hp <= 0:
            # ded
            del self


class Troll(Fighter):

    def __init__(self, *args, stats: tuple = (2, 1, 0), character: str = 'T',
                 color: tuple = GREEN, **kwargs) -> None:
        kwargs.update({'stats':stats, 'character': character, 'color': color})
        self.move_counter = 0
        super().__init__(*args, **kwargs)

    def draw(self, surface: pygame.Surface):
        if self.visible(self.player.position):
            super().draw(surface)

    def update(self):
        self.move_counter += 1
        self.move_counter %= 2
        visible = self.visible(self.player.position)
        if visible and self.move_counter:
            dist = visible
            d_pos = self.player.position - self.position
            if dist >= 2:
                # move
                self.velocity = vector(map(lambda x: int(round(x / dist)), d_pos))
            elif self.player.hp > 0:
                self.deal_damage(self.player)
            else:
                pass
        elif self.move_counter:
            self.velocity = vector([randrange(-1, 2) for _ in range(2)])
        else:
            self.velocity = vector([0, 0])
        super().update()


class Player(Fighter):

    def __init__(self, *args, character: str = '@', **kwargs) -> None:
        kwargs.update({'character': character})
        super().__init__(*args, **kwargs)
        self.inventory = []

    def update(self):
        keypresses = list(map(int, pygame.key.get_pressed()))
        self.velocity = vector([keypresses[K_d] - keypresses[K_a],
                                keypresses[K_s] - keypresses[K_w]])
        super().update()

    def take_damage(self, damage):
        super().take_damage(damage)
        if self.hp - damage <= 0:
            pygame.event.post(pygame.event.Event(PLAYER_KILL, {}))
