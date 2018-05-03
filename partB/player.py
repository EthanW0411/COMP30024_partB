from partB import game_const as const


class Player:

    def __init__(self, colour):
        self.colour = colour
        self.turnNum = 0
        self.game = Game()


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

    """scoreboard has been generated in Game class"""

    def generate_initial_scoreboard(self, colour):
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

