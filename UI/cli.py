from typing import Optional

import chess

from Engine.evaluation import evaluate_position

class ChessCLI:
    def __init__(self):
        self.board = chess.Board()
        self.move_history = []
        
    def print_board(self):
        print("\n  a b c d e f g h")
        print(" +-----------------+")
        for rank in range(7, -1, -1):
            print(f"{rank + 1}|", end=" ")
            for file in range(8):
                square = chess.square(file, rank)
                piece = self.board.piece_at(square)
                if piece is None:
                    print(".", end=" ")
                else:
                    symbol = piece.symbol()
                    print(symbol, end=" ")
            print(f"|{rank + 1}")
        print(" +-----------------+")
        print("  a b c d e f g h")
        
    def get_move(self) -> Optional[chess.Move]:
        while True:
            try:
                move_str = input("\nEnter your move (e.g., 'e2e4') or 'quit' to exit: ")
                if move_str.lower() == 'quit':
                    return None
                    
                move = chess.Move.from_uci(move_str)
                if move in self.board.legal_moves:
                    return move
                else:
                    print("Illegal move! Try again.")
            except ValueError:
                print("Invalid move format! Use format like 'e2e4'.")
                
    def show_evaluation(self):
        eval_score = evaluate_position(self.board)
        print(f"\nPosition evaluation: {eval_score:+.2f}")
        
    def run(self):
        print("Welcome to Chess CLI!")
        print("Enter moves in UCI format (e.g., 'e2e4')")
        print("Type 'quit' to exit")
        
        while not self.board.is_game_over():
            self.print_board()
            print(f"\nCurrent turn: {'White' if self.board.turn else 'Black'}")
            
            move = self.get_move()
            if move is None:
                break
                
            self.board.push(move)
            self.move_history.append(move)
            self.show_evaluation()
            
        # Game over
        self.print_board()
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn else "White"
            print(f"\nCheckmate! {winner} wins!")
        elif self.board.is_stalemate():
            print("\nStalemate! The game is a draw.")
        elif self.board.is_insufficient_material():
            print("\nDraw due to insufficient material.")
        elif self.board.is_fifty_moves():
            print("\nDraw by fifty-move rule.")
        elif self.board.is_repetition():
            print("\nDraw by repetition.")
            
        print("\nGame Over!")

if __name__ == "__main__":
    game = ChessCLI()
    game.run()
