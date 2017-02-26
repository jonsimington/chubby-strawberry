
class Board(list):
    def __init__(self, fen=None):
        """
        :param fen: String adhering to Forsyth-Edwards Notation format.
        """
        super().__init__()
        self.width = 8
        self.height = 8
        self.generate_by(fen)

    def copy(self):
        pass

    def generate_by(self, fen):
        del self[:]
        if fen is None:
            self.append(["r", "n", "b", "q", "k", "b", "n", "r"])
            self.append(["p", "p", "p", "p", "p", "p", "p", "p"])
            self.append(["",  "",  "",  "",  "",  "",  "",  ""])
            self.append(["",  "",  "",  "",  "",  "",  "",  ""])
            self.append(["",  "",  "",  "",  "",  "",  "",  ""])
            self.append(["",  "",  "",  "",  "",  "",  "",  ""])
            self.append(["P", "P", "P", "P", "P", "P", "P", "P"])
            self.append(["R", "N", "B", "Q", "K", "B", "N", "R"])
        else:
            fen_pieces = fen.split(" ")[0]  # Strips FEN of non-location info
            row_lists = fen_pieces.split("/")
            for r in range(row_lists):
                rank = 8-r
                file = 0  # file should go from 0-7 representing a-h
                row = []
                for c in r.split(""):
                    if c.isdigit():
                        for _ in range(c):
                            row.append("")
                    else:
                        row.append(c)
                self.append(row)
            # This implementation actually puts ranks 8 descending in list first
            # [r8, r7, r6, r5, r4, r3, r2, r1]
            # Must be reversed to be able to address easily by rank.
            # [r1, r2, r3, r4, r5, r6, r7, r8]
            self.reverse()
        pass
