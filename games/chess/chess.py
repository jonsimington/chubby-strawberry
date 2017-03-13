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
        x, y = get_coordinates(self.rank, self.file)
        self.__space_color = "Black" if x + y % 2 == 0 else "White"

    def copy(self):
        return Piece(self.owner, self.type, self.file, self.rank, self.has_moved, self.id)

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
