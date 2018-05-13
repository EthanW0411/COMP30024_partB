from copy import deepcopy
import random


# --------------------------------------------------------------------------- #

# GAME CONST


"""initial value for heuristic function"""
INITIAL_VALUE = 0
CORNER_VALUE = -2
SURROUNDED_VALUE = -1
"""Constant for game board"""

UNOCCUPIED = '-'
CORNER = 'X'
BLACK = '@'
WHITE = 'O'
INITIAL_BOARD_SIDE = 8
INITIAL_CORNER_LOCATION = [(0, 0), (7, 0), (7, 7), (0, 7)]
DIRECTIONS = UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)
INITIAL_BY_CORNER_LOCATION = [(1, 0), (0, 1), (6, 0), (7, 1), (6, 7), (7, 6), (1, 7), (0, 6)]

# --------------------------------------------------------------------------- #

def print_board(board):
    for y in range(INITIAL_BOARD_SIDE):
        for x in range(INITIAL_BOARD_SIDE):
            print('%3d ' % board[y][x].value, end='')
        print("\n")


def print_board_piece(board):

    for x in range(INITIAL_BOARD_SIDE):
        line = ""
        for y in range(INITIAL_BOARD_SIDE):
            line += board[x][y].piece + " "
        print(line)


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
        print_board_piece(self.game.board)
        self.game.eliminate_about(action)
        print("Player own game board updated: " + self.colour)
        print_board_piece(self.game.board)
        #print("Scoreboard: ")
        #print_board(self.game.board)
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
            if turns == 1:
                if self.game.board[5][7].piece == UNOCCUPIED:
                    action = (7, 5)
                    self.game.update_action_in_search(action)
                    self.game.eliminate_about(action)
                else:
                    root = Node(None, self.game, 1, None, self.colour)
                    alpha_beta = AlphaBeta(None)
                    action = alpha_beta.alpha_beta_search(root)
                    self.game.update_action_in_search(action)
                    self.game.eliminate_about(action)
                    print("Action: " + str(action))
                return action
            if turns == 2:
                if self.game.board[2][7].piece == UNOCCUPIED:
                    action = (7, 2)
                    self.game.update_action_in_search(action)
                    self.game.eliminate_about(action)
                else:
                    root = Node(None, self.game, 1, None, self.colour)
                    alpha_beta = AlphaBeta(None)
                    action = alpha_beta.alpha_beta_search(root)
                    self.game.update_action_in_search(action)
                    self.game.eliminate_about(action)
                    print("Action: " + str(action))
                return action
            if turns == 3:
                if self.game.board[5][0].piece == UNOCCUPIED:
                    action = (0, 5)
                    self.game.update_action_in_search(action)
                    self.game.eliminate_about(action)
                else:
                    root = Node(None, self.game, 1, None, self.colour)
                    alpha_beta = AlphaBeta(None)
                    action = alpha_beta.alpha_beta_search(root)
                    self.game.update_action_in_search(action)
                    self.game.eliminate_about(action)
                    print("Action: " + str(action))
                return action
            root = Node(None, self.game, 1, None, self.colour)
            alpha_beta = AlphaBeta(None)
            action = alpha_beta.alpha_beta_search(root)
            self.game.update_action_in_search(action)
            self.game.eliminate_about(action)
            print("Action: " + str(action))
            return action

        if self.game.phase == 'moving':
            root = Node(None, self.game, 1, None, self.colour)
            alpha_beta = AlphaBeta(None)
            action = alpha_beta.alpha_beta_search(root)
            self.game.update_action_in_search(action)
            self.game.eliminate_about(action)
            print("Action: " + str(action) + " by " + self.colour)
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
            self.board[y][x].piece = CORNER
            self.board[y][x].value = CORNER_VALUE

        # tracking progress through game phases
        self.turns = 0
        self.phase = 'placing'
        self.pieces = {WHITE: 0, BLACK: 0}
        self.n_shrinks = 0
        self.start_prediction = False

        self.initialize_scoreboard(self.colour)

    def update_action(self, action):
        """
        update game board by a given action

        :param action: the opponent's recent action
        """
        # self.refresh_scoreboard()
        self.check_shrink_board()

        try:
            old_x, old_y = action[0]
            x, y = action[1]
            self.board[old_y][old_x].piece = UNOCCUPIED
            self.board[y][x].piece = self.opponent()
            self.pieces[self.opponent()] += 1

        except:
            x, y = action
            self.board[y][x].piece = self.opponent()
            self.pieces[self.opponent()] += 1

        self.update_scoreboard()

    def check_shrink_board(self):
        # shrink board
        if (self.turns in [127, 191] and self.colour == 'black') or \
                (self.turns in [126, 190] and self.colour == 'white'):
            self.shrink_board()

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
                self.board[y][x].piece = ' '

        # we have now shrunk the board once more!
        self.n_shrinks = s = s + 1

        # replace the corners (and perform corner elimination)
        for corner in [(s, s), (s, 7 - s), (7 - s, 7 - s), (7 - s, s)]:
            x, y = corner
            piece = self.board[y][x].piece
            if piece in self.pieces:
                self.pieces[piece] -= 1
            self.board[y][x].piece = CORNER
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
            action_from = action[0]
            action_to = action[1]
            # print("The action from is: %s" %(action_from,))
            # print("The action to is: %s" %(action_to,))
            a, b = action_from
            c, d = action_to
            self.board[b][a].piece = UNOCCUPIED
            #print(self.board[b][a].piece)
            self.board[d][c].piece = self.allies()
            self.pieces[self.allies()] += 1
            #print(self.board[d][c].piece)
            #self.refresh_scoreboard()




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

        # update game phase
        if turns in [0, 1] and self.turns != 0 and self.phase == 'placing':
            self.phase = 'moving'
            #print(self.phase + " in " + self.colour + "---------------------------------------------")



        self.turns = turns
        #print('Turns: ' + str(self.turns) + self.colour)

    def update_scoreboard(self):
        """
        update value for each square

        """
        start = self.n_shrinks
        end = INITIAL_BOARD_SIDE - self.n_shrinks
        dirs = [(-1, 0), (1, 0), (0, 1), (0, -1)]
        #print(str(start))
        #print(str(end))
        #print("test*********************")
        for x in range(start, end):
            for y in range(start, end):
                if self.board[y][x].piece == CORNER:
                    self.board[y][x].value = CORNER_VALUE
                    for dx, dy in dirs:
                        try:
                            self.board[y + dy][x + dx].value = SURROUNDED_VALUE
                        except:
                            None
                for dx, dy in dirs:
                    if self.check_surrounded(x, y, dx, dy):
                        self.board[y][x].value = SURROUNDED_VALUE


    def initialize_scoreboard(self, colour):
        print("New initialise scoreboard for: " + colour)
        """"
        assign values for each square in game board for placing phase

        """
        #for square in INITIAL_BY_CORNER_LOCATION:
            #x, y = square
            #self.board[y][x].value = SURROUNDED_VALUE

        for y in range(INITIAL_BOARD_SIDE):
            for x in range(INITIAL_BOARD_SIDE):
                if colour == "white" and ((x in [0, 2, 4, 6, 7] and y == 2) or (x in [0, 1, 3, 5, 7] and y == 3)):
                    """
                    2: two corners on best defensive line
                    """
                    self.board[y][x].value = 200

                if colour == "black" and ((x in [0, 2, 4, 6, 7] and y == 5) or (x in [0, 1, 3, 5, 7] and y == 4)):
                    """
                    5: two corners on best offensive line
                    """
                    self.board[y][x].value = 200
        #print_board(self.board)



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
        if self.board[y][x].piece == ' ':
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
            return {WHITE, CORNER}
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
        if piece == BLACK:
            return {WHITE}
        elif piece == WHITE:
            return {BLACK}
        elif piece == CORNER:
            return {WHITE, BLACK}
        return set()

    def check_surrounded(self, x, y, dx, dy):
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
            firstval = self.board[ya][xa].piece

        xb, yb = x - dx, y - dy
        secondval = None
        if self.within_board(xb, yb):
            secondval = self.board[yb][xb].piece

        # If both adjacent squares have enemies then this piece is surrounded!
        piece = self.allies()
        enemies = self.enemies(piece)
        return (firstval in enemies and secondval in enemies)

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
            firstval = self.board[ya][xa].piece

        xb, yb = x - dx, y - dy
        secondval = None
        if self.within_board(xb, yb):
            secondval = self.board[yb][xb].piece

        # If both adjacent squares have enemies then this piece is surrounded!
        piece = self.board[y][x].piece
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
        try:
            x,y = square[1]
        except:
            x,y = square

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
                    #print(self.board[target_y][target_x].piece + " at " + "(%d, %d)" % (target_y, target_x))
                    self.board[target_y][target_x].piece = UNOCCUPIED
                    self.pieces[targetval] -= 1

        # Check if the current piece is surrounded and should be eliminated
        if piece in self.pieces:
            if self.surrounded(x, y, 1, 0) or self.surrounded(x, y, 0, 1):
                #print(self.board[y][x].piece + " at " + "(%d, %d)" % (y, x))
                self.board[y][x].piece = UNOCCUPIED
                self.pieces[piece] -= 1

    def moves_placing(self):
        """
        :return list of possible moves in placing phase
        To do:
        """

        moves = []
        #print_board_piece(self.board)
        if self.phase == 'placing':
            for x in range(INITIAL_BOARD_SIDE):
                for y in range(INITIAL_BOARD_SIDE):
                    if self.colour == "white" and 2<= y <= 5:
                        # print(self.colour)
                        if self.board[y][x].piece == UNOCCUPIED:
                            # print("test in moves_placing when colour == white and y <=5")
                            # print(self.board[y][x].piece)
                            # print(self.board[y][x].piece)
                            moves.append((x, y))
                    if self.colour == "black" and 2<= y <= 5:
                        # print("test in moves_placing when colour == black and y >=2")
                        if self.board[y][x].piece == UNOCCUPIED:
                            # print(self.board[y][x].piece)
                            moves.append((x, y))
            # print("list of possible moves: " + str(moves))
            random.shuffle(moves)
            return moves

        if self.phase == 'moving':
            #print("The move has been called in the moves_placing function")
            # check current board size
            start = self.n_shrinks
            end = INITIAL_BOARD_SIDE - self.n_shrinks

            # possible move and jump space
            possible_moves = [(-1, 0), (1, 0), (0, 1), (0, -1)]
            for x in range(start, end):
                for y in range(start, end):
                    if self.colour == 'white' and self.board[y][x].piece == WHITE:
                        for dx, dy in possible_moves:
                            move_to_x, move_to_y = x + dx, y + dy
                            if self.within_board(move_to_x, move_to_y):
                                if self.board[move_to_y][move_to_x].piece == UNOCCUPIED \
                                        and self.board[move_to_y][move_to_x].value >= 0:
                                    #print("add a possible move in white")
                                    moves.append(((x, y), (move_to_x, move_to_y)))
                                if self.board[move_to_y][move_to_x].piece in self.pieces:
                                    #print("check jump in white")
                                    # check jump
                                    move_to_x, move_to_y = move_to_x + dx, move_to_y + dy
                                    #print(str(((x, y), (move_to_x, move_to_y))))
                                    if self.within_board(move_to_x, move_to_y) \
                                        and self.board[move_to_y][move_to_x].piece == UNOCCUPIED\
                                            and self.board[move_to_y][move_to_x].value >= 0:
                                        #print("add a possible jump in white")
                                        moves.append(((x, y), (move_to_x, move_to_y)))

                    if self.colour == 'black' and self.board[y][x].piece == BLACK:
                        for dx, dy in possible_moves:
                            move_to_x, move_to_y = x + dx, y + dy
                            if self.within_board(move_to_x, move_to_y):
                                if self.board[move_to_y][move_to_x].piece == UNOCCUPIED \
                                        and self.board[move_to_y][move_to_x].value >= 0:
                                    #print("add a possible move in black")
                                    moves.append(((x, y), (move_to_x, move_to_y)))
                                if self.board[move_to_y][move_to_x].piece in self.pieces:
                                    # check jump
                                    move_to_x, move_to_y = move_to_x + dx, move_to_y + dy
                                    if self.within_board(move_to_x, move_to_y) \
                                        and self.board[move_to_y][move_to_x].piece == UNOCCUPIED \
                                            and self.board[move_to_y][move_to_x].value >= 0:
                                        #print("add a possible jump in black")
                                        moves.append(((x, y), (move_to_x, move_to_y)))
            # no possible moves
            if not moves:
                for x in range(start, end):
                    for y in range(start, end):
                        if self.colour == 'white' and self.board[y][x].piece == WHITE:
                            for dx, dy in possible_moves:
                                move_to_x, move_to_y = x + dx, y + dy
                                if self.within_board(move_to_x, move_to_y):
                                    if self.board[move_to_y][move_to_x].piece == UNOCCUPIED:
                                        #print("add a possible move in white")
                                        moves.append(((x, y), (move_to_x, move_to_y)))
                                    if self.board[move_to_y][move_to_x].piece in self.pieces:
                                        #print("check jump in white")
                                        # check jump
                                        move_to_x, move_to_y = move_to_x + dx, move_to_y + dy
                                        #print(str(((x, y), (move_to_x, move_to_y))))
                                        if self.within_board(move_to_x, move_to_y) \
                                            and self.board[move_to_y][move_to_x].piece == UNOCCUPIED:
                                            #print("add a possible jump in white")
                                            moves.append(((x, y), (move_to_x, move_to_y)))

                        if self.colour == 'black' and self.board[y][x].piece == BLACK:
                            for dx, dy in possible_moves:
                                move_to_x, move_to_y = x + dx, y + dy
                                if self.within_board(move_to_x, move_to_y):
                                    if self.board[move_to_y][move_to_x].piece == UNOCCUPIED:
                                        #print("add a possible move in black")
                                        moves.append(((x, y), (move_to_x, move_to_y)))
                                    if self.board[move_to_y][move_to_x].piece in self.pieces:
                                        # check jump
                                        move_to_x, move_to_y = move_to_x + dx, move_to_y + dy
                                        if self.within_board(move_to_x, move_to_y) \
                                            and self.board[move_to_y][move_to_x].piece == UNOCCUPIED:
                                            #print("add a possible jump in black")
                                            moves.append(((x, y), (move_to_x, move_to_y)))


            #print(str(moves))
            random.shuffle(moves)
            return moves

    def refresh_scoreboard(self, node_level=None):
        """
        This scoreboard incentivize the AI to have a more defensive approach in playing the game

        :return: Does not return anything, just updates scoreboard
        """
        if self.start_prediction:
            if self.colour == 'white':
                if (119 < self.turns + node_level) < 126 or (182 < self.turns + node_level < 190):
                    start = self.n_shrinks
                    end = INITIAL_BOARD_SIDE - self.n_shrinks
                    s = self.n_shrinks
                    for i in range(s, 8 - s):
                        for square in [(i, s), (s, i), (i, 7 - s), (7 - s, i)]:
                            x, y = square
                            if self.board[y][x].piece == WHITE:
                                possible_moves = [(-1, 0), (1, 0), (0, 1), (0, -1)]
                                for dx, dy in possible_moves:
                                    if self.within_board(x + dx, y + dy) and self.board[y+dy][x+dx].piece == UNOCCUPIED:
                                        self.board[y+dy][x+dx].value = 500
                                    elif self.within_board(x + dx, y + dy) and \
                                            (self.board[y+dy][x+dx].piece == WHITE
                                             or self.board[y+dy][x+dx].piece == BLACK):
                                        if self.within_board(x + (2*dx), y + (2*dy)) and \
                                                self.board[y+(2*dy)][x+(2*dx)].piece == UNOCCUPIED:
                                            self.board[y+(2*dy)][x+(2*dx)] = 500
            if self.colour == 'black':
                if (120 < self.turns + node_level) < 127 or (183 < self.turns + node_level < 191):
                    start = self.n_shrinks
                    end = INITIAL_BOARD_SIDE - self.n_shrinks
                    s = self.n_shrinks
                    for i in range(s, 8 - s):
                        for square in [(i, s), (s, i), (i, 7 - s), (7 - s, i)]:
                            x, y = square
                            if self.board[y][x].piece == BLACK:
                                possible_moves = [(-1, 0), (1, 0), (0, 1), (0, -1)]
                                for dx, dy in possible_moves:
                                    if self.within_board(x + dx, y + dy) and self.board[y+dy][x+dx].piece == UNOCCUPIED:
                                        self.board[y+dy][x+dx].value = 500
                                    elif self.within_board(x + dx, y + dy) and \
                                            (self.board[y+dy][x+dx].piece == WHITE
                                             or self.board[y+dy][x+dx].piece == BLACK):
                                        if self.within_board(x + (2*dx), y + (2*dy)) and \
                                                self.board[y+(2*dy)][x+(2*dx)].piece == UNOCCUPIED:
                                            self.board[y+(2*dy)][x+(2*dx)] = 500
            for square in [(i, s), (s, i), (i, 7 - s), (7 - s, i)]:
                x, y = square
                self.board[y][x].value = -100

        else:
            refresh_board_no_predict_shrink(self)


def refresh_board_no_predict_shrink(self):
    start = self.n_shrinks
    end = INITIAL_BOARD_SIDE - self.n_shrinks
    possible_moves = [(-1, 0), (1, 0), (0, 1), (0, -1)]
    for x in range(start, end):
        for y in range(start, end):
            # This looks at the scoreboard when the player is white
            if self.colour == 'white':
                # Defensive behaviour
                if self.board[y][x].piece == WHITE:
                    for dx, dy in possible_moves:
                        if self.within_board(x + dx, y + dy):
                            if self.board[y + dy][x + dx].piece == BLACK:
                                if self.within_board(x + (-1 * dx), y + (-1 * dy)):
                                    if self.board[y + (-1 * dy)][x + (-1 * dx)].piece == UNOCCUPIED:
                                        self.board[y + (-1 * dy)][x + (-1 * dx)].value = 300
                                    if self.board[y + (-1 * dy)][x + (-1 * dx)].piece == WHITE:
                                        self.board[y + (-1 * dy)][x + (-1 * dx)].value = 400
                # Aggressive behaviour
                if self.board[y][x].piece == BLACK:
                    for dx, dy in possible_moves:
                        if self.within_board(x + dx, y + dy):
                            if self.board[y + dy][x + dx].piece == UNOCCUPIED:
                                if self.within_board(x + (-1 * dx), y + (-1 * dy)):
                                    if self.board[y + (-1 * dy)][x + (-1 * dx)].piece == WHITE or \
                                            self.board[y + (-1 * dy)][x + (-1 * dx)].piece == CORNER:
                                        self.board[y + dy][x + dx].value = 150
                                    if self.board[y + (-1 * dy)][x + (-1 * dx)].piece == UNOCCUPIED:
                                        self.board[y + dy][x + dx].value = 50
                                        self.board[y + (-1 * dy)][x + (-1 * dx)].value = 50

            # This looks at the scoreboard when the player is black
            if self.colour == 'black':
                # Defensive behaviour
                if self.board[y][x].piece == BLACK:
                    for dx, dy in possible_moves:
                        if self.within_board(x + dx, y + dy):
                            if self.board[y + dy][x + dx].piece == WHITE:
                                if self.within_board(x + (-1 * dx), y + (-1 * dy)):
                                    if self.board[y + (-1 * dy)][x + (-1 * dx)].piece == UNOCCUPIED:
                                        self.board[y + (-1 * dy)][x + (-1 * dx)].value = 300
                                    if self.board[y + (-1 * dy)][x + (-1 * dx)].piece == BLACK:
                                        self.board[y + (-1 * dy)][x + (-1 * dx)].value = 400
                # Aggressive behaviour
                if self.board[y][x].piece == WHITE:
                    for dx, dy in possible_moves:
                        if self.within_board(x + dx, y + dy):
                            if self.board[y + dy][x + dx].piece == UNOCCUPIED:
                                if self.within_board(x + (-1 * dx), y + (-1 * dy)):
                                    if self.board[y + (-1 * dy)][x + (-1 * dx)].piece == BLACK or \
                                            self.board[y + (-1 * dy)][x + (-1 * dx)].piece == CORNER:
                                        self.board[y + dy][x + dx].value = 150
                                    if self.board[y + (-1 * dy)][x + (-1 * dx)].piece == UNOCCUPIED:
                                        self.board[y + dy][x + dx].value = 50
                                        self.board[y + (-1 * dy)][x + (-1 * dx)].value = 50







# --------------------------------------------------------------------------- #

# HELPER CLASS FOR GAME

class Square:
    """Represent the a sprite on game board"""
    def __init__(self, piece, x, y):
        self.piece = piece
        self.value = INITIAL_VALUE
        self.x = x
        self.y = y

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
            board.check_shrink_board()
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
            board.check_shrink_board()
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


        return node.value

    def create_successors(self, node):
        assert node is not None
        return node.game.moves_placing()

    def is_terminal(self, node):
        assert node is not None
        depth = 3
        if node.game.turns > 128:
            depth += 1
        elif node.game.turns > 192:
            depth += 2
        return node.level == depth

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
