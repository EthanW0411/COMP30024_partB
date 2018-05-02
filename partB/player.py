#from partB import game_const as const


class Player:

    def __init__(self, colour):
        self.colour = colour
        self.turnNum = 0
        self.board = Game()


    def update(self, move):
        self.update(move)

    def action(self, turns):
        self.turnNum = turns
        action = self.action(turns)
        return action

    def generate_initial_scoreboard(self):
        if self.colour == const.WHITE:
            for x in range(const.INITIAL_BOARD_SIDE):
                for y in range(const.INITIAL_BOARD_SIDE):
                    if self.board[x][y].piece == const.UNOCCUPIED:
                        self.board[x][y].set_value(0)
            self.board[0][5].set_value(200)
            self.board[7][5].set.value(200)




    def placementPhase(self):
        current_score = 0
        for x in range(const.INITIAL_BOARD_SIDE):
            for y in range(const.INITIAL_BOARD_SIDE):
                if self.board[x][y].value > current_score




class Game:
    """"Represent the state of a game of Watch Your Back!"""
    def __init__(self):
        for x in range(const.INITIAL_BOARD_SIDE):
            for y in range(const.INITIAL_BOARD_SIDE):
                self.board[x][y] = Square(const.UNOCCUPIED)
        for square in const.INITIAL_CORNER_LOCATION:
            x, y = square
            self.board[y][x].piece = const.CORNER


        # tracking progress through game phases
        self.turns = 0
        self.phase = 'placing'
        self.pieces = {const.WHITE: 0, const.BLACK: 0}

class Square:
    """Represent the a sprite on game board"""
    def __init__(self, piece):
        self.piece = piece
        self.value = const.INITIAL_VALUE

    def set_value(self, value):
        self.value = value

