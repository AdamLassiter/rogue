#! /usr/bin/env python3

from constants import LADDER_EVENT
from effects import Effect


class Pickup(Effect):

    def __init__(self, *args, solid: bool = False, **kwargs) -> None:
        kwargs.update({'solid': solid})
        super().__init__(*args, **kwargs)

    def pickup(self):
        self.game.player.inventory.append(self)
        self.destroy()

    def drop(self):
        self.spawn()

    @property
    def render(self):
        if self.visible(self.game.player.position):
            return super().render
        else:
            return None

    def update(self):
        if self.game.player.position == self.position:
            self.pickup()


class Ladder(Pickup):

    def __init__(self, *args, sprite: str = 'H', **kwargs) -> None:
        kwargs.update({'sprite': sprite})
        super().__init__(*args, **kwargs)

    def update(self):
        if self.game.player.position == self.position:
            self.game.events.append(LADDER_EVENT)
        super().update()


class Sword(Pickup):

    def __init__(self, *args, sprite: str = '/', **kwargs) -> None:
        kwargs.update({'sprite': sprite})
        super().__init__(*args, **kwargs)

    def pickup(self):
        self.game.player.attack += 1
        super().pickup()

    def drop(self):
        self.game.player.attack -= 1
        super().drop()
