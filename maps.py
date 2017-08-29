#! /usr/bin/python3

from random import shuffle, choice, randint, randrange
import resource
import sys
from typing import *

from constants import *
from objects import Object
from tiles import Wall, Dirt, Bonfire
from fighters import Troll, Gorgon, Wizard
from pickups import Ladder, Sword
from vector import vector

import pygame
import numpy
from numpy import array, concatenate

resource.setrlimit(resource.RLIMIT_STACK, (2**29, -1))
sys.setrecursionlimit(10**6)
numpy.set_printoptions(threshold=numpy.inf)
pygame.init()


class Room:

    def __init__(self, x: int, y: int, w: int, h: int):
        self.x1, self.x2 = x, x + w - 1
        self.y1, self.y2 = y, y + h - 1
        self.w, self.h = w, h

    def __contains__(self, point: vector) -> bool:
        x, y = point
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2

    def __str__(self) -> str:
        return '(%s %s %s %s)' % (self.x1, self.x2, self.y1, self.y2)

    @property
    def center(self) -> vector:
        return vector([self.x1 + self.x2, self.y1 + self.y2]) // 2

    def overlaps(self, other) -> bool:
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

    @property
    def slice(self) -> tuple:
        return (slice(self.x1 + 1, self.x2, None), slice(self.y1 + 1, self.y2))


class Map:

    def __init__(self, player_ref, size: vector, from_map: array = None):
        self.player = player_ref
        self.size = size
        self.player_start = None
        self.effects = []
        if from_map:
            self.map = from_map
        else:
            self.gen_map()
        assert self.map.ndim >= 2

    def __getitem__(self, slice_):
        xs, ys = slice_
        ret_sl = not isinstance(slice_, vector)
        if ret_sl and None not in [xs.start, xs.stop] and xs.start < 0 <= xs.stop:
            left = self[slice(xs.start, None), ys]
            right = self[slice(None, xs.stop), ys]
            return concatenate((left, right), axis=1)
        elif ret_sl and None not in [ys.start, ys.stop] and ys.start < 0 <= ys.stop:
            top = self[xs, slice(ys.start, None)]
            botm = self[xs, slice(None, ys.stop)]
            return concatenate((top, botm), axis=0)
        return self.map[ys, xs]

    def __setitem__(self, slice_, value):
        xs, ys = slice_
        self.map[ys, xs] = value

    def __repr__(self):
        return '\n'.join([''.join([repr(tile) for tile in row])
                          for row in self.map])

    def gen_map(self):
        raise NotImplementedError

    def draw(self, surface: pygame.Surface):
        x0, y0 = position = self.player.position
        xc, yc = position - GAME_CENTER
        mslice = self[xc:xc + GAME_SPRITE_WIDTH, yc:yc + GAME_SPRITE_HEIGHT]
        MapSlice(self.player, mslice).draw(surface)
        for effect in self.effects:
            effect.draw(surface)

    def update(self):
        x0, y0 = position = self.player.position
        xc, yc = position - GAME_CENTER
        mslice = self[xc:xc + GAME_SPRITE_WIDTH, yc:yc + GAME_SPRITE_HEIGHT]
        MapSlice(self.player, mslice).update()
        for effect in self.effects:
            effect.update()


class MapSlice(Map):

    def __init__(self, player_ref, map_slice: array):
        self.player = player_ref
        self.size = vector([len(map_slice[0]), len(map_slice)])
        self.map = map_slice

    def draw(self, surface: pygame.Surface):
        # print(self.map)
        for row in self.map:
            for cell in row:
                cell.draw(surface)

    def update(self):
        for row in self.map.copy():
            for cell in row:
                cell.update()


class Maze(Map):

    def gen_map(self):
        def make_maze(w=20, h=20):
            vis = [[0] * w + [1] for _ in range(h)] + [[1] * (w + 1)]
            ver = [["# "] * w + ['#'] for _ in range(h)] + [[]]
            hor = [["##"] * w + ['#'] for _ in range(h + 1)]

            def walk(x, y):
                vis[y][x] = 1
                d = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]
                shuffle(d)
                for (xx, yy) in d:
                    if vis[yy][xx]:
                        continue
                    if xx == x:
                        hor[max(y, yy)][x] = "# "
                    if yy == y:
                        ver[y][max(x, xx)] = "  "
                    walk(xx, yy)

            walk(randrange(w), randrange(h))
            mapdat = []
            for rrow in zip(hor, ver):
                mapdat.extend([''.join(x) for x in rrow])
            return mapdat

        mapdat = make_maze(*self.size)
        w = lambda x, y: Wall(self.player, self, vector([x, y]))
        d = lambda x, y: Dirt(self.player, self, vector([x, y]))
        _map = [[w(x, y) if mapdat[y][x] == '#'
                 or x+1 in self.size or y+1 in self.size
                 else d(x, y)
                 for x in range(self.size[0])] for y in range(self.size[1])]
        self.map = array(_map, ndmin=2)
        self.player_start = vector([1, 1])
        self[self.player_start] = Bonfire(self.player, self, self.player_start)


class Dungeon(Maze):
    ATTEMPTS = 40

    def populate(self):
        items = [Sword, Ladder]
        for Item, room in zip(items, self.rooms):
            pos = vector([randrange(room.x1+1, room.x2),
                          randrange(room.y1+1, room.y2)])
            Item(self.player, self, pos).spawn()
        for room in self.rooms[len(items):]:
            Spawn = choice([Troll, Wizard, Gorgon])
            pos = vector([randrange(room.x1+1, room.x2),
                          randrange(room.y1+1, room.y2)])
            self[pos] = Spawn(self.player, self, pos)

    def gen_map(self):
        super().gen_map()
        self.rooms = []
        for _ in range(Dungeon.ATTEMPTS):
            width = randrange(ROOM_MIN_SIZE, ROOM_MAX_SIZE, 2)
            height = randrange(ROOM_MIN_SIZE, ROOM_MAX_SIZE, 2)
            x = randrange(0, self.size[0] - width, 2)
            y = randrange(0, self.size[1] - height, 2)
            room = Room(x, y, width, height)
            if not any(map(room.overlaps, self.rooms)):
                self.rooms.append(room)
                self[room.slice] = [[Dirt(self.player, self, vector([x, y]))
                                     for x in range(room.x1 + 1, room.x2)]
                                    for y in range(room.y1 + 1, room.y2)]
        self.populate()
