#! /usr/bin/python3

import pygame
from pygame.locals import *
from random import randrange

BLACK = (0, 0, 0)
GREY = (100, 100, 100)
WHITE = (255, 255, 255)
BROWN = (70, 35, 10)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


class Room:
    MIN_SIZE = 6
    MAX_SIZE = 10

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
        assert size[0] % 2 == size[1] % 2 == 1
        self.size = size
        self.gen_map()

    def get_at(self, position):
        x, y = position
        return self.map[y][x]

    def set_at(self, position, value):
        x, y = position
        self.mapdata[y][x] = value

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
            for x in range(room.x1, room.x2):
                for y in range(room.y1, room.y2 + 1):
                    self.mapdata[y][x] = ('.', BROWN, False)

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

        self.mapdata = [[('#', GREY, True) for x in range(self.size[0])]
                        for y in range(self.size[1])]
        self.rooms = gen_rooms(self.size[0] * self.size[1])
        carve(self.rooms)
        self.update()

    def update(self):
        self.map = [[Tile((x, y), *t) for x, t in enumerate(row)]
                    for y, row in enumerate(self.mapdata)]

    def draw(self, surface):
        for row in self.map:
            for cell in row:
                cell.draw(surface)


class Tile:

    def __init__(self, position, character, color=WHITE, solid=False, transparent=None):
        self.sprite = Sprite(position, character, color)
        self.solid = solid
        self.transparent = not solid if transparent is None else transparent

    def draw(self, surface):
        self.sprite.draw(surface)


class Sprite:
    SIZE = 20

    def __init__(self, position, character, color=WHITE):
        self.character = pygame.font.SysFont(
            'Monospace Regular', Sprite.SIZE).render(character, True, color)
        self.position = position
        self.velocity = [0, 0]

    def draw(self, surface):
        surface.blit(self.character,
                     [x * Sprite.SIZE * .75 for x in self.position])

    def update(self):
        x, y = self.position
        dx, dy = self.velocity
        new_pos = (x + dx, y + dy)
        if not Game.MAP.get_at(new_pos).solid:
            self.position = new_pos


class Game:
    WIDTH = 800
    HEIGHT = 600
    MAP = None

    def __init__(self):
        pygame.init()
        self.main_surf = pygame.display.set_mode((Game.WIDTH, Game.HEIGHT))
        self.map = Game.MAP = Map((53, 39))
        self.player = Sprite((20, 15), '@')

    def draw(self):
        # clear
        self.main_surf.fill(BLACK)
        # draw background
        self.map.draw(self.main_surf)
        # draw foreground
        self.player.draw(self.main_surf)
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
