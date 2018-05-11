from copy import deepcopy
import random


# --------------------------------------------------------------------------- #

# GAME CONST


"""initial value for heuristic function"""
INITIAL_VALUE = 0
CORNER_VALUE = -2
BY_CORNER_VALUE = -1
"""Constant for game board"""

UNOCCUPIED = '-'
CORNER = 'X'
BLACK = '@'
WHITE = 'O'
INITIAL_BOARD_SIDE = 8
INITIAL_CORNER_LOCATION = [(0, 0), (7, 0), (7, 7), (0, 7)]
DIRECTIONS = UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)
INITIAL_BY_CORNER_LOCATION = [(1, 0), (0, 1), (6, 0), (7, 1), (6, 7), (7, 6), (1, 7), (0, 7)]

# --------------------------------------------------------------------------- #

def print_board(board):
    for y in range(INITIAL_BOARD_SIDE):
        for x in range(INITIAL_BOARD_SIDE):
            print('%3d ' % board[y][x].value, end='')
        print("\n")


def print_board_piece(board):
    for y in range(INITIAL_BOARD_SIDE):
        for x in range(INITIAL_BOARD_SIDE):
            print(board[y][x].piece + ' ', end='')
        print("\n")


# PLAYER WHICH RUNS ALPHABETA PRUNING

class Player:

    def __init__(self, colour):
        self.colour = colour
        self.game = GameBoard(colour)



    def update(self, action):
        """
        Called by referee to inform the player about the opponent's most recent move
        In placing, an action is represented by a tuple, as this (x, y)
        In moving, an action is represented by a nested tuple, as this ((a, b), (c, d))
        To represent a forfeited turn, use the value None

        :param action: the opponent's recent action
        :return:
        """
        print("-----------------------------------------update player---------------------------------------------")
        self.game.update_action(action)
        self.game.eliminate_about(action)
        print("Player own game board updated: " + self.colour)
        print_board_piece(self.game.board)
        print("-----------------------------------------finish update---------------------------------------------")

    def action(self, turns):
        """
        Called by referee to request an action by the player

        :param turns: the number of turns that have taken place since the start of the current game phase
        :return:
        """

        # update turn number
        self.game.update_turns(turns)

        '''
                if turns <= 2:
            best_square = sorted(self.game.board, key=lambda x: x.value, reverse=True)
            action = (best_square.x, best_square.y)
            return action
        '''

        #print_board_piece(self.game.board)
        if self.game.phase == 'placing':
            if turns == 0:
                action = (0, 2)
                self.game.update_action_in_search(action)
                self.game.eliminate_about(action)
                return action
            root = Node(None, self.game, 1, None, self.colour)
            alpha_beta = AlphaBeta(None)
            action = alpha_beta.alpha_beta_search(root)
            self.game.update_action_in_search(action)
            self.game.eliminate_about(action)
            print("Action: " + str(action))
            return action




# --------------------------------------------------------------------------- #

# HELPER CLASS FOR PLAYER

class GameBoard:
    """"Represent the state of a game of Watch Your Back!
        Modified from referee.py written by Matt Farrugia
        and Shreyash Patodia.
    """
    def __init__(self, colour):
        self.colour = colour
        self.board = [[Square(UNOCCUPIED, _, _) for _ in range(INITIAL_BOARD_SIDE)]
                      for _ in range(INITIAL_BOARD_SIDE)]
        for square in INITIAL_CORNER_LOCATION:
            x, y = square
            self.board[y][x].set_piece(CORNER)
            self.board[y][x].set_value(CORNER_VALUE)

        # tracking progress through game phases
        self.turns = 0
        self.phase = 'placing'
        self.pieces = {WHITE: 0, BLACK: 0}

        self.initialize_scoreboard(self.colour)

    def update_action(self, action):
        """
        update game board by a given action

        :param action: the opponent's recent action
        """
        if self.phase == 'placing':
            if self.turns == 24:
                self.phase = 'moving'
                self.turns = 0
            x, y = action
            self.board[y][x].piece = self.opponent()
            self.pieces[self.opponent()] += 1

        if self.phase == 'moving':
            action_from, action_to = action
            a, b = action_from
            c, d = action_to
            self.board[b][a].piece = UNOCCUPIED
            self.board[d][c].piece = self.opponent()

    def shrink_board(self):
        """
        Shrink the board, eliminating all pieces along the outermost layer,
        and replacing the corners.

        This method can be called up to two times only.
        """
        s = self.n_shrinks  # number of shrinks so far, or 's' for short
        # Remove edges
        for i in range(s, 8 - s):
            for square in [(i, s), (s, i), (i, 7 - s), (7 - s, i)]:
                x, y = square
                piece = self.board[y][x].piece
                if piece in self.pieces:
                    self.pieces[piece] -= 1
                self.board[y][x] = ' '

        # we have now shrunk the board once more!
        self.n_shrinks = s = s + 1

        # replace the corners (and perform corner elimination)
        for corner in [(s, s), (s, 7 - s), (7 - s, 7 - s), (7 - s, s)]:
            x, y = corner
            piece = self.board[y][x].piece
            if piece in self.pieces:
                self.pieces[piece] -= 1
            self.board[y][x] = 'X'
            self.eliminate_about(corner)

    def update_action_in_search(self, action):
        """
        update game board by a given action

        :param action: the self's possible action
        """
        if self.phase == 'placing':
            x, y = action
            self.board[y][x].piece = self.allies()
            self.pieces[self.allies()] += 1

        if self.phase == 'moving':
            action_from, action_to = action
            a, b = action_from
            c, d = action_to
            self.board[b][a].piece = UNOCCUPIED
            self.board[d][c].piece = self.allies()


    def opponent(self):
        """
        check opponent's piece

        :return: opponent's piece
        """
        if self.colour == 'white':
            return BLACK

        if self.colour == 'black':
            return WHITE

    def opponent_colour(self):
        """
        check opponent's piece

        :return: opponent's piece
        """
        if self.colour == 'white':
            return 'black'

        if self.colour == 'black':
            return 'white'

    def allies(self):
        """
        check allies' piece

        :return: allies' piece
        """
        if self.colour == 'white':
            return WHITE
        if self.colour == 'black':
            return BLACK

    def update_turns(self, turns):
        """
        update turn number and game phase based on given turn number

        :param turns: the number of turns that have taken place since the start of the current game phase
        """
        self.turns = turns

        # update game phase
        if self.phase == 'placing' and turns > 24:
            self.phase = 'moving'


    def initialize_scoreboard(self, colour):
        print("New initialise scoreboard for: " + colour)
        """"
        assign values for each square in game board for placing phase

        """
        for square in INITIAL_BY_CORNER_LOCATION:
            x, y = square
            self.board[y][x].set_value(BY_CORNER_VALUE)

        for y in range(INITIAL_BOARD_SIDE):
            for x in range(INITIAL_BOARD_SIDE):
                if colour == "white"  and x in [0, 2, 4, 6, 7] and y in [2, 3]:
                    """
                    3: traps on second defensive line
                    2: two corners on best defensive line
                    """
                    self.board[y][x].set_value(200)

                if colour == "black" and x in [0, 2, 4, 6, 7] and y in [5]:
                    """
                    5: two corners on best offensive line
                    3: check traps on second offensive line
                    """
                    # check traps on (0,3) and (7,3)
                    if x == 3 and self.board[y][x].is_white():
                        self.board[y][x-1].set_value(-1)
                        break
                    self.board[y][x].set_value(200)
        print_board(self.board)



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
            if coord < 0 or coord > (INITIAL_BOARD_SIDE - 1):
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
        if piece == BLACK:
            return {CORNER, WHITE}
        elif piece == WHITE:
            return {BLACK, CORNER}
        return set()

    def targets(self, piece):

        """
        Which pieces can a piece of this type eliminate?
        Modified from referee.py written by Matt Farrugia
        and Shreyash Patodia.

        :param piece: the type of piece ('B', 'W', or 'X')
        :return: the set of piece types that a piece of this type can eliminate
        """
        if piece == '@':
            return {'O'}
        elif piece == '0':
            return {'@'}
        elif piece == 'X':
            return {'O', '@'}
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

    def eliminate_about(self, square):
        """
        A piece has entered this square: look around to eliminate adjacent
        (surrounded) enemy pieces, then possibly eliminate this piece too.
        Modified from referee.py written by Matt Farrugia
        and Shreyash Patodia.

        :param square: the square to look around
        """
        x, y = square
        piece = self.board[y][x].piece
        targets = self.targets(piece)

        # Check if piece in square eliminates other pieces
        for dx, dy in [(-1, 0), (1, 0), (0, 1), (0, -1)]:
            target_x, target_y = x + dx, y + dy
            targetval = None
            if self.within_board(target_x, target_y):
                targetval = self.board[target_y][target_x].piece
            if targetval in targets:
                if self.surrounded(target_x, target_y, -dx, -dy):
                    self.board[target_y][target_x].piece = '-'
                    self.pieces[targetval] -= 1

        # Check if the current piece is surrounded and should be eliminated
        if piece in self.pieces:
            if self.surrounded(x, y, 1, 0) or self.surrounded(x, y, 0, 1):
                self.board[y][x].piece = '-'
                self.pieces[piece] -= 1

    def moves_placing(self):
        """
        :return list of possible moves in placing phase
        To do:
        """

        #print_board_piece(self.board)
        moves = []
        for x in range(INITIAL_BOARD_SIDE):
            for y in range(INITIAL_BOARD_SIDE):

                if self.colour == "white" and y <= 5 and y >= 2:
                    #print(self.colour)
                    if self.board[y][x].piece == UNOCCUPIED:
                        #print("test in moves_placing when colour == white and y <=5")
                       # print(self.board[y][x].piece)
                        #print(self.board[y][x].piece)
                        moves.append((x, y))
                if self.colour == "black" and y >= 2 and y <= 5:

                   # print("test in moves_placing when colour == black and y >=2")
                    if self.board[y][x].piece == UNOCCUPIED:
                       # print(self.board[y][x].piece)
                        moves.append((x, y))
        #print("list of possible moves: " + str(moves))
        random.shuffle(moves)
        return moves


# --------------------------------------------------------------------------- #

# HELPER CLASS FOR GAME

class Square:
    """Represent the a sprite on game board"""
    def __init__(self, piece, x, y):
        self.piece = piece
        self.value = INITIAL_VALUE
        self.x = x
        self.y = y

    def set_value(self, value):
        self.value = value

    def set_piece(self, piece):
        self.piece = piece

    def get_piece(self):
        return self.piece

    def get_value(self):
        return self.value

    def is_white(self):
        return self.piece == WHITE

    def is_black(self):
        return self.piece == BLACK

    def is_corner(self):
        return self.piece == CORNER

    def add_value(self, value):
        self.value += value

    def sub_value(self, value):
        self.value -= value


# --------------------------------------------------------------------------- #

# ALPHA BETA PRUNING

class AlphaBeta:
    def __init__(self, root):
        self.root = root

    def alpha_beta_search(self, node):
        #print("Calling alpha beta search--------------------------------------------------------------------------")
        infinity = float('inf')
        value = -infinity
        alpha = -infinity
        beta = infinity

        successors = self.create_successors(node)
        best_state = None
        for state in successors:
            #print("State in alpha_beta search:" + str(state[0]))
            board = deepcopy(node.game)
            board.update_action_in_search(state)
            board.eliminate_about(state)
            next_level = node.level + 1
            next_state = Node(0, board, next_level, state, board.colour)
            node.add_children(next_state)
            next_value = self.min_value(next_state, alpha, beta)
            if next_value > value:
                value = next_value
                best_state = state
        #print("AlphaBeta:  Utility Value of Root Node: = " + str(alpha))
        #print("AlphaBeta:  Best State is: " + best_state.name)
        return best_state


    def max_value(self, node, alpha, beta):
       # print("Calling max_value%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        #print("AlphaBeta-->MAX: Visited Node::" + node.name)
        if self.is_terminal(node):
            return self.get_utility(node)

        infinity = float('inf')
        value = -infinity

        successors = self.create_successors(node)
        for state in successors:
           # print("State in max_value:" + str(state))
            board = deepcopy(node.game)
            board.update_action_in_search(state)
            board.eliminate_about(state)
            next_level = node.level + 1
            next_state = Node(0, board, next_level, state, board.opponent_colour())
            node.add_children(next_state)
            next_value = self.min_value(next_state, alpha, beta)
            if next_value > value:
                value = next_value
            if next_value > alpha:
                alpha = next_value
            if next_value >= beta:
                return next_value
        return value

    def min_value(self, node, alpha, beta):
        #print("Calling min_value################################################################################")
        #print("AlphaBeta-->MIN: Visited Node::" + node.name)
        if self.is_terminal(node):
            return self.get_utility(node)
        infinity = float('inf')
        value = infinity

        successors = self.create_successors(node)

        for state in successors:
           # print("State in min_value:" + str(state))
            board = deepcopy(node.game)
            board.update_action_in_search(state)
            board.eliminate_about(state)
            next_level = node.level + 1
            next_state = Node(0, board, next_level, state, board.opponent_colour())
            node.add_children(next_state)
            next_value = self.max_value(next_state, alpha, beta)
            if next_value < value:
                value = next_value
            if next_value <= alpha:
                return value
            if next_value < beta:
                beta = next_value
        return value

    def get_utility(self, node):
        '''
        Calculate utility from a given game state

        :param node: the given game state
        :return: utility
        '''
        assert node is not None
        for x in range(INITIAL_BOARD_SIDE):
            for y in range(INITIAL_BOARD_SIDE):
                if node.game.board[y][x].piece == node.game.opponent():
                    node.value -= (100 + node.game.board[y][x].value) * 1.2
                    #print("Utility opponent: " + str(node.value))
                elif node.game.board[y][x].piece == node.game.allies():
                    node.value += (100 + node.game.board[y][x].value) * 1.2
                    #print("Utility allies: " + str(node.value))

        #infinity = float('inf')
        #print("The node colour is: " + node.colour)
        #if node.colour == "white":
        #    #print("Node colour is white")
        #    for x in range(INITIAL_BOARD_SIDE):
        #        for y in range(INITIAL_BOARD_SIDE):
        #            if x >= 6:
        #                #print("The y position is: " + str(y) +" and x position is: " + str(x))
        #                break
        #            else:
        #                if node.game.board[y][x] == node.game.opponent():
        #                    node.value -= (100 + node.game.board[y][x].value) * 1.2
        #                elif node.game.board[y][x] == node.game.allies():
        #                    node.value += (100 + node.game_board.board[y][x].value) * 1.2
        #if node.colour == "black":
        #    for x in range(INITIAL_BOARD_SIDE):
        #        for y in range(INITIAL_BOARD_SIDE):
        #            if x <= 2:
        #                #print("The y position is: " + str(y) + " and x position is: " + str(x))
        #                break
        #            else:
        #                if node.game.board[y][x] == node.game.opponent():
        #                    node.value -= (100 + node.game.board[y][x].value) * 1.2
        #                elif node.game.board[y][x] == node.game.allies():
        #                    node.value += (100 + node.game.board[y][x].value) * 1.2
        #print("Utility: " + str(node.value))
        return node.value

    def create_successors(self, node):
        assert node is not None
        return node.game.moves_placing()

    def is_terminal(self, node):
        assert node is not None
        return node.level == 3


# --------------------------------------------------------------------------- #

# NODE STRUCTURE FOR TREE USED IN ALPHABETA PRUNING

class Node:
    def __init__(self, value, game_board, level, move, colour):
        self.value = value
        self.children = []
        self.game = game_board
        self.level = level
        self.move = move
        self.colour = colour

    def add_children(self, node):
        assert node is not None
        self.children.append(node)
