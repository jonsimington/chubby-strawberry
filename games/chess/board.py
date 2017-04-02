from games.chess.chess import get_coordinates


class Board(list):
    def __init__(self, fen=None, board=None):
        """
        :param fen: String adhering to Forsyth-Edwards Notation format.
        """
        super().__init__()
        self.width = 8
        self.height = 8
        if fen is not None:
            self.__generate_from_fen(fen)
            self._fen = fen
        elif board is not None:
            # Initial state
            self.__generate_from_board(board)
            self._fen = self.__create_fen()
        else:
            raise ValueError("Must pass a FEN or a Board to create a Board from")

    def __hash__(self):
        return hash(self.fen)

    @property
    def fen(self):
        return self._fen

    def __create_fen(self):
        fen = ""
        placeholder = [[y for y in self[x]] for x in range(len(self))]
        placeholder = list(map(list, zip(*placeholder)))
        placeholder.reverse()
        # Board should be oriented for proper display here
        for r in placeholder:
            for c in r:
                count = 0
                if c.isdigit():
                    count += 1
                else:
                    if count != 0:
                        fen += count
                    fen += c
            fen += "/"
        fen.rstrip("/")
        return fen

    def copy(self):
        """ Creates a copy of the current board using the Forsyth-Edwards Notation representation of the board """
        return Board(board=self)

    def __generate_from_fen(self, fen):
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

    def __generate_from_board(self, board):
        [self.append([c for c in r]) for r in board]
        assert len(self) == len(board)

    def move_piece(self, xi=None, yi=None, xf=None, yf=None, ri=None, fi=None, rf=None, ff=None):
        """ Moves the token marker for a piece from one space to another.
            Simply a wrapper to handle moving either xy system or rank-file system

            :param xi: int representing the initial x coordinate of the piece to be moved
            :param yi: int representing the initial y coordinate of the piece to be moved
            :param xf: int representing the final x coordinate of the piece to be moved
            :param yf: int representing the final y coordinate of the piece to be moved

            :param ri: int representing the initial rank of the piece to be moved
            :param fi: chr representing the initial file of the piece to be moved
            :param rf: int representing the final rank of the piece to be moved
            :param ff: chr representing the final file of the piece to be moved
        """
        if xi is not None and yi is not None and xf is not None and yf is not None:
            self.move_piece_xy(xi, yi, xf, yf)
        elif ri is not None and fi is not None and rf is not None and ff is not None:
            self.move_piece_rf(ri, fi, rf, ff)

    def move_piece_rf(self, ri, fi, rf, ff):
        """ Moves the token marker for a piece from one space to another.

            :param ri: int representing the initial rank of the piece to be moved
            :param fi: chr representing the initial file of the piece to be moved
            :param rf: int representing the final rank of the piece to be moved
            :param ff: chr representing the final file of the piece to be moved
        """
        xi, yi = get_coordinates(ri, fi)
        xf, yf = get_coordinates(rf, ff)
        self.move_piece_xy(xi, yi, xf, yf)

    def move_piece_xy(self, xi, yi, xf, yf):
        """ Moves the token marker for a piece from one space to another.

            :param xi: int representing the initial x coordinate of the piece to be moved
            :param yi: int representing the initial y coordinate of the piece to be moved
            :param xf: int representing the final x coordinate of the piece to be moved
            :param yf: int representing the final y coordinate of the piece to be moved
        """
        marker = self[xi][yi]
        self[xi][yi] = ""
        self[xf][yf] = marker

    def nice_print(self):
        print("========================")
        [print(x) for x in self]
        print("========================")
