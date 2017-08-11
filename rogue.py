#! /usr/bin/python3

from typing import *

import pygame
from pygame.locals import *

from constants import *
from hud import Hud
from dungeon import Map, Room
from objects import Player
from vector import vector

pygame.init()

class Game:

    def __init__(self) -> None:
        self.main_surf = pygame.display.set_mode((GAME_PIXEL_WIDTH, GAME_PIXEL_HEIGHT),
                                                 pygame.FULLSCREEN)
        self.player = Player(None, None, None)
        self.map = Map(self.player, vector([100, 100]))
        self.hud = Hud(self.player)
        Player.__init__(self.player, self.player, self.map, self.map.rooms[0].center(),
                        stats=(10, 10, 10))
        self.map.objects.extend([self.player, self.hud])

    def draw(self):
        self.main_surf.fill(BLACK)
        self.map.draw(self.main_surf)
        for obj in self.map.objects:
            obj.draw(self.main_surf)
        self.player.draw(self.main_surf)
        pygame.display.flip()

    def update(self):
        self.map.update()
        for obj in self.map.objects:
            obj.update()

    def eval_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.state = 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key in [K_ESCAPE, KMOD_LALT | K_F4]:
                    self.state = 'quit'
            if event.type == LADDER_EVENT:
                self.player.hp -= 1
                # self.state = 'quit'

    def main_loop(self):
        self.state = 'play'
        fps = pygame.time.Clock()
        while self.state == 'play':
            fps.tick(8)
            # update gamestate
            self.update()
            # draw everything
            self.draw()
            # eval event
            self.eval_events()
        # exit
        pygame.quit()
        exit()


def main():
    game = Game()
    game.main_loop()


if __name__ == '__main__':
    main()
