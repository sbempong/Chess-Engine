"""Train the evaluation model used by Engine.enhanced_engine.

Fits a linear model and a gradient-boosted model on Engine.features and
keeps whichever scores better on a held-out split. Run from the repo root
after Scripts/generate_synthetic_data.py.
"""
import argparse
import os
import pickle
import sys

import chess
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Engine.features import FEATURE_NAMES, extract_features  # noqa: E402


def prepare_training_data(data, max_samples=None):
    if max_samples and len(data) > max_samples:
        data = data.sample(max_samples, random_state=42)

    features, targets = [], []
    for fen, target in zip(data['position_fen'], data['position_evaluation']):
        try:
            board = chess.Board(fen)
        except ValueError as exc:
            print(f"Skipping bad FEN {fen!r}: {exc}")
            continue
        if board.is_game_over():
            continue  # the engines short-circuit these; no need to learn them
        features.append(extract_features(board))
        targets.append(float(target))
    return np.array(features), np.array(targets)


def candidate_models():
    return {
        "ridge": Ridge(alpha=1.0),
        "hist_gradient_boosting": HistGradientBoostingRegressor(
            max_iter=300, learning_rate=0.08, max_leaf_nodes=31, random_state=42),
    }


def evaluate(model, X, y):
    pred = model.predict(X)
    return {
        "r2": r2_score(y, pred),
        "mse": mean_squared_error(y, pred),
        "mae": mean_absolute_error(y, pred),
    }


def train(X, y):
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    best_name, best_model, best_metrics = None, None, None
    for name, model in candidate_models().items():
        model.fit(X_train, y_train)
        metrics = evaluate(model, X_val, y_val)
        print(f"  {name:24s} R²={metrics['r2']:.3f}  MSE={metrics['mse']:.3f}  MAE={metrics['mae']:.3f}")
        if best_metrics is None or metrics["r2"] > best_metrics["r2"]:
            best_name, best_model, best_metrics = name, model, metrics
    print(f"Selected: {best_name}")
    return best_model, best_metrics


def save_model(model, file_path='Data/trained_model.pkl'):
    with open(file_path, 'wb') as handle:
        pickle.dump(model, handle)
    print(f"Model saved to {file_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="Data/training_data.csv")
    parser.add_argument("--output", default="Data/trained_model.pkl")
    parser.add_argument("--max-samples", type=int, default=None)
    args = parser.parse_args()

    data = pd.read_csv(args.data)
    print(f"Loaded {len(data)} rows from {args.data}")
    X, y = prepare_training_data(data, args.max_samples)
    print(f"Training on {len(X)} positions with {X.shape[1]} features: {', '.join(FEATURE_NAMES)}")

    model, metrics = train(X, y)
    save_model(model, args.output)
    print(f"Validation R²={metrics['r2']:.3f}  MAE={metrics['mae']:.3f} pawns")


if __name__ == "__main__":
    main()
