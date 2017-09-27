#! /usr/bin/env python3

from objects import Object
from vector import vector


class Effect(Object):

    def __init__(self, *args, solid: bool = False, transparent: bool = True, **kwargs):
        kwargs.update({'solid': solid, 'transparent': transparent})
        super().__init__(*args, **kwargs)

    def update(self):
        self.position += self.velocity

    def spawn(self):
        self.game.map.effects.append(self)

    def destroy(self):
        if self in self.game.map.effects:
            del self.game.map.effects[self.game.map.effects.index(self)]


class HitMarker(Effect):

    def __init__(self, *args, sprite: str = '*', **kwargs):
        kwargs.update({'sprite': sprite})
        super().__init__(*args, **kwargs)
        self.position += vector([0, 1, 0])
        self.lifespan = 3

    def update(self):
        if self.lifespan <= 0:
            self.destroy()
        self.lifespan -= 1
        super().update()


class BonfireFlame(HitMarker):

    def __init__(self, *args, sprite: str = '*', **kwargs):
        kwargs.update({'sprite': sprite})
        super().__init__(*args, **kwargs)


class StoneGlare(Effect):

    def __init__(self, *args, sprite: str = 'X', **kwargs):
        kwargs.update({'sprite': sprite})
        super().__init__(*args, **kwargs)
        if self.game.player.speed > 0:
            self.game.player.speed -= 1
            self.dv = 1
        else:
            self.dv = 0
        self.lifespan = 5

    def update(self):
        self.lifespan -= 1
        if self.lifespan <= 0:
            self.game.player.speed += self.dv
            self.destroy()
        self.position = self.game.player.position + self.game.player.velocity


class Fireball(Effect):

    def __init__(self, *args, parent: Object = None, sprite: str = 'o', **kwargs):
        kwargs.update({'sprite': sprite})
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.path = Object.bresenham(parent.position, self.game.player.position)
        self.distance = 0

    def update(self):
        self.distance += 1
        self.distance %= len(self.path)
        self.distance += self.distance == 0
        d_pos = self.path[self.distance] - self.path[self.distance - 1]
        next_obj = self.game.map[self.position + d_pos]
        if next_obj.solid:
            if hasattr(next_obj, 'take_damage') and next_obj is not self.parent:
                self.parent.deal_damage(next_obj)
            self.destroy()
        else:
            self.velocity = d_pos
        super().update()
