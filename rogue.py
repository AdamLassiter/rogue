#! /usr/bin/python3

from copy import copy

import pygame
from pygame.locals import *

from constants import *
from hud import Hud
from maps import Dungeon
from fighters import Player
from vector import vector

pygame.init()


class Game:

    def __init__(self):
        self.main_surf = pygame.display.set_mode((GAME_PIXEL_WIDTH, GAME_PIXEL_HEIGHT),
                                                 pygame.FULLSCREEN)
        self.savestate = []
        self.init(Dungeon)

    def init(self, Maptype):
        self.player = p = Player(None, None, None)
        self.map = m = Maptype(p, vector([51, 51]))
        Player.__init__(p, p, m, m.player_start)
        for item in self.savestate:
            item.player = p
            item.pickup()
        self.hud = Hud(self.player, lambda: str(self.savestate))

    def draw(self):
        self.main_surf.fill(BLACK)
        self.map.draw(self.main_surf)
        self.hud.draw(self.main_surf)
        pygame.display.flip()
        # print(self.map)

    def update(self):
        self.eval_events()
        self.map.update()
        self.hud.update()

    def eval_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.state = 'quit'
            elif event.type == pygame.KEYDOWN:
                if event.key in [K_ESCAPE, KMOD_LALT | K_F4]:
                    self.state = 'quit'
            elif event.type == LADDER_EVENT:
                self.state = 'quit'
            elif event.type == PLAYER_KILL:
                self.init(type(self.map))
                pygame.event.clear()
            elif event.type == BONFIRE_EVENT:
                self.savestate = copy(self.player.inventory)

    def main_loop(self):
        self.state = 'play'
        fps = pygame.time.Clock()
        while self.state == 'play':
            fps.tick(8)
            # update gamestate
            self.update()
            # draw everything
            self.draw()
        # exit
        pygame.quit()
        exit()


def main():
    game = Game()
    game.main_loop()


if __name__ == '__main__':
    main()
