import csv
import os

import chess
import pytest

from Engine.board import Board
from Engine.chess_suggester import ChessSuggester
from Engine.evaluation import PositionEvaluator, evaluate_position

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRAINING_DATA = os.path.join(ROOT, "Data", "training_data.csv")


def sample_training_fens(limit=5):
    if not os.path.exists(TRAINING_DATA):
        return []
    with open(TRAINING_DATA, newline="") as handle:
        return [row["position_fen"] for _, row in zip(range(limit), csv.DictReader(handle))]


@pytest.fixture(scope="module")
def material():
    return PositionEvaluator(use_stockfish=False)


def test_initial_position_roughly_equal():
    # With Stockfish this is a small White edge; without it, exactly 0.
    assert abs(evaluate_position(chess.Board(), depth=8)) < 1.0


def test_material_pawn_up(material):
    board = chess.Board("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")
    board.remove_piece_at(chess.E7)
    assert material.evaluate_position(board) == pytest.approx(1.0)


def test_material_queen_down(material):
    board = chess.Board()
    board.remove_piece_at(chess.D1)
    assert material.evaluate_position(board) == pytest.approx(-9.0)


def test_checkmate_detection():
    board = chess.Board()
    for san in ("f3", "e5", "g4", "Qh4"):
        board.push_san(san)
    assert board.is_checkmate()
    assert evaluate_position(board) < -100


@pytest.mark.parametrize("fen", ["k7/8/8/8/8/8/8/K7 w - - 0 1", "k7/8/1K6/8/8/8/8/8 w - - 0 1"])
def test_draws_are_zero(fen):
    board = chess.Board(fen)
    assert board.is_insufficient_material()
    assert evaluate_position(board) == 0.0


def test_board_wrapper_round_trip():
    board = Board()
    assert board.make_move(chess.Move.from_uci("e2e4"))
    assert not board.make_move(chess.Move.from_uci("e2e4"))
    assert board.get_pgn() == "1. e4"
    assert board.undo_move() == chess.Move.from_uci("e2e4")
    assert board.get_fen() == chess.STARTING_FEN
    board.make_move(chess.Move.from_uci("d2d4"))
    board.reset()
    assert board.get_fen() == chess.STARTING_FEN and board.move_history == []


@pytest.mark.parametrize("fen", sample_training_fens() or [pytest.param(None, marks=pytest.mark.skip("no training data"))])
def test_training_positions_are_processable(fen):
    board = chess.Board(fen)
    suggestions = ChessSuggester().get_move_suggestions(board)
    assert suggestions["suggested_moves"]
    assert isinstance(evaluate_position(board, depth=6), float)
