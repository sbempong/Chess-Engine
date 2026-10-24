"""Feature extraction shared by the trained model and the training scripts.

The feature vector layout is part of the trained model's contract
(Data/trained_model.pkl). Changing the order or meaning of features requires
retraining via Scripts/train_engine.py.
"""
import chess
import numpy as np

from Engine.piece_square_tables import positional_score

PIECE_VALUES = {
    chess.PAWN: 1.0,
    chess.KNIGHT: 3.0,
    chess.BISHOP: 3.0,
    chess.ROOK: 5.0,
    chess.QUEEN: 9.0,
    chess.KING: 100.0,
}

PIECE_ORDER = (chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING)

FEATURE_NAMES = (
    [f"{side}_{chess.piece_name(pt)}_material" for pt in PIECE_ORDER for side in ("white", "black")]
    + ["mobility", "white_king_center_distance", "black_king_center_distance",
       "doubled_pawns", "isolated_pawns", "game_phase", "positional_score"]
)


def _king_center_distance(board, color):
    square = board.king(color)
    if square is None:
        return 0.0
    return abs(3.5 - chess.square_file(square)) + abs(3.5 - chess.square_rank(square))


def _isolated_pawns(pawns):
    """Count pawns with no friendly pawn on an adjacent file."""
    files_with_pawns = {chess.square_file(sq) for sq in pawns}
    return sum(1 for sq in pawns
               if not ({chess.square_file(sq) - 1, chess.square_file(sq) + 1} & files_with_pawns))


def extract_features(board):
    """Return the model's feature vector for `board` as a numpy array.

    Signed so that positive values favour White.
    """
    features = []

    for piece_type in PIECE_ORDER:
        value = PIECE_VALUES[piece_type]
        features.append(len(board.pieces(piece_type, chess.WHITE)) * value)
        features.append(-len(board.pieces(piece_type, chess.BLACK)) * value)

    mobility = board.legal_moves.count()
    features.append(mobility if board.turn else -mobility)

    features.append(-_king_center_distance(board, chess.WHITE))
    features.append(_king_center_distance(board, chess.BLACK))

    doubled_pawns = 0
    white_pawns = board.pieces(chess.PAWN, chess.WHITE)
    black_pawns = board.pieces(chess.PAWN, chess.BLACK)
    for file_mask in chess.BB_FILES:
        doubled_pawns += max(0, len(white_pawns & file_mask) - 1)
        doubled_pawns -= max(0, len(black_pawns & file_mask) - 1)
    features.append(doubled_pawns)

    features.append(_isolated_pawns(white_pawns) - _isolated_pawns(black_pawns))

    features.append(len(board.piece_map()) / 32.0)

    features.append(positional_score(board) / 100.0)

    assert len(features) == len(FEATURE_NAMES)
    return np.array(features, dtype=float)
