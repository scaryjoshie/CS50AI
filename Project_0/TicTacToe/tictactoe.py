"""
Tic Tac Toe Player
"""

import math
# imports from defuault python library
from collections import Counter
from copy import deepcopy
# python imports
from util import Node, StackFrontier, EmptyFrontierException

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
    # Turns board into one long list
    raw_list = board[0] + board[1] + board[2]

    # Dict for counting
    counting_dict = {
        X: 0,
        O: 0,
        EMPTY: 0
    }

    # Counts
    for square in raw_list:
        counting_dict[square] += 1

    # Returns based on which has more
    if counting_dict[X] > counting_dict[O]:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_moves = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                possible_moves.add((i, j))
    return possible_moves



def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if action not in actions(board):
        raise ActionNotValidException
    else:
        # Gets the next piece
        next_piece = player(board)
        # Copies board
        imaginary_board = deepcopy(board)
        # Applies the next piece to the board
        imaginary_board[action[0]][action[1]] = next_piece

        #print(f"BOARD OG: {board}")
        #print(f"BOARD IMG: {imaginary_board}")

        return imaginary_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    winning_paths = [
        board[0], board[1], board[2], # horizontal
        [board[0][0],board[1][0],board[2][0]], [board[0][1],board[1][1],board[2][1]], [board[0][2],board[1][2],board[2][2]], #vertical
        [board[0][0],board[1][1],board[2][2]], [board[0][2],board[1][1],board[2][0]] # diagonal
    ]
    for path in winning_paths:
        if path == [X,X,X]:
            return X
        if path == [O,O,O]:
            return O
        
        ''' # Im proud of this but its kind of unclear so i decided to include the above code :(
        if path in [[O,O,O],[X,X,X]]:
            return path[0]
        '''
        
    return None
    


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) != None or len(actions(board)) == 0:
        return True
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    
    winning_dict = {X: 1, O: -1, None: 0,}
    return winning_dict[winner(board=board)]


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    # Returns None if baord is terminal
    if terminal(board):
        return None
    
    # initializes stack
    queue = StackFrontier()
    queue.add(node=Node(state=board, 
                           parent=None,
                           is_max_player=player(board) == X,
                           depth=0, 
                           utility=None, 
                           action=None,))
        
    counter = 0
    while True:
        counter += 1
        print(counter)

        try:
            node = queue.remove()
        except EmptyFrontierException:
            #print("Empty frontier")
            break

        if terminal(node.state):
            continue

        else:
            for action in actions(node.state):
                child = Node(state = result(board=node.state, action=action),
                                    parent = node,
                                    depth = node.depth+1,
                                    is_max_player = not node.is_max_player,
                                    utility = None,
                                    action = action)
                queue.add(child)
                node.children.append(queue.frontier[-1])


    sorted_nodes = sorted(queue.explored_nodes, key=lambda x: x.depth, reverse=True) 
    terminally_sorted_nodes = []

    while True:

        if terminal(sorted_nodes[0].state):
            sorted_nodes[0].utility = utility(sorted_nodes[0].state) * (0.99 ** sorted_nodes[0].depth)

            terminally_sorted_nodes.append(sorted_nodes[0])
            sorted_nodes.pop(0)
            continue

        children_utilites = [child.utility for child in sorted_nodes[0].children]
        #print(children_utilites)
        if all(child_utility != None for child_utility in children_utilites):

            if sorted_nodes[0].is_max_player:
                sorted_nodes[0].utility = max(children_utilites)
            else:
                sorted_nodes[0].utility = min(children_utilites)
            
            if sorted_nodes[0].depth == 0:
                depth_1_nodes = sorted_nodes[0].children
                depth_1_nodes.sort(key=lambda x: x.utility, reverse=player(board) == X)

                return depth_1_nodes[0].action
            
            terminally_sorted_nodes.append(sorted_nodes[0])
            sorted_nodes.pop(0)



class ActionNotValidException(Exception):
   pass

##########################################
if __name__ == "__main__":
    print(minimax([['X', None, None], [None, 'O', None], ['X', None, None]]))