"""Blunder detection against Stockfish. Skipped when Stockfish isn't installed."""
import chess
import chess.engine
import pytest

from Engine.evaluation import find_stockfish

STOCKFISH = find_stockfish()
pytestmark = pytest.mark.skipif(STOCKFISH is None, reason="Stockfish not installed")

BLUNDER_THRESHOLD = -3.0   # pawns lost (from the mover's perspective)
LIMIT = chess.engine.Limit(depth=12)
MULTIPV = 5


@pytest.fixture(scope="module")
def engine():
    with chess.engine.SimpleEngine.popen_uci(STOCKFISH) as engine:
        yield engine


def is_blunder(engine, board, move):
    """A move is a blunder if it loses more than BLUNDER_THRESHOLD pawns and
    isn't among the engine's top MULTIPV choices."""
    mover = board.turn
    before = engine.analyse(board, LIMIT)["score"].pov(mover).score(mate_score=10000)

    board.push(move)
    after = engine.analyse(board, LIMIT)["score"].pov(mover).score(mate_score=10000)
    board.pop()

    eval_drop = (after - before) / 100
    top_moves = [line["pv"][0] for line in engine.analyse(board, LIMIT, multipv=MULTIPV) if line.get("pv")]
    return eval_drop < BLUNDER_THRESHOLD and move not in top_moves


def test_castling_is_not_a_blunder(engine):
    board = chess.Board("r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 6")
    assert not is_blunder(engine, board, chess.Move.from_uci("e1g1"))


def test_hanging_the_queen_is_a_blunder(engine):
    # 1.e4 d5 2.Qg4?? drops the queen to ...Bxg4
    board = chess.Board("rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 2")
    assert is_blunder(engine, board, chess.Move.from_uci("d1g4"))
