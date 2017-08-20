#! /usr/bin/python3

from random import randrange
from typing import *

from constants import *
from objects import Object
from tiles import Tile, Ladder
from fighters import Troll, Gorgon, Wizard
from vector import vector

import pygame
pygame.init()


class Room:

    def __init__(self, x: int, y: int, w: int, h: int) -> None:
        self.x1, self.x2 = x, x + w - 1
        self.y1, self.y2 = y, y + h - 1

    def __contains__(self, point: vector) -> bool:
        x, y = point
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2

    def __str__(self) -> str:
        return '(%s %s %s %s)' % (self.x1, self.x2, self.y1, self.y2)

    def center(self) -> vector:
        return vector([self.x1 + self.x2, self.y1 + self.y2]) // 2

    def overlaps(self, other) -> bool:
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


class Map:

    def __init__(self, player_ref, size: vector) -> None:
        self.player = player_ref
        self.size = size
        self.effects = []

    def __getitem__(self, slices: Union[slice, Iterable]):
        if isinstance(slices, (list, tuple)):
            h, v = slices[0], slices[1]
        else:
            h, v = slices, slice(0, -1, 1)
        return_slice = isinstance(h, slice) or isinstance(v, slice)
        if not isinstance(h, slice):
            h = slice(h, h + 1)
        if not isinstance(v, slice):
            v = slice(v, v + 1)
        hd, vd = (h.start, h.stop, h.step), (v.start, v.stop, v.step)
        hl = len(self.map[0])
        vl = len(self.map)
        if hd[0] < 0 or hd[1] > hl:
            return MapSlice(self.player, [a + b for a, b in zip(self[hd[0] % hl:hl:hd[2], v],
                                                                self[0:hd[1] % hl:hd[2], v])])
        if vd[0] < 0 or vd[1] > vl:
            ret = self[h, vd[0] % vl:vl:vd[2]] + self[h, 0:vd[1] % vl:vd[2]]
        else:
            if not return_slice:
                return self.map[vd[0]][hd[0]]
            ret = [row[h] for row in self.map[v]]
        return MapSlice(self.player, ret)

    def __setitem__(self, slices: Union[slice, Iterable], val: Union[Iterable, Tile]):
        if isinstance(slices, (list, tuple)):
            h, v = slices[0], slices[1]
        else:
            h, v = slices, slice(None, None, None)
        if isinstance(val, Object):
            self.map[v][h] = val
        else:
            self.mapdata[v][h] = val

    def gen_map(self):
        def gen_rooms(attempts: int) -> List[Room]:
            rooms = []
            for _ in range(attempts):
                width = randrange(ROOM_MIN_SIZE, ROOM_MAX_SIZE, 2)
                height = randrange(ROOM_MIN_SIZE, ROOM_MAX_SIZE, 2)
                x = randrange(1, self.size[0] - width, 2)
                y = randrange(1, self.size[1] - height, 2)
                room = Room(x, y, width, height)
                if any(map(room.overlaps, rooms)):
                    continue
                else:
                    rooms.append(room)
            return rooms

        def carve_room(room: Room):
            for x in range(room.x1, room.x2 + 1):
                for y in range(room.y1, room.y2 + 1):
                    self[x, y] = ['.', BROWN, False]

        def carve_tunnel(from_room: Room, to_room: Room):
            def horizontal_tunnel(from_x, to_x, y):
                x0, x1 = min((from_x, to_x)), max((from_x, to_x))
                carve_room(Room(x0, y, x1 - x0 + 1, 1))

            def vertical_tunnel(from_y: int, to_y: int, x: int):
                y0, y1 = min((from_y, to_y)), max((from_y, to_y))
                carve_room(Room(x, y0, 1, y1 - y0 + 1))

            from_x, from_y = from_room.center()
            to_x, to_y = to_room.center()
            if randrange(2) == 1:
                horizontal_tunnel(from_x, to_x, from_y)
                vertical_tunnel(from_y, to_y, to_x)
            else:
                vertical_tunnel(from_y, to_y, from_x)
                horizontal_tunnel(from_x, to_x, to_y)

        def carve(rooms: Iterable[Room]):
            last_room = None
            for room in rooms:
                if last_room:
                    carve_tunnel(last_room, room)
                carve_room(room)
                last_room = room

        self.mapdata = [[['#', GREY, True] for x in range(self.size[0])]
                        for y in range(self.size[1])]
        # self.rooms = gen_rooms(int((self.size[0] * self.size[1]) ** 0.5))
        self.rooms = gen_rooms(10)
        carve(self.rooms)
        self.build()
        self.populate()

    def populate(self):
        self[self.rooms[1].center()] = Troll(self.player, self, self.rooms[1].center())
        self[self.rooms[2].center()] = Gorgon(self.player, self, self.rooms[2].center())
        self[self.rooms[3].center()] = Wizard(self.player, self, self.rooms[3].center())
        self[self.rooms[-1].center()] = Ladder(self.player, self, self.rooms[-1].center())

    def build(self):
        self.map = [[Tile(self.player, self, vector([x, y]), *t) for x, t in enumerate(row)]
                    for y, row in enumerate(self.mapdata)]

    def draw(self, surface: pygame.Surface):
        x0, y0 = position = self.player.position
        xc, yc = position - GAME_CENTER
        self[xc:xc + GAME_SPRITE_WIDTH, yc:yc + GAME_SPRITE_HEIGHT].draw(surface)
        for effect in self.effects:
            effect.draw(surface)

    def update(self):
        x0, y0 = position = self.player.position
        xc, yc = position - GAME_CENTER
        self[xc:xc + GAME_SPRITE_WIDTH, yc:yc + GAME_SPRITE_HEIGHT].update()
        for effect in self.effects:
            effect.update()

    def blocked(self, position: vector) -> bool:
        return self[position].solid


class MapSlice(list):

    def __init__(self, player_ref, map_slice) -> None:
        from functools import reduce
        self.player = player_ref
        self.size = vector([len(map_slice[0]), len(map_slice)])
        super().__init__(map_slice)

    def draw(self, surface: pygame.Surface):
        for row in self:
            for cell in row:
                cell.draw(surface)

    def update(self):
        for row in self:
            for cell in row:
                cell.update()
