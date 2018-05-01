from partB import game_const as const


class Player:

    def __init__(self, colour):
        self.colour = colour

    def update(self, move):
        self.update(move)

    def action(self, turns):
        action = self.action(turns)
        return action


class Game:
    """"Represent the state of a game of Watch Your Back!"""
    def __init__(self):
        self.board = [[Square(const.UNCCUPIED) for _ in range(const.INITIAL_BOARD_SIDE)]
                      for _ in range(const.INITIAL_BOARD_SIDE)]
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
