import chess
import pytest

from Engine.chess_suggester import ChessSuggester
from Engine.enhanced_engine import EnhancedChessSuggester

WHITE_MATE_IN_ONE = "r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4"
BLACK_MATE_IN_ONE = "rnbqkbnr/pppp1ppp/8/4p3/6P1/5P2/PPPPP2P/RNBQKBNR b KQkq g3 0 2"
WHITE_FREE_QUEEN = "4k3/8/8/3q4/8/4N3/8/4K3 w - - 0 1"
BLACK_FREE_QUEEN = "4k3/8/4n3/8/3Q4/8/8/4K3 b - - 0 1"


@pytest.fixture(params=[ChessSuggester, EnhancedChessSuggester])
def suggester(request):
    return request.param()


def top_move(suggester, fen):
    board = chess.Board(fen)
    moves = suggester.suggest_moves(board)
    assert moves, "expected at least one suggestion"
    return moves[0][0].uci()


def test_white_finds_mate_in_one(suggester):
    assert top_move(suggester, WHITE_MATE_IN_ONE) == "h5f7"


def test_black_finds_mate_in_one(suggester):
    assert chess.Board(BLACK_MATE_IN_ONE).turn == chess.BLACK
    assert top_move(suggester, BLACK_MATE_IN_ONE) == "d8h4"


def test_white_captures_free_queen(suggester):
    assert top_move(suggester, WHITE_FREE_QUEEN) == "e3d5"


def test_black_captures_free_queen(suggester):
    assert top_move(suggester, BLACK_FREE_QUEEN) == "e6d4"


def test_evaluation_is_white_perspective(suggester):
    board = chess.Board(WHITE_FREE_QUEEN)
    assert suggester.evaluate_position(board) < 0
    board = chess.Board(BLACK_FREE_QUEEN)
    assert suggester.evaluate_position(board) > 0


def test_does_not_hang_a_piece(suggester):
    # White queen on d1, black rook on d8 with an open d-file: Qd5?? would be
    # captured by the rook. A 2-ply search must not suggest it as the best move.
    board = chess.Board("3rk3/8/8/8/8/8/8/3QK3 w - - 0 1")
    moves = suggester.suggest_moves(board)
    assert moves[0][0].uci() != "d1d5"


def test_get_move_suggestions_shape(suggester):
    result = suggester.get_move_suggestions(chess.Board())
    assert set(result) >= {"current_evaluation", "suggested_moves", "is_check",
                           "is_checkmate", "is_stalemate", "is_insufficient_material"}
    assert 1 <= len(result["suggested_moves"]) <= 5
    for entry in result["suggested_moves"]:
        assert {"move", "san", "evaluation", "comment"} <= set(entry)


def test_no_suggestions_when_game_over(suggester):
    board = chess.Board("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3")
    assert board.is_checkmate()
    assert suggester.suggest_moves(board) == []
