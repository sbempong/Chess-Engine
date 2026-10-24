"""End-to-end smoke test of the analysis pipeline used by main.py and app.py."""
import chess
import pytest

from Engine.chess_suggester import ChessSuggester
from Engine.enhanced_engine import EnhancedChessSuggester

CHECKMATE = "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3"
STALEMATE = "k7/2K5/1Q6/8/8/8/8/8 b - - 0 1"


@pytest.fixture(scope="module", params=[ChessSuggester, EnhancedChessSuggester])
def engine(request):
    return request.param()


def test_opening_analysis(engine):
    board = chess.Board()
    for san in ("e4", "e5", "Nf3", "Nc6"):
        board.push_san(san)
    analysis = engine.get_move_suggestions(board)
    assert isinstance(analysis["current_evaluation"], float)
    assert len(analysis["suggested_moves"]) == 5
    assert all(chess.Move.from_uci(m["move"]) in board.legal_moves for m in analysis["suggested_moves"])
    assert analysis["is_check"] is False


def test_checkmate_analysis(engine):
    analysis = engine.get_move_suggestions(chess.Board(CHECKMATE))
    assert analysis["is_checkmate"] is True
    assert analysis["current_evaluation"] < -1000
    assert analysis["suggested_moves"] == []


def test_stalemate_analysis(engine):
    analysis = engine.get_move_suggestions(chess.Board(STALEMATE))
    assert analysis["is_stalemate"] is True
    assert analysis["current_evaluation"] == 0.0
    assert analysis["suggested_moves"] == []


def test_enhanced_engine_falls_back_without_model(tmp_path):
    engine = EnhancedChessSuggester(model_path=str(tmp_path / "missing.pkl"))
    assert engine.use_model is False
    assert engine.evaluate_position(chess.Board()) == 0.0
