#! /usr/bin/env python3
import pygame

pygame.init()

pygame.display.set_mode()
FONT = pygame.font.Font(open('DejaVuSansMono.ttf', 'rb'), 12)

for char in range(32, 45):
    surf = FONT.render(chr(char), False, (255, 255, 255)).convert()
    pygame.image.save(surf, '%s.png' % (char,))
