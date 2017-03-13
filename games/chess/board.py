from games.chess.chess import get_coordinates


class Board(list):
    def __init__(self, fen=None):
        """
        :param fen: String adhering to Forsyth-Edwards Notation format.
        """
        super().__init__()
        self.width = 8
        self.height = 8
        if fen is not None:
            self.fen = fen
        else:
            # Initial state
            self.fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        self.generate_by(self.fen)

    def copy(self):
        """ Creates a copy of the current board using the Forsyth-Edwards Notation representation of the board
        """
        return Board(self.fen)

    def generate_by(self, fen):
        """
        Modifies the board 'self' to represent the board-state given, or the initial board-state.
        :param fen: Forsyth-Edwards Notation representation of board state
        :return: No return value. Simply modified the called Board to represent the given FEN string
        """
        del self[:]
        fen_pieces = fen.split(" ")[0]  # Strips FEN of non-location info
        row_lists = fen_pieces.split("/")
        placeholder = []
        for r in row_lists:
            row = []
            for c in r:
                if c.isdigit():
                    for _ in range(int(c)):
                        row.append("")
                else:
                    row.append(c)
            placeholder.append(row)
        # This implementation actually puts ranks 8 descending in list first
        # [r8, r7, r6, r5, r4, r3, r2, r1]
        # Must be reversed to be able to address easily by rank.
        # [r1, r2, r3, r4, r5, r6, r7, r8]
        placeholder.reverse()
        # Transpose to allow board[x][y] indexing instead of board[y][x]
        placeholder = list(map(list, zip(*placeholder)))
        [self.append(x) for x in placeholder]

    def move_piece(self, xi=None, yi=None, xf=None, yf=None, ri=None, fi=None, rf=None, ff=None):
        if xi is not None and yi is not None and xf is not None and yf is not None:
            self.move_piece_xy(xi, yi, xf, yf)
        elif ri is not None and fi is not None and rf is not None and ff is not None:
            self.move_piece_rf(ri, fi, rf, ff)

    def move_piece_rf(self, ri, fi, rf, ff):
        xi, yi = get_coordinates(ri, fi)
        xf, yf = get_coordinates(rf, ff)
        self.move_piece_xy(xi, yi, xf, yf)

    def move_piece_xy(self, xi, yi, xf, yf):
        marker = self[xi][yi]
        self[xi][yi] = ""
        self[xf][yf] = marker

    def nice_print(self):
        print("========================")
        [print(x) for x in self]
        print("========================")
