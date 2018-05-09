class Alphabeta:

    def __init__(self, root, turns):
        self.root = root
        self.turns = turns

    def alpha_beta_search(self, node):
        infinity = float('inf')
        alpha = -infinity
        beta = infinity

        # successors = empty(tp_to_board(node.board), opposite(node.colour))
        # if self.turns < 24:
        successors = surround_empty(tp_to_board(node.board, self.turns), opposite(node.colour))

        # print(successors)
        best_state = None
        for spaces in successors:
            # add peice to board
            # tp to board, board to tp, create child node
            board = tp_to_board(node.board, self.turns)
            colour = opposite(node.colour)
            board = update_board(board, spaces, colour)
            eliminate(board, colour)
            board = board_to_tp(board)

            state = Tree(None, board, colour, 1, spaces)
            node.add_child(state)
            value = self.min_value(state, alpha, beta)
            if value > alpha:
                alpha = value
                best_state = state
        return best_state


    def max_value(self, node, alpha, beta):
        if self.isTerminal(node):
            return self.getValue(node)
        infinity = float('inf')
        value = -infinity

        # successor = self.createSuccessors(node)
        # if self.turns < 24:
        successor = surround_empty(tp_to_board(node.board, self.turns), opposite(node.colour))
        for spaces in successor:
            #add_to_board(node.self.board, )
            board = tp_to_board(node.board, self.turns)
            colour = opposite(node.colour)
            board = update_board(board, spaces, colour)
            eliminate(board, colour)
            board = board_to_tp(board)
            level = node.level
            level += 1
            state = Tree(None, board, colour, level, spaces)
            node.add_child(state)

            value = max(value, self.min_value(state, alpha, beta))
            if value >= beta:
                return valu