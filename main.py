import os

import pygame

from objects import Game_
from screens import Menu

WIDTH = 900
HEIGHT = 480
FPS = 60
NAME = "WinterRun"
FONT_PATH = os.path.dirname(__file__) + "/font.otf"
game = Game_(width=WIDTH, height=HEIGHT, fps=FPS, name=NAME,font_path= FONT_PATH)

screen = Menu(game)
game.run(screen)
