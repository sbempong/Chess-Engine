import time

import chess
import pytest

from Engine.chess_suggester import ChessSuggester
from Engine.enhanced_engine import EnhancedChessSuggester

# Generous bounds (CI runners are slow); the pre-batching implementation took
# ~1.1s for the enhanced engine from the start position.
BUDGET_SECONDS = {ChessSuggester: 0.25, EnhancedChessSuggester: 0.5}


@pytest.mark.parametrize("cls", list(BUDGET_SECONDS))
def test_start_position_suggestions_are_fast(cls):
    engine = cls()
    board = chess.Board()
    engine.get_move_suggestions(board)  # warm-up (model load, imports)

    start = time.perf_counter()
    result = engine.get_move_suggestions(board)
    elapsed = time.perf_counter() - start

    assert len(result["suggested_moves"]) == 5
    assert elapsed < BUDGET_SECONDS[cls], f"{cls.__name__} took {elapsed:.2f}s"


def test_batch_and_single_evaluation_agree():
    engine = EnhancedChessSuggester()
    boards = [chess.Board()]
    for san in ("e4", "e5", "Nf3", "Nc6", "Bb5"):
        boards.append(boards[-1].copy())
        boards[-1].push_san(san)
    boards.append(chess.Board("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3"))  # mate

    batch = engine.evaluate_positions(boards)
    single = [engine.evaluate_position(b) for b in boards]
    assert batch == pytest.approx(single)
