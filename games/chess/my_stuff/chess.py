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
    y = rank - 1  # Account for list index offset
    x = ord(file) - 97  # 97 for ASCII offset
    return tuple((x, y))
