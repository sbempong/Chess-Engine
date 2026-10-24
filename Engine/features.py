"""Feature extraction shared by the trained model and the training scripts.

The feature vector layout is part of the trained model's contract
(Data/trained_model.pkl). Changing the order or meaning of features requires
retraining via Scripts/train_engine.py.
"""
import chess
import numpy as np

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
       "doubled_pawns", "isolated_pawns", "game_phase"]
)


def _king_center_distance(board, color):
    square = board.king(color)
    if square is None:
        return 0.0
    return abs(3.5 - chess.square_file(square)) + abs(3.5 - chess.square_rank(square))


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

    # Isolated pawns were never implemented in the original training run, so
    # the model was trained with this feature fixed at 0. Kept for layout
    # compatibility; implement and retrain together.
    features.append(0)

    features.append(len(board.piece_map()) / 32.0)

    assert len(features) == len(FEATURE_NAMES)
    return np.array(features, dtype=float)
