#! /usr/bin/python3

from random import randrange

import pygame
from pygame.locals import *

from constants import *
from objects import Object
from effects import HitMarker, StoneGlare, Fireball
from vector import vector

pygame.init()


class Fighter(Object):

    def __setattr__(self, name, value):
        if name == 'position' and value is not None:
            if self.underneath is not None:
                self.map[self.position] = self.underneath
                self.last_position = self.position
            self.underneath = self.map[value]
            self.map[value] = self
        super().__setattr__(name, value)

    def __init__(self, *args, stats: tuple = (0, 0, 0, 0), transparent: bool =
                 True, **kwargs):
        self.max_hp, self.attack, self.defense, self.speed = stats
        self.hp = self.max_hp
        self.underneath = None
        kwargs.update({'transparent': transparent})
        self.last_position = args[2]
        super().__init__(*args, **kwargs)
        self.move_counter = 1

    def draw(self, surface: pygame.Surface):
        if self.visible(self.player.position):
            super().draw(surface)
        else:
            self.underneath.draw(surface)

    def update(self):
        if self.move_counter == 0:
            super().update()
        if self.underneath is not None:
            self.underneath.update()
        self.move_counter += 1
        self.move_counter %= 5 - self.speed

    def deal_damage(self, target: Object):
        damage = max((self.attack - target.defense, 0))
        target.take_damage(damage)

    def take_damage(self, damage: int):
        hit = HitMarker(self.player, self.map, self.position)
        hit.spawn()
        self.hp -= damage
        if self.hp <= 0:
            pygame.event.post(pygame.event.Event(PLAYER_KILL, {}))


class Player(Fighter):

    def __init__(self, *args, stats: tuple = (5, 2, 0, 4), character: str = '@',
                 **kwargs):
        kwargs.update({'stats': stats, 'character': character})
        super().__init__(*args, **kwargs)
        self.inventory = []

    def update(self):
        self.keypresses = kp = list(map(int, pygame.key.get_pressed()))
        if self.move_counter == 0:
            self.velocity = vector([kp[K_d] - kp[K_a],
                                    kp[K_s] - kp[K_w]])
        super().update()

    def take_damage(self, damage: int):
        super().take_damage(damage)
        if self.hp <= 0:
            pygame.event.post(pygame.event.Event(PLAYER_KILL, {}))


class Troll(Fighter):

    def __init__(self, *args, stats: tuple = (5, 1, 1, 1), character: str = 'T',
                 color: tuple = GREEN, **kwargs):
        kwargs.update({'stats':stats, 'character': character, 'color': color})
        super().__init__(*args, **kwargs)

    def update(self):
        visible = self.visible(self.player.position)
        if visible and self.move_counter == 0:
            dist = visible
            d_pos = self.player.position - self.position
            if dist >= 2:
                self.velocity = vector(map(lambda x: int(round(x / dist)), d_pos))
            elif self.player.hp > 0:
                self.deal_damage(self.player)
            else:
                pass
        elif self.move_counter == 0:
            self.velocity = vector([randrange(-1, 2) for _ in range(2)])
        else:
            self.velocity = vector([0, 0])
        super().update()


class Gorgon(Fighter):

    def __init__(self, *args, stats: tuple = (1, 0, 0, 0), character: str = 'G',
                 color: tuple = GREEN, **kwargs):
        kwargs.update({'stats': stats, 'character': character, 'color': color})
        super().__init__(*args, **kwargs)
        self.explored = False

    def update(self):
        dist = self.visible(self.player.position)
        if dist:
            self.explored = True
        if 0 < dist < 10 and self.move_counter == 0:
            StoneGlare(self.player, self.map, self.player.position).spawn()
        super().update()


class Wizard(Fighter):

    def __init__(self, *args, stats: tuple = (5, 2, 0, 3), character: str = 'W',
                 color: tuple = PURPLE, **kwargs):
        kwargs.update({'stats': stats, 'character': character, 'color': color})
        super().__init__(*args, **kwargs)
        self.fireball_counter = 0

    def update(self):
        dist = self.visible(self.player.position)
        if 0 < dist < 10 and self.move_counter == self.fireball_counter == 0:
            Fireball(self.player, self.map, self.position, parent=self).spawn()
        if self.move_counter == 0:
            self.velocity = vector([randrange(-1, 2) for _ in range(2)])
            self.fireball_counter = (self.fireball_counter + 1) % 5
        super().update()
