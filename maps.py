#! /usr/bin/env python3

from random import shuffle, choice, randrange
import resource
import sys
from typing import *

import pygame
from numpy import array, concatenate, set_printoptions, inf

from constants import *
from objects import UpdateRenderable
from tiles import Air, Wall, Dirt, Bonfire
from fighters import Goblin, Gorgon, Wizard
from pickups import Ladder, Sword
from vector import vector

resource.setrlimit(resource.RLIMIT_STACK, (2**29, -1))
sys.setrecursionlimit(10**6)
set_printoptions(threshold=inf)
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
        return vector([self.x1 + self.x2, self.y1 + self.y2, 2]) // 2

    def overlaps(self, other) -> bool:
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

    @property
    def slice(self) -> tuple:
        return (slice(self.x1, self.x2),
                slice(self.y1, self.y2),
                slice(None, None))


class Map(metaclass=UpdateRenderable):

    def __init__(self, game_ref, size: vector, from_map: array = None):
        self.game = game_ref
        self.size = size
        self.player_start = None
        self.effects = []
        if from_map is not None:
            self.map = from_map
        else:
            self.gen_map()

    def __getitem__(self, slice_):
        if len(slice_) == 3:
            xs, ys, zs = slice_
        else:
            xs, ys = slice_
            zs = slice(None, None)
        ret_sl = not isinstance(slice_, vector)
        if ret_sl and None not in [xs.start, xs.stop] and xs.start < 0 <= xs.stop:
            left = self[slice(xs.start, None), ys, zs]
            right = self[slice(None, xs.stop), ys, zs]
            return concatenate((left, right), axis=1)
        elif ret_sl and None not in [ys.start, ys.stop] and ys.start < 0 <= ys.stop:
            top = self[xs, slice(ys.start, None), zs]
            botm = self[xs, slice(None, ys.stop), zs]
            return concatenate((top, botm), axis=0)
        return self.map[ys, xs, zs]

    def __setitem__(self, slice_, value):
        if len(slice_) == 3:
            xs, ys, zs = slice_
        else:
            xs, ys = slice_
            zs = slice(None, None)
        self.map[ys, xs, zs] = value

    def __repr__(self):
        return '\n'.join([''.join([repr(tile[1]) if not isinstance(tile[1], Air)
                                   else repr(tile[0]) for tile in row])
                          for row in self.map])

    def gen_map(self):
        raise NotImplementedError

    @property
    def renders(self) -> list:
        effect_objs = [effect.render for effect in self.effects]
        tile_objs = self.mapslice.renders
        return effect_objs + tile_objs

    def update(self):
        xc, yc, _ = position = self.game.player.position
        x0, y0, _ = position - vector([DISP_WIDTH, DISP_HEIGHT, 0]) // 2
        mslice = self[x0:x0 + DISP_WIDTH, y0:y0 + DISP_HEIGHT, :]
        self.mapslice = MapSlice(self.game, mslice)
        self.mapslice.update()
        for effect in self.effects:
            effect.update()


class MapSlice(Map):

    def __init__(self, game_ref, map_slice: array):
        size = vector([len(map_slice[0]), len(map_slice), len(map_slice[0, 0])])
        super().__init__(game_ref, size, from_map=map_slice)

    @property
    def renders(self) -> list:
        tile_vecs = []
        for row in self.map:
            for column in row:
                for cell in column:
                    tile_vecs.append(cell.render)
        return tile_vecs

    def update(self):
        for row in self.map.copy():
            for column in row:
                for cell in column:
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

        mapdat = make_maze(self.size[0], self.size[1])
        w = lambda x, y: [Wall(self.game, vector([x, y, z]))
                          for z in range(self.size[2])]
        d = lambda x, y: [Dirt(self.game, vector([x, y, 0]))] + \
                         [Air(self.game, vector([x, y, z]))
                          for z in range(1, self.size[2])]
        x_max, y_max, z_max = self.size
        _map = [[w(x, y) if mapdat[y][x] == '#' or
                 x + 1 == x_max or y + 1 == y_max
                 else d(x, y)
                 for x in range(self.size[0])] for y in range(self.size[1])]
        self.map = array(_map, ndmin=3)
        self.player_start = vector([1, 1, 1])

    def populate(self):
        pass


class Dungeon(Maze):
    ATTEMPTS = 40

    def populate(self):
        self.player_start = self.rooms[0].center
        self[self.player_start] = Bonfire(self.game, self.player_start)

        items = [Ladder, Sword]
        for Item, room in zip(items, self.rooms[1:]):
            pos = vector([randrange(room.x1, room.x2),
                          randrange(room.y1, room.y2),
                          1])
            Item(self.game, pos).spawn()

        for room in self.rooms[len(items) + 1:]:
            Spawn = choice([Goblin, Wizard, Gorgon])
            pos = vector([randrange(room.x1, room.x2),
                          randrange(room.y1, room.y2),
                          1])
            self[pos] = Spawn(self.game, pos)

    def gen_map(self):
        super().gen_map()
        br_x, br_y, _ = self.size - ROOM_MIN_SIZE
        self.rooms = [Room(1, 1, ROOM_MIN_SIZE, ROOM_MIN_SIZE),
                      Room(br_x, br_y, ROOM_MIN_SIZE, ROOM_MIN_SIZE)]

        for _ in range(Dungeon.ATTEMPTS):
            width = randrange(ROOM_MIN_SIZE, ROOM_MAX_SIZE, 2)
            height = randrange(ROOM_MIN_SIZE, ROOM_MAX_SIZE, 2)
            x = randrange(1, self.size[0] - width, 2)
            y = randrange(1, self.size[1] - height, 2)
            room = Room(x, y, width, height)
            if not any(map(room.overlaps, self.rooms)):
                self.rooms.append(room)

        for room in self.rooms:
            self[room.slice] = [[[Dirt(self.game, vector([x, y, 0])),
                                  Air(self.game, vector([x, y, 1]))]
                                 for x in range(room.x1, room.x2)]
                                for y in range(room.y1, room.y2)]
