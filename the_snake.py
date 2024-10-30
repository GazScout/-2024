from random import randint, randrange  # Убедитесь, что используете все импортируемые функции
import sys
import pygame as pg

pg.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

TURNING = {
    LEFT: {pg.K_UP: UP, pg.K_DOWN: DOWN},
    RIGHT: {pg.K_UP: UP, pg.K_DOWN: DOWN},
    UP: {pg.K_LEFT: LEFT, pg.K_RIGHT: RIGHT},
    DOWN: {pg.K_LEFT: LEFT, pg.K_RIGHT: RIGHT},
}

BOARD_BACKGROUND_COLOR = (200, 200, 220)
BORDER_COLOR = (200, 200, 220)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
SNAKE_BLOOD_COLOR = (230, 66, 245)
SKIN_COLOR = (104, 53, 44)
WALLS_COLOR = (57, 69, 102)

SPEED = 10
ACCELERATION = 2

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption("Для выхода из игры нажмите ESC.")
clock = pg.time.Clock()
screen.fill(BOARD_BACKGROUND_COLOR)


class GameObject:
    """Базовый класс игрового объекта."""

    def __init__(self, body_color=None) -> None:
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    def draw_cell(self, position, color=None) -> None:
        """Отрисовывает ячейку на экране."""
        color = color or self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Метод отрисовки наследников объекта."""

    def randomize_position(self, positions) -> None:
        """Устанавливает случайную позицию объекта."""
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if self.position not in positions:
                break


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self, body_color: tuple = SNAKE_COLOR) -> None:
        super().__init__(body_color)
        self.positions = [self.position]
        self.length = len(self.positions)
        self.direction: tuple = RIGHT
        self.last = None

    def update_direction(self, direction) -> None:
        """Обновляет направление движения змейки."""
        self.direction = direction

    def move(self) -> None:
        """Перемещает змейку в заданном направлении."""
        self.position = (
            (self.position[0] + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH,
            (self.position[1] + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT,
        )

        past_length: int = len(self.positions)
        self.positions.insert(0, self.position)
        if self.length == past_length:
            self.last = self.positions.pop()
        elif self.length < past_length:
            self.last = self.positions.pop()
            self.draw_cell(self.position)
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Отрисовывает змейку на экране."""
        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)
        for position in self.positions:
            color = (randrange(0, 55, 5), randrange(150, 255, 5), 0)
            self.draw_cell(position, color)
        self.draw_cell(self.position)

    def draw_damage(self):
        """Отрисовывает эффект повреждения змейки."""
        self.draw_cell(self.get_head_position(), SNAKE_BLOOD_COLOR)
        pg.display.update()

    def get_head_position(self) -> tuple:
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def check_collision(self, walls) -> bool:
        """Проверяет столкновение змейки с препятствиями."""
        if self.get_head_position() in self.positions[4:] + walls.positions:
            self.draw_damage()
            return True
        return False

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние."""
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.positions = [self.position]
        self.length = len(self.positions)
        self.direction = RIGHT


class Apple(GameObject):
    """Класс яблока."""

    def __init__(self, busy=list(), body_color: tuple = APPLE_COLOR) -> None:
        super().__init__(body_color)
        self.randomize_position(busy)

    def draw(self):
        """Отрисовывает яблоко на экране."""
        self.draw_cell(self.position)


class Skins(GameObject):
    """Класс скинов змейки."""

    def __init__(self, body_color: tuple = SKIN_COLOR) -> None:
        super().__init__(body_color)
        self.positions = set()

    def add_skin(self, position):
        """Добавляет новую позицию скина."""
        self.positions.add(position)

    def draw(self):
        """Отрисовывает скины на экране."""
        for position in self.positions:
            self.draw_cell(position)

    def reset(self):
        """Сбрасывает скины."""
        self.positions.clear()


class Walls(GameObject):
    """Класс стен."""

    def __init__(self, body_color: tuple = WALLS_COLOR) -> None:
        super().__init__(body_color)
        self.positions = list()

    def randomize_position(self, positions) -> None:
        """Устанавливает случайную позицию стены."""
        super().randomize_position(positions)
        self.positions.append(self.position)

    def draw(self):
        """Отрисовывает стены на экране."""
        if len(self.positions) != 0:
            self.draw_cell(self.positions[-1])

    def reset(self):
        """Сбрасывает стены."""
        self.positions = list()


def ate(snake, apple, skin, walls):
    """Проверяет, съела ли змейка яблоко или скин."""
    last = snake.last
    if apple.position == snake.get_head_position():
        snake.length += 1
        list_positions = (
            front(snake) + snake.positions +
            list(skin.positions) + walls.positions
        )
        apple.randomize_position(list_positions)
        if not snake.length % 5:
            skin.add_skin(last)
        if not snake.length % 2 and snake.length > 5:
            walls.randomize_position(list_positions + [apple.position])

    for skin_position in list(skin.positions):
        if skin_position == snake.get_head_position():
            snake.length -= 1
            if not snake.length:
                skin.positions = set()
                snake.draw_damage()
                return False
            skin.positions.discard(snake.get_head_position())
            skin.add_skin(snake.positions[-1])
            skin.add_skin(snake.positions[-2])
    return True


def front(snake) -> list:
    """Возвращает позиции, находящиеся перед головой змейки."""
    list_busy: list = [
        (
            (snake.positions[0][0] + snake.direction[0] * GRID_SIZE * before)
            % SCREEN_WIDTH,
            (snake.positions[0][1] + snake.direction[1] * GRID_SIZE * before)
            % SCREEN_HEIGHT,
        )
        for before in range(1, 5)
    ]
    return list_busy


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш для управления змейкой."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()

            if event.key in TURNING[game_object.direction]:
                return game_object.update_direction(
                    TURNING[game_object.direction][event.key]
                )


def pressed_shift():
    """Проверяет, зажата ли клавиша Shift."""
    keys = pg.key.get_pressed()
    if keys[pg.K_LSHIFT] or keys[pg.K_RSHIFT]:
        return ACCELERATION
    return 1


def draw(*args):
    """Отрисовывает все переданные игровые объекты."""
    for game_object in args:
        game_object.draw()


def restart(*args):
    """Сбрасывает состояние всех переданных объектов."""
    for game_object in args:
        game_object.reset()
    screen.fill(BOARD_BACKGROUND_COLOR)


def main():
    """Основная функция запуска игры."""
    snake = Snake()
    apple = Apple(front(snake) + snake.positions)
    skin = Skins()
    walls = Walls()

    points = 0
    max_points = 0

    while True:
        game_speed = (SPEED + snake.length // 5) * pressed_shift()
        clock.tick(game_speed)

        handle_keys(snake)
        snake.move()
        if not ate(snake, apple, skin, walls) or snake.check_collision(walls):
            clock.tick(1)
            restart(snake, skin, walls)
            apple.randomize_position(snake.positions)
            points = 0
            continue
        draw(snake, apple, skin, walls)

        points = snake.length
        max_points = max(max_points, points)
        pg.display.set_caption(
            "Змейка.Выход-ESC"
            f"Длина змейки:{points}.Рекорд:{max_points}"
            f"SHIFT - ускорение."
        )
        pg.display.update()


if __name__ == "__main__":
    main()