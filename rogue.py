#! /usr/bin/python3

from random import randrange

import pygame
from pygame.locals import *
pygame.init()


BLACK = (0, 0, 0)
GREY = (100, 100, 100)
WHITE = (255, 255, 255)
BROWN = (70, 35, 10)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


class Room:
    MIN_SIZE = 10
    MAX_SIZE = 15

    def __init__(self, x, y, w, h):
        self.x1, self.x2 = x, x + w - 1
        self.y1, self.y2 = y, y + h - 1

    def __contains__(self, point):
        x, y = point
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2

    def __str__(self):
        return '(%s %s %s %s)' % (self.x1, self.x2, self.y1, self.y2)

    def center(self):
        return (int((self.x1 + self.x2) / 2), int((self.y1 + self.y2) / 2))

    def overlaps(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


class Map:

    def __init__(self, size):
        self.size = size
        self.gen_map()

    def __getitem__(self, slices):
        if isinstance(slices, tuple):
            h, v = slices
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
            return [a + b for a, b in zip(self[hd[0] % hl:hl:hd[2], v],
                                          self[0:hd[1] % hl:hd[2], v])]
        if vd[0] < 0 or vd[1] > vl:
            return self[h, vd[0] % vl:vl:vd[2]] + self[h, 0:vd[1] % vl:vd[2]]
        return [row[h] for row in self.map[v]] if return_slice else self.map[vd[0]][hd[0]]

    def __setitem__(self, slices, val):
        if isinstance(slices, tuple):
            h, v = slices
        else:
            h, v = slices, slice(None, None, None)
        self.mapdata[v][h] = val

    def gen_map(self):
        def gen_rooms(attempts):
            rooms = []
            for _ in range(attempts):
                width = randrange(Room.MIN_SIZE, Room.MAX_SIZE, 2)
                height = randrange(Room.MIN_SIZE, Room.MAX_SIZE, 2)
                x = randrange(1, self.size[0] - width, 2)
                y = randrange(1, self.size[1] - height, 2)
                room = Room(x, y, width, height)
                if any(map(room.overlaps, rooms)):
                    continue
                else:
                    rooms.append(room)
            return rooms

        def carve_room(room):
            for x in range(room.x1, room.x2 + 1):
                for y in range(room.y1, room.y2 + 1):
                    self[x, y] = ['#', BROWN, False]

        def carve_tunnel(from_room, to_room):
            def horizontal_tunnel(from_x, to_x, y):
                x0, x1 = min((from_x, to_x)), max((from_x, to_x))
                carve_room(Room(x0, y, x1 - x0, 1))

            def vertical_tunnel(from_y, to_y, x):
                y0, y1 = min((from_y, to_y)), max((from_y, to_y))
                carve_room(Room(x, y0, 1, y1 - y0))

            from_x, from_y = from_room.center()
            to_x, to_y = to_room.center()
            if randrange(2) == 1:
                horizontal_tunnel(from_x, to_x, from_y)
                vertical_tunnel(from_y, to_y, to_x)
            else:
                vertical_tunnel(from_y, to_y, from_x)
                horizontal_tunnel(from_x, to_x, to_y)

        def carve(rooms):
            last_room = None
            for room in rooms:
                if last_room:
                    carve_tunnel(last_room, room)
                carve_room(room)
                last_room = room

        self.mapdata = [[['#', GREY, True] for x in range(self.size[0])]
                        for y in range(self.size[1])]
        self.rooms = gen_rooms(int((self.size[0] * self.size[1]) ** 0.5))
        carve(self.rooms)
        self.update()

    def update(self):
        self.map = [[Tile((x, y), *t) for x, t in enumerate(row)]
                    for y, row in enumerate(self.mapdata)]

    def draw(self, surface, position):
        w, dw = divmod(Game.WIDTH, Sprite.SIZE)
        h, dh = divmod(Game.HEIGHT, Sprite.SIZE)
        x0, y0 = position
        x, y = (x0 + dw - w // 2, y0 + dh - h // 2)
        for y, row in enumerate(self[x:x + w, y:y + h]):
            for x, cell in enumerate(row):
                cell.draw(surface, [x, y])


class Tile:

    def __init__(self, position, character, color=WHITE, solid=False, transparent=None):
        self.sprite = Sprite(position, character, color)
        self.solid = solid
        self.transparent = not solid if transparent is None else transparent

    def draw(self, surface, position):
        self.sprite.draw(surface, position)


class Sprite:
    SIZE = 40
    FONT = pygame.font.SysFont('Monospace Regular', int(SIZE * 1.5))

    def __init__(self, position, character, color=WHITE):
        self.character = Sprite.FONT.render(character, True, color)
        self.position = position
        self.velocity = [0, 0]

    def draw(self, surface, position):
        blit_at = list(map(lambda x: x * Sprite.SIZE, position))
        surface.blit(self.character, blit_at)

    def update(self):
        x, y = self.position
        dx, dy = self.velocity
        if not Game.MAP[x + dx, y + dy].solid:
            self.position = [x + dx, y + dy]


class Game:
    WIDTH = 800
    HEIGHT = 600
    MAP = None

    def __init__(self):
        self.main_surf = pygame.display.set_mode((Game.WIDTH, Game.HEIGHT))
        self.map = Game.MAP = Map((100, 100))
        self.player = Sprite(self.map.rooms[0].center(), '@')

    def draw(self):
        # clear
        self.main_surf.fill(BLACK)
        # draw background
        self.map.draw(self.main_surf, self.player.position)
        # draw foreground
        self.player.draw(self.main_surf, [Game.WIDTH // Sprite.SIZE // 2,
                                          Game.HEIGHT // Sprite.SIZE // 2])
        # update
        pygame.display.flip()

    def update(self):
        self.player.update()

    def eval_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

        keypresses = list(map(int, pygame.key.get_pressed()))
        self.player.velocity[0] = keypresses[K_d] - keypresses[K_a]
        self.player.velocity[1] = keypresses[K_s] - keypresses[K_w]

    def main_loop(self):
        self.running = True
        fps = pygame.time.Clock()
        while self.running:
            fps.tick(10)
            # eval event
            self.eval_events()
            # update gamestate
            self.update()
            self.draw()
        # exit
        pygame.quit()
        exit()


if __name__ == '__main__':
    g = Game()
    g.main_loop()
