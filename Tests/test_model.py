"""Sanity checks on Data/trained_model.pkl: it must track material and side
with the material-only engine on obvious positions."""
import os
import warnings

import chess
import numpy as np
import pytest

from Engine.enhanced_engine import load_model
from Engine.features import FEATURE_NAMES, extract_features

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Data", "trained_model.pkl")

START = chess.Board()
WHITE_UP_QUEEN = chess.Board("rnb1kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
BLACK_UP_QUEEN = chess.Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNB1KBNR w KQkq - 0 1")
WHITE_UP_ROOK = chess.Board("1nbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w Kk - 0 1")
BLACK_UP_ROOK = chess.Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/1NBQKBNR w Kk - 0 1")


@pytest.fixture(scope="module")
def model():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        loaded = load_model(MODEL_PATH)
    if loaded is None:
        pytest.skip("no trained model")
    return loaded


def predict(model, board):
    return float(model.predict(extract_features(board).reshape(1, -1))[0])


def test_model_matches_feature_layout(model):
    assert model.n_features_in_ == len(FEATURE_NAMES)


def test_start_position_is_near_zero(model):
    assert abs(predict(model, START)) < 1.0


def test_material_ordering(model):
    assert predict(model, BLACK_UP_QUEEN) < predict(model, BLACK_UP_ROOK) < predict(model, START) \
        < predict(model, WHITE_UP_ROOK) < predict(model, WHITE_UP_QUEEN)


def test_queen_advantage_is_substantial(model):
    assert predict(model, WHITE_UP_QUEEN) > 3.0
    assert predict(model, BLACK_UP_QUEEN) < -3.0


def test_batch_prediction_matches_single(model):
    boards = [START, WHITE_UP_QUEEN, BLACK_UP_ROOK]
    batch = model.predict(np.vstack([extract_features(b) for b in boards]))
    assert batch == pytest.approx([predict(model, b) for b in boards])
