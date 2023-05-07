from random import randint
class BoardException(Exception): #отлавливаем выстрелы за пределы поля (когда вводятся координаты за пределом поля)
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Выстрел за пределы доски! Введите правильные коррдинаты"

class BoardUsedException(BoardException):
    def __str__(self):
        return "В это поле уже был произведен выстрел! Введите другие координаты для выстрела"

class BoardWrongShipException(BoardException): #будем вызывать при ошибочном размещении корабля
    pass

class Dot: #точки на игровом поле
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, other): #проверка точек в списке
        return self.x == other.x and self.y == other.y

class Ship: #класс кораблей
    def __init__(self, size, start_pos, orient):
        self.size = size
        self.start_pos = start_pos
        self.orient = orient
        self.lives = size #количество жизней у корабля соответствует количеству его точек(размеру)

    @property
    def dots(self): #описываем корабль по его свойствам
        ship_dots = []
        for i in range(self.size):
            cur_x = self.start_pos.x
            cur_y = self.start_pos.y

            if self.orient == 0: #горизонтальный
                cur_x += i
            else: #вертикальный
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def shooted(self, shot): #проверяем, было лп попадание по кораблю
        return shot in self.dots


class Board: #игровая доска
    def __init__(self, hidden=False, board_size = 6):
        self.hidden = hidden #используем для скрытия кораблей соперника на его доске
        self.board_size = board_size

        self.count = 0

        self.field = [["O"] * board_size for i in range(board_size)] #все поля доски

        self.busy = [] #занятые поля
        self.ships = [] #корабли
    def out(self, d):
        return not((0<= d.x < self.board_size) and (0<= d.y < self.board_size))
    def print_board(self): #рисуем доску
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        res += f"\n---------------------------"
        for i, row in enumerate(self.field):
            #res += f"\n---------------------------"
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        res += f"\n---------------------------"
        if self.hidden: #если доска соперника, то меняем символы кораблей на 0
            res = res.replace("■", "O")
        return res

    def add_ship(self, ship): #добавляем корабль на доску

        for dot in ship.dots:
            if self.out(dot) or dot in self.busy: #если пытаемся поставить корябль на занятое место или за пределы карты, то вызываем исключение
                raise BoardWrongShipException()
        for dot in ship.dots:
            self.field[dot.x][dot.y] = "■"
            self.busy.append(dot)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False): #обводим контур корабля если True, помечаем соседние точки как недоступные
        near = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dot in ship.dots:
            for dot_x, dot_y in near:
                cur = Dot(dot.x + dot_x, dot.y + dot_y)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def shot(self, d): #выстрел
        if self.out(d): #проверка выстрела за границу доски
            raise BoardOutException()

        if d in self.busy: #проверка выстрела в уже простреляное поле
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships: #если по кораблю попадаем
            if ship.shooted(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True) #обводим убитый корабль точками
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True #для повторения хода пользователя

        self.field[d.x][d.y] = "."
        print("Промах!")
        return False #переход хода

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        pass


    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
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
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hidden = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        ships = [3, 2, 2, 1, 1, 1, 1]
        board = Board(board_size=self.size)
        attempts = 0
        for s in ships:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(s, Dot(randint(0, self.size), randint(0, self.size)), randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
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

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board.print_board())
            print("Доска компьютера:")
            print(self.ai.board.print_board())
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
