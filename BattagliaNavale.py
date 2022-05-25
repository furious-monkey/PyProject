'''
Programma per giocare a Battaglia Navale contro il computer.

~ Fase 1: Piazzamento delle navi.
Piazzamento delle navi in base a quelle disponibili, descritte secondo (lunghezza_nave, quantita_disponibile) nella lista sottostante.
+ Comandi:
← ↑ → ↓ : Per muovere la selezione della nave.
   r    : Per ruotare la nave.
<Invio> : Per piazzare la nave.


~ Fase 2: Gioco.
A turno si colpisce un punto del campo avversario, vince chi affonda tutte le navi avversarie.
+ Comandi:
← ↑ → ↓ : Per muovere il mirino.
<Invio> : Per colpire il punto selezionato.

Requisiti:
keyboard: pip install keyboard (richiede sudo su linux, anche per l'esecuzione)

Programma creato per Windows, su Unix potrebbero esserci problemi nella gestione dell'input.
'''

from os import system, name
from random import randint
from keyboard import add_hotkey, remove_hotkey, wait

# -----------
# Game variables
BOARD_WIDTH = 10
BOARD_HEIGHT = 10
AVAILABLE_BOATS = [(4, 1),
                   (3, 2),
                   (2, 3)]

# -----------
# Graphic elements
EMPTY = ' '
MISS = '·'
BOAT = '○'
HIT = '●'
SUNK = '◆'

SELECTORS = ('⎡', '⎦')

# -----------
# Don't touch
HORIZONTAL = 0
VERTICAL = 1

# Testing
SHOW_OPPONENT_BOARD = False


class Boat:
    def __init__(self, size: int, pos: tuple, direction: int):
        self.size = size
        self.direction = direction
        self.hits = []
        self.sunk = False

        # Initialize the coordinates along the orientation
        self.coords = []
        if direction == HORIZONTAL:
            for i in range(size):
                self.coords.append((pos[0], pos[1] + i))
        elif direction == VERTICAL:
            for i in range(size):
                self.coords.append((pos[0] + i, pos[1]))

    def hit(self, pos: tuple):
        # Check if a hit is valid, and if the boat is sunk
        if pos in self.coords:
            if pos not in self.hits:
                self.hits.append(pos)
            if len(self.hits) == self.size:
                self.sunk = True
                return 4
            return 3
        return 1


class Screen:
    def __init__(self):
        self.pointerx = self.pointery = 0

        if name == 'nt':
            self.clear = lambda: system('cls')
        else:
            self.clear = lambda: print('\033c')

    def render_board(self, board: list, selected: list = None, hidden: bool = False):
        # Turn the board list into a string
        res = '┌' + '───┬' * (BOARD_WIDTH-1) + '───┐\n'
        for i in range(BOARD_HEIGHT):
            res += '│'
            for j in range(BOARD_WIDTH):
                if selected is not None and (i, j) in selected:
                    selectors = SELECTORS
                else:
                    selectors = (' ', ' ')

                if board[i][j] == 0:
                    res += selectors[0] + EMPTY + selectors[1]
                elif board[i][j] == 1:
                    res += selectors[0] + MISS + selectors[1]
                elif board[i][j] == 2:
                    if hidden:
                        res += selectors[0] + EMPTY + selectors[1]
                    else:
                        res += selectors[0] + BOAT + selectors[1]
                elif board[i][j] == 3:
                    res += selectors[0] + HIT + selectors[1]
                elif board[i][j] == 4:
                    res += selectors[0] + SUNK + selectors[1]

                res += '│'

            # Line separator
            if i != BOARD_HEIGHT-1:
                res += '\n├' + '───┼' * (BOARD_WIDTH-1) + '───┤\n'

        res += '\n└' + '───┴' * (BOARD_WIDTH-1) + '───┘'

        return res

    def render(self, first_board: list, second_board: list = None, selected: list = None):
        if second_board is None:
            # If there is no opponent board (when creating a boat) show only the first one
            first_board = self.render_board(first_board, selected)
            second_board = ''

        else:
            # General case with both boards (when playing)
            first_board = self.render_board(first_board, selected, not SHOW_OPPONENT_BOARD) + '\n  ~' + '^~' * (BOARD_WIDTH*2-2)  # Separator between boards
            second_board = self.render_board(second_board)

        # Clear the screen, TODO: find the best way to do this
        self.clear()

        # Print the boards
        print(first_board)
        print(second_board)

    def is_valid(self, board: list, boat: Boat):
        # Check if the boat is out of bounds
        if boat.direction == HORIZONTAL:
            if (boat.coords[0][1] + boat.size) > BOARD_WIDTH:
                return False
        elif boat.direction == VERTICAL:
            if (boat.coords[0][0] + boat.size) > BOARD_HEIGHT:
                return False

        # Check if the boat overlaps with another one
        for y, x in boat.coords:
            if board[y][x] != 0:
                return False

        return True

    # Generate one boat
    def init_boat(self, board: list, length: int, random: bool = False):
        # Generate a boat with random position and direction
        if random:
            y = randint(0, BOARD_HEIGHT-1)
            x = randint(0, BOARD_WIDTH-1)

            boat = Boat(length, (y, x), randint(0, 1))

            # If the boat is valid return it, otherwise try again
            if self.is_valid(board, boat):
                return boat

            return self.init_boat(board, length, True)

        else:
            # Starting orientation
            d = HORIZONTAL

            # Function called on keypress
            def move(_y: int = 0, _x: int = 0, _d: bool = False):
                nonlocal d

                # Move the boat
                self.pointery += _y
                self.pointerx += _x

                # Reset if out of bounds, TODO: check full length of boat
                if self.pointery < 0 or self.pointery >= BOARD_HEIGHT:
                    self.pointery -= _y
                if self.pointerx < 0 or self.pointerx >= BOARD_WIDTH:
                    self.pointerx -= _x

                # Change direction
                if _d:
                    d = not d

                # Generate selected coordinates
                if d == HORIZONTAL:
                    select = [(self.pointery, self.pointerx + i) for i in range(length)]
                elif d == VERTICAL:
                    select = [(self.pointery + i, self.pointerx) for i in range(length)]

                # Refresh the screen
                self.render(board, selected=select)

            # Add keypress hooks to move the boat
            add_hotkey('left', move, args=(0, -1), suppress=True)
            add_hotkey('up', move, args=(-1, 0), suppress=True)
            add_hotkey('right', move, args=(0, 1), suppress=True)
            add_hotkey('down', move, args=(1, 0), suppress=True)
            add_hotkey('r', move, args=(0, 0, True), suppress=True)

            # Render the board
            move()

            # Wait for the user to select a position and press enter
            wait('enter', suppress=True)

            # Remove keypress hooks
            remove_hotkey('left')
            remove_hotkey('up')
            remove_hotkey('right')
            remove_hotkey('down')
            remove_hotkey('r')

            # Generate boat based on selected coordinates and direction
            boat = Boat(length, (self.pointery, self.pointerx), d)

            # Check if the boat is valid and return it, otherwise try again
            if self.is_valid(board, boat):
                return boat

            return self.init_boat(board, length)

    def select_for_hit(self, first_board: list, second_board: list):

        # Function called on keypress
        def move(_y: int = 0, _x: int = 0):
            # Move the selection
            self.pointery += _y
            self.pointerx += _x

            # Reset if out of bounds
            if self.pointery < 0 or self.pointery >= BOARD_HEIGHT:
                self.pointery -= _y
            if self.pointerx < 0 or self.pointerx >= BOARD_WIDTH:
                self.pointerx -= _x

            self.render(first_board, second_board, [(self.pointery, self.pointerx)])

        # Add keypress hooks to move the boat
        add_hotkey('left', move, args=(0, -1), suppress=True)
        add_hotkey('up', move, args=(-1, 0), suppress=True)
        add_hotkey('right', move, args=(0, 1), suppress=True)
        add_hotkey('down', move, args=(1, 0), suppress=True)

        # Render the board
        move()

        # Wait for the user to select a position and press enter
        wait('enter', suppress=True)

        # Remove keypress hooks
        remove_hotkey('left')
        remove_hotkey('up')
        remove_hotkey('right')
        remove_hotkey('down')

        return (self.pointery, self.pointerx)


class Game:
    def __init__(self, screen: Screen):
        self.screen = screen
        self.player_boats = []
        self.opponent_boats = []
        self.player_board = [[0 for i in range(BOARD_WIDTH)] for j in range(BOARD_HEIGHT)]
        self.opponent_board = [[0 for i in range(BOARD_WIDTH)] for j in range(BOARD_HEIGHT)]

    def player_turn(self):
        hit_coords = self.screen.select_for_hit(self.opponent_board, self.player_board)

        for boat in self.opponent_boats:
            hit_res = boat.hit(hit_coords)

            self.opponent_board[hit_coords[0]][hit_coords[1]] = hit_res

            if hit_res != 1:
                # Sunk boat
                if hit_res == 4:
                    # Update all coordinates to be sunk
                    for i in boat.coords:
                        self.opponent_board[i[0]][i[1]] = 4

                    # Check if all boats are sunk
                    if sum([boat.sunk for boat in self.opponent_boats]) == len(self.opponent_boats):
                        self.end()

                # Boat hit already found, no need to continue
                break

    def opponent_turn(self):
        # TODO: AI
        # Hit a random coordinate
        hit_coords = (randint(0, BOARD_HEIGHT-1), randint(0, BOARD_WIDTH-1))

        for boat in self.player_boats:
            hit_res = boat.hit(hit_coords)

            self.player_board[hit_coords[0]][hit_coords[1]] = hit_res

            if hit_res != 1:
                if hit_res == 4:
                    for i in boat.coords:
                        self.player_board[i[0]][i[1]] = 4

                    if sum([boat.sunk for boat in self.player_boats]) == len(self.player_boats):
                        self.end(False)

                break

    def init_boats(self, player: bool = True):
        for l, q in AVAILABLE_BOATS:
            for j in range(q):
                # RANDOM OPPONENT BOATS
                boat = self.screen.init_boat(self.opponent_board, l, random=True)
                self.opponent_boats.append(boat)
                for y, x in boat.coords:
                    self.opponent_board[y][x] = 2

                # PLAYER BOATS
                boat = self.screen.init_boat(self.player_board, l)
                self.player_boats.append(boat)
                for y, x in boat.coords:
                    self.player_board[y][x] = 2

    def start(self):
        self.in_game = True

        while True:
            self.player_turn()
            if not self.in_game:
                break

            self.opponent_turn()
            if not self.in_game:
                break

    def end(self, win: bool = True):
        self.in_game = False

        self.screen.render(self.opponent_board, self.player_board)

        print()
        if win:
            print(' ' * (BOARD_WIDTH*2-11) + '▀▄▀▄▀▄ YOU WON ! ▄▀▄▀▄▀')
        else:
            print(' ' * (BOARD_WIDTH*2-11) + '▀▄▀▄▀▄ YOU LOST ! ▄▀▄▀▄▀')

        if input('\nPress enter to exit, or r+enter to restart.\n') == 'r':
            self.player_boats = []
            self.opponent_boats = []
            self.player_board = [[0 for i in range(BOARD_WIDTH)] for j in range(BOARD_HEIGHT)]
            self.opponent_board = [[0 for i in range(BOARD_WIDTH)] for j in range(BOARD_HEIGHT)]

            self.init_boats()
            self.start()


def main():
    game = Game(Screen())
    game.init_boats()
    game.start()


if __name__ == '__main__':
    main()
