#! /usr/bin/env python3
"""

from numpy import array

from constants import WHITE, OBJECT_SIZE, FONT_FILE
from objects import Object, UpdateDrawable
from vector import vector


class Label(metaclass=UpdateDrawable):

    def __init__(self, position: vector, label: str, value, color: tuple = WHITE):
        self.position = position
        self.label = label
        self.value = value
        self.color = color

    def draw(self, surface: pygame.Surface):
        surface.blit(self.surface, self.position * OBJECT_SIZE)

    def update(self):
        self.surface = Label.FONT.render(self.label + ' ' + self.value(),
                                         False, self.color).convert()


class Inventory(metaclass=UpdateDrawable):
    FONT = Object.FONT

    def __init__(self, game_ref, position: vector):
        self.game = game_ref
        self.position = position
        self.items = [x for x in self.game.player.inventory]

    def draw(self, surface: pygame.Surface):
        if self.items != self.game.player.inventory:
            self.items = [x for x in self.game.player.inventory]
        for n, item in enumerate(self.items):
            surface.blit(item.character,
                         (self.position + vector([0, n])) * OBJECT_SIZE)

    def update(self):
        pass


class MessageBox(metaclass=UpdateDrawable):
    MESSAGE_SIZE = OBJECT_SIZE // 2
    FONT = pygame.font.Font(FONT_FILE(), MESSAGE_SIZE)

    def __init__(self, position: vector, size: vector, color: tuple = WHITE):
        self.position = position
        self.size = size
        self.color = color
        self.redraw = True
        self.message_box = array([[' ' for _ in range(size[0])]
                                  for _ in range(size[1])], ndmin=2)
        self.surface_box = array([[None for _ in range(size[0])]
                                  for _ in range(size[1])], ndmin=2)

    def draw(self, surface: pygame.Surface):
        if self.redraw:
            for y, row in enumerate(self.surface_box):
                for x, _ in enumerate(row):
                    char = MessageBox.FONT.render(self.message_box[y, x],
                                                  False, self.color)
                    self.surface_box[y, x] = char.convert()
            self.redraw = False
        for y, row in enumerate(self.surface_box):
            for x, surf in enumerate(row):
                p = (self.position + vector([x, y])) * MessageBox.MESSAGE_SIZE
                surface.blit(surf, p)

    def update(self):
        for message in pygame.event.get(HUD_MESSAGE):
            self.redraw = True
            text = message.text
            lines, lastlen = divmod(len(text), self.size[0])
            text += ' ' * (self.size[0] - lastlen)
            self.message_box[:-lines] = self.message_box[lines:]
            self.message_box[-lines:] = [text[y * self.size[0]:(y + 1) * self.size[0]]
                                         for y in range(lines)]


class Hud(metaclass=UpdateDrawable):

    def __init__(self, game_ref):
        self.game = gr = game_ref
        self.position = p = vector([0, 0])
        labels = [(' HP', lambda: str(gr.player.hp)),
                  ('ATK', lambda: str(gr.player.attack)),
                  ('DEF', lambda: str(gr.player.defense)),
                  ('SPD', lambda: str(gr.player.speed)),
                  ('SAV', lambda: str(gr.inventory_save))]
        self.labels = [Label(p + vector([0, i]), text, value)
                       for i, (text, value) in enumerate(labels)]
        self.inventory = Inventory(gr, p + vector([GAME_SPRITE_WIDTH - 1, 0]))
        self.message_box = MessageBox(p + len(labels), vector([20, 10]))
        self.solid = False

    def draw(self, surface: pygame.Surface):
        self.inventory.draw(surface)
        self.message_box.draw(surface)
        for label in self.labels:
            label.draw(surface)

    def update(self):
        self.inventory.update()
        self.message_box.update()
        for label in self.labels:
            label.update()
"""
