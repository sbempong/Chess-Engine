import chess
from typing import List, Optional, Tuple
from .evaluation import evaluate_position, get_best_move

class Board:
    def __init__(self):
        self.board = chess.Board()
        self.move_history = []
        
    def make_move(self, move: chess.Move) -> bool:
        if move in self.board.legal_moves:
            self.board.push(move)
            self.move_history.append(move)
            return True
        return False
        
    def reset(self) -> None:
        self.board.reset()
        self.move_history.clear()

    def undo_move(self) -> Optional[chess.Move]:
        if self.move_history:
            move = self.move_history.pop()
            self.board.pop()
            return move
        return None
        
    def get_legal_moves(self) -> List[chess.Move]:
        return list(self.board.legal_moves)
        
    def is_game_over(self) -> bool:
        return self.board.is_game_over()
        
    def get_game_result(self) -> Optional[str]:
        if not self.is_game_over():
            return None
            
        if self.board.is_checkmate():
            return "Checkmate"
        elif self.board.is_stalemate():
            return "Stalemate"
        elif self.board.is_insufficient_material():
            return "Draw by insufficient material"
        elif self.board.is_fifty_moves():
            return "Draw by fifty-move rule"
        elif self.board.is_repetition():
            return "Draw by repetition"
        return None
        
    def get_fen(self) -> str:
        return self.board.fen()
        
    def get_pgn(self) -> str:
        return self.board.variation_san(self.move_history)
        
    def get_evaluation(self, depth: int = 15) -> float:
        return evaluate_position(self.board, depth)
        
    def get_best_move(self, depth: int = 15) -> Tuple[Optional[chess.Move], float]:
        return get_best_move(self.board, depth)
        
    def is_check(self) -> bool:
        return self.board.is_check()
        
    def is_checkmate(self) -> bool:
        return self.board.is_checkmate()
        
    def is_stalemate(self) -> bool:
        return self.board.is_stalemate()
        
    def get_turn(self) -> bool:
        return self.board.turn
        
    def get_piece_at(self, square: int) -> Optional[chess.Piece]:
        return self.board.piece_at(square)
        
    def get_square_color(self, square: int) -> Optional[bool]:
        piece = self.get_piece_at(square)
        return piece.color if piece else None
    
    def reset(self):
        """Reset the board to the starting position."""
        self.board = chess.Board()
        self.move_history = [] 