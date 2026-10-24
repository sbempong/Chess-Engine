import atexit
import os
import shutil
import threading
from typing import Optional, Tuple

import chess
import chess.engine

# Piece values in centipawns
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

MATE_SCORE = 20000

STOCKFISH_CANDIDATES = (
    "/opt/homebrew/bin/stockfish",   # macOS, Apple Silicon Homebrew
    "/usr/local/bin/stockfish",      # macOS, Intel Homebrew
    "/usr/games/stockfish",          # Debian/Ubuntu
    "/usr/bin/stockfish",
    "./stockfish",
    "./stockfish.exe",
)


def find_stockfish() -> Optional[str]:
    """Return a path to a Stockfish binary, or None if none can be found.

    Checks the STOCKFISH_PATH environment variable, then PATH, then a few
    well-known install locations.
    """
    env_path = os.environ.get("STOCKFISH_PATH")
    if env_path and os.path.isfile(env_path):
        return env_path
    on_path = shutil.which("stockfish")
    if on_path:
        return on_path
    for candidate in STOCKFISH_CANDIDATES:
        if os.path.isfile(candidate):
            return candidate
    return None


def _register_shutdown(callback) -> None:
    """Run `callback` at interpreter exit, *before* non-daemon threads are joined.

    SimpleEngine runs its event loop on a non-daemon thread, and regular
    atexit hooks only fire after Python has finished joining such threads, so
    using atexit alone deadlocks on exit. threading._register_atexit is the
    hook concurrent.futures uses for exactly this situation.
    """
    register = getattr(threading, "_register_atexit", None)
    if register is not None:
        register(callback)
    else:  # pragma: no cover - Python < 3.9
        atexit.register(callback)


class PositionEvaluator:
    """Evaluates positions with Stockfish when available, otherwise by material.

    All scores are in pawns from White's perspective: positive favours White,
    negative favours Black, regardless of who is to move.
    """

    def __init__(self, stockfish_path: Optional[str] = None, use_stockfish: bool = True):
        self.engine: Optional[chess.engine.SimpleEngine] = None
        self._path = stockfish_path
        self._use_stockfish = use_stockfish
        self._started = False

    def _ensure_engine(self) -> Optional[chess.engine.SimpleEngine]:
        if self._started or not self._use_stockfish:
            return self.engine
        self._started = True
        path = self._path or find_stockfish()
        if path is None:
            return None
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(path)
            _register_shutdown(self.close)
        except (OSError, chess.engine.EngineError) as exc:
            print(f"Warning: could not start Stockfish at {path}: {exc}. Using material evaluation.")
            self.engine = None
        return self.engine

    @property
    def has_stockfish(self) -> bool:
        return self._ensure_engine() is not None

    def material_evaluation(self, board: chess.Board) -> float:
        if board.is_checkmate():
            return -MATE_SCORE / 100.0 if board.turn else MATE_SCORE / 100.0
        if board.is_game_over():
            return 0.0

        score = 0
        for piece_type, value in PIECE_VALUES.items():
            score += value * len(board.pieces(piece_type, chess.WHITE))
            score -= value * len(board.pieces(piece_type, chess.BLACK))
        return score / 100.0

    def evaluate_position(self, board: chess.Board, depth: int = 15) -> float:
        # Mate and decided draws are definitive; don't ask the engine (older
        # Stockfish builds return small non-zero scores for dead draws).
        if board.is_game_over():
            return self.material_evaluation(board)
        engine = self._ensure_engine()
        if engine is None:
            return self.material_evaluation(board)
        try:
            info = engine.analyse(board, chess.engine.Limit(depth=depth))
            score = info.get("score")
            if score is None:
                return self.material_evaluation(board)
            return score.white().score(mate_score=MATE_SCORE) / 100.0
        except chess.engine.EngineError as exc:
            print(f"Warning: Stockfish evaluation failed: {exc}")
            return self.material_evaluation(board)

    def get_best_move(self, board: chess.Board, depth: int = 15) -> Tuple[Optional[chess.Move], float]:
        if board.is_game_over():
            return None, self.material_evaluation(board)
        engine = self._ensure_engine()
        if engine is None:
            return self.get_simple_best_move(board)
        try:
            info = engine.analyse(board, chess.engine.Limit(depth=depth))
            pv = info.get("pv")
            score = info.get("score")
            if not pv or score is None:
                return self.get_simple_best_move(board)
            return pv[0], score.white().score(mate_score=MATE_SCORE) / 100.0
        except chess.engine.EngineError as exc:
            print(f"Warning: Stockfish analysis failed: {exc}")
            return self.get_simple_best_move(board)

    def get_simple_best_move(self, board: chess.Board) -> Tuple[Optional[chess.Move], float]:
        """One-ply material search. Returns (move, White-perspective score)."""
        best_move = None
        best_score = None
        prefer_higher = board.turn == chess.WHITE

        for move in board.legal_moves:
            board.push(move)
            score = self.material_evaluation(board)
            board.pop()
            if best_score is None or (score > best_score if prefer_higher else score < best_score):
                best_score = score
                best_move = move

        return best_move, (best_score if best_score is not None else self.material_evaluation(board))

    def close(self) -> None:
        if self.engine is not None:
            try:
                self.engine.quit()
            except chess.engine.EngineError:
                pass
            self.engine = None


_evaluator: Optional[PositionEvaluator] = None


def get_evaluator() -> PositionEvaluator:
    """Shared evaluator, created on first use rather than at import time."""
    global _evaluator
    if _evaluator is None:
        _evaluator = PositionEvaluator()
    return _evaluator


def evaluate_position(board: chess.Board, depth: int = 15) -> float:
    return get_evaluator().evaluate_position(board, depth)


def get_best_move(board: chess.Board, depth: int = 15) -> Tuple[Optional[chess.Move], float]:
    return get_evaluator().get_best_move(board, depth)
