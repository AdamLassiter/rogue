#! /usr/bin/env python3

from copy import copy
from multiprocessing import Pipe
from time import sleep, time

from constants import *
from glwrap import GlManager
# from hud import Hud
from maps import Dungeon
from fighters import Player
from vector import vector


class GameManager:

    def __init__(self, pipe):
        self.pipe = pipe
        self.inventory_save = []
        self.state = 'game'
        self.keypresses = {}
        self.render_objs = []
        self.init(Dungeon)

    def init(self, Maptype):
        self.events = []
        self.pipe.send('textures')
        self.textures = self.pipe.recv()
        self.map = Maptype(self, vector([41, 41, 2]))
        self.map.populate()
        self.player = Player(self, self.map.player_start)
        for item in self.inventory_save:
            item.game = self
            # self.hud = Hud(self)

    def eval_events(self):
        for i, event in enumerate(reversed(self.events)):
            if event in (QUIT, LADDER_EVENT) or self.keypresses.get(chr(27), 0):
                self.state = 'quit'
            elif event == PLAYER_KILL:
                self.init(type(self.map))
            elif event == BONFIRE_EVENT:
                del self.events[-i - 1]
                self.inventory_save = copy(self.player.inventory)

    def loop(self):
        while self.state == 'game':
            t0 = time()
            self.pipe.send('keypresses')
            self.keypresses = self.pipe.recv()
            self.map.update()
            self.eval_events()
            self.pipe.send('render')
            self.pipe.send([self.map.renders, self.state, self.player.position])
            sleep_time = 0.125 - (t0 - time())
            sleep(sleep_time if sleep_time > 0.1 else 0.1)


def main():
    game_pipe, gl_pipe = Pipe()
    gl = GlManager(gl_pipe, GAME_WIDTH, GAME_HEIGHT)
    gl.loop()
    game = GameManager(game_pipe)
    game.loop()


if __name__ == '__main__':
    main()
