import pygame
import random

pygame.init()

# Основные игровые константы
SCREEN_WIDTH = 300       # Ширина игрового окна в пикселях
SCREEN_HEIGHT = 600      # Высота игрового окна в пикселях
BLOCK_SIZE = 30          # Размер одного блока/клетки в пикселях
GRID_WIDTH = 10          # Ширина игровой сетки в блоках (колонки)
GRID_HEIGHT = 20         # Высота игровой сетки в блоках (строки)
FPS = 60                 # Частота обновления кадров в секунду

COLORS = [
    (0, 0, 0),  # Черный (фон)
    (255, 0, 0),  # Красный
    (0, 150, 0),  # Зеленый
    (0, 0, 255),  # Синий
    (255, 120, 0),  # Оранжевый
    (255, 255, 0),  # Желтый
    (180, 0, 255),  # Пурпурный
    (0, 220, 220)  # Голубой
]

# Формы тетромино (матрицы)
# 1 - наличие блока, 0 - пустое пространство
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]]
]


class Tetromino:
    """
    Класс для представления тетромино (фигуры в тетрисе).

    Attributes:
        shape (list): 2D-матрица, определяющая форму тетромино.
        color (int): Индекс цвета из глобального списка COLORS.
        x (int): Горизонтальная позиция в сетке.
        y (int): Вертикальная позиция в сетке.

    Методы:
        rotate: Поворачивает фигуру на 90 градусов по часовой стрелке.
    """

    def __init__(self, x, y):
        """
        Инициализирует новый тетромино со случайными параметрами.
        """

        self.shape = random.choice(SHAPES)
        self.color = random.randint(1, len(COLORS) - 1)
        self.x = x
        self.y = y

    def rotate(self):
        self.shape = [list(row)[::-1] for row in zip(*self.shape)]


class Game:
    """
    Основной класс, управляющий игровой логикой и отрисовкой.

    Attributes:
        current_piece (Tetromino): Активная падающая фигура (экземпляр класса Tetromino)
        screen (pygame.Surface): Основное окно отрисовки Pygame
        clock (pygame.time.Clock): Таймер для контроля FPS
        font (pygame.font.Font): Шрифт для отображения текста
        grid (list[list[int]]): Матрица 20x10, представляющая игровое поле:
        score (int): Накопленные очки (увеличивается за собранные линии)
        level (int): Текущий уровень сложности (1-10)
        fall_speed (int): Интервал падения фигур в миллисекундах
        last_fall (int): Время последнего автоматического смещения фигуры вниз

    Methods:
        new_piece(): Создает новую фигуру и проверяет Game Over
        draw_grid(): Отрисовывает сетку и зафиксированные блоки
        draw_piece(): Отрисовывает текущую падающую фигуру
        check_collision(): Проверяет столкновения с границами и другими блоками
        merge_piece(): Фиксирует фигуру в игровом поле
        clear_lines(): Удаляет заполненные линии и обновляет счет
        game_over(): Обрабатывает завершение игры
        run(): Запускает главный игровой цикл

    """
    def __init__(self):
        """
        Инициализирует игровое окружение и устанавливает начальные параметры.
        """

        self.current_piece = None
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20)
        self.grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.level = 1
        self.fall_speed = 1000
        self.last_fall = pygame.time.get_ticks()
        self.new_piece()

    def new_piece(self):
        """
        Генерирует новую фигуру и проверяет условие Game Over.
        """
        self.current_piece = Tetromino(4, 0)
        if self.check_collision(0, 0):
            self.game_over()

    def draw_grid(self):
        """
        Отрисовывает игровую сетку и зафиксированные блоки на экране.

        Метод выполняет две основные задачи:
        1. Рисует цветные блоки в соответствии с данными из матрицы self.grid:
            - Каждая ячейка сетки представлена квадратом размера BLOCK_SIZE.
            - Цвет блока определяется значением в матрице grid через глобальный список COLORS.
        2. Рисует серую сетку поверх блоков для визуального разделения:
        """

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(
                    x * BLOCK_SIZE + (SCREEN_WIDTH - GRID_WIDTH * BLOCK_SIZE) // 2,
                    y * BLOCK_SIZE,
                    BLOCK_SIZE - 1,
                    BLOCK_SIZE - 1
                )
                pygame.draw.rect(self.screen, COLORS[self.grid[y][x]], rect)

        start_x = (SCREEN_WIDTH - GRID_WIDTH * BLOCK_SIZE) // 2

        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(
                self.screen,
                (40, 40, 40),  # Серый цвет
                (start_x + x * BLOCK_SIZE, 0),
                (start_x + x * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE),
                1
            )

        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(
                self.screen,
                (40, 40, 40),
                (start_x, y * BLOCK_SIZE),
                (start_x + GRID_WIDTH * BLOCK_SIZE, y * BLOCK_SIZE),
                1
            )

    def draw_piece(self, piece):
        """
        Отрисовывает текущую падающую фигуру на игровом поле.

        Действия метода:
            - Перебирает матрицу формы фигуры (piece.shape).
            - Для каждой заполненной ячейки (значение 1) вычисляет экранные координаты:
            - Рисует квадрат с цветом фигуры (COLORS[piece.color]) и небольшим
              отступом (BLOCK_SIZE - 1) для визуального разделения блоков.
        """

        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        (piece.x + x) * BLOCK_SIZE +
                        (SCREEN_WIDTH - GRID_WIDTH * BLOCK_SIZE) // 2,
                        (piece.y + y) * BLOCK_SIZE,
                        BLOCK_SIZE - 1,
                        BLOCK_SIZE - 1
                    )
                    pygame.draw.rect(self.screen, COLORS[piece.color], rect)

    def check_collision(self, dx, dy):
        """
        Проверяет столкновение текущей фигуры с границами игрового поля или зафиксированными блоками.

        Действия метода:
            1. Для каждой заполненной ячейки фигуры (cell == 1):
                - Вычисляет новые координаты: new_x = текущий x + dx + смещение ячейки в форме.
                - Вычисляет новые координаты: new_y = текущий y + dy + смещение ячейки в форме.
            2. Проверяет условия столкновения:
                - Выход за границы сетки: new_x < 0, new_x >= GRID_WIDTH, new_y >= GRID_HEIGHT.
                - Пересечение с занятой ячейкой в сетке (new_y >= 0 и self.grid[new_y][new_x] != 0).
            3. Возвращает True при первом обнаруженном столкновении.
        """

        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = self.current_piece.x + x + dx
                    new_y = self.current_piece.y + y + dy
                    if not (0 <= new_x < GRID_WIDTH and new_y < GRID_HEIGHT):
                        return True
                    if new_y >= 0 and self.grid[new_y][new_x]:
                        return True
        return False

    def merge_piece(self):
        """
        Фиксирует текущую падающую фигуру в игровой сетке и запускает связанные процессы.

        Действия метода:
            1. Перенос блоков в сетку:
               - Перебирает матрицу формы текущей фигуры (current_piece.shape).
               - Для каждой заполненной ячейки (cell == 1) обновляет соответствующую позицию
                 в игровой сетке (self.grid), присваивая ей цвет фигуры.
               - Координаты вычисляются относительно позиции фигуры (current_piece.x, current_piece.y).

            2. Очистка линий:
               - Вызывает метод clear_lines() для удаления заполненных горизонтальных линий,
                 обновления счета и уровня сложности.

            3. Создание новой фигуры:
               - Вызывает new_piece() для генерации следующей фигуры.
        """
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece.y + y][self.current_piece.x + x] = self.current_piece.color
        self.clear_lines()
        self.new_piece()

    def clear_lines(self):
        """
        Удаляет заполненные линии из игровой сетки и обновляет игровые параметры.

        Действия метода:
            1. Поиск заполненных линий:
               - Перебирает каждую строку сетки сверху вниз.
               - Проверяет, все ли ячейки строки заняты (значение != 0).

            2. Очистка линий:
               - Удаляет найденные заполненные строки из сетки.
               - Добавляет новые пустые строки ([0] * GRID_WIDTH) в верхнюю часть сетки.
               - Учитывает количество удаленных строк (lines_cleared).

            3. Обновление состояния игры:
               - Увеличивает счет: +100 очков за каждую удаленную строку * текущий уровень.
               - Пересчитывает уровень: level = 1 + score // 1000 (повышение каждые 1000 очков).
               - Уменьшает интервал падения фигур: fall_speed = max(100, 1000 - level * 100).
        """

        lines_cleared = 0
        for i, row in enumerate(self.grid):
            if all(row):
                del self.grid[i]
                self.grid.insert(0, [0] * GRID_WIDTH)
                lines_cleared += 1
        if lines_cleared:
            self.score += 100 * lines_cleared * self.level
            self.level = 1 + self.score // 1000
            self.fall_speed = max(100, 1000 - (self.level * 100))

    def game_over(self):
        """
        Обрабатывает завершение игры и запускает перезапуск.

        Действия метода:
            1. Отображение экрана завершения:
               - Выводит текст "Game Over!" с итоговым счетом в центре экрана.
               - Использует белый цвет текста (RGB: 255, 255, 255).

            2. Принудительное обновление экрана:
               - Вызывает pygame.display.update() для мгновенного отображения сообщения.

            3. Пауза на 3 секунды:
               - Останавливает выполнение кода на 3000 мс с помощью pygame.time.wait().

            4. Перезапуск игры:
               - Вызывает self.__init__() для сброса всех параметров (счет, уровень, сетка)
                 и начала новой игры.
        """

        text = self.font.render(f"Game Over! Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2,
                                SCREEN_HEIGHT // 2 - text.get_height() // 2))
        pygame.display.update()
        pygame.time.wait(3000)
        self.__init__()

    def run(self):
        """
        Запускает и управляет главным игровым циклом.

        Действия метода:
            1. Основной цикл:
               - Бесконечно обрабатывает события, обновляет состояние игры и отрисовывает кадры.
               - Прерывается только при закрытии окна (событие pygame.QUIT).

            2. Обработка событий:
               - Клавиши ←/→: Движение фигуры влево/вправо с проверкой коллизий.
               - Клавиша ↓: Ускоренное падение фигуры вниз.
               - Клавиша ↑: Поворот фигуры (с коррекцией при выходе за границы).
               - Пробел: Мгновенное падение фигуры до нижней позиции.

            3. Автоматическое падение:
               - Фигура смещается вниз каждые fall_speed миллисекунд (зависит от уровня).
               - При столкновении фиксируется в сетке (вызов merge_piece()).

            4. Отрисовка:
               - Очистка экрана, отрисовка сетки, активной фигуры и интерфейса (счет, уровень).
               - Обновление текстовых элементов (score_text, level_text) в реальном времени.
        """
        while True:
            self.screen.fill(COLORS[0])
            now = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if not self.check_collision(-1, 0):
                            self.current_piece.x -= 1
                    elif event.key == pygame.K_RIGHT:
                        if not self.check_collision(1, 0):
                            self.current_piece.x += 1
                    elif event.key == pygame.K_DOWN:
                        if not self.check_collision(0, 1):
                            self.current_piece.y += 1
                    elif event.key == pygame.K_UP:
                        self.current_piece.rotate()
                        if self.check_collision(0, 0):
                            for _ in range(3):
                                self.current_piece.rotate()
                    elif event.key == pygame.K_SPACE:
                        while not self.check_collision(0, 1):
                            self.current_piece.y += 1
                        self.merge_piece()

            if now - self.last_fall > self.fall_speed:
                if not self.check_collision(0, 1):
                    self.current_piece.y += 1
                    self.last_fall = now
                else:
                    self.merge_piece()

            self.draw_grid()
            self.draw_piece(self.current_piece)

            score_text = self.font.render(
                f"Score: {self.score}", True, (255, 255, 255))
            level_text = self.font.render(
                f"Level: {self.level}", True, (255, 255, 255))
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(level_text, (10, 40))

            pygame.display.update()
            self.clock.tick(FPS)
            pygame.display.set_caption("Tetris")

# Запуск игры
if __name__ == "__main__":
    game = Game()
    game.run()