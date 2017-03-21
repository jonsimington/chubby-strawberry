from collections import namedtuple
from games.chess.board import Board
from games.chess.chess import *

Move = namedtuple("Move", "piece, file, rank, promotion, capture")
Move.__new__.__defaults__ = (False, None)


# noinspection PyShadowingNames,PyProtectedMember
class State:
    def __init__(self, game, parent=None, action=None):
        """ :param action - tuple of the form (piece, rank, file) with optional fourth term `promotion`
            :param parent - parent state on which to apply action
            :param action - action to be applied to parent state
        """

        if parent is None and action is None:  # Initialize from game FEN
            self._board = Board(game.fen)  # Have to change in future assignments
            self._color = game.current_player.color
            assert self._color in ["Black", "White"]
            self._fen = game.fen
            self._en_passant_target = get_en_passant_coordinates(game.fen)
            for p in game.players:
                if self._color == p.color:
                    self._friendly_pieces = [MyPiece(x.owner.color, x.type, x.file, x.rank, x.has_moved, pid=x.id) for x in p.pieces]
                else:
                    self._enemy_pieces = [MyPiece(x.owner.color, x.type, x.file, x.rank, x.has_moved, pid=x.id) for x in p.pieces]
            self._turns_to_draw = get_draw_counter(game.fen)
            self._castle = list(game.fen.split(" ")[2])

        else:  # Initialize from acting upon a parent
            assert parent is not None and action is not None
            self._board = parent.board.copy()
            self._board.move_piece_rf(action.piece.rank, action.piece.file, action.rank, action.file)
            self._color = "White" if parent.to_move == "Black" else "Black"

            # Check for en passant target
            if action.piece.type == "Pawn" and (action.rank - action.piece.rank == 2 or
                                                action.rank - action.piece.rank == -2):
                r = int((action.piece.rank + action.rank) / 2)
                self._en_passant_target = get_coordinates(r, action[0].file)
            else:
                self._en_passant_target = None

            self._friendly_pieces = []  # Modify the piece that was moved'
            self._enemy_pieces = []

            for p in parent._friendly_pieces:
                c = p.copy()
                if c.id == action.piece.id:
                    c.has_moved = True
                    c.file = action.file
                    c.rank = action.rank
                self._enemy_pieces.append(c)  # Parent friendly pieces become enemy pieces
            self._friendly_pieces = [p for p in parent._enemy_pieces]  # Parent enemies are current friendlies

            # Captures can only occur on players that are currently friendly (assuming two-player Chess)
            if action.piece.type == "Pawn" or len(self._friendly_pieces) != len(parent._friendly_pieces):
                self._turns_to_draw = 50
            else:
                self._turns_to_draw = parent._turns_to_draw - 1

            self._castle = parent._castle  # Keep track of castling
            if self._castle:
                if (action[0].type == "Rook" and action[0].file == 'a') or action[0].type == "King":
                    try:
                        self._castle.remove('q' if action[0].color == "White" else 'Q')
                    except ValueError:  # Will trigger if the move was not in the list to begin with
                        pass
                if (action[0].type == "Rook" and action[0].file == 'h') or action[0].type == "King":
                    try:
                        self._castle.remove('k' if action[0].color == "White" else 'K')
                    except ValueError:  # Will trigger if the move was not in the list to begin with
                        pass

        self._moves = self.__potential_moves()
        self._game = game
        self._utility = self.__find_utility()

    # ----------------- PROPERTIES -----------------

    @property
    def board(self):
        return self._board

    @property
    def game(self):
        return self._game

    @property
    def moves(self):
        return self._moves

    @property
    def terminal(self):
        return self.__test_draw() or self.__in_checkmate()

    @property
    def to_move(self):
        return self._color

    @property
    def utility(self):
        return self._utility

    # -------------- PUBLIC FUNCTIONS --------------

    def move_result(self, action):
        """ move_result creates a copy of the current state, applies the given action, and returns the result state """
        return State(self._game, parent=self, action=action)

    # ----------------- IMPLEMENT ------------------
    def __find_utility(self):
        utility = 0
        for f in self._friendly_pieces:
            utility += f.evaluate()
        for e in self._enemy_pieces:
            utility -= e.evaluate()
        return utility

    # ----------------- PRIVATE FUNCTIONS -----------------
    def __add_direction(self, piece, moves, dx, dy):
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
            space_status = self.__test_space(xc + dx, yc + dy)
            assert space_status in ["Blocked", "Open", "Capturable"]
            if space_status == "Open" and not self.__in_check(xi, yi, xc+dx, yc+dy):
                moves.append(Move(piece, file=chr(xc + dx + 96 + 1), rank=(yc + dy + 1)))
            elif space_status == "Capturable" and not self.__in_check(xi, yi, xc+dx, yc+dy):
                moves.append(Move(piece, file=chr(xc + dx + 96 + 1), rank=(yc + dy + 1),
                                  capture=self._board[xc+dx][yc+dy]))
            if space_status != "Open":
                break
            xc += dx
            yc += dy

    def __enemy(self, piece: str):
        """
            Used to quickly and easily refer to friendly pieces by their representative
            character (FEN) regardless of player color.
            :param piece: String (intended to be single character but not required).
            :return: Returns the given string either in fully upper-case or lower-case
                     depending on player color, to reflect Forsyth-Edwards Notation
        """
        assert type(piece) is str
        if self._color == "White":
            return piece.lower()
        elif self._color == "Black":
            return piece.upper()

    def __friendly(self, piece: str):
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

    def __in_check(self, xi=0, yi=0, xf=0, yf=0, move_king=False):
        """
            Cycles through all potentially dangerous spaces to confirm whether or not if king is in check
            after a specific move is taken. In other words, confirms whether a move should be prevented by allowing
            a check to occur.

            :param xi: integer representing the initial x coordinate of piece to move
            :param yi: integer representing the initial y coordinate of piece to move
            :param xf: integer representing the final x coordinate of piece to move
            :param yf: integer representing the final y coordinate of piece to move
            :param move_king: bool representing whether or not the piece being moved is the friendly king

            Returns:
                bool:   Represents whether or not friendly king is in check
        """
        king = next(p for p in self._friendly_pieces if p.type == "King")
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
                enemies = [self.__enemy("Q"), self.__enemy("B")]
            else:
                enemies = [self.__enemy("Q"), self.__enemy("R")]
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
                if new_board[x][y] == self.__enemy(piece):
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
        else:  # if self._color == "Black":
            dy = -1
        for dx in [-1, 1]:
            if space_threatens_check(kx + dx, ky + dy, "P"):
                return True

        # Rooks, bishop, queen, by radiating a direction
        dir_mods = [-1, 0, 1]
        for dx in dir_mods:
            for dy in dir_mods:
                if not (dx == 0 and dy == 0) and direction_threatens_check(dx, dy):
                    return True

        # Enemy king
        x_mods = [1, 0, -1]
        y_mods = [1, 0, -1]
        for dx in x_mods:
            for dy in y_mods:
                if not (dx == 0 and dy == 0) and space_threatens_check(kx + dx, ky + dy, "K"):
                    return True

        # No pieces threatening check!
        return False

    def __in_checkmate(self):
        """ Performs a check that the friendly player is currently checkmated """
        return self.__in_check() and len(self.moves) == 0

    def __insufficient_material(self):
        """ Performs a check that the state is not one of insufficient material - which results in a draw """
        fp = [p.type for p in self._friendly_pieces]
        ep = [p.type for p in self._enemy_pieces]

        # Test for Kk
        if len(fp) is 1 and len(ep) is 1:
            return True

        # Test for KNk with N on either side
        elif (len(fp) is 1 and len(ep) is 2 and "Knight" in ep) \
                or (len(ep) is 1 and len(fp) is 2 and "Knight" in fp):
            return True

        #  Test for KBk with B on either side
        elif (len(fp) is 1 and len(ep) is 2 and "Bishop" in ep) \
                or (len(ep) is 1 and len(fp) is 2 and "Bishop" in fp):
            return True

    def __potential_moves(self):
        """ Cycles through all pieces and generates a list of moves that are valid given the current state of the game.
           :return: List of valid moves from current state. tuple(piece, file, rank)
        """
        valid_move_list = []

        def conditional_append(ol, el):
            """ Meant to prevent an append of a list of zero potential moves
                :param ol -- original list
                :param el -- new list of elements to append
            """
            if el is not None:
                [ol.append(e) for e in el]

        assert len(self._friendly_pieces) > 0
        for p in self._friendly_pieces:
            piece_type = p.type.strip('\n')
            if piece_type == "Queen":  # DONE: Confirmed working.
                queen_moves = self.__potential_queen_moves(p)
                conditional_append(valid_move_list, queen_moves)
            elif piece_type == "Pawn":
                pawn_moves = self.__potential_pawn_moves(p)
                conditional_append(valid_move_list, pawn_moves)
            elif piece_type == "King":
                king_moves = self.__potential_king_moves(p)
                conditional_append(valid_move_list, king_moves)
            elif piece_type == "Knight":
                knight_moves = self.__potential_knight_moves(p)
                conditional_append(valid_move_list, knight_moves)
            elif piece_type == "Rook":
                rook_moves = self.__potential_rook_moves(p)
                conditional_append(valid_move_list, rook_moves)
            elif piece_type == "Bishop":
                bishop_moves = self.__potential_bishop_moves(p)
                conditional_append(valid_move_list, bishop_moves)

        return valid_move_list

    def __potential_bishop_moves(self, bishop):
        """ Tests all possible moves from given bishop and returns list of valid moves """
        assert bishop.type == "Bishop"
        move_list = []
        self.__add_direction(bishop, move_list, 1, 1)
        self.__add_direction(bishop, move_list, -1, 1)
        self.__add_direction(bishop, move_list, 1, -1)
        self.__add_direction(bishop, move_list, -1, -1)
        if len(move_list) == 0:
            return None
        return move_list

    def __potential_king_moves(self, king):
        """ Tests all possible moves from given king and returns list of valid moves """
        assert king.type == "King"
        x, y = get_coordinates(king.rank, king.file)
        move_list = []

        def append_space_if_valid(xf, yf):
            space = self.__test_space(xf, yf)
            if space == "Open" and not self.__in_check(x, y, xf, yf, move_king=True):
                move_list.append(Move(king, file=chr(xf + 97), rank=(yf + 1)))
            elif space == "Capturable" and not self.__in_check(x, y, xf, yf, move_king=True):
                move_list.append(Move(king, file=chr(xf + 97), rank=(yf + 1), capture=self._board[xf][yf]))

        append_space_if_valid(x+1, y)  # Straight-right
        append_space_if_valid(x+1, y+1)  # Diagonal right-down
        append_space_if_valid(x+1, y-1)  # Diagonal right-up
        append_space_if_valid(x-1, y)  # Straight-left
        append_space_if_valid(x-1, y+1)  # Diagonal left-down
        append_space_if_valid(x-1, y-1)  # Diagonal left-up
        append_space_if_valid(x, y+1)  # Straight down
        append_space_if_valid(x, y-1)  # Straight up

        if self.__friendly("K") in self._castle and not self.__in_check(x, y, x, y):
            # King-side castle
            if self.__test_space(x+1, y) == "Open" and self.__test_space(x+2, y) == "Open":
                if not self.__in_check(x, y, x+1, y, move_king=True) and \
                        not self.__in_check(x, y, x+2, y, move_king=True):
                    move_list.append(Move(king, file=chr(x+2 + 97), rank=(y + 1)))

        if self.__friendly("Q") in self._castle and not self.__in_check(x, y, x, y):
            # Queen-side castle
            if self.__test_space(x - 1, y) == "Open" and self.__test_space(x - 2, y) == "Open" \
                    and self.__test_space(x - 3, y) == "Open" and not self.__in_check(x, y, x - 1, y, move_king=True) \
                    and not self.__in_check(x, y, x - 2, y, move_king=True):
                print("Q - Appending %s %s" % (chr(x-2 + 97), y+1))
                move_list.append(Move(king, file=chr(x - 2 + 97), rank=(y + 1)))

        if len(move_list) == 0:
            return None
        return move_list

    def __potential_knight_moves(self, knight):
        """ Tests all possible moves from given knight and returns list of valid moves """
        assert knight.type == "Knight"
        x, y = get_coordinates(knight.rank, knight.file)
        move_list = []
        for m in [(2, 1), (2, -1), (-1, -2), (1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2)]:
            dx, dy = m
            if 0 <= x+dx < self._board.width and 0 <= y+dy < self._board.height:
                space = self.__test_space(x + dx, y + dy)
                if space == "Open" and not self.__in_check(x, y, x+dx, y+dy):
                    move_list.append(Move(knight, file=chr(x+dx + 97), rank=(y+dy + 1)))
                elif space == "Capturable" and not self.__in_check(x, y, x+dx, y+dy):
                    move_list.append(Move(knight, file=chr(x+dx + 97), rank=(y+dy + 1),
                                          capture=self._board[x+dx][y+dy]))
        if len(move_list) == 0:
            return None
        return move_list

    def __potential_pawn_moves(self, pawn):
        """ Tests all possible moves from given pawn and returns list of valid moves """
        assert pawn.type == "Pawn"
        x, y = get_coordinates(pawn.rank, pawn.file)
        move_list = []
        if self._color == "White":
            dy = 1
        else:  # if self._color == "Black":
            dy = -1

        def add_pawn_move(xf, yf, capture=None):
            """ Wrapper to add the pawns movement. Main purpose is to handle promotions. """
            f = chr(xf + 97)
            r = yf + 1
            if (self._color == "White" and r == 8) or (self._color == "Black" and r == 1):
                promotions = ["Bishop", "Rook", "Knight", "Queen"]
                [move_list.append(Move(pawn, file=f, rank=r, promotion=p, capture=capture)) for p in promotions]
            else:
                move_list.append(Move(pawn, file=f, rank=r))

        # Check immediate ahead is open
        if self.__test_space(x, y+dy) == "Open" and not self.__in_check(x, y, x, y+dy):
            add_pawn_move(x, y+dy)

        # Check double-forward. Both on initial row, and both spaces immediately ahead are open.
        if (pawn.rank == 2 and self._color == "White") or (pawn.rank == 7 and self._color == "Black"):
            if self.__test_space(x, y+2*dy) == "Open" and self.__test_space(x, y+dy) == "Open":
                if not self.__in_check(x, y, x, y+2*dy):
                    add_pawn_move(x, y+2*dy)

        # Check for capturable units including en passant target
        if self.__test_space(x-1, y+dy) == "Capturable":  # or (x-1, y+dy) == self._en_passant_target:
            if not self.__in_check(x, y, x-1, y+dy):
                add_pawn_move(x-1, y+dy, capture=self._board[x-1][y+dy])
        if self.__test_space(x+1, y+dy) == "Capturable":  # or (x+1, y+dy) == self._en_passant_target:
            if not self.__in_check(x, y, x+1, y+dy):
                add_pawn_move(x+1, y+dy, capture=self._board[x+1][y+dy])

        if (x-1, y+dy) == self._en_passant_target:
            if not self.__in_check(x, y, x-1, y+dy):
                add_pawn_move(x-1, y+dy)
        if (x+1, y+dy) == self._en_passant_target:
            if not self.__in_check(x, y, x+1, y+dy):
                add_pawn_move(x+1, y+dy)

        if len(move_list) == 0:
            return None
        return move_list

    def __potential_rook_moves(self, rook):
        """ Tests all possible moves from given rook and returns list of valid moves """
        assert rook.type == "Rook"
        move_list = []
        self.__add_direction(rook, move_list, 0, 1)  # Down
        self.__add_direction(rook, move_list, 0, -1)  # Up
        self.__add_direction(rook, move_list, 1, 0)  # Right
        self.__add_direction(rook, move_list, -1, 0)  # Left
        if len(move_list) == 0:
            return None
        return move_list

    def __potential_queen_moves(self, queen):
        """ Tests all possible moves from given queen and returns list of valid moves """
        assert queen.type == "Queen"
        move_list = []
        self.__add_direction(queen, move_list, 1, 1)  # Down-right diagonal
        self.__add_direction(queen, move_list, -1, 1)  # Down-left diagonal
        self.__add_direction(queen, move_list, 1, -1)  # Up-right diagonal
        self.__add_direction(queen, move_list, -1, -1)  # Up-left diagonal
        self.__add_direction(queen, move_list, 0, 1)  # Straight down
        self.__add_direction(queen, move_list, 0, -1)  # Straight up
        self.__add_direction(queen, move_list, 1, 0)  # Straight right
        self.__add_direction(queen, move_list, -1, 0)  # Straight left

        return move_list

    def __test_draw(self):
        """ Returns:
            bool:   True under the standard conditions for a stalemate, or a draw
                    either by turn or insufficient material
        """
        return (not self.__in_check() and len(self.moves) == 0) \
                or self._turns_to_draw == 0 \
                or self.__insufficient_material()

    def __test_space(self, x, y):
        """ Returns:
            str:  Represents the state of that space, which can be any of:
                  `Capturable', `Blocked', `Open', `Out of Bounds'
        """
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
