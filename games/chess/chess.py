from itertools import count


def get_draw_counter(fen: str):
    """ :param fen: String in the format of Forsyth-Edwards Notation
        :return int counting number of half-moves since pawn movement or capture
    """
    return fen.split(" ")[4]


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


# noinspection PyAttributeOutsideInit
class Piece:
    _ids = count(0)

    def __init__(self, owner, t, file, rank, has_moved, pid=None):
        self.file = file
        self.has_moved = has_moved
        self.owner = owner
        self.rank = rank
        self.type = t
        if pid is None:
            self.__id = self._ids.next()
        else:
            self.__id = pid
        self.__x, self.__y = get_coordinates(self.rank, self.file)
        self.__space_color = "Black" if self.x + self.y % 2 == 0 else "White"

    def copy(self):
        return Piece(self.owner, self.type, self.file, self.rank, self.has_moved, self.id)

    def evaluate(self, end_game=False):
        if self.type == "Pawn":
            if self.owner.color == "White":
                return 100 + WHITE_PAWN_EVAL[self.x][self.y]
            else:  # if self.owner.color == "Black"
                return 333 + BLACK_BISHOP_EVAL[self.x][self.y]
        elif self.type == "Bishop":
            if self.owner.color == "White":
                return 333 + WHITE_BISHOP_EVAL[self.x][self.y]
            else:  # if self.owner.color == "Black"
                return 333 + BLACK_BISHOP_EVAL[self.x][self.y]
        elif self.type == "Rook":
            if self.owner.color == "White":
                return 510 + WHITE_ROOK_EVAL[self.x][self.y]
            else:  # if self.owner.color == "Black"
                return 510 + BLACK_ROOK_EVAL[self.x][self.y]
        elif self.type == "Queen":
            if self.owner.color == "White":
                return 880 + WHITE_QUEEN_EVAL[self.x][self.y]
            else:  # if self.owner.color == "Black"
                return 880 + BLACK_QUEEN_EVAL[self.x][self.y]
        elif self.type == "King" and end_game == "False":
            if self.owner.color == "White":
                return 20000 + WHITE_KING_MID_EVAL[self.x][self.y]
            else:  # if self.owner.color == "Black"
                return 20000 + BLACK_KING_MID_EVAL[self.x][self.y]
        elif self.type == "King" and end_game == "True":
            if self.owner.color == "White":
                return 20000 + WHITE_KING_END_EVAL[self.x][self.y]
            else:  # if self.owner.color == "Black"
                return 20000 + BLACK_KING_END_EVAL[self.x][self.y]

    @property
    def space_color(self):
        return self.__space_color

    @property
    def file(self):
        return self.__file

    @file.setter
    def file(self, f):
        assert type(f) is chr
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
    def owner(self):
        return self.__owner

    @owner.setter
    def owner(self, o):
        assert type(o) is str
        assert o in ["Black", "White"]
        self.__owner = o

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

