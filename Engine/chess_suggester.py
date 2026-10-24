import chess


class ChessSuggester:
    """Material-based move suggester.

    All evaluations are from White's perspective: positive favours White,
    negative favours Black. Move ranking takes the side to move into account,
    so the best move for the mover is always first regardless of colour.
    """

    suggestion_comment = "Heuristic evaluation"

    def __init__(self, search_depth=2):
        self.search_depth = search_depth
        self.material_values = {
            chess.PAWN: 1.0,
            chess.KNIGHT: 3.0,
            chess.BISHOP: 3.0,
            chess.ROOK: 5.0,
            chess.QUEEN: 9.0,
            chess.KING: 100.0
        }

    def evaluate_position(self, board):
        if board.is_game_over():
            if board.is_checkmate():
                return -10000.0 if board.turn else 10000.0
            return 0.0

        score = 0.0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is None:
                continue
            value = self.material_values[piece.piece_type]
            if piece.color:
                score += value
            else:
                score -= value
        return score

    def _score_after_move(self, board, move, depth):
        """White-perspective score of the position reached after `move`,
        assuming the opponent then picks the reply that is worst for us."""
        board.push(move)
        try:
            if depth <= 1 or board.is_game_over():
                return self.evaluate_position(board)
            replies = [self._score_after_move(board, reply, depth - 1)
                       for reply in board.legal_moves]
            return max(replies) if board.turn == chess.WHITE else min(replies)
        finally:
            board.pop()

    def suggest_moves(self, board, limit=5):
        if board.is_game_over():
            return []

        mover_sign = 1 if board.turn == chess.WHITE else -1
        moves = []
        for move in board.legal_moves:
            score = self._score_after_move(board, move, self.search_depth)
            moves.append((move, score, self.suggestion_comment))

        moves.sort(key=lambda item: mover_sign * item[1], reverse=True)
        return moves[:limit]

    def get_move_suggestions(self, board):
        current_eval = self.evaluate_position(board)
        move_suggestions = self.suggest_moves(board)

        formatted_suggestions = []
        for move, eval_score, comment in move_suggestions:
            formatted_suggestions.append({
                "move": move.uci(),
                "san": board.san(move),
                "evaluation": eval_score,
                "comment": comment
            })

        return {
            "current_evaluation": current_eval,
            "is_check": board.is_check(),
            "is_checkmate": board.is_checkmate(),
            "is_stalemate": board.is_stalemate(),
            "is_insufficient_material": board.is_insufficient_material(),
            "suggested_moves": formatted_suggestions
        }


if __name__ == "__main__":
    board = chess.Board()
    suggester = ChessSuggester()
    suggestions = suggester.get_move_suggestions(board)

    print(f"Current evaluation: {suggestions['current_evaluation']:.2f}")
    print(f"Check: {suggestions['is_check']}")
    print(f"Checkmate: {suggestions['is_checkmate']}")
    print(f"Stalemate: {suggestions['is_stalemate']}")
    print(f"Insufficient material: {suggestions['is_insufficient_material']}")

    print("\nSuggested moves:")
    for i, move in enumerate(suggestions['suggested_moves'], 1):
        print(f"{i}. {move['san']} (evaluation: {move['evaluation']:.2f}) - {move['comment']}")
