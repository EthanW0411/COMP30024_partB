from partB import game_const as const

# --------------------------------------------------------------------------- #

# A player made for playing the Watch Your Back!
class Player:

    def __init__(self, colour):
        self.colour = colour
        self.turnNum = 0
        self.game = Game()
        "dadaa"


    def update(self, move):
        self.update(move)

    def action(self, turns):
        #self.turnNum = turns
        action = self.action(turns)
        return action
    '''
        def placement_phase(self):
        current_score = 0
        for x in range(const.INITIAL_BOARD_SIDE):
            for y in range(const.INITIAL_BOARD_SIDE):
                if self.board[x][y].value > current_score
    '''




# --------------------------------------------------------------------------- #

# HELPER CLASS FOR PLAYER

class Game:
    """"Represent the state of a game of Watch Your Back!
        Modified from referee.py written by Matt Farrugia
        and Shreyash Patodia.
    """
    def __init__(self):
        self.board = [[Square(const.UNOCCUPIED) for _ in range(const.INITIAL_BOARD_SIDE)]
                      for _ in range(const.INITIAL_BOARD_SIDE)]
        for square in const.INITIAL_CORNER_LOCATION:
            x, y = square
            self.board[y][x].set_piece(const.CORNER)
            self.board[y][x].set_value(const.CORNER_VALUE)

        # tracking progress through game phases
        self.turns = 0
        self.phase = 'placing'
        self.pieces = {const.WHITE: 0, const.BLACK: 0}

    def get_board(self):
        return self.board



    def initialize_scoreboard(self, colour):
        """"
        assign values for each square in game board for placing phase

        """
        for square in const.INITIAL_BY_CORNER_LOCATION:
            x, y = square
            self.board[y][x].set_value(const.BY_CORNER_VALUE)
        for x in range(const.INITIAL_BOARD_SIDE):
            for y in range(const.INITIAL_BOARD_SIDE):
                if colour == "white":
                    if y in [0, 7] and x in [2, 3, 5]:
                        """
                        5: two corners on best offensive line
                        3: traps on second defensive line
                        2: two corners on best defensive line
                        """
                        self.board[y][x].set_value(200)
                if colour == "black":
                    if y in [0, 7] and x in [2, 4, 5]:
                        """
                        5: two corners on best offensive line
                        4: check traps on second offensive line
                        2: two corners on best defensive line
                        """
                        if x == 4:
                            self.board[y][x].is_white()
                            self.board[y][x-1].set_value(-1)
                        else:
                            self.board[y][x].set_value(200)

    def within_board(self, x, y):
        """
        Check if a given pair of coordinates is 'on the game board'
        Modified from referee.py written by Matt Farrugia
        and Shreyash Patodia.

        :param x: column value
        :param y: row value
        :return:  True iff the coordinate is on the game board
        """
        for coord in [y, x]:
            if coord < 0 or coord > (const.INITIAL_BOARD_SIDE - 1):
                return False
        if self.board[y][x] == ' ':
            return False
        return True

    def enemies(self, piece):
        """
        which pieces can eliminate a piece of this type?
        Modified from referee.py written by Matt Farrugia
        and Shreyash Patodia.

        :param piece: the type of piece ('B', 'W', or 'X')
        :return: set of piece types that can eliminate a piece of this type
        """
        if piece == const.BLACK:
            return {const.CORNER, const.WHITE}
        elif piece == const.WHITE:
            return {const.BLACK, const.CORNER}
        return set()

    def targets(self, piece):

        """
        Which pieces can a piece of this type eliminate?
        Modified from referee.py written by Matt Farrugia
        and Shreyash Patodia.

        :param piece: the type of piece ('B', 'W', or 'X')
        :return: the set of piece types that a piece of this type can eliminate
        """
        if piece == 'B':
            return {'W'}
        elif piece == 'W':
            return {'B'}
        elif piece == 'X':
            return {'B', 'W'}
        return set()

    def surrounded(self, x, y, dx, dy):
        """
        Check if piece on (x, y) is surrounded on (x + dx, y + dy) and
        (x - dx, y - dy).
        Modified from referee.py written by Matt Farrugia
        and Shreyash Patodia.

        :param x: column of the square to be checked
        :param y: row of the square to be checked
        :param dx: 1 if adjacent cols are to be checked (dy should be 0)
        :param dy: 1 if adjacent rows are to be checked (dx should be 0)
        :return: True iff the square is surrounded
        """
        xa, ya = x + dx, y + dy
        firstval = None
        if self.within_board(xa, ya):
            firstval = self.board[ya][xa].get_piece()

        xb, yb = x - dx, y - dy
        secondval = None
        if self.within_board(xb, yb):
            secondval = self.board[yb][xb].get_piece()

        # If both adjacent squares have enemies then this piece is surrounded!
        piece = self.board[y][x].get_piece()
        enemies = self.enemies(piece)
        return (firstval in enemies and secondval in enemies)


# --------------------------------------------------------------------------- #

# HELPER CLASS FOR GAME

class Square:
    """Represent the a sprite on game board"""
    def __init__(self, piece):
        self.piece = piece
        self.value = const.INITIAL_VALUE

    def set_value(self, value):
        self.value = value

    def set_piece(self, piece):
        self.piece = piece

    def get_piece(self):
        return self.piece

    def get_value(self):
        return self.value

    def is_white(self):
        return self.piece == const.WHITE

    def is_black(self):
        return self.piece == const.BLACK

    def is_corner(self):
        return self.piece == const.CORNER

    def add_value(self, value):
        self.value += value

    def sub_value(self, value):
        self.value -= value
