# coding: utf8

# импортируем библиотеку пигейм и модуль рандома

import pygame
import random

# определяем размеры игрового поля, размер одной ячейки и шрифта, который будет использоваться в игре, задаем фон 
# (пока черный, но вдруг захочу что-то красивое нарисовать)
#*** для удобства фон заменен на просто черный экран
# определяем размеры информационного поля и полный размер окна с его учетом 
# определяем цвета всех элементов

SCREEN_X = 1280
SCREEN_Y = 768

CELL_SIZE = 8
FONT_SIZE = max(CELL_SIZE, 16)

TEXT_ZONE = int(FONT_SIZE * 2.5)
SCREEN_Y_WITH_TEXT = SCREEN_Y + TEXT_ZONE

#*** BACKGROUND = 'fon.png'

BACKGROUND_COLOR = (0, 0, 128)
CELL_COLOR = (255, 255, 0)

TEXT_BACKGROUND_COLOR = (0, 0, 0)

TEXT_COLOR_1 = (255, 0, 0)
TEXT_COLOR_2 = (0, 255, 255)

# определяем количество ячеек по горизонтали и вертикали, а также нужно ли делать задержку 
# ! задержка дается в значении максимально допустимого fps ! (0 - без ограничений)

NUMBER_X = SCREEN_X // CELL_SIZE
NUMBER_Y = SCREEN_Y // CELL_SIZE

DELAY = 0

# сколько должно быть рядом живых клеток, чтоб появилась новая и 
# сколько должно быть рядом живых клеток, чтоб не умирала живая

NEAR_TO_BORN = 3
NEAR_TO_LIVE = 2

DATA_FILE = 'data.txt'

# класс клетки, есть ли клетки в этом месте, и какие у нее кооридинаты в единицах размера ячейки

class Cell:
    def __init__(self, x, y, is_cell):
        self.is_cell = is_cell
        self.x = x * CELL_SIZE
        self.y = y * CELL_SIZE

# отрисовка клетки на холсте, если клетки есть - рисовать квадрат со стороной размера ячейки темно-зеленым, 
# если нет - оставляем черный фон

    def render(self, where):
        if self.is_cell: 
            color = CELL_COLOR
            self.sur = pygame.Surface((CELL_SIZE, CELL_SIZE))
            self.sur.fill(color) 
            where.blit(self.sur, (self.x, self.y))
#        else: 
#            color = (0, 0, 0)

# класс ящика, в котором живут клетки, по умолчанию заполнен пустыми ячейками, у каждой из которых 0 заполненных
# соседей и всего 0 клеток в ящике

class Box:
    def __init__(self):
        self.box = [[Cell(x, y, False) for y in range(NUMBER_Y)] for x in range(NUMBER_X)]
        self.near = [[0 for y in range(NUMBER_Y)] for x in range(NUMBER_X)]
        self.total = 0

# отрисовка всех клеток
        
    def render(self, where):
        for x in range(NUMBER_X):
            for y in range(NUMBER_Y):
                self.box[x][y].render(where)

# случайное заполнение ящика клетками

    def random(self):
        for x in range(NUMBER_X):
            for y in range(NUMBER_Y):
                self.box[x][y].is_cell = random.randint(0,1)

# очистка ящика

    def clear(self):
        self.__init__()

# сохранение и загрузка ящика из файла с данными

    def save(self, datafile):
        with open(datafile, 'w') as data:
            data.write(str(NUMBER_X) + '\n' + str(NUMBER_Y) + '\n')
            for x in range(NUMBER_X):
                for y in range(NUMBER_Y):
                    data.write(str(int(self.box[x][y].is_cell)))

    def load(self, datafile):
        try:
            with open(datafile, 'r') as data_file:
                data = data_file.read().split('\n')
                if int(data[0]) != NUMBER_X or int(data[1]) != NUMBER_Y:
                    print('Поле неверного размера, невозможно загрузить')
                else:
                    for x in range(NUMBER_X):
                        for y in range(NUMBER_Y):
                            if data[2][x*NUMBER_Y + y] == '1':
                                 self.box[x][y].is_cell = True
                            else: 
                                 self.box[x][y].is_cell = False
        except:
            print('Файл для загрузки отсутствует или имеет неверный формат')

# обновление ящика
# для каждой клетки на поле посчитать количество соседей с учетом замкнутости поля, т.е. соседом
# для первой клетки будет последняя по х и у

    def update(self, where):
        for x in range(NUMBER_X):
            for y in range(NUMBER_Y):
                self.near[x][y] = 0
                for i in range(-1, 2):
                    for j in range(-1, 2):

                        if j == 0 and i == 0: 
                            continue

                        if (x+i) < 0:
                            temp_x = NUMBER_X -1
                        elif (x+i) >= NUMBER_X:
                            temp_x = 0
                        else:
                            temp_x = x+i

                        if (y+j) < 0:
                            temp_y = NUMBER_Y -1
                        elif (y+j) >= NUMBER_Y:
                            temp_y = 0
                        else:
                            temp_y = y+j

                        if self.box[temp_x][temp_y].is_cell:
                            self.near[x][y] += 1

# когда посчитали количество соседей, то обновить поле - если соседа три, то создать новую клетку, 
# если соседа не два и есть в ячейке клетка - ее убрать, посчитать, сколько всего клеток в ящике

        self.total = 0

        for x in range(NUMBER_X):
            for y in range(NUMBER_Y):
                if self.near[x][y] == NEAR_TO_BORN:
                    self.box[x][y].is_cell = True
                elif not (self.near[x][y] == NEAR_TO_LIVE and self.box[x][y].is_cell):
                    self.box[x][y].is_cell = False

                if self.box[x][y].is_cell:
                    self.total += 1
                    
# готовим (или меняем) поле

def prepare():

# определяем условие выхода из цикла и берем глобальную переменную хода 

    exit = False
    global turn
    
    while not exit:

# если нажали крестик - выйти из подготовки и из игры, если нажали пробел или ввод - вышли из подготовки и запустили
# главный цикл игры, если нажали r - заполнили поле случайно клетками, c - очистили поле,
# s - сохранить данные в фыйл, l - прочитать данные из файла,
# если нажата клавиша мыши, определяем ее координаты, переводим координаты из пикселей в номер ячейки (с учетом ширины 
# текстовой зоны вверху экрана, и меняем клетку в ячейке, если ее не было - создаем, если была - убираем

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                global new_game
                new_game = False
                exit = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    exit = True
                elif event.key == pygame.K_r:
                    screen_box.random()
                elif event.key == pygame.K_c:
                    screen_box.clear()
                elif event.key == pygame.K_s:
                    screen_box.save(DATA_FILE)
                elif event.key == pygame.K_l:
                    screen_box.load(DATA_FILE)
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()                      
                if pos[1] > TEXT_ZONE:
                    screen_box.box[pos[0]//CELL_SIZE][(pos[1]-TEXT_ZONE)//CELL_SIZE].is_cell = not screen_box.box[pos[0]//CELL_SIZE][(pos[1]-TEXT_ZONE)//CELL_SIZE].is_cell

# инициируем фон, шрифты, римуем ящик, создаем информационное сообщение вверху экрана, отрисовываем ящик и информацию в окне

#        fon = pygame.image.load(BACKGROUND)
        fon = pygame.Surface((SCREEN_X, SCREEN_Y))
        fon.fill(BACKGROUND_COLOR) 

        screen.blit(fon, (0, 0))

        screen_box.render(screen)

        font_base = pygame.Surface((SCREEN_X, TEXT_ZONE))
        font_base.fill(TEXT_BACKGROUND_COLOR) 
        score_font = pygame.font.SysFont("comicsansms", FONT_SIZE)
        result = score_font.render("Установите клетки и нажмите пробел для запуска игры. Ход: " + str(turn), 1, TEXT_COLOR_1)
        result_2 = score_font.render("Для случайного распределения нажмите r, для очистки экрана нажмите c, для сохранения/загрузки поля нажмите s/l", 1, TEXT_COLOR_2)
        font_base.blit(result, (0, 0))
        font_base.blit(result_2, (0, FONT_SIZE))

        window.blit(font_base, (0, 0))
        window.blit(screen, (0, TEXT_ZONE))

        pygame.display.flip()


# основной цикл игры

def lunch(score = 0):

# запускаем таймер, берем глобальную переменную ход, определяем условия выхода

    timer = pygame.time.Clock()
    exit = False
    global turn
    
    while not exit:

# во время игры мы можем или выйти, или поставить на паузу с возможностью редактирования поля (выйти, не меняя значение
# глобальной перменной, определяющий главный цикл

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                global new_game
                new_game = False
                exit = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    exit = True

# загружаем фон, рисуем ящик, меняем ящик по правилам клеточного автомата

#        fon = pygame.image.load(BACKGROUND)
        fon = pygame.Surface((SCREEN_X, SCREEN_Y))
        fon.fill(BACKGROUND_COLOR) 

        screen.blit(fon, (0, 0))

        screen_box.render(screen)

        screen_box.update(screen)

# создаем информационное сообщение, добавляем ход, отрисовываем основное поле и информационное сообщение в окне, по необходимости
# делаем задержку, перерисовываем экран

        font_base = pygame.Surface((SCREEN_X, TEXT_ZONE))
        font_base.fill(TEXT_BACKGROUND_COLOR) 
        score_font = pygame.font.SysFont("comicsansms", FONT_SIZE)
        result = score_font.render("Нажмите пробел для паузы и/или режима установки доволнительны клеток. Ход: " + str(turn), 1, TEXT_COLOR_1)
        result_2 = score_font.render("Количество живых клеток: " + str(screen_box.total), 1, TEXT_COLOR_2)
        font_base.blit(result, (0, 0))
        font_base.blit(result_2, (0, FONT_SIZE))

        turn += 1

        window.blit(font_base, (0, 0))
        window.blit(screen, (0, TEXT_ZONE))
        timer.tick(DELAY)
        pygame.display.flip()


if __name__ == '__main__':

# создаем главное окно, даем ему название, создаем экран на главном окне, где все будет происходить, задаем условия выхода из цикла
# инициализируем шрифты

    window = pygame.display.set_mode((SCREEN_X, SCREEN_Y_WITH_TEXT))
    pygame.display.set_caption('Игра "Жизнь"')
    screen = pygame.Surface((SCREEN_X, SCREEN_Y))
    pygame.font.init()

# обнуляем ход, генерируем пустой ящий, в котором будет происходить жизнь,
# если есть - загружаем сохраненное поле

    turn = 0 

    new_game = True
    screen_box = Box()
    screen_box.load(DATA_FILE)

# главный цикл игры, запускаем подготовку, если не надо после нее выходить, то запускаем игру

    while new_game:
        prepare()
        if new_game:
            lunch()

