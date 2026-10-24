import chess
import pytest

from Engine.evaluation import PositionEvaluator, find_stockfish

FREE_QUEEN_WHITE = "4k3/pppp4/8/3q4/8/4N3/PPPP4/4K3 w - - 0 1"
FREE_QUEEN_BLACK = "4k3/pppp4/4n3/8/3Q4/8/PPPP4/4K3 b - - 0 1"
FOOLS_MATE = "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3"


@pytest.fixture
def material():
    return PositionEvaluator(use_stockfish=False)


def test_material_only_evaluator_never_spawns_engine(material):
    assert material.has_stockfish is False
    assert material.engine is None


def test_start_position_is_equal(material):
    assert material.evaluate_position(chess.Board()) == 0.0


def test_material_is_white_perspective(material):
    assert material.evaluate_position(chess.Board(FREE_QUEEN_WHITE)) < 0
    assert material.evaluate_position(chess.Board(FREE_QUEEN_BLACK)) > 0


def test_checkmate_scores(material):
    assert material.evaluate_position(chess.Board(FOOLS_MATE)) < -100


def test_stalemate_is_zero(material):
    assert material.evaluate_position(chess.Board("k7/8/8/8/8/8/8/K7 w - - 0 1")) == 0.0


def test_simple_best_move_white_takes_queen(material):
    move, score = material.get_simple_best_move(chess.Board(FREE_QUEEN_WHITE))
    assert move.uci() == "e3d5"
    assert score > 0


def test_simple_best_move_black_takes_queen(material):
    move, score = material.get_simple_best_move(chess.Board(FREE_QUEEN_BLACK))
    assert move.uci() == "e6d4"
    assert score < 0


def test_best_move_on_finished_game(material):
    move, _ = material.get_best_move(chess.Board(FOOLS_MATE))
    assert move is None


@pytest.mark.skipif(find_stockfish() is None, reason="Stockfish not installed")
def test_stockfish_is_discovered_and_white_perspective():
    evaluator = PositionEvaluator()
    try:
        assert evaluator.has_stockfish
        # Black is a queen up with no tactic for White; must be negative whoever is to move.
        assert evaluator.evaluate_position(chess.Board("4k3/pppp4/8/3q4/8/8/PPPP4/4K3 w - - 0 1"), depth=6) < 0
        assert evaluator.evaluate_position(chess.Board("4k3/pppp4/8/3q4/8/8/PPPP4/4K3 b - - 0 1"), depth=6) < 0
        move, score = evaluator.get_best_move(chess.Board(FREE_QUEEN_WHITE), depth=6)
        assert move.uci() == "e3d5"
        assert score > 0
    finally:
        evaluator.close()
