import time
from random import randint




class Dot:                      # Создаем точку
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"





class BoardException(Exception):   # общий класс исключений
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass


class Ship:                           #Класс коробля
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):        # показывает попали или нет
        return shot in self.dots


class Board:                        # Игровое поле
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0              # Кол-во пораженных кораблей

        self.field = [["O"] * size for _ in range(size)] # Клетка которая хранит состояние

        self.busy = []              # Занятые точки
        self.ships = []             # Список кораблей





    def __str__(self):              # Вывод корабля на доску
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field): # Проходимся по строкам доски
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:                # Отвечает за скрытие символов корабля
            res = res.replace("■", "O")
        return res


    def out(self, d):               # Проверяет находится ли точка за пределами доски
        return not((0<= d.x < self.size) and (0<= d.y < self.size))




    def contour(self, ship, verb = False):
        near = [                    # Содержит сдвиги
            (-1, -1), (-1, 0) , (-1, 1),
            (0, -1), (0, 0) , (0 , 1),
            (1, -1), (1, 0) , (1, 1)
        ]
        for d in ship.dots:         # Проходимся циклом по списку near
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy) # Сдвигаем исходную точку
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)





    def add_ship(self, ship):      # Размещение коробля

        for d in ship.dots:
            if self.out(d) or d in self.busy: # Проверка что не выходит за границы и не занято
                raise BoardWrongShipException() # Если не так то исключение
        for d in ship.dots:        # Пройдемся по точкам коробля и поставим квадрат
            self.field[d.x][d.y] = "■"
            self.busy.append(d)    # Запишем эту точку в список занятых

        self.ships.append(ship)    # Список кораблей
        self.contour(ship)         # Обводим по контуру





    def shot(self, d):            # Делает выстрел
        if self.out(d):           # Проверка выходит ли за границы
            raise BoardOutException() # Если да то исключение

        if d in self.busy:        # Занята ли точка
            raise BoardUsedException() # Если да то исключение

        self.busy.append(d)       # Обьявляем что точка занята

        for ship in self.ships:   # Проходимся циколом по кораблям
            if ship.shooten(d):   # Если корабль прострелен
                ship.lives -= 1   # Уменьшаем кол-во hp
                self.field[d.x][d.y] = "X" # Ставим Х на место прострела
                if ship.lives == 0: # Если у корабля кончились жизни
                    self.count += 1 # Добавляем к счетчику уничтоженных кораблей
                    self.contour(ship, verb=True) # Обводим по контуру
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "." # Если мимо
        print("Мимо!")
        return False

    def begin(self):   # Хранит куда стрелял игрок
        self.busy = []
    def defeat(self):
        return self.count == len(self.ships)





class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError() # будет у потомков класса

    def move(self):
        while True:
            try:
                target = self.ask() # Просим дать координаты
                repeat = self.enemy.shot(target) # Если выстрел прошел хорошо
                return repeat # Повторяем ход
            except BoardException as e: # Если плохо то исключение, цикл продолжается
                print(e)





class AI(Player):
    def ask(self):
        time.sleep(5) # Задержка хода противника
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d





class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)






class Game:

    def __init__(self, size=6): # Конструктор доски
        self.lens = [3, 2, 2, 1, 1, 1, 1] # Длины кораблей
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True           # Скрываем корабли для компьютера

        self.ai = AI(co, pl)    # Доска AI
        self.us = User(pl, co)  # Дoска User


    def random_place(self):
        board = Board(size=self.size)
        attempts = 0  # Кол-во попыток поставить корабли
        for l in self.lens:
            while True:
                attempts += 1
                if attempts > 2000: # > 2000 вернем пустую доску
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)  # Пробуем добавить корабль
                    break                 # Если все хорошо break
                except BoardWrongShipException: # Если исключение продолжаем итерацию
                    pass
        board.begin()
        return board


    def random_board(self):  # гарантированно генерирует случайную доску
        board = None
        while board is None:
            board = self.random_place()
        return board


    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def print_boards(self):
        print("-" * 20)
        print("Доска пользователя:")
        print(self.us.board)
        print("-" * 20)
        print("Доска компьютера:")
        print(self.ai.board)

    def loop(self): # Игровой цикл
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move() # Отвечает за ход
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.defeat():
                self.print_boards()
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.defeat():
                self.print_boards()
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()