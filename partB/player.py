"""initial value for heuristic function"""
INITIAL_VALUE = 0

"""Constant for game board"""

UNOCCUPIED = '-'
CORNER = 'X'
BLACK = '@'
WHITE = 'O'
INITIAL_BOARD_SIDE = 8
INITIAL_CORNER_LOCATION = [(0, 0), (7, 0), (7, 7), (0, 7)]
DIRECTIONS = UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)
ENEMIES = {WHITE: {BLACK, CORNER}, BLACK: {WHITE, CORNER}}
FRIENDS = {WHITE: {WHITE, CORNER}, BLACK: {BLACK, CORNER}}
infinity = float('inf')


def step(position, direction):
    px, py = position
    dx, dy = direction
    return px + dx, py + dy


class Player:

    def __init__(self, colour):
        self.colour = colour
        self.turnNum = 0
        self.board = Board()


    def update(self, move):
        self.update(move)

    def action(self, turns):
        self.turnNum = turns
        action = self.action(turns)
        return action

    def generate_initial_scoreboard(self):
        if self.colour == WHITE:
            for x in range(INITIAL_BOARD_SIDE):
                for y in range(INITIAL_BOARD_SIDE):
                    if self.board[x][y].piece == UNOCCUPIED:
                        self.board[x][y].set_value(0)
            self.board[0][5].set_value(200)
            self.board[7][5].set.value(200)



#
#    def placementPhase(self):
#        current_score = 0
#        for x in range(INITIAL_BOARD_SIDE):
#            for y in range(INITIAL_BOARD_SIDE):
#                if self.board[x][y].value > current_score




class Board:
    """"Represent the state of a game of Watch Your Back!"""
    def __init__(self):
        self.grid = {}
        self.white_pieces = []
        self.black_pieces = []
        for x in range(INITIAL_BOARD_SIDE):
            for y in range(INITIAL_BOARD_SIDE):
                self.board[x][y] = Square(UNOCCUPIED)
        for square in INITIAL_CORNER_LOCATION:
            x, y = square
            self.board[y][x].piece = CORNER


        # tracking progress through game phases
        self.turns = 0
        self.phase = 'placing'
        self.pieces = {WHITE: 0, BLACK: 0}

    def find_pieces(self, square):
        for piece in self.black_pieces + self.white_pieces:
            if piece.alive and piece.pos == square:
                return piece

class Square:
    """Represent the a sprite on game board"""
    def __init__(self, piece):
        self.piece = piece
        self.value = INITIAL_VALUE

    def set_value(self, value):
        self.value = value

class Piece:

    def __init__(self, player, pos, board):
        self.player = player
        self.pos = pos
        self.board = board
        self.alive = True

    def moves(self):
        possible_moves = []
        for direction in DIRECTIONS:
            adjacent_square = step(self.pos, direction)
            if adjacent_square in self.board.grid:
                if self.board.grid[adjacent_square] == UNOCCUPIED:
                    possible_moves.append(adjacent_square)
                    continue
            opposite_square = step(adjacent_square, direction)
            if opposite_square in self.board.grid:
                if self.board.grid[opposite_square] == UNOCCUPIED:
                    possible_moves.append(opposite_square)
        return possible_moves

    def makemove(self, newpos):

        oldpos = self.pos
        self.pos = newpos
        self.board.grid[oldpos] = UNOCCUPIED
        self.board.grid[newpos] = self.player

        eliminated_pieces = []

        for direction in DIRECTIONS:
            adjacent_square = step(self.pos, direction)
            opposite_square = step(adjacent_square, direction)
            if opposite_square in self.board.grid:
                if self.board.grid[adjacent_square] in ENEMIES[self.player] \
                        and self.board.grid[opposite_square] in FRIENDS[self.player]:
                    eliminated_piece = self.board.find_piece(adjacent_square)
                    eliminated_piece.eliminate()
                    eliminated_pieces.append(eliminated_piece)

        for forward, backward in [(UP, DOWN), (LEFT, RIGHT)]:
            front_square = step(self.pos, forward)
            back_square = step(self.pos, backward)
            if front_square in self.board.grid \
                    and back_square in self.board.grid:
                if self.board.grid[front_square] in ENEMIES[self.player] \
                        and self.board.grid[back_square] in ENEMIES[self.player]:
                    self.eliminate()
                    eliminated_pieces.append(self)
                    break

        return eliminated_pieces

    def eliminate(self):
        self.alive = False
        self.board.grid[self.pos] = UNOCCUPIED


def alphabeta_cutoff_search(state, game, d=4, cutoff_test=None, eval_fn=None):
    """Search game to determine best action; use alpha-beta pruning.
    This version cuts off search and uses an evaluation function."""

    player = game.to_move(state)

    # Functions used by alphabeta
    def max_value(board, alpha, beta, depth):
        if cutoff_test(state, depth):
            return eval_fn(state)
        v = -infinity
        for a in game.actions(state):
            v = max(v, min_value(game.result(state, a),
                                 alpha, beta, depth + 1))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(state, alpha, beta, depth):
        if cutoff_test(state, depth):
            return eval_fn(state)
        v = infinity
        for a in game.actions(state):
            v = min(v, max_value(game.result(state, a),
                                 alpha, beta, depth + 1))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    # Body of alphabeta_cutoff_search starts here:
    # The default test cuts off at depth d or at a terminal state
    cutoff_test = (cutoff_test or
                   (lambda state, depth: depth > d or
                    game.terminal_test(state)))
    eval_fn = eval_fn or (lambda state: game.utility(state, player))
    best_score = -infinity
    beta = infinity
    best_action = None
    for a in game.actions(state):
        v = min_value(game.result(state, a), best_score, beta, 1)
        if v > best_score:
            best_score = v
            best_action = a
    return best_action