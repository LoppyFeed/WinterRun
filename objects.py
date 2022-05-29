import copy
import os
import random
import time

import pygame

from characteristics import *
from database import Database


class House:
    def __init__(self, game: "Game_", x: int):
        self.__game = game
        self.__x = x
        self.__y = game.size.height
        self.__last_time = time.time()
        dirname = os.path.dirname(__file__) + "/sprites"
        file = random.choice([file for file in os.listdir(dirname) if "house" in file])
        print(file)
        self.__surface = pygame.image.load(os.path.dirname(__file__) + f"/sprites/{file}")

    @property
    def surface(self):
        return self.__surface

    @property
    def size(self):
        return Size(self.__surface.get_width(), self.__surface.get_height())

    @property
    def position(self):
        if time.time() - self.__last_time > 0.01:
            if not self.__game.suspended:
                self.__x -= self.__game.speed
            self.__last_time = time.time()
        return Position(self.__x, self.__y)


class Icicle:
    def __init__(self, game: "Game_", size: Size, x: int):
        self.__game = game
        self.__x = x
        self.__y = -size.height - 10
        self.__size = size
        self.__speed = 5
        self.__last_time = time.time()
        dirname = os.path.dirname(__file__) + "/sprites"
        files = [file for file in os.listdir(dirname) if "icicle" in file]

        self.__frames = [pygame.image.load(os.path.dirname(__file__) + f"/sprites/{file}") for file in files]
        self.__framer = 0
        self.__ticker = 20
        self.__surface = self.__frames[0]

    @property
    def surface(self):
        return self.__surface

    @property
    def size(self):
        return self.__size

    @property
    def position(self):
        if time.time() - self.__last_time > 0.01:
            if not self.__game.suspended:
                self.__y += self.__speed
                self.__x -= self.__game.speed
            self.__last_time = time.time()

            if not self.__game.suspended:
                self.__framer += 1
                self.__framer = 0 if self.__framer >= self.__ticker * len(self.__frames) else self.__framer

                self.__surface = self.__frames[self.__framer // self.__ticker]

        return Position(self.__x, self.__y)


class Player:
    def __init__(self, game: "Game_", player_n=1):
        self.__game = game
        self.__is_dead = False
        self.__x = 0
        self.__y = game.size.height
        self.__speed = 10
        self.__last_time = time.time()

        dirname = os.path.dirname(__file__) + "/sprites"
        files = [file for file in os.listdir(dirname) if f"player{player_n}" in file and "dead" not in file]
        files.sort()

        self.__frames = [pygame.image.load(os.path.dirname(__file__) + f"/sprites/{file}") for file in files]
        self.__dead_frame = pygame.image.load(os.path.dirname(__file__) + f"/sprites/player{player_n}_dead.png")
        self.__framer = 0
        self.__ticker = 20
        self.__surface = self.__frames[0]

        self.__size = Size(self.__surface.get_width(), self.__surface.get_height())

    @property
    def surface(self):
        return self.__surface

    @property
    def size(self):
        return self.__size

    @property
    def is_alive(self):
        return not self.__is_dead

    def kill(self):
        self.__surface = self.__dead_frame
        self.__is_dead = True

    @property
    def position(self):
        if time.time() - self.__last_time > 0.01:
            if self.__is_dead:
                if not self.__game.suspended:
                    self.__x -= self.__game.speed
            elif not self.__game.suspended:
                self.__framer += 1
                self.__framer = 0 if self.__framer >= self.__ticker * len(self.__frames) else self.__framer
                self.__surface = self.__frames[self.__framer // self.__ticker]
            self.__last_time = time.time()
        return Position(self.__x, self.__y)

    def move_right(self):
        if time.time() - self.__last_time > 0.01 and not self.__is_dead:
            self.position
            self.__x = min(self.__game.size.width - self.__size.width, max(self.__x + self.__speed, 0))
            self.__last_time = time.time()

    def move_left(self):
        if time.time() - self.__last_time > 0.01 and not self.__is_dead:
            self.position
            self.__x = max(0, min(self.__x - self.__speed, self.__game.size.width - self.__size.width))
            self.__last_time = time.time()


class Game_:
    def __init__(self, width, height, fps, name, font_path):
        self.__font_path = font_path
        self.__width = width
        self.__height = height
        self.__fps = fps
        self.__name = name
        self.__speed = 1
        self.database = Database()
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption(self.__name)
        self.__screen = pygame.display.set_mode((self.__width, self.__height))
        self.__clock = pygame.time.Clock()
        self.__mouse = pygame.mouse
        self.__running = True
        self.__suspended = False
        self.__frames = {}

    def font(self, font_size):
        return pygame.font.Font(self.__font_path, font_size)

    @property
    def is_running(self):
        return self.__running

    @property
    def speed(self):
        return self.__speed

    @property
    def size(self):
        return Size(width=self.__width, height=self.__height)

    @property
    def suspended(self):
        return self.__suspended

    @property
    def screen(self):
        return self.__screen

    @property
    def mouse(self):
        return self.__mouse

    def add_frame(self, name: str, frame):
        self.__frames[name] = frame

    def remove_frame(self, name: str):
        if name in self.__frames.keys():
            del self.__frames[name]

    def clear_frames(self):
        self.__frames = {}

    def pause(self):
        self.__suspended = True

    def unpause(self):
        self.__suspended = False

    def stop(self):
        self.__running = False

    def fill_screen(self):
        pygame.draw.rect(self.__screen,
                         color=Colors.Black(),
                         rect=(0, 0, self.__width, self.__height))

    def open_screen(self, screen):
        self.fill_screen()
        screen.draw()

    def run(self, start_screen):
        self.open_screen(start_screen)
        while self.__running:
            self.__update()

    def __update(self):
        self.__clock.tick(self.__fps)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.__running = False
        frames = copy.copy(self.__frames)
        for frame in frames.values():
            frame(events)

        pygame.display.update()


class Button:
    def __init__(self, game: Game_, text: str, position: Position, size: Size, on_tap_up=None):
        self.__game = game
        self.__text = text
        self.__position = position
        self.__size = size
        self.__pressed = False
        self.__on_tap_up = on_tap_up

    def draw(self):
        self.__game.add_frame(self.__text, self.frame)
        pygame.draw.rect(self.__game.screen,
                         color=Colors.White(),
                         rect=(self.__position.x, self.__position.y, self.__size.width, self.__size.height),
                         border_radius=15)
        font_size = int(self.__size.height * 0.8)
        center = Position(self.__position.x + self.__size.width / 2, self.__position.y + self.__size.height / 2)
        text = self.__game.font(font_size).render(self.__text, True, Colors.LiteBlue())
        shift = Shift(-text.get_width() // 2, -font_size // 2 + -5)
        self.__game.screen.blit(text, (center.x + shift.x, center.y + shift.y))

    def __down(self):
        self.__pressed = True

    def __up(self, inside=True):
        self.__pressed = False
        if inside and self.__on_tap_up is not None:
            self.__on_tap_up()

    def frame(self, events):
        for event in events:
            if event.type not in [1025, 1026]:
                continue
            if event.button != 1:
                continue
            pos = event.pos
            pressed = event.type == 1025
            if pressed:
                if self.__position.x < pos[0] < self.__position.x + self.__size.width:
                    if self.__position.y < pos[1] < self.__position.y + self.__size.height:
                        self.__down()
                continue
            if self.__pressed:
                if self.__position.x < pos[0] < self.__position.x + self.__size.width:
                    if self.__position.y < pos[1] < self.__position.y + self.__size.height:
                        self.__up()
                        continue
                self.__up(inside=False)


class GameResults:
    def __init__(self, game: Game_, position: Position, size: Size):
        self.__game = game
        self.__position = position
        self.__size = size

    def draw(self, time_: int, player_win: int):
        pygame.draw.rect(self.__game.screen,
                         color=Colors.LiteBlue(),
                         rect=(self.__position.x, self.__position.y, self.__size.width, self.__size.height),
                         border_radius=15)
        font_size = int(self.__size.height * 0.4)
        center = Position(self.__position.x + self.__size.width / 2, self.__position.y + self.__size.height / 2)
        if player_win != 0:
            text1 = self.__game.font(font_size).render(f"Выиграл игрок {player_win}", True, Colors.White())
        else:
            text1 = self.__game.font(font_size).render(f"Сосулька настигла вас...", True, Colors.White())
        text2 = self.__game.font(font_size).render(f"Время: {int(time_)}с", True, Colors.White())
        shift1 = Shift(-text1.get_width() // 2, -font_size)
        shift2 = Shift(-text2.get_width() // 2, 0)
        self.__game.screen.blit(text1, (center.x + shift1.x, center.y + shift1.y))
        self.__game.screen.blit(text2, (center.x + shift2.x, center.y + shift2.y))


class Timer:
    def __init__(self, game: Game_, position: Position, size: Size):
        self.__game = game
        self.__position = position
        self.__size = size
        self.__time = 0

    def draw(self):
        pygame.draw.rect(self.__game.screen,
                         color=Colors.White(),
                         rect=(self.__position.x, self.__position.y, self.__size.width, self.__size.height),
                         border_radius=15)
        font_size = int(self.__size.height * 0.8)
        center = Position(self.__position.x + self.__size.width / 2, self.__position.y + self.__size.height / 2)
        text = self.__game.font(font_size).render(f"Время: {int(self.__time)}с", True, Colors.LiteBlue())
        shift = Shift(-text.get_width() // 2, -font_size // 2-3)
        self.__game.screen.blit(text, (center.x + shift.x, center.y + shift.y))

    def add_time(self, t: float):
        self.__time += t
        self.draw()

    @property
    def time(self):
        return self.__time
