import unittest
from games.chess.board import Board


class PawnTestCase(unittest.TestCase):
    def setUp(self):
        fen = "8/8/8/8/1R6/5rR1/1P2P1P1/8 w KQkq -"
        self.board = Board(fen)

    def test_pawn_forward_double_open(self):
        pass

    def test_pawn_forward_double_blocked(self):
        pass

    def test_pawn_forward_single_open(self):
        pass

    def test_pawn_forward_single_blocked(self):
        pass

    def test_pawn_capture_normal_left(self):
        pass

    def test_pawn_capture_normal_right(self):
        pass

    def test_pawn_capture_enpassant_left(self):
        pass

    def test_pawn_capture_enpassant_right(self):
        pass


class KingTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_king_up_open(self):
        pass

    def test_king_up_blocked(self):
        pass

    def test_king_up_capturable(self):
        pass

    def test_king_down_open(self):
        pass

    def test_king_down_blocked(self):
        pass

    def test_king_down_capturable(self):
        pass

    def test_king_left_open(self):
        pass

    def test_king_left_blocked(self):
        pass

    def test_king_left_capturable(self):
        pass

    def test_king_right_open(self):
        pass

    def test_king_right_blocked(self):
        pass

    def test_king_right_capturable(self):
        pass
