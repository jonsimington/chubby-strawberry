def get_draw_counter(fen: str):
    """ :param fen: String in the format of Forsyth-Edwards Notation
        :return int counting number of half-moves since pawn movement or capture
    """
    return fen.split(" ")[4]

