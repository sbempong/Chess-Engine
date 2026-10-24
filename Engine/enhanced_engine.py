import pickle

import chess

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
    
    def evaluate_position(self, board):
        if board.is_game_over():
            if board.is_checkmate():
                return -10000.0 if board.turn else 10000.0
            return 0.0
        
        if self.use_model and self.model is not None and hasattr(self.model, 'predict'):
            # Extract features and use the model
            features = extract_features(board)
            model_eval = self.model.predict([features])[0]
            
            # Combine with material evaluation (weighted average)
            material_eval = super().evaluate_position(board)
            combined_eval = 0.7 * model_eval + 0.3 * material_eval
            
            return combined_eval
        else:
            # Fall back to the original evaluation
            return super().evaluate_position(board)
    
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