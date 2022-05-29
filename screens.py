from objects import *


class Menu:
    def __init__(self, game: Game_):
        self.__width = 0.5
        self.__game = game
        self.__vertical_padding = 180
        self.__button_height = 50
        self.__general_padding = 10

    def draw(self):
        self.__game.clear_frames()
        width = self.__game.size.width * self.__width
        size = Size(width, self.__game.size.height - 2 * self.__vertical_padding)

        background = pygame.image.load(os.path.dirname(__file__) + f"/sprites/menu_background.png")
        background = pygame.transform.scale(background, (self.__game.size.width, self.__game.size.height))

        left_top = Position(self.__game.size.width * (1 - self.__width) / 2, self.__vertical_padding)
        inner_top = left_top.y + self.__general_padding
        inner_left = left_top.x + self.__general_padding
        inner_width = size.width - 2 * self.__general_padding

        button_height = 50
        button_size = Size(inner_width, button_height)
        button_position = lambda n: Position(inner_left, inner_top + (self.__general_padding + button_size.height) * n)

        open_one_player_game = lambda: self.__game.open_screen(Game(self.__game))
        open_two_player_game = lambda: self.__game.open_screen(Game(self.__game, one_player=False))
        open_records = lambda: self.__game.open_screen(Records(self.__game))

        self.__game.screen.blit(background, (0, 0))
        Button(self.__game, "Одиночная игра", button_position(0), button_size, open_one_player_game).draw()
        Button(self.__game, "Состязание", button_position(1), button_size, open_two_player_game).draw()
        Button(self.__game, "Рекорды", button_position(2), button_size, open_records).draw()
        Button(self.__game, "Выйти", button_position(3), button_size, self.__game.stop).draw()


class Records:
    def __init__(self, game: Game_):
        self.__width = 0.5
        self.__game = game
        self.__vertical_padding = 20
        self.__button_height = 50
        self.__general_padding = 10

    def get_records(self):
        return sorted(self.__game.database.get_records(), reverse=True)

    def draw(self):
        self.__game.clear_frames()
        width = self.__game.size.width * self.__width
        size = Size(width, self.__game.size.height - 2 * self.__vertical_padding)

        left_top = Position(self.__game.size.width * (1 - self.__width) / 2, self.__vertical_padding)
        inner_top = left_top.y + self.__general_padding
        inner_left = left_top.x + self.__general_padding
        inner_width = size.width - 2 * self.__general_padding

        background = pygame.image.load(os.path.dirname(__file__) + f"/sprites/menu_background.png")
        background = pygame.transform.scale(background, (self.__game.size.width, self.__game.size.height))

        button_size = Size(inner_width, 50)
        table_size = Size(inner_width, min(len(self.get_records()) + 1, 10) * 25)
        table_position = Position(inner_left, inner_top + self.__general_padding)
        button_position = Position(inner_left, inner_top + self.__general_padding * 5 + table_size.height)

        open_menu = lambda: self.__game.open_screen(Menu(self.__game))

        self.__game.screen.blit(background, (0, 0))
        pygame.draw.rect(self.__game.screen,
                         color=Colors.White(),
                         rect=(left_top.x, left_top.y, size.width, size.height),
                         border_radius=15)

        self.__draw_table(table_position, table_size, self.get_records())
        Button(self.__game, "Назад", button_position, button_size, open_menu).draw()

    def __draw_table(self, position: Position, size: Size, data: list):
        pygame.draw.rect(self.__game.screen,
                         color=Colors.LiteBlue(),
                         rect=(position.x, position.y, size.width, size.height),
                         border_radius=15)
        lines = min(len(data), 10)
        item_height = size.height // (lines + 1)

        for line in range(lines):
            font_size = int(item_height * 0.8)
            left = Position(position.x + 20, position.y + item_height / 2 + item_height * line)
            right = Position(position.x - 40 + size.width, position.y + item_height / 2 + item_height * line)

            text = self.__game.font(font_size).render(f"Самый долгий забег {line + 1}", True, Colors.White())
            record = self.__game.font(font_size).render(f"{data[line]}c", True, Colors.White())
            shift = Shift(-record.get_width(), -font_size // 2-3)

            self.__game.screen.blit(text, (left.x, left.y + shift.y))
            self.__game.screen.blit(record, (right.x + shift.x, right.y + shift.y))
            pygame.draw.line(self.__game.screen, Colors.White(),
                             (left.x, left.y - shift.y),
                             (right.x, right.y - shift.y))


class Game:
    def __init__(self, game: Game_, one_player=True):
        game.unpause()
        self.__game = game
        self.__one_player = one_player
        self.__is_playing = True
        if one_player:
            self.__player_1 = Player(game, 1)
        if not one_player:
            t = [Player(game, 1), Player(game, 2)]
            self.__player_1 = t.pop(random.randint(0, 1))
            self.__player_2 = t[-1]
            print(self.__player_1, self.__player_2)
        self.__icicles = []
        self.__houses = []
        l_p = 0
        while l_p < self.__game.size.width:
            house = House(game, l_p)
            self.__houses.append(house)
            l_p += house.size.width - 2
        self.__last_time = time.time()
        self.__spawn_speed = 0.2

        open_menu = lambda: self.__game.open_screen(Menu(self.__game))
        restart = lambda: self.__game.open_screen(Game(self.__game)) if self.__one_player else self.__game.open_screen(
            Game(self.__game, one_player=False))
        timer_size = Size(150, 25)
        timer_position = Position(game.size.width - timer_size.width, 0)
        game_results_size = Size(500, 75)
        game_results_position = Position(game.size.width // 2 - game_results_size.width // 2,
                                         game.size.height // 2 - game_results_size.height // 2)
        button_size = Size(300, 50)
        button_position = Position(0, 0)
        button_shift = Shift(0, 60)

        self.unpause_button = Button(self.__game, "Продолжить", button_position + button_shift, button_size,
                                     self.__game.unpause)
        self.pause_button = Button(self.__game, "Пауза", button_position, button_size, self.__game.pause)
        self.menu_button = Button(self.__game, "Меню", button_position, button_size, open_menu)
        self.restart_button = Button(self.__game, "Заново", button_position + button_shift, button_size, restart)
        self.timer = Timer(self.__game, timer_position, timer_size)
        self.game_results = GameResults(self.__game, game_results_position, game_results_size)

    def draw(self):
        if not self.__is_playing:
            self.menu_button.draw()
            self.restart_button.draw()
            winner = 1 if self.__player_1.is_alive else 2 if not self.__one_player and self.__player_2.is_alive else 0
            self.game_results.draw(self.timer.time, winner)
            return
        self.__game.clear_frames()
        self.__game.add_frame("OnePlayerGame", self.frame)
        self.__game.fill_screen()
        player_1_position = self.__player_1.position
        if not self.__one_player:
            player_2_position = self.__player_2.position
        for i, house in enumerate(self.__houses[::-1]):
            position = house.position
            if i == 0:
                if position.x < self.__game.size.width + 20:
                    self.__houses.append(House(self.__game, position.x + house.size.width - 2))

            self.__game.screen.blit(house.surface, (position.x, position.y - house.size.height))
            if position.x < - house.size.width:
                self.__houses.remove(house)

        for icicle in self.__icicles[::-1]:
            position = icicle.position
            self.__game.screen.blit(icicle.surface, (position.x, position.y))
            if player_1_position.x - icicle.size.width <= position.x <= player_1_position.x + self.__player_1.size.width:
                if self.__game.size.height - self.__player_1.size.width < position.y < self.__game.size.height - self.__player_1.size.width + 10:
                    self.__player_1.kill()
                    self.__is_playing = False
                    if self.__one_player:
                        self.__game.database.add_record(self.timer.time.__round__(2))
            if not self.__one_player:
                if player_2_position.x - icicle.size.width <= position.x <= player_2_position.x + self.__player_2.size.width:
                    if self.__game.size.height - self.__player_2.size.width < position.y < self.__game.size.height - self.__player_2.size.width + 10:
                        self.__player_2.kill()
                        self.__is_playing = False
            if position.y > self.__game.size.height + 5 or position.x < - icicle.size.width:
                self.__icicles.remove(icicle)

        self.__game.screen.blit(self.__player_1.surface,
                                (player_1_position.x, player_1_position.y - self.__player_1.size.height))

        if not self.__one_player:
            self.__game.screen.blit(self.__player_2.surface,
                                    (player_2_position.x, player_2_position.y - self.__player_2.size.height))

        if self.__game.suspended:
            self.unpause_button.draw()
            self.menu_button.draw()
        else:
            self.pause_button.draw()
            self.restart_button.draw()
        self.timer.draw()

    def frame(self, events):
        if not self.__game.suspended and self.__is_playing:
            pressed_keys = pygame.key.get_pressed()
            if pressed_keys[pygame.K_LEFT]:
                self.__player_1.move_left()
            elif pressed_keys[pygame.K_RIGHT]:
                self.__player_1.move_right()
            if not self.__one_player:
                if pressed_keys[pygame.K_a]:
                    self.__player_2.move_left()
                elif pressed_keys[pygame.K_d]:
                    self.__player_2.move_right()
            t = time.time()
            if t - self.__last_time > self.__spawn_speed:
                self.__icicles.append(
                    Icicle(self.__game, Size(5, 15), random.randint(100, self.__game.size.width + 100)))
                if self.__player_1.is_alive and self.__one_player:
                    self.timer.add_time(t - self.__last_time)
                elif not self.__one_player and self.__player_1.is_alive and self.__player_1.is_alive:
                    self.timer.add_time(t - self.__last_time)

                self.__last_time = t
                self.__spawn_speed = max(self.__spawn_speed / 1.001, 0.06)
        self.draw()
