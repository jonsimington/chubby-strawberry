# This is where you build your AI for the Chess game.

from games.chess.state import State
from joueur.base_ai import BaseAI
import random

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

        # Here is where you'll want to code your AI.

        # We've provided sample code that:
        #    1) prints the board to the console
        #    2) prints the opponent's last move to the console
        #    3) prints how much time remaining this AI has to calculate moves
        #    4) makes a random (and probably invalid) move.

        # 1) print the board to the console
        self.print_current_board()

        # 2) print the opponent's last move to the console
        if len(self.game.moves) > 0:
            print("Opponent's Last Move: '" + self.game.moves[-1].san + "'")

        # 3) print how much time remaining this AI has to calculate moves
        print("Time Remaining: " + str(self.player.time_remaining) + " ns")

        # 4) Make a random valid move
        current_state = State(self.game)
        valid_moves = current_state.moves
        # [print("%s to %s %s " % (x[0].type, x[2], x[1])) for x in valid_moves]
        choice = random.choice(valid_moves)
        if choice.promotion is not None:
            [print("%s to %s %s" % (x.piece.type, x.file, x.rank)) for x in valid_moves if x[0].id == choice.piece.id]
            choice.piece.move(choice.file, choice.rank)
        else:
            [print("%s to %s %s" % (x.piece.type, x.file, x.rank)) for x in valid_moves if x[0].id == choice.piece.id]
            choice.piece.move(choice.file, choice.rank, choice.promotion)
        print("\n")
        return True  # to signify we are done with our turn.

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


# noinspection PyUnboundLocalVariable
def mini_max_decision(state):  # returns an action
    """ Decides what move to take by the MiniMax algorithm detailed in chapter 5 """

    player = to_move(state)

    # noinspection PyShadowingNames
    def max_value(state, depth, max_depth):  # returns a utility value
        """ Selects the maximum value for the utility of a state resulting from a move by the AI player """
        if terminal_test(state) or depth == max_depth:
            return utility(state, player)
        v = -infinity
        for a in actions(state):
            v = max(v, min_value(result(state, a), depth + 1, max_depth))
        return v

    # noinspection PyShadowingNames
    def min_value(state, depth, max_depth):  # returns a utility value
        """ Selects the minimum value for the utility of a state resulting from a move by the enemy player """
        if terminal_test(state) or depth == max_depth:
            return utility(state, player)
        v = infinity
        for a in actions(state):
            v = min(v, max_value(result(state, a), depth + 1, max_depth))
        return v

    for max_depth in range(3):  # TODO: Figure out best depth
        max_utility = -infinity
        for a in actions(state):
            min_utility = min_value(result(state, a), depth=0, max_depth=max_depth)
            if min_utility > max_utility:  # Guaranteed to trigger on first completion of min_value
                max_utility = min_utility
                best_action = a
        last_depth_best = best_action
    return last_depth_best


def actions(state):
    """"Return a list of the allowable moves at this point."""
    return state.moves


def result(state, move):
    """Return the state that results from making a move from a state."""
    if move not in state.moves:
        return state
    return State(state.game, parent=state, action=move)


def terminal_test(state):
    """"Return True if this is a final state for the game."""
    return state.terminal


def to_move(state):
    """Return the player whose move it is in this state."""
    return state.to_move


def utility(state, player):
    """"Return the value of this final state to player."""
    return state.utility if player == state.to_move else -state.utility
