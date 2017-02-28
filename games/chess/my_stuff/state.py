from my_stuff.board import Board
from my_stuff.chess import get_draw_counter, get_en_passant_coordinates

# TODO: King -- castling
#   TODO: en passant
# TODO: Knight
# TODO: 'check' avoidance function
# Note: Print in algebraic notation?? Don't want to do this.


class State:
    def __init__(self, game, player):
        # Assert types? Have to import a bunch of weird SIG-Game code to do that.
        self._board = Board(game.fen)  # Have to change in future assignments
        self._color = player.color()
        assert self._color in ["Black", "White"]
        self._en_passant_target = get_en_passant_coordinates(game.fen)
        self._fen = game.fen
        self._pieces = player.pieces()
        self._turns_to_draw = get_draw_counter(game.fen)

    def add_direction(self, piece, moves, dx, dy):
        """ Used to generate legal moves for a given piece, in a single given direction.
            Meant to be called for each diagonal on the Bishop and Queen, and for each direct path for Rook and Queen.

            :param piece -- the piece whose moves are to be tested
            :param moves -- the list of moves to which to be appended
            :param dx -- step unit for the x coordinate of the board
            :param dy -- step unit for the y coordinate of the board

            Note: dx and dy adhere to the computer representation of the board (origin 0,0 top left) and not
                  the standard representation of a chess board (origin 1-A in the bottom left)

                  WHITE IS STILL ON LOW RANKS. BLACK IS STILL ON HIGH RANKS.

            """
        y = piece.rank - 1  # Account for list index offset
        x = ord(piece.file) - 97  # 97 for ASCII offset
        while 0 <= x + dx < 8 and 0 <= y + dy < 8 and self._board[x + dx][y + dy] is "":
            # This should handle IndexOutOfBounds. If stuff goes wonky add an assert or try/catch here.
            space_status = self.test_space(x + dx, y + dy)
            assert space_status in ["Blocked", "Open", "Capturable"]
            # TODO: Conditional to prevent move in the event of 'check'
            if space_status is not "Blocked":
                moves.append("%s %s %s" % (piece.id, chr(x + dx + 96 + 1), y + dy + 1))
            if space_status is not "Open":
                break

    def test_space(self, x, y):
        if 0 <= x < self._board.width and 0 <= y < self._board.height:
            if self._board[x][y] is not "":
                if (self._color is "White" and self._board[x][y].islower()) or \
                        (self._color is "Black" and self._board[x][y].isupper()):
                    return "Capturable"
                else:
                    return "Blocked"
            else:
                return "Open"
        else:
            return "Out of Bounds"

    def potential_moves(self):
        """ Cycles through all pieces and generates a list of moves that are valid
            given the current state of the game.

            Returns: List of valid moves from current state
            Return type: list
        """
        # Cycle through _pieces
        # Check each potential move
        valid_move_list = []

        def conditional_append(ol, el):
            """ :param ol -- original list
                :param el -- new list of elements to append
            """
            if el is not None:
                [ol.append(e) for e in el]

        for p in self._pieces:
            if p.type() is "King":
                king_moves = self.potential_king_moves(p)
                conditional_append(valid_move_list, king_moves)
            elif p.type() is "Queen":
                queen_moves = self.potential_queen_moves(p)
                conditional_append(valid_move_list, queen_moves)
            elif p.type() is "Knight":
                knight_moves = self.potential_knight_moves(p)
                conditional_append(valid_move_list, knight_moves)
            elif p.type() is "Rook":
                rook_moves = self.potential_rook_moves(p)
                conditional_append(valid_move_list, rook_moves)
            elif p.type() is "Bishop":
                bishop_moves = self.potential_bishop_moves(p)
                conditional_append(valid_move_list, bishop_moves)
            elif p.type() is "Pawn":
                pawn_moves = self.potential_pawn_moves(p)
                conditional_append(valid_move_list, pawn_moves)
        return valid_move_list

    def potential_bishop_moves(self, bishop):
        """ Tests all possible moves from given bishop and returns list of valid moves """
        assert bishop.type() is "Bishop"
        move_list = []
        self.add_direction(bishop, move_list, 1, 1)
        self.add_direction(bishop, move_list, -1, 1)
        self.add_direction(bishop, move_list, 1, -1)
        self.add_direction(bishop, move_list, -1, -1)
        if len(move_list) is 0:
            return None
        return move_list

    def potential_king_moves(self, king):
        """ Tests all possible moves from given king and returns list of valid moves """
        assert king.type() is "King"
        y = king.rank - 1  # Account for list index offset
        x = ord(king.file) - 97  # ASCII value of 'a' is 97
        move_list = []

        def append_space_if_valid(x_file, y_rank):
            # TODO: Add conditional for 'check'
            if self.test_space(x_file, y_rank) in ["Open", "Capturable"]:
                # Test for "check"
                move_list.append("%s %s %s" % (king.id, chr(x_file + 97), y_rank + 1))

        append_space_if_valid(x+1, y)  # Straight-right
        append_space_if_valid(x+1, y+1)  # Diagonal right-down
        append_space_if_valid(x+1, y-1)  # Diagonal right-up
        append_space_if_valid(x-1, y)  # Straight-left
        append_space_if_valid(x-1, y+1)  # Diagonal left-down
        append_space_if_valid(x-1, y-1)  # Diagonal left-up
        append_space_if_valid(x, y+1)  # Straight down
        append_space_if_valid(x, y-1)  # Straight up
        # TODO: DON'T FORGET CASTLING
        if len(move_list) is 0:
            return None
        return move_list

    def potential_knight_moves(self, knight):
        """ Tests all possible moves from given knight and returns list of valid moves """
        assert knight.type() is "Knight"
        y = knight.rank - 1  # Account for list index offset
        x = ord(knight.file) - 97  # 96 for ASCII offset, 1 for index
        move_list = []
        mods = [(2, 1), (2, -1), (-1, -2), (1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2)]
        for m in mods:
            dx, dy = m
            if 0 <= x+dx < self._board.width and 0 <= y+dy < self._board.height:
                if self.test_space(x+dx, y+dy) in ["Open", "Capturable"]:
                    # TODO: if not in check
                    move_list.append("%s %s %s" % (knight.id, chr(x+dx + 97), y+dy + 1))
        if len(move_list) is 0:
            return None
        return move_list

    def potential_pawn_moves(self, pawn):
        """ Tests all possible moves from given pawn and returns list of valid moves """
        assert pawn.type() is "Pawn"
        y = pawn.rank() - 1  # Account for list index offset
        x = ord(pawn.file) - 97  # 96 for ASCII offset, 1 for index
        move_list = []
        if self._color is "White":
            dy = 1
        elif self._color is "Black":
            dy = -1

        # TODO: Add conditional for 'check'
        # Check immediate ahead is open
        if self.test_space(x, y+dy) is "Open":
            move_list.append("%s %s %s" % (pawn.id, chr(x + 97), y+dy + 1))

        # Check double-forward. Both on initial row, and both spaces immediately ahead are open.
        if (pawn.rank() is 2 and self._color is "White") or (pawn.rank() is 7 and self._color is "Black") and \
                self.test_space(x, y+2*dy) is "Open" and self.test_space(x, y+dy) is "Open":
            move_list.append("%s %s %s" % (pawn.id, chr(x + 97), y+2*dy + 1))

        # Check for capturable units.
        if self.test_space(x-1, y+dy) is "Capturable":
            move_list.append("%s %s %s" % (pawn.id, chr(x-1 + 97), y+dy + 1))
        if self.test_space(x+1, y+dy) is "Capturable":
            move_list.append("%s %s %s" % (pawn.id, chr(x+1 + 97), y+dy + 1))

        # Check for en passant capture
        if (x+1, y+dy) == self._en_passant_target:
            move_list.append("%s %s %s" % (pawn.id, chr(x+1 + 97), y+dy + 1))
        elif (x-1, y+dy) == self._en_passant_target:
            move_list.append("%s %s %s" % (pawn.id, chr(x+1 + 97), y+dy + 1))
        if len(move_list) is 0:
            return None
        return move_list

    def potential_rook_moves(self, rook):
        """ Tests all possible moves from given rook and returns list of valid moves """
        assert rook.type() is "Rook"
        move_list = []
        self.add_direction(rook, move_list, 0, 1)  # Down
        self.add_direction(rook, move_list, 0, -1)  # Up
        self.add_direction(rook, move_list, 1, 0)  # Right
        self.add_direction(rook, move_list, -1, 0)  # Left
        if len(move_list) is 0:
            return None
        return move_list

    def potential_queen_moves(self, queen):
        """ Tests all possible moves from given queen and returns list of valid moves """
        assert queen.type() is "Queen"
        move_list = []
        self.add_direction(queen, move_list, 1, 1)  # Down-right diagonal
        self.add_direction(queen, move_list, -1, 1)  # Down-left diagonal
        self.add_direction(queen, move_list, 1, -1)  # Up-right diagonal
        self.add_direction(queen, move_list, -1, -1)  # Up-left diagonal
        self.add_direction(queen, move_list, 0, 1)  # Straight down
        self.add_direction(queen, move_list, 0, -1)  # Straight up
        self.add_direction(queen, move_list, 1, 0)  # Straight right
        self.add_direction(queen, move_list, -1, 0)  # Straight left

        return move_list
