#! /usr/bin/env python3

# from constants import *
from glwrap import GlObject
from vector import vector


class UpdateRenderable(type):

    def __new__(mcs, name, bases, body):
        cls_ok = False
        # Must have one of these
        for prop in ['render', 'renders']:
            if prop in body or any(map(lambda x: hasattr(x, prop), bases)):
                cls_ok = True
        # Must have all of these
        for prop in ['update']:
            if prop not in body and not any(map(lambda x: hasattr(x, prop), bases)):
                cls_ok = False
        if cls_ok:
            return super().__new__(mcs, name, bases, body)
        else:
            raise TypeError('Derived class (%s) is invalid.' % name)


class Object(object, metaclass=UpdateRenderable):

    def __init__(self, game_ref, position: vector, sprite: str = ' ',
                 solid: bool = True, transparent: bool = None):
        self.game = game_ref
        self.sprite = sprite
        texid = game_ref.textures['font/%03d.png' % ord(sprite)]
        self.gl_obj = GlObject(position, texid)
        self.position = position
        self.solid = solid
        self.transparent = not solid if transparent is None else transparent
        self.velocity = vector([0, 0, 0])

    def _get_position(self):
        return self.pos

    def _set_position(self, v: vector):
        self.pos = self.gl_obj.position = v

    position = property(_get_position, _set_position)

    def __repr__(self):
        return self.sprite
        if hasattr(self, 'explored'):
            visible = getattr(self, 'explored')
        else:
            visible = self.visible(self.game.player.position)
        return self.sprite if visible else ' '

    @staticmethod
    def dist(objA: tuple, objB: tuple) -> float:
        x1, y1, z1 = objA
        x2, y2, z2 = objB
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

    @property
    def render(self) -> GlObject:
        return self.gl_obj

    @staticmethod
    def bresenham(start: vector, end: vector) -> list:
        # TODO: Memoise 0 -> (end - start) bresenhams
        x1, y1, z1 = start
        x2, y2, z2 = end
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
            coord = vector([y, x, z1]) if is_steep else vector([x, y, z1])
            points.append(coord)
            error -= abs(dy)
            if error < 0:
                y += ystep
                error += dx
        return list(reversed(points)) if swapped else points

    def visible(self, other_position: vector) -> int:
        if self.position == other_position:
            return True
        line_of_sight = self.bresenham(self.position, other_position)[1:-1]
        if all([self.game.map[x].transparent for x in line_of_sight]):
            return Object.dist(self.position, other_position)
        return False

    def update(self):
        if any(self.velocity):
            if not self.game.map[self.position + self.velocity].solid:
                self.position += self.velocity
        self.velocity = vector([0, 0, 0])
