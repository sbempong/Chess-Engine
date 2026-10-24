import pickle

import chess
import numpy as np

from Engine.chess_suggester import ChessSuggester
from Engine.features import extract_features  # noqa: F401  (re-exported for backwards compatibility)


def load_model(file_path='Data/trained_model.pkl'):
    try:
        with open(file_path, 'rb') as f:
            model = pickle.load(f)
        print(f"Model loaded from {file_path}")
        return model
    except FileNotFoundError:
        print(f"Model file {file_path} not found")
        return None

class EnhancedChessSuggester(ChessSuggester):

    suggestion_comment = "Enhanced evaluation"

    def __init__(self, model_path='Data/trained_model.pkl', search_depth=2):
        super().__init__(search_depth=search_depth)
        self.model = load_model(model_path)
        self.use_model = self.model is not None
    
    MODEL_WEIGHT = 0.7

    def _model_available(self):
        return self.use_model and self.model is not None and hasattr(self.model, 'predict')

    def _blend(self, model_eval, material_eval):
        return self.MODEL_WEIGHT * float(model_eval) + (1 - self.MODEL_WEIGHT) * material_eval

    def evaluate_position(self, board):
        if board.is_game_over() or not self._model_available():
            return super().evaluate_position(board)
        model_eval = self.model.predict(extract_features(board).reshape(1, -1))[0]
        return self._blend(model_eval, super().evaluate_position(board))

    def evaluate_positions(self, boards):
        """One model.predict() call for every live position instead of one per
        leaf; sklearn's per-call overhead otherwise dominates the search."""
        if not self._model_available():
            return super().evaluate_positions(boards)

        scores = [None] * len(boards)
        live_indices = []
        for i, board in enumerate(boards):
            if board.is_game_over():
                scores[i] = super().evaluate_position(board)
            else:
                live_indices.append(i)

        if live_indices:
            features = np.vstack([extract_features(boards[i]) for i in live_indices])
            predictions = self.model.predict(features)
            for i, model_eval in zip(live_indices, predictions):
                scores[i] = self._blend(model_eval, super().evaluate_position(boards[i]))
        return scores


if __name__ == "__main__":
    # Example usage
    board = chess.Board()
    suggester = EnhancedChessSuggester()
    suggestions = suggester.get_move_suggestions(board)
    
    print(f"Current evaluation: {suggestions['current_evaluation']:.2f}")
    print(f"Check: {suggestions['is_check']}")
    print(f"Checkmate: {suggestions['is_checkmate']}")
    print(f"Stalemate: {suggestions['is_stalemate']}")
    print(f"Insufficient material: {suggestions['is_insufficient_material']}")
    
    print("\nSuggested moves:")
    for i, move in enumerate(suggestions['suggested_moves'], 1):
        print(f"{i}. {move['san']} (evaluation: {move['evaluation']:.2f}) - {move['comment']}") 