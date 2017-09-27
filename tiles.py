#! /usr/bin/env python3

from constants import *
from effects import BonfireFlame
from objects import Object


class Tile(Object):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.explored = False

    @property
    def render(self):
        if self.explored:
            return super().render
        else:
            return None

    def update(self):
        if not self.explored:
            if self.visible(self.game.player.position):
                self.explored = True


class Air(Tile):

    def __init__(self, *args, sprite: str = ' ', solid: bool = False, **kwargs):
        kwargs.update({'sprite': sprite, 'solid': solid})
        super().__init__(*args, **kwargs)

    @property
    def render(self):
        return None


class Dirt(Tile):

    def __init__(self, *args, sprite: str = '.', solid: bool = False, **kwargs):
        kwargs.update({'sprite': sprite, 'solid': solid})
        super().__init__(*args, **kwargs)


class Wall(Tile):

    def __init__(self, *args, sprite: str = '#', solid: bool = True, **kwargs):
        kwargs.update({'sprite': sprite, 'solid': solid})
        super().__init__(*args, **kwargs)


class Bonfire(Tile):

    def __init__(self, *args, sprite: str = 'x', solid: bool = False, **kwargs):
        kwargs.update({'sprite': sprite, 'solid': solid})
        super().__init__(*args, **kwargs)

    def update(self):
        if self.position == self.game.player.position:
            self.game.events.append(BONFIRE_EVENT)
        # for _ in range(3):
        #     BonfireFlame(self.game, self.position).spawn()
        super().update()
