from games.chess.board import Board
from games.chess.chess import get_draw_counter, get_en_passant_coordinates, get_coordinates

# TODO: Castling and en passant should be grabbed without FEN for future states
# Note: Print in algebraic notation?? Don't want to do this.
# Note: Could probably write a "format move function" to replace all the tuple calls,
#       in case I decide to change how to send the move back to the AI.


class State:
    def __init__(self, game, player):
        # Assert types? Have to import a bunch of weird SIG-Game code to do that.
        self._board = Board(game.fen)  # Have to change in future assignments
        self._color = player.color
        assert self._color in ["Black", "White"]
        self._en_passant_target = get_en_passant_coordinates(game.fen)
        self._fen = game.fen
        self._pieces = player.pieces
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
        xi, yi = get_coordinates(piece.rank, piece.file)
        xc, yc = xi, yi
        while 0 <= xc + dx < 8 and 0 <= yc + dy < 8:
            # This should handle IndexOutOfBounds. If stuff goes wonky add an assert or try/catch here.
            space_status = self.test_space(xc + dx, yc + dy)
            assert space_status in ["Blocked", "Open", "Capturable"]
            if space_status != "Blocked" and not self.in_check(xi, yi, xc+dx, yc+dy):
                moves.append(tuple((piece, chr(xc + dx + 96 + 1), yc + dy + 1)))
            if space_status != "Open":
                break
            xc += dx
            yc += dy

    def test_space(self, x, y):
        if 0 <= x < self._board.width and 0 <= y < self._board.height:
            if self._board[x][y] != "":
                if (self._color == "White" and self._board[x][y].islower()) or \
                        (self._color == "Black" and self._board[x][y].isupper()):
                    return "Capturable"
                else:
                    return "Blocked"
            else:
                return "Open"
        else:
            return "Out of Bounds"

    def in_check(self, xi, yi, xf, yf, move_king=False):
        king = next(p for p in self._pieces if p.type == "King")
        if move_king is False:
            kx, ky = get_coordinates(king.rank, king.file)
        else:
            kx, ky = xf, yf

        new_board = self._board.copy()

        # Move piece indicator
        marker = new_board[xi][yi]
        new_board[xi][yi] = ""
        new_board[xf][yf] = marker

        def direction_threatens_check(dx, dy):
            x = kx
            y = ky
            if dx != 0 and dy != 0:
                enemies = [self.enemy("Q"), self.enemy("B")]
            else:
                enemies = [self.enemy("Q"), self.enemy("R")]
            while 0 <= x + dx < 8 and 0 <= y + dy < 8:
                if new_board[x + dx][y + dy] != "":
                    if new_board[x + dx][y + dy] in enemies:
                        return True
                    else:
                        return False
                x += dx
                y += dy
            return False

        def space_threatens_check(x, y, piece):
            if 0 <= x < new_board.width and 0 <= y < new_board.height:
                if new_board[x][y] == self.enemy(piece):
                    return True

        # Knights encircling the king
        knight_mods = [(2, 1), (2, -1), (-1, -2), (1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2)]
        for m in knight_mods:
            dx, dy = m
            if space_threatens_check(kx + dx, ky + dy, "N"):
                return True

        # Pawns diagonal and facing king
        if self._color == "White":
            dy = 1
        elif self._color == "Black":
            dy = -1
        for dx in [-1, 1]:
            if space_threatens_check(kx + dx, ky + dy, "P"):
                return True

        # Rooks, bishop, queen, by radiating a direction
        dir_mods = [-1, 0, 1]
        for dx in dir_mods:
            for dy in dir_mods:
                if direction_threatens_check(dx, dy):
                    return True

        # Enemy king
        x_mods = [1, 0, -1]
        y_mods = [1, 0, -1]
        for dx in x_mods:
            for dy in y_mods:
                if space_threatens_check(kx + dx, ky + dy, "K"):
                    return True

        # No pieces threatening check!
        return False

    def enemy(self, piece: str):
        assert type(piece) is str
        if self._color == "White":
            return piece.lower()
        elif self._color == "Black":
            return piece.upper()

    def friendly(self, piece: str):
        """
        Used to quickly and easily refer to friendly pieces by their representative
        character (FEN) regardless of player color.
        :param piece: String (intended to be single character but not required).
        :return: Returns the given string either in fully upper-case or lower-case
                 depending on player color, to reflect Forsyth-Edwards Notation
        """
        assert type(piece) is str
        if self._color == "White":
            return piece.upper()
        elif self._color == "Black":
            return piece.lower()

    def potential_moves(self):
        """
        Cycles through all pieces and generates a list of moves that are valid given the current state of the game.
        :return: List of valid moves from current state. tuple(piece, file, rank)
        """
        valid_move_list = []

        def conditional_append(ol, el):
            """ :param ol -- original list
                :param el -- new list of elements to append
            """
            if el is not None:
                [ol.append(e) for e in el]

        assert len(self._pieces) > 0
        for p in self._pieces:
            piece_type = p.type.strip('\n')
            if piece_type == "Queen":  # DONE: Confirmed working.
                queen_moves = self.potential_queen_moves(p)
                conditional_append(valid_move_list, queen_moves)
            elif piece_type == "Pawn":
                pawn_moves = self.potential_pawn_moves(p)
                conditional_append(valid_move_list, pawn_moves)
            elif piece_type == "King":
                king_moves = self.potential_king_moves(p)
                conditional_append(valid_move_list, king_moves)
            # elif piece_type == "Knight":
            #     print("Made it into if Knight")
            #     knight_moves = self.potential_knight_moves(p)
            #     conditional_append(valid_move_list, knight_moves)
            elif piece_type == "Rook":
                rook_moves = self.potential_rook_moves(p)
                conditional_append(valid_move_list, rook_moves)
            elif piece_type == "Bishop":
                print("Made it into if Bishop")
                bishop_moves = self.potential_bishop_moves(p)
                conditional_append(valid_move_list, bishop_moves)

        assert len(valid_move_list) > 0
        return valid_move_list

    def potential_bishop_moves(self, bishop):
        """ Tests all possible moves from given bishop and returns list of valid moves """
        assert bishop.type == "Bishop"
        move_list = []
        self.add_direction(bishop, move_list, 1, 1)
        self.add_direction(bishop, move_list, -1, 1)
        self.add_direction(bishop, move_list, 1, -1)
        self.add_direction(bishop, move_list, -1, -1)
        if len(move_list) == 0:
            return None
        return move_list

    def potential_king_moves(self, king):
        """ Tests all possible moves from given king and returns list of valid moves """
        assert king.type == "King"
        x, y = get_coordinates(king.rank, king.file)
        move_list = []

        def append_space_if_valid(xf, yf):
            if self.test_space(xf, yf) in ["Open", "Capturable"] and not self.in_check(x, y, xf, yf, move_king=True):
                move_list.append(tuple((king, chr(xf + 97), yf + 1)))

        append_space_if_valid(x+1, y)  # Straight-right
        append_space_if_valid(x+1, y+1)  # Diagonal right-down
        append_space_if_valid(x+1, y-1)  # Diagonal right-up
        append_space_if_valid(x-1, y)  # Straight-left
        append_space_if_valid(x-1, y+1)  # Diagonal left-down
        append_space_if_valid(x-1, y-1)  # Diagonal left-up
        append_space_if_valid(x, y+1)  # Straight down
        append_space_if_valid(x, y-1)  # Straight up

        castle = self._fen.split(" ")[2]
        if self.friendly("K") in castle:
            # King-side castle
            if self.test_space(x+1, y) == "Open" and self.test_space(x+2, y) == "Open":
                if not self.in_check(x, y, x+1, y) and not self.in_check(x, y, x+2, y):
                    move_list.append(tuple((king, chr(x+2 + 97), y + 1)))

        if self.friendly("Q") in castle:
            # Queen-side castle
            if self.test_space(x - 1, y) == "Open" and self.test_space(x - 2, y) == "Open":
                if not self.in_check(x, y, x - 1, y) and not self.in_check(x, y, x - 2, y):
                    move_list.append(tuple((king, chr(x + 2 + 97), y + 1)))

        if len(move_list) == 0:
            return None
        return move_list

    # TODO: Still needs to be done.
    def potential_knight_moves(self, knight):
        """ Tests all possible moves from given knight and returns list of valid moves """
        assert knight.type == "Knight"
        x, y = get_coordinates(knight.rank, knight.file)
        move_list = []
        mods = [(2, 1), (2, -1), (-1, -2), (1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2)]
        for m in mods:
            dx, dy = m
            if 0 <= x+dx < self._board.width and 0 <= y+dy < self._board.height:
                if self.test_space(x+dx, y+dy) in ["Open", "Capturable"] and not self.in_check(x, y, x+dx, y+dy):
                    move_list.append(tuple((knight, chr(x+dx + 97), y+dy + 1)))
        if len(move_list) == 0:
            return None
        return move_list

    def potential_pawn_moves(self, pawn):
        """ Tests all possible moves from given pawn and returns list of valid moves """
        assert pawn.type == "Pawn"
        x, y = get_coordinates(pawn.rank, pawn.file)
        move_list = []
        if self._color == "White":
            dy = 1
        elif self._color == "Black":
            dy = -1

        def add_pawn_move(xf, yf):
            f = chr(xf + 97)
            r = yf + 1
            if (self._color == "White" and r == 8) or (self._color == "Black" and r == 1):
                promotions = ["Bishop", "Rook", "Knight", "Queen"]
                [move_list.append(tuple((pawn, f, r, p))) for p in promotions]
            else:
                move_list.append(tuple((pawn, f, r)))

        # Check immediate ahead is open
        if self.test_space(x, y+dy) == "Open" and not self.in_check(x, y, x, y+dy):
            add_pawn_move(x, y+dy)

        # Check double-forward. Both on initial row, and both spaces immediately ahead are open.
        if (pawn.rank == 2 and self._color == "White") or (pawn.rank == 7 and self._color == "Black"):
            if self.test_space(x, y+2*dy) == "Open" and self.test_space(x, y+dy) == "Open":
                if not self.in_check(x, y, x, y+2*dy):
                    add_pawn_move(x, y+2*dy)

        # Check for capturable units including en passant target
        if self.test_space(x-1, y+dy) == "Capturable":  # or (x-1, y+dy) == self._en_passant_target:
            if not self.in_check(x, y, x-1, y+dy):
                add_pawn_move(x-1, y+dy)
        if self.test_space(x+1, y+dy) == "Capturable":  # or (x+1, y+dy) == self._en_passant_target:
            if not self.in_check(x, y, x+1, y+dy):
                add_pawn_move(x+1, y+dy)

        if (x-1, y+dy) == self._en_passant_target:
            if not self.in_check(x, y, x-1, y+dy):
                add_pawn_move(x-1, y+dy)
        if (x+1, y+dy) == self._en_passant_target:
            if not self.in_check(x, y, x+1, y+dy):
                add_pawn_move(x+1, y+dy)

        if len(move_list) == 0:
            return None
        return move_list

    def potential_rook_moves(self, rook):
        """ Tests all possible moves from given rook and returns list of valid moves """
        assert rook.type == "Rook"
        move_list = []
        self.add_direction(rook, move_list, 0, 1)  # Down
        self.add_direction(rook, move_list, 0, -1)  # Up
        self.add_direction(rook, move_list, 1, 0)  # Right
        self.add_direction(rook, move_list, -1, 0)  # Left
        if len(move_list) == 0:
            return None
        return move_list

    def potential_queen_moves(self, queen):  # DONE: Confirmed working.
        """ Tests all possible moves from given queen and returns list of valid moves """
        assert queen.type == "Queen"
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
