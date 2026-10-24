import chess

from Engine.piece_square_tables import positional_score


class ChessSuggester:
    """Material + piece-square-table move suggester.

    All evaluations are from White's perspective in pawns: positive favours
    White, negative favours Black. Move ranking takes the side to move into
    account, so the best move for the mover is always first regardless of
    colour. The positional term is small (tens of centipawns per piece) so
    material always dominates; it exists to break ties between quiet moves.
    """

    suggestion_comment = "Heuristic evaluation"
    positional_weight = 1.0  # multiplier on the piece-square-table term

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

        return self.material_score(board) + self.positional_weight * positional_score(board) / 100.0

    def material_score(self, board):
        score = 0.0
        for piece_type, value in self.material_values.items():
            score += value * len(board.pieces(piece_type, chess.WHITE))
            score -= value * len(board.pieces(piece_type, chess.BLACK))
        return score

    def evaluate_positions(self, boards):
        """Evaluate many positions at once. Subclasses with a batch-friendly
        evaluator (e.g. an ML model) override this to avoid per-leaf overhead."""
        return [self.evaluate_position(board) for board in boards]

    def _collect_leaves(self, board, depth, leaves):
        """Build the minimax tree below `board`, appending leaf positions to
        `leaves`. Returns either ('leaf', index) or ('node', turn, children)."""
        if depth <= 0 or board.is_game_over():
            leaves.append(board.copy(stack=False))
            return ('leaf', len(leaves) - 1)
        children = []
        for move in board.legal_moves:
            board.push(move)
            children.append(self._collect_leaves(board, depth - 1, leaves))
            board.pop()
        return ('node', board.turn, children)

    @staticmethod
    def _resolve(node, scores):
        """Minimax over a tree from _collect_leaves using White-perspective
        leaf scores: White maximises, Black minimises."""
        if node[0] == 'leaf':
            return scores[node[1]]
        _, turn, children = node
        values = [ChessSuggester._resolve(child, scores) for child in children]
        return max(values) if turn == chess.WHITE else min(values)

    def suggest_moves(self, board, limit=5):
        if board.is_game_over():
            return []

        leaves = []
        roots = []
        for move in board.legal_moves:
            board.push(move)
            roots.append((move, self._collect_leaves(board, self.search_depth - 1, leaves)))
            board.pop()

        scores = self.evaluate_positions(leaves)
        mover_sign = 1 if board.turn == chess.WHITE else -1
        moves = [(move, self._resolve(node, scores), self.suggestion_comment) for move, node in roots]
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
