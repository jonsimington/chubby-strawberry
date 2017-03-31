from games.chess.game_object import GameObject
from itertools import count


def get_player(fen: str):
    return str(fen.split(" ")[1])


def get_draw_counter(fen: str):
    """ :param fen: String in the format of Forsyth-Edwards Notation
        :return int counting number of half-moves since pawn movement or capture
    """
    return int(fen.split(" ")[4])


def get_en_passant_coordinates(fen: str):
    """ :param fen: String in the format of Forsyth-Edwards Notation
        :return two-tuple containing the x and y coordinates of the en-passant target
    """
    target = fen.split(" ")[3]
    if target is "-":
        return None
    file, rank = list(target)
    rank = int(rank)
    return get_coordinates(rank, file)


def get_coordinates(rank, file):
    """ :param rank: int representing a rank on the chess board
        :param file: chr representing a file on the chess board
        :return two-tuple containing the x and y coordinates of the given rank and file.
    """
    x = ord(file) - 97
    y = rank - 1
    return tuple((x, y))


def get_file_rank(x, y):
    file = chr(x+97)
    rank = y + 1
    return tuple((file, rank))


# noinspection PyAttributeOutsideInit
class MyPiece(GameObject):
    _ids = count(0)

    def __init__(self, color, t, file, rank, has_moved, captured=False, pid=None):
        GameObject.__init__(self)

        self.file = file
        self.has_moved = has_moved
        self.__color = color
        self.rank = rank
        self.type = t
        self.captured = captured
        if pid is None:
            self.__id = self._ids.__next__()
        else:
            self.__id = pid
        self.__x, self.__y = get_coordinates(self.rank, self.file)
        self.__space_color = "Black" if self.x + self.y % 2 == 0 else "White"

    def copy(self):
        return MyPiece(self.color, self.type, self.file, self.rank, self.has_moved, self.captured, self.id)

    def evaluate(self, end_game=False):
        assert self.type in ["Pawn", "Knight", "Bishop", "Rook", "Queen", "King"]
        assert self.color in ["White", "Black"]
        if self.captured is True:
            return 0
        if self.type == "Pawn":
            if self.color == "White":
                return 100 + WHITE_PAWN_EVAL[self.x][self.y]
            else:  # if self.owner.color == "Black"
                return 100 + BLACK_PAWN_EVAL[self.x][self.y]
        elif self.type == "Knight":
            if self.color == "White":
                return 320 + WHITE_KNIGHT_EVAL[self.x][self.y]
            else:  # if self.color == "Black"
                return 320 + BLACK_KNIGHT_EVAL[self.x][self.y]
        elif self.type == "Bishop":
            if self.color == "White":
                return 333 + WHITE_BISHOP_EVAL[self.x][self.y]
            else:  # if self.owner.color == "Black"
                return 333 + BLACK_BISHOP_EVAL[self.x][self.y]
        elif self.type == "Rook":
            if self.color == "White":
                return 510 + WHITE_ROOK_EVAL[self.x][self.y]
            else:  # if self.owner.color == "Black"
                return 510 + BLACK_ROOK_EVAL[self.x][self.y]
        elif self.type == "Queen":
            if self.color == "White":
                return 880 + WHITE_QUEEN_EVAL[self.x][self.y]
            else:  # if self.owner.color == "Black"
                return 880 + BLACK_QUEEN_EVAL[self.x][self.y]
        if self.type == "King" and end_game is False:
            if self.color == "White":
                return 200000 + WHITE_KING_MID_EVAL[self.x][self.y]
            else:  # if self.owner.color == "Black"
                return 200000 + BLACK_KING_MID_EVAL[self.x][self.y]
        elif self.type == "King" and end_game is True:
            if self.color == "White":
                return 200000 + WHITE_KING_END_EVAL[self.x][self.y]
            else:  # if self.owner.color == "Black"
                return 200000 + BLACK_KING_END_EVAL[self.x][self.y]

    def move(self, file, rank, promotionType=""):
        """ Moves the Piece from its current location to the given rank and file.

        Args:
            file (str): The file coordinate to move to. Must be [a-h].
            rank (int): The rank coordinate to move to. Must be [1-8].
            promotion_type (Optional[str]): If this is a Pawn moving to the end of the board then this parameter is what to promote it to. When used must be 'Queen', 'Knight', 'Rook', or 'Bishop'.

        Returns:
            Move: The Move you did if successful, otherwise None if invalid. In addition if your move was invalid you will lose.
        """
        return self._run_on_server('move', file=file, rank=rank, promotionType=promotionType)

    @property
    def space_color(self):
        return self.__space_color

    @property
    def captured(self):
        return self.__captured

    @captured.setter
    def captured(self, c):
        assert type(c) is bool
        self.__captured = c

    @property
    def file(self):
        return self.__file

    @file.setter
    def file(self, f):
        assert type(f) is str
        assert f in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        self.__file = f

    @property
    def has_moved(self):
        return self.__has_moved

    @has_moved.setter
    def has_moved(self, h):
        assert type(h) is bool
        self.__has_moved = h

    @property
    def id(self):
        return self.__id

    @property
    def color(self):
        return self.__color

    @property
    def rank(self):
        return self.__rank

    @rank.setter
    def rank(self, r):
        assert type(r) is int
        assert 1 <= r <= 8
        self.__rank = r

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, t):
        assert type(t) is str
        assert t in ["Pawn", "Rook", "Knight", "Bishop", "Queen", "King"]
        self.__type = t

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

# ---------- PIECE EVALUATION MODIFIERS ----------

BLACK_PAWN_EVAL = [[0, 50, 10, 5, 0, 5, 5, 0],
                   [0, 50, 10, 5, 0, -5, 10, 0],
                   [0, 50, 20, 10, 0, -10, 10, 0],
                   [0, 50, 30, 25, 20, 0, -20, 0],
                   [0, 50, 30, 25, 20, 0, -20, 0],
                   [0, 50, 20, 10, 0, -10, 10, 0],
                   [0, 50, 10, 5, 0, -5, 10, 0],
                   [0, 50, 10, 5, 0, 5, 5, 0]]

WHITE_PAWN_EVAL = [[0,   5,   5,  0,  5, 10, 50, 0],
                   [0,  10,  -5,  0,  5, 10, 50, 0],
                   [0,  10, -10,  0, 10, 20, 50, 0],
                   [0, -20,   0, 20, 25, 30, 50, 0],
                   [0, -20,   0, 20, 25, 30, 50, 0],
                   [0,  10, -10,  0, 10, 20, 50, 0],
                   [0,  10,  -5,  0,  5, 10, 50, 0],
                   [0,   5,   5,  0,  5, 10, 50, 0]]

BLACK_KNIGHT_EVAL = [[-50, -40, -30, -30, -30, -30, -40, -50],
                     [-40, -20,   0,   5,   5,   0, -20, -40],
                     [-30,   5,  10,  15,  15,  10,   5, -30],
                     [-30,   0,  15,  20,  20,  15,   0, -30],
                     [-30,   5,  15,  20,  20,  15,   5, -30],
                     [-30,   0,  10,  15,  15,  10,   0, -30],
                     [-40, -20,   0,   0,   0,   0, -20, -40],
                     [-50, -40, -30, -30, -30, -30, -40, -50]]


WHITE_KNIGHT_EVAL = [[-50, -40, -30, -30, -30, -30, -40, -50],
                     [-40, -20,   0,   0,   0,   0, -20, -40],
                     [-30,   0,  10,  15,  15,  10,   0, -30],
                     [-30,   5,  15,  20,  20,  15,   5, -30],
                     [-30,   0,  15,  20,  20,  15,   0, -30],
                     [-30,   5,  10,  15,  15,  10,   5, -30],
                     [-40, -20,   0,   5,   5,   0, -20, -40],
                     [-50, -40, -30, -30, -30, -30, -40, -50]]

BLACK_BISHOP_EVAL = [[-20, -10, -10, -10, -10, -10, -10, -20],
                     [-10,   0,   0,   5,   0,  10,   5, -10],
                     [-10,   0,   5,   5,  10,  10,   0, -10],
                     [-10,   0,  10,  10,  10,  10,   0, -10],
                     [-10,   0,  10,  10,  10,  10,   0, -10],
                     [-10,   0,   5,   5,  10,  10,   0, -10],
                     [-10,   0,   0,   5,   0,  10,   5, -10],
                     [-20, -10, -10, -10, -10, -10, -10, -20]]

WHITE_BISHOP_EVAL = [[-20, -10, -10, -10, -10, -10, -10, -20],
                     [-10,   5,  10,   0,   5,   0,   0, -10],
                     [-10,   0,  10,  10,   5,   5,   0, -10],
                     [-10,   0,  10,  10,  10,  10,   0, -10],
                     [-10,   0,  10,  10,  10,  10,   0, -10],
                     [-10,   0,  10,  10,   5,   5,   0, -10],
                     [-10,   5,  10,   0,   5,   0,   0, -10],
                     [-20, -10, -10, -10, -10, -10, -10, -20]]

BLACK_ROOK_EVAL = [[0,  5, -5, -5, -5, -5, -5, 0],
                   [0, 10,  0,  0,  0,  0,  0, 0],
                   [0, 10,  0,  0,  0,  0,  0, 0],
                   [0, 10,  0,  0,  0,  0,  0, 5],
                   [0, 10,  0,  0,  0,  0,  0, 5],
                   [0, 10,  0,  0,  0,  0,  0, 0],
                   [0, 10,  0,  0,  0,  0,  0, 0],
                   [0,  5, -5, -5, -5, -5, -5, 0]]

WHITE_ROOK_EVAL = [[0, -5, -5, -5, -5, -5,  5, 0],
                   [0,  0,  0,  0,  0,  0, 10, 0],
                   [0,  0,  0,  0,  0,  0, 10, 0],
                   [5,  0,  0,  0,  0,  0, 10, 0],
                   [5,  0,  0,  0,  0,  0, 10, 0],
                   [0,  0,  0,  0,  0,  0, 10, 0],
                   [0,  0,  0,  0,  0,  0, 10, 0],
                   [0, -5, -5, -5, -5, -5,  5, 0]]

BLACK_QUEEN_EVAL = [[-20, -10, -10, -5,  0, -10, -10, -20],
                    [-10,   0,   0,  0,  0,   5,   0, -10],
                    [-10,   0,   5,  5,  5,   5,   5, -10],
                    [ -5,   0,   5,  5,  5,   5,   0,  -5],
                    [ -5,   0,   5,  5,  5,   5,   0,  -5],
                    [-10,   0,   5,  5,  5,   5,   0, -10],
                    [-10,   0,   0,  0,  0,   0,   0, -10],
                    [-20, -10, -10, -5, -5, -10, -10, -20]]

WHITE_QUEEN_EVAL = [[-20, -10, -10,  0, -5, -10, -10, -20],
                    [-10,   0,   0,  0,  0,   5,   0, -10],
                    [-10,   0,   5,  5,  5,   5,   5, -10],
                    [ -5,   0,   5,  5,  5,   5,   0,  -5],
                    [ -5,   0,   5,  5,  5,   5,   0,  -5],
                    [-10,   0,   5,  5,  5,   5,   0, -10],
                    [-10,   0,   0,  0,  0,   0,   0, -10],
                    [-20, -10, -10, -5, -5, -10, -10, -20]]

BLACK_KING_MID_EVAL = [[-30, -30, -30, -30, -20, -10, 20, 20],
                       [-40, -40, -40, -40, -30, -20, 20, 30],
                       [-40, -40, -40, -40, -30, -20,  0, 10],
                       [-50, -50, -50, -50, -40, -20,  0,  0],
                       [-50, -50, -50, -50, -40, -20,  0,  0],
                       [-40, -40, -40, -40, -30, -20,  0, 10],
                       [-40, -40, -40, -40, -30, -20, 20, 30],
                       [-30, -30, -30, -30, -20, -10, 20, 20]]

WHITE_KING_MID_EVAL = [[20, 20, -10, -20, -30, -30, -30, -30],
                       [30, 20, -20, -30, -40, -40, -40, -40],
                       [10,  0, -20, -30, -40, -40, -40, -40],
                       [ 0,  0, -20, -40, -50, -50, -50, -50],
                       [ 0,  0, -20, -40, -50, -50, -50, -50],
                       [10,  0, -20, -30, -40, -40, -40, -40],
                       [30, 20, -20, -30, -40, -40, -40, -40],
                       [20, 20, -10, -20, -30, -30, -30, -30]]

BLACK_KING_END_EVAL = [[-50, -30, -30, -30, -30, -30, -30, -50],
                       [-40, -20, -10, -10, -10, -10, -30, -30],
                       [-30, -10,  20,  30,  30,  20,   0, -30],
                       [-20,   0,  30,  40,  40,  30,   0, -30],
                       [-20,   0,  30,  40,  40,  30,   0, -30],
                       [-30, -10,  20,  30,  30,  20,   0, -30],
                       [-40, -20, -10, -10, -10, -10, -30, -30],
                       [-50, -30, -30, -30, -30, -30, -30, -50]]

WHITE_KING_END_EVAL = [[-50, -30, -30, -30, -30, -30, -30, -50],
                       [-30, -30, -10, -10, -10, -10, -20, -40],
                       [-30,   0,  20,  30,  30,  20, -10, -30],
                       [-30,   0,  30,  40,  40,  30,   0, -20],
                       [-30,   0,  30,  40,  40,  30,   0, -20],
                       [-30,   0,  20,  30,  30,  20, -10, -30],
                       [-30, -30, -10, -10, -10, -10, -20, -40],
                       [-50, -30, -30, -30, -30, -30, -30, -50]]

