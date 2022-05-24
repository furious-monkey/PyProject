'''
Programma per giocare a Battaglia Navale contro il computer.
'''
import curses
from random import randint
from secrets import choice
from time import sleep


BOARD_WIDTH = 10
BOARD_HEIGHT = 10
AVAILABLE_BOATS = [(4, 1),
                   (3, 2),
                   (2, 3)]

HORIZONTAL = 0
VERTICAL = 1


class Boat:
    def __init__(self, size: int, pos: tuple, direction: int):
        self.size = size
        self.direction = direction
        self.hits = []
        self.sunk = False

        self.coords = []
        if direction == HORIZONTAL:
            for i in range(size):
                self.coords.append((pos[0] + i, pos[1]))
        elif direction == VERTICAL:
            for i in range(size):
                self.coords.append((pos[0], pos[1] + i))

    def hit(self, pos: tuple):
        if pos in self.coords:
            self.hits.append(pos)
            if len(self.hits) == self.size:
                self.sunk = True
                return 2
            return 1
        return 0


class Screen:
    def __init__(self):
        self.stdscr = curses.initscr()
        self.stdscr.resize(50, 24)
        curses.noecho()

    def check_if_valid(self, board: list, boat: Boat):
        if boat.direction == HORIZONTAL:
            if (boat.coords[0][0] + boat.size) > BOARD_WIDTH:
                return False
        elif boat.direction == VERTICAL:
            if (boat.coords[0][1] + boat.size) > BOARD_HEIGHT:
                return False

        for x, y in boat.coords:
            if board[x][y] != 0:
                return False

        return True

    def init_boat(self, length: int):
        sleep(1)
        return Boat(length, (randint(0, BOARD_WIDTH-3), randint(0, BOARD_HEIGHT-3)), choice([HORIZONTAL, VERTICAL]))

    def select(self, pos: tuple):
        pass

    def convert_board(self, board: list):
        board_string = ''
        for i in range(BOARD_HEIGHT):
            for j in range(BOARD_WIDTH):
                if board[i][j] == 0:
                    board_string += '.'
                elif board[i][j] == 1:
                    board_string += 'O'
                elif board[i][j] == 2:
                    board_string += 'X'
                board_string += ' '
            board_string += '\n'
        return board_string

    def update(self, player_board: list, opponent_board: list):
        player_board = self.convert_board(player_board)
        opponent_board = self.convert_board(opponent_board)

        self.stdscr.clear()
        self.stdscr.addstr(0, 0, player_board)
        self.stdscr.addstr(0, 22, opponent_board)
        self.stdscr.refresh()


class Game:
    def __init__(self, screen: Screen):
        self.screen = screen
        self.player_boats = []
        self.opponent_boats = []
        self.player_board = [[0 for i in range(BOARD_WIDTH)] for j in range(BOARD_HEIGHT)]
        self.opponent_board = [[0 for i in range(BOARD_WIDTH)] for j in range(BOARD_HEIGHT)]

    def init_boats(self, player: bool = True):
        if player:
            for i in AVAILABLE_BOATS:
                for j in range(i[1]):
                    self.add_boat(self.screen.init_boat(i[0]), player=True)

    def add_boat(self, boat: Boat, player: bool = True):
        if player:
            self.player_boats.append(boat)
            for i in boat.coords:
                self.player_board[i[0]][i[1]] = 1

        else:
            self.opponent_boats.append(boat)
            for i in boat.coords:
                self.opponent_board[i[0]][i[1]] = 1

        #! testing, remove later
        self.screen.update(self.player_board, self.opponent_board)


def main():
    game = Game(Screen())
    game.init_boats()
    game.add_boat(Boat(2, (0, 0), HORIZONTAL))


if __name__ == '__main__':
    main()
