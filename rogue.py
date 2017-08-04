#! /usr/bin/python3

from random import randrange

import pygame
from pygame.locals import *
pygame.init()


BLACK = (0, 0, 0)
GREY = (150, 150, 150)
WHITE = (255, 255, 255)
BROWN = (70, 35, 10)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


class vector(list):

    def __or__(self, other):
        return vector(list(self) + list(other))

    def __add__(self, other):
        if isinstance(other, vector):
            return vector(map(lambda x, y: x + y, self, other))
        else:
            return vector(map(lambda x: x + other, self))

    def __neg__(self):
        return vector(map(lambda x: -x, self))

    def __sub__(self, other):
        return self + other.__neg__()

    def __mul__(self, other):
        if isinstance(other, vector):
            return vector(map(lambda x, y: x * y, self, other))
        else:
            return vector(map(lambda x: x * other, self))

    def __div__(self, other):
        if isinstance(other, vector):
            return vector(map(lambda x, y: x / y, self, other))
        else:
            return vector(map(lambda x: x / other, self))

    def __floordiv__(self, other):
        if isinstance(other, vector):
            return vector(map(lambda x, y: x // y, self, other))
        else:
            return vector(map(lambda x: x // other, self))


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
        return vector([self.x1 + self.x2, self.y1 + self.y2]) // 2

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
                    self[x, y] = ['.', BROWN, False]

        def carve_tunnel(from_room, to_room):
            def horizontal_tunnel(from_x, to_x, y):
                x0, x1 = min((from_x, to_x)), max((from_x, to_x))
                carve_room(Room(x0, y, x1 - x0 + 1, 1))

            def vertical_tunnel(from_y, to_y, x):
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
        self.map = [[Tile(vector([x, y]), *t) for x, t in enumerate(row)]
                    for y, row in enumerate(self.mapdata)]

    def draw(self, surface, position):
        x0, y0 = position
        xc, yc = position - Game.CENTER
        for y, row in enumerate(self[xc:xc + Game.SPRITE_WIDTH, yc:yc + Game.SPRITE_HEIGHT]):
            for x, cell in enumerate(row):
                cell.draw(surface, vector([x, y]))


class Tile:

    def __init__(self, position, character, color=WHITE, solid=False, transparent=None):
        self.sprite = Sprite(position, character, color)
        self.solid = solid
        self.transparent = not solid if transparent is None else transparent
        self.explored = False

    def draw(self, surface, position):
        def bresenham(start, end):
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

        if self.explored:
            self.sprite.draw(surface, position)
        else:
            line_of_sight = bresenham(self.sprite.position, Game.PLAYER.position)[1:-1]
            visible = all(map(lambda x: Game.MAP[x[0], x[1]].transparent, line_of_sight))
            self.explored = visible


class Sprite:
    SIZE = 40
    SHADOW = 10
    FONT = pygame.font.SysFont('Monospace Regular', int(SIZE * 1.4))

    def __init__(self, position, character, color=WHITE):
        self.character = Sprite.FONT.render(character, False, color).convert()
        self.position = position
        self.velocity = vector([0, 0])

    def draw(self, surface, position):
        def dist(objA, objB):
            x1, y1 = objA
            x2, y2 = objB
            return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
        self.character.set_alpha(255 / (dist(Game.CENTER, position) / Sprite.SHADOW + 1) ** 2)
        blit_at = position * Sprite.SIZE
        rect = self.character.get_rect(center=blit_at + Sprite.SIZE // 2)
        surface.blit(self.character, rect)

    def update(self):
        x, y = self.position
        dx, dy = self.velocity
        if not Game.MAP[x + dx, y + dy].solid:
            self.position = self.position + self.velocity


class Game:
    WIDTH = 1920
    HEIGHT = 1080
    BORDER_WIDTH = (WIDTH % Sprite.SIZE) // 2
    BORDER_HEIGHT = (HEIGHT % Sprite.SIZE) // 2
    SPRITE_WIDTH = WIDTH // Sprite.SIZE
    SPRITE_HEIGHT = HEIGHT // Sprite.SIZE
    CENTER = vector([SPRITE_WIDTH, SPRITE_HEIGHT]) // 2
    MAP = None
    PLAYER = None

    def __init__(self):
        self.main_surf = pygame.display.set_mode(
            (Game.WIDTH, Game.HEIGHT), pygame.FULLSCREEN)
        self.map = Game.MAP = Map(vector([100, 100]))
        self.player = Game.PLAYER = Sprite(self.map.rooms[0].center(), '@')

    def draw(self):
        # clear
        self.main_surf.fill(BLACK)
        # draw background
        self.map.draw(self.main_surf, self.player.position)
        # draw foreground
        self.player.draw(self.main_surf, Game.CENTER)
        # update
        pygame.display.flip()

    def update(self):
        self.player.update()

    def eval_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key in [K_ESCAPE, KMOD_LALT | K_F4]:
                self.running = False

        keypresses = list(map(int, pygame.key.get_pressed()))
        self.player.velocity = vector([keypresses[K_d] - keypresses[K_a],
                                       keypresses[K_s] - keypresses[K_w]])

    def main_loop(self):
        self.running = True
        fps = pygame.time.Clock()
        while self.running:
            fps.tick(10)
            # eval event
            self.eval_events()
            # update gamestate
            self.update()
            # draw everything
            self.draw()
        # exit
        pygame.quit()
        exit()


if __name__ == '__main__':
    g = Game()
    g.main_loop()
