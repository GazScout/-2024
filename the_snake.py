"""THE_SNAKE.
Модуль представляет собой реализацию игры The snake.
Предпологается, что этот модуль будет запускаться на прямую.
Основной цикл модуля реализован в функции main().

Классы:
GameObject - родительский для всех игровых объектов.
Snake - дочерний класс реализующий игровой объект змейка.
Apple - дочерний класс реализующий игровой объект яблоко.

Функции:
handle_keys - отслеживает действий пользователя.
had_ate - логика поведения объектов при поедании объектом змейка.

Для ревьюера:
По мимо основного задания реализован выбрдлины змейки константой
SNAKE_LENGH.

Изменение скорости в функции main().

Случайный выбор направления при новом старте в методе reset
класса Snake.
"""
from random import randint, randrange


import sys
import pygame as pg

# Инициализация PyGame:
pg.init()

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
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

# Цвета
BOARD_BACKGROUND_COLOR = (200, 200, 220)
BORDER_COLOR = (200, 200, 220)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
SNAKE_BLOOD_COLOR = (230, 66, 245)
SKIN_COLOR = (104, 53, 44)
WALLS_COLOR = (57, 69, 102)

# Пораметры игры:
SPEED = 10
ACCELERATION = 2

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption("Змейка. Для выхода из игры нажмите ESC.")
clock = pg.time.Clock()
screen.fill(BOARD_BACKGROUND_COLOR)


class GameObject:
    """Базовый класс игровых объектов."""

    def __init__(self, body_color=None) -> None:
        self.position = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))
        self.body_color = body_color

    def draw_cell(self, position, color=None) -> None:
        """Отрисовывает одну заданную ячейку поля."""
        color = color or self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Нужен для отрисовки произвольного наследника."""

    def randomize_position(self, positions) -> None:
        """Устанавливает случайное положение яблока, или стены на игровом поле,
        не занятое другими объектами.
        """
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if self.position not in positions:
                break


class Snake(GameObject):
    """Класс игровых объектов Змейка."""

    def __init__(self, body_color: tuple = SNAKE_COLOR) -> None:
        super().__init__(body_color)

        self.positions = [self.position]
        self.length = len(self.positions)
        self.direction: tuple = RIGHT
        self.last = None

    def update_direction(self, direction) -> None:
        """Обновляет направления движения змейки после нажатия на кнопку."""
        self.direction = direction

    def move(self) -> None:
        """Обновляет позицию змейки (координаты каждой секции), добавляя новую
        голову в начало списка positions и удаляя последний элемент, если
        длина змейки не увеличилась.
        """
        self.position = (
            (self.position[0] + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH,
            (self.position[1] + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT
        )

        past_length: int = len(self.positions)
        self.positions.insert(0, self.position)
        if self.length == past_length:
            self.last = self.positions.pop()
        elif self.length < past_length:
            # Для кожи: сбрасываю кожу, затираю хвост.
            self.last = self.positions.pop()
            self.draw_cell(self.position)
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Рисуем змейку целеком."""
        # Затирание последнего сегмента.
        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)
        # Создаю эффект ползанья змейки.
        for position in self.positions:
            color = (randrange(0, 55, 5), randrange(150, 255, 5), 0)
            self.draw_cell(position, color)
        # Четко рисую голову.
        self.draw_cell(self.position)

    def draw_damage(self):
        """Рисую клетку, в которой змея получила повреждение."""
        self.draw_cell(self.get_head_position(), SNAKE_BLOOD_COLOR)
        pg.display.update()

    def get_head_position(self) -> tuple:
        """Возвращает позицию головы змейки - первый элемент в списке
        positions.
        """
        return self.positions[0]

    def check_collision(self, walls) -> bool:
        """Проверяет столкновение."""
        if self.get_head_position() in self.positions[4:] + walls.positions:
            self.draw_damage()
            return True
        return False

    def reset(self) -> None:
        """Cбрасывает змейку в начальное состояние после столкновения с
        собой.
        """
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.positions = [self.position]
        self.length = len(self.positions)
        self.direction = RIGHT


class Apple(GameObject):
    """Класс игровых объектов Яблоко."""

    def __init__(self, busy=list(), body_color: tuple = APPLE_COLOR) -> None:
        super().__init__(body_color)
        self.randomize_position(busy)

    # def reset(self):
    #     """Задаю первое яблоко, таким образом, чтоб оно точно не стояло на
    #     змейке.
    #     """
    #     self.randomize_position(self.busy_positions)

    def draw(self):
        """Рисую яблоко."""
        self.draw_cell(self.position)


class Skins(GameObject):
    """Класс игровых объектов Кожа."""

    def __init__(self, body_color: tuple = SKIN_COLOR) -> None:
        super().__init__(body_color)
        self.positions = set()

    def add_skin(self, position):
        """Добавляет сброшенную кожу."""
        self.positions.add(position)

    def draw(self):
        """Рисую сброшенную кожу, которая всегда остаётся за змейкой,
        и никогда не стоит на Змейке, которая стоит на Яблоке.
        """
        for position in self.positions:
            self.draw_cell(position)
        # Когда змейка съедает кожу, она травится, и сбрасывает
        # в два раза больше кожи. Геймплеейно, так интересней.

    def reset(self):
        """Отчищает множество позиций."""
        self.positions.clear()


class Walls(GameObject):
    """Класс игровых объектов Яблоко."""

    def __init__(self, body_color: tuple = WALLS_COLOR) -> None:
        super().__init__(body_color)
        self.positions = list()

    def randomize_position(self, positions) -> None:
        """Устанавливает случайное положение стены на игровом поле."""
        super().randomize_position(positions)
        self.positions.append(self.position)

    def draw(self):
        """Рисую стену, если она есть, которая не стоит на Яблоке,
        которое не стоит на Змейке.
        """
        if len(self.positions) != 0:
            # Всё равно в начале стену не рисуем, а когда рисуем,
            # то по одной за раз. Предыдущие уже нарисованы.
            self.draw_cell(self.positions[-1])

    def reset(self):
        """Отчищает множество позиций."""
        self.positions = list()


def ate(snake, apple, skin, walls):
    """Проверяет события поедания объекта."""
    last = snake.last
    if apple.position == snake.get_head_position():
        snake.length += 1
        list_positions = (front(snake) + snake.positions
                          + list(skin.positions) + walls.positions)
        apple.randomize_position(list_positions)
        # Каждые 5 яблок ускоряют метоболизм змейки
        # змейка сбрасывает кожу.
        if not snake.length % 5:
            skin.add_skin(last)
        # После того как змейка станет больше 5 ячеек
        # её начинают ограничивать стены каждый раз,
        # как она выростает на 2 ячейки.
        if not snake.length % 2 and snake.length > 5:
            walls.randomize_position(list_positions + [apple.position])

    for skin_position in list(skin.positions):
        if skin_position == snake.get_head_position():
            # Длина змейки уменьшается на следующей строке, и значение меньше
            # единици не пройдёт, если длина змейки была = 2,
            # после уменьшения на еденицу в блок if
            # программа не заходит. Длина snake.positions до следующей
            # итерации основного цикла в main() не меняется и имеют минимум
            # два элемента. Мне кажется что так проще реализовать отрисовку.
            # впринципи её можно перенеси и в snake.move(), но мне показалось,
            # что выглядеть будет еще менее четабильно, + придётся в змейке
            # тащить кожу, а она еще и не созданна как экземпляр.
            snake.length -= 1
            if not snake.length:
                skin.positions = set()
                snake.draw_damage()
                return False
            skin.positions.discard(snake.get_head_position())
            skin.add_skin(snake.positions[-1])
            # На самом деле ошибки не будет, я подумал что это явно, но сам
            # когда читал, понял что нужно прокоментировать.
            skin.add_skin(snake.positions[-2])
    return True


def front(snake) -> list:
    """Определяет позиции перед змейкой."""
    list_busy: list = [
        (
            (snake.positions[0][0] + snake.direction[0] * GRID_SIZE * before)
            % SCREEN_WIDTH,
            (snake.positions[0][1] + snake.direction[1] * GRID_SIZE * before)
            % SCREEN_HEIGHT
        )
        for before in range(1, 5)]
    return list_busy


def handle_keys(game_object):
    """Функция обработки действий пользователя."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()  # Равносильно raise SystemExit, но с лишним import sys.

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()

            if event.key in TURNING[game_object.direction]:
                return game_object.update_direction(
                    TURNING[game_object.direction][event.key])


def pressed_shift():
    """Возвращает коэфициент ускорения."""
    keys = pg.key.get_pressed()
    if keys[pg.K_LSHIFT] or keys[pg.K_RSHIFT]:
        return ACCELERATION
    return 1


def draw(*args):
    """Рисуем всё"""
    for game_object in args:
        game_object.draw()


def restart(*args):
    """Перезапуск"""
    for game_object in args:
        game_object.reset()
    screen.fill(BOARD_BACKGROUND_COLOR)


def main():
    """Выполняется если the_snake запущен напрямую."""
    snake = Snake()
    apple = Apple(front(snake) + snake.positions)
    skin = Skins()
    walls = Walls()

    points = 0
    max_points = 0

    while True:
        # Изменение скорости с ростом змейки на 1 за 5 съеденных яблок.
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
            "Змейка. Выход - ESC.  "
            f"Длина змейки: {points}. Рекорд: {max_points}  "
            f"SHIFT - ускорение."
        )
        pg.display.update()


if __name__ == "__main__":
    main()
