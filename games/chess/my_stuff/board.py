
class Board(list):
    def __init__(self, fen=None):
        """
        :param fen: String adhering to Forsyth-Edwards Notation format.
        """
        super().__init__()
        self.width = 8
        self.height = 8
        if fen is not None:
            self.generate_by(fen)
            self.fen = fen
        else:
            # Initial state
            self.fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    def copy(self):
        return Board(self.fen)

    def generate_by(self, fen=None):
        del self[:]
        if fen is not None:
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
        # else:  # Initial state
        #     self.append(["r", "n", "b", "q", "k", "b", "n", "r"])
        #     self.append(["p", "p", "p", "p", "p", "p", "p", "p"])
        #     self.append(["",  "",  "",  "",  "",  "",  "",  ""])
        #     self.append(["",  "",  "",  "",  "",  "",  "",  ""])
        #     self.append(["",  "",  "",  "",  "",  "",  "",  ""])
        #     self.append(["",  "",  "",  "",  "",  "",  "",  ""])
        #     self.append(["P", "P", "P", "P", "P", "P", "P", "P"])
        #     self.append(["R", "N", "B", "Q", "K", "B", "N", "R"])
        pass
