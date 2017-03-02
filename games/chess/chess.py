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
    file, rank = target.split("")
    return get_coordinates(rank, file)


def get_coordinates(rank, file):
    x = ord(file) - 97
    y = rank - 1
    return tuple((x, y))
