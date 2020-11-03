"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy
from operator import itemgetter

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """

    # Count all the precious EMPTY fields and return the player
    empty_fields_count = 0

    for row in board:
        empty_fields_count += row.count(EMPTY)

    if empty_fields_count % 2 == 0:
        return O
    elif empty_fields_count % 1 == 0:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """

    possible_actions = set()

    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                possible_actions.add((i, j))

    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    # Raise IndexError if action is invalid
    if board[action[0]][action[1]] != EMPTY:
        raise IndexError

    # Check which player is to move
    player_to_move = player(board)

    # Make a deepcopy of the board to not modify it
    copy_of_board = deepcopy(board)

    # Let the current player make its move according to action
    copy_of_board[action[0]][action[1]] = player_to_move

    # Return the modified board
    return copy_of_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    # Create a turned by 90 degrees board
    turned_row = []
    turned_board = []

    for i in range(3):
        for j in range(2, -1, -1):
            turned_row.append(board[j][i])
        turned_board.append(turned_row)
        turned_row = []

    # Check all horizontal rows
    for row in board:
        x_count = row.count(X)
        o_count = row.count(O)
        if x_count == 3:
            return X
        elif o_count == 3:
            return O

    # Check all vertical rows
    for row in turned_board:
        x_count = row.count(X)
        o_count = row.count(O)
        if x_count == 3:
            return X
        elif o_count == 3:
            return O

    x_count = 0
    o_count = 0
    turned_x_count = 0
    turned_o_count = 0

    # Check all diagonal rows
    for i in range(3):

        # Check the diagonal on the normal board
        if board[i][i] == X:
            x_count += 1
        elif board[i][i] == O:
            o_count += 1
        if x_count == 3:
            return X
        elif o_count == 3:
            return O

        # Check the diagonal on the turned board
        if turned_board[i][i] == X:
            turned_x_count += 1
        elif turned_board[i][i] == O:
            turned_o_count += 1
        if turned_x_count == 3:
            return X
        elif turned_o_count == 3:
            return O

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    # Return True if there is a winner
    if winner(board) is not None:
        return True

    # Return False if there is an EMPTY field
    for row in board:
        if row.count(EMPTY) != 0:
            return False

    # Return True if all fields are filled but there is no winner
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    player_winner = winner(board)

    if player_winner == X:
        return 1
    elif player_winner == O:
        return -1
    elif player_winner is None:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    optimal_move = tuple()
    utilities = set()
    player_to_move = player(board)

    for action in actions(board):
        if player_to_move == X:
            v = -math.inf
            v = max(v, min_value(result(board, action)))
            utilities.add((v, action))
            optimal_move = max(utilities, key=itemgetter(0))[1]
        elif player_to_move == O:
            v = math.inf
            v = min(v, max_value(result(board, action)))
            utilities.add((v, action))
            optimal_move = min(utilities, key=itemgetter(0))[1]

    return optimal_move


def max_value(board):

    if terminal(board):
        return utility(board)

    v = -math.inf

    for action in actions(board):
        v = max(v, min_value(result(board, action)))

    return v


def min_value(board):

    if terminal(board):
        return utility(board)

    v = math.inf

    for action in actions(board):
        v = min(v, max_value(result(board, action)))

    return v
