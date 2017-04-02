# This is where you build your AI for the Chess game.

import time
from games.chess.state import State
from joueur.base_ai import BaseAI

infinity = float('inf')


class AI(BaseAI):
    """ The basic AI functions that are the same between games. """

    @staticmethod
    def get_name():
        """ This is the name you send to the server so your AI will control the
        player named this string.

        Returns
            str: The name of your Player.
        """

        return "team-john-maruska"  # REPLACE THIS WITH YOUR TEAM NAME

    def start(self):
        """ This is called once the game starts and your AI knows its playerID
        and game. You can initialize your AI here.
        """

        # replace with your start logic

    def game_updated(self):
        """ This is called every time the game's state updates, so if you are
        tracking anything you can update it here.
        """
        # replace with your game updated logic
        # Counter to keep track of 50 turn of no-conflict expiration goes here

    # noinspection PyMethodOverriding
    def end(self, won, reason):
        """ This is called when the game ends, you can clean up your data and
        dump files here if need be.

        Args:
            won (bool): True means you won, False means you lost.
            reason (str): The human readable string explaining why you won or
                          lost.
        """

        # replace with your end logic

    def run_turn(self):
        """ This is called every time it is this AI.player's turn.

        Returns:
            bool: Represents if you want to end your turn. True means end your
                  turn, False means to keep your turn going and re-call this
                  function.
        """

        # 1) print the board to the console
        self.print_current_board()

        # 2) print the opponent's last move to the console
        if len(self.game.moves) > 0:
            print("Opponent's Last Move: '" + self.game.moves[-1].san + "'")

        # 3) print how much time remaining this AI has to calculate moves
        print("Time Remaining: " + str(self.player.time_remaining) + " ns")

        # 4) Make a move
        current_state = State(self.game)
        choice, best_utility = mini_max_decision(current_state)

        if choice.promotion is not None:
            choice.piece.move(choice.file, choice.rank, choice.promotion)
        else:
            choice.piece.move(choice.file, choice.rank)

        print("Best utility: %s" % best_utility)
        print("%s %s%s" % (choice.piece.type, choice.piece.file, choice.piece.rank))
        print("\n")
        return True

    def print_current_board(self):
        """Prints the current board using pretty ASCII art
        Note: you can delete this function if you wish
        """

        # iterate through the range in reverse order
        for r in range(9, -2, -1):
            if r == 9 or r == 0:
                # then the top or bottom of the board
                output = "   +------------------------+"
            elif r == -1:
                # then show the ranks
                output = "     a  b  c  d  e  f  g  h"
            else:  # board
                output = " " + str(r) + " |"
                # fill in all the files with pieces at the current rank
                for file_offset in range(0, 8):
                    # start at a, with with file offset increasing the char
                    f = chr(ord("a") + file_offset)
                    current_piece = None
                    for piece in self.game.pieces:
                        if piece.file == f and piece.rank == r:
                            # then we found the piece at (file, rank)
                            current_piece = piece
                            break

                    code = "."  # default "no piece"
                    if current_piece:
                        # the code will be the first character of their type
                        # e.g. 'Q' for "Queen"
                        code = current_piece.type[0]

                        if current_piece.type == "Knight":
                            # 'K' is for "King", we use 'N' for "Knights"
                            code = "N"

                        if current_piece.owner.id == "1":
                            # the second player (black) is lower case.
                            # Otherwise it's uppercase already
                            code = code.lower()

                    output += " " + code + " "

                output += "|"
            print(output)
        print(self.game.fen)

states_checked = 0
start_time = 0
EXPECTED_MOVES = 75
MAX_TURN_TIME = 900 / EXPECTED_MOVES  # 15 minutes * 60 seconds / 1 minute = 900 seconds


# noinspection PyUnboundLocalVariable
def mini_max_decision(state):  # returns an action
    """ Decides what move to take by the MiniMax algorithm detailed in chapter 5 """
    global start_time
    start_time = time.time()
    player = to_move(state)
    history_table = dict()

    print("MiniMax Decision")

    def add_to_table(curr_state, action):
        try:
            history_table[(curr_state.hash, action)] += 1
        except KeyError:
            history_table[(curr_state.hash, action)] = 1

    # noinspection PyShadowingNames,PyUnboundLocalVariable
    def max_value(state, alpha, beta, depth, max_depth):  # returns a utility value
        """ Selects the maximum value for the utility of a state resulting from a move by the AI player """
        global states_checked
        # print("Max: %s" % states_checked)
        if terminal_test(state) or depth == max_depth:
            # print("Terminal test confirmed!")
            states_checked += 1
            return utility(state, player)

        v = -infinity
        best_action = actions(state)[0]
        for a in actions(state):
            if time.time() - start_time > MAX_TURN_TIME:
                break
            mv = min_value(result(state, a), alpha, beta, depth + 1, max_depth)
            if mv > v:  # Will always trigger on the first run
                v = mv
                best_action = a
            if v >= beta:
                add_to_table(state, best_action)
                return v
            alpha = max(alpha, v)
        states_checked += 1
        add_to_table(state, best_action)
        return v

    # noinspection PyShadowingNames,PyUnboundLocalVariable
    def min_value(state, alpha, beta, depth, max_depth):  # returns a utility value
        global states_checked
        # print("Min: %s" % states_checked)
        """ Selects the minimum value for the utility of a state resulting from a move by the enemy player """
        if terminal_test(state) or depth == max_depth:
            states_checked += 1
            return utility(state, player)
        v = infinity
        best_action = actions(state)[0]
        for a in actions(state):
            if time.time() - start_time > MAX_TURN_TIME:
                break
            mv = max_value(result(state, a), alpha, beta, depth + 1, max_depth)
            if mv < v:
                v = mv
                best_action = a
            if v <= alpha:
                add_to_table(state, best_action)
                return v
            beta = min(beta, v)
        states_checked += 1
        add_to_table(state, best_action)
        return v

    for m_depth in range(2):
        global states_checked
        states_checked = 0
        max_depth = m_depth + 1
        print("Max depth of %s" % max_depth)
        max_utility = -infinity
        for a in actions(state):  # Find the maximum
            if time.time() - start_time > MAX_TURN_TIME:
                break
            min_utility = min_value(result(state, a), -infinity, infinity, 0, max_depth)
            if min_utility > max_utility:  # Guaranteed to trigger on first completion of min_value
                max_utility = min_utility
                best_action = a
        last_depth_best = best_action
    print("Time used: %s" % (time.time() - start_time))
    return last_depth_best, max_utility


def actions(state):
    """"Return a list of the allowable moves at this point."""
    return state.moves


def result(state, move):
    """Return the state that results from making a move from a state."""
    if move not in state.moves:
        return state
    return state.move_result(action=move)


def terminal_test(state):
    """"Return True if this is a final state for the game."""
    return state.terminal


def to_move(state):
    """Return the player whose move it is in this state."""
    return state.to_move


def utility(state, player):
    """"Return the value of this final state to player."""
    return state.utility if player == state.to_move else -state.utility
