from my_stuff.board import Board
from my_stuff.chess import get_draw_counter


class State:
    def __init__(self, game, player):
        self._board = Board(game.fen)  # Have to change in future assignments
        self._turns_to_draw = get_draw_counter(game.fen)
        # self._player = player
        self._pieces = player.pieces

    def potential_moves(self):
        """ Cycles through all pieces and generates a list of moves that are valid
            given the current state of the game.

            Returns: List of valid moves from current state
            Return type: list
        """
        # Cycle through _pieces
        # Check each potential move
        valid_move_list = []
        for p in self._pieces:
            if p.type() is "King":
                king_moves = self.potential_king_moves(p)
                if king_moves is not None:
                    valid_move_list.append(king_moves)
            elif p.type() is "Queen":
                queen_moves = self.potential_queen_moves(p)
                if queen_moves is not None:
                    valid_move_list.append(queen_moves)
            elif p.type() is "Knight":
                knight_moves = self.potential_knight_moves(p)
                if knight_moves is not None:
                    valid_move_list.append(knight_moves)
            elif p.type() is "Rook":
                rook_moves = self.potential_rook_moves(p)
                if rook_moves is not None:
                    valid_move_list.append(self.potential_rook_moves(p))
            elif p.type() is "Bishop":
                bishop_moves = self.potential_bishop_moves(p)
                if bishop_moves is not None:
                    valid_move_list.append(self.potential_bishop_moves(p))
            elif p.type() is "Pawn":
                pawn_moves = self.potential_pawn_moves(p)
                if pawn_moves is not None:
                    valid_move_list.append(pawn_moves)
        return valid_move_list

    def potential_bishop_moves(self, bishop):
        """ Tests all possible moves from given bishop and returns list of valid moves """
        assert bishop.type() is "Bishop"
        y = bishop.rank - 1  # Account for list index offset
        x = ord(bishop.file) - 97  # 96 for ASCII offset, 1 for index
        list_empty = True
        move_list = []
        # TODO: go through board
        if list_empty:
            return None
        return move_list

    def potential_king_moves(self, king):
        """ Tests all possible moves from given king and returns list of valid moves """
        # DON'T FORGET CASTLING
        assert king.type() is "King"
        y = king.rank - 1  # Account for list index offset
        x = ord(king.file) - 97  # 96 for ASCII offset, 1 for index
        list_empty = True
        move_list = []
        # TODO: go through board
        if list_empty:
            return None
        return move_list

    def potential_knight_moves(self, knight):
        """ Tests all possible moves from given knight and returns list of valid moves """
        assert knight.type() is "Knight"
        y = knight.rank - 1  # Account for list index offset
        x = ord(knight.file) - 97  # 96 for ASCII offset, 1 for index
        list_empty = True
        move_list = []
        # TODO: go through board
        if list_empty:
            return None
        return move_list

    def potential_pawn_moves(self, pawn):
        """ Tests all possible moves from given pawn and returns list of valid moves """
        # DON'T FORGET EN PASSANT
        assert pawn.type() is "Pawn"
        y = pawn.rank - 1  # Account for list index offset
        x = ord(pawn.file) - 97  # 96 for ASCII offset, 1 for index
        list_empty = True
        move_list = []
        # TODO: go through board
        if list_empty:
            return None
        return move_list

    def potential_rook_moves(self, rook):
        """ Tests all possible moves from given rook and returns list of valid moves """
        # DON'T FORGET CASTLING
        assert rook.type() is "Rook"
        y = rook.rank - 1  # Account for list index offset
        x = ord(rook.file) - 97  # 96 for ASCII offset, 1 for index
        list_empty = True
        move_list = []
        # TODO: go through board
        if list_empty:
            return None
        return move_list

    def potential_queen_moves(self, queen):
        """ Tests all possible moves from given queen and returns list of valid moves """
        assert queen.type() is "Queen"
        y = queen.rank - 1  # Account for list index offset
        x = ord(queen.file) - 97  # 96 for ASCII offset, 1 for index
        list_empty = True
        move_list = []
        # TODO: go through board
        if list_empty:
            return None
        return move_list
