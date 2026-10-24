import pathlib
import sys
import threading
from typing import List, Optional, Tuple

import chess
import pygame
from pygame._freetype import Font as FreeTypeFont, init as freetype_init

from Engine.chess_suggester import ChessSuggester
from Engine.enhanced_engine import EnhancedChessSuggester

MAX_VISIBLE_MOVE_PAIRS = 10

class ChessGame:
    def __init__(self):
        self.board = chess.Board()
        self.screen_size = (1000, 800)  
        self.square_size = 700 // 8 
        
        pygame.init()
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Chess Engine with Real-time Analysis")
        
        # Use _freetype directly (avoids pygame.font/sysfont circular import on Python 3.13)
        freetype_init()
        self.font = FreeTypeFont(None, 24)
        self.small_font = FreeTypeFont(None, 18)
        self.large_font = FreeTypeFont(None, 32)
        
        # Chess piece images
        self.pieces = {}
        self.load_pieces()
        
        # Initialize chess engines
        self.enhanced_engine = EnhancedChessSuggester()
        self.basic_engine = ChessSuggester()
        
        # Game state
        self.selected_square = None
        self.valid_moves = []
        self.move_history = []
        self.san_history = []
        self.analysis_data = None
        self._analysis_generation = 0
        self._analysis_lock = threading.Lock()
        self.analysis_pending = False
        
        # Analysis panel dimensions
        self.analysis_panel_x = 720
        self.analysis_panel_width = 280
        
        # Animated evaluation bar
        self.displayed_eval = 0.0
        self.eval_animation_speed = 0.15  # Higher = faster animation
        
        # Update analysis on initialization
        self.update_analysis()
        
    def load_pieces(self):
        piece_image_map = {
            'P': 'wP.png', 'N': 'wN.png', 'B': 'wB.png', 'R': 'wR.png', 'Q': 'wQ.png', 'K': 'wK.png',
            'p': 'bP.png', 'n': 'bN.png', 'b': 'bB.png', 'r': 'bR.png', 'q': 'bQ.png', 'k': 'bK.png',
        }
        # Use Wikipedia set from chessboardjs-1
        base_path = pathlib.Path(__file__).parent / 'UI' / 'chesswebapp' / 'static' / 'chessboardjs-1' / 'img' / 'chesspieces' / 'wikipedia'
        for symbol, filename in piece_image_map.items():
            try:
                image_path = (base_path / filename).resolve()
                image = pygame.image.load(str(image_path))
                image = pygame.transform.smoothscale(image, (self.square_size, self.square_size))
                self.pieces[symbol] = image
            except Exception as e:
                print(f"Error loading image {symbol} from {image_path}: {e}")
                self.pieces[symbol] = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
    
    @staticmethod
    def mobility(board: chess.Board, color: chess.Color) -> int:
        """Number of legal moves `color` would have if it were their turn."""
        if board.turn == color:
            return board.legal_moves.count()
        probe = board.copy(stack=False)
        probe.turn = color
        probe.ep_square = None
        return probe.legal_moves.count()

    def game_over_text(self) -> Optional[str]:
        if not self.board.is_game_over():
            return None
        if self.board.is_checkmate():
            return "Checkmate - " + ("Black" if self.board.turn else "White") + " wins"
        if self.board.is_stalemate():
            return "Draw - stalemate"
        if self.board.is_insufficient_material():
            return "Draw - insufficient material"
        if self.board.is_fifty_moves():
            return "Draw - fifty-move rule"
        if self.board.is_repetition():
            return "Draw - repetition"
        return "Draw"

    def update_analysis(self):
        """Run the engine on a worker thread so the render loop never blocks.
        Results for a position that has since changed are discarded."""
        self._analysis_generation += 1
        generation = self._analysis_generation
        snapshot = self.board.copy(stack=False)
        self.analysis_pending = True

        def work():
            try:
                result = self.enhanced_engine.get_move_suggestions(snapshot)
            except Exception as e:
                print(f"Error updating analysis: {e}")
                result = self.basic_engine.get_move_suggestions(snapshot)
            with self._analysis_lock:
                if generation == self._analysis_generation:
                    self.analysis_data = result
                    self.analysis_pending = False

        threading.Thread(target=work, daemon=True).start()
    
    def get_square_from_pos(self, pos: Tuple[int, int]) -> Optional[int]:
        x, y = pos
        # Process clicks within the chess board area
        if x >= self.square_size * 8:
            return None
            
        file_idx = x // self.square_size
        rank_idx = 7 - (y // self.square_size)  # Flip: Chess ranks from bottom-to-top
        
        if 0 <= file_idx < 8 and 0 <= rank_idx < 8:
            return chess.square(file_idx, rank_idx)
        return None
    
    def get_valid_moves(self, square: int) -> List[chess.Move]:
        valid_moves = []
        for move in self.board.legal_moves:
            if move.from_square == square:
                valid_moves.append(move)
        return valid_moves
    
    def highlight_square(self, square: int, color: Tuple[int, int, int, int] = (255, 255, 0, 128)):
        file_idx = chess.square_file(square)
        rank_idx = 7 - chess.square_rank(square)
        
        # Semi-transparent surface for highlighting
        highlight = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
        pygame.draw.rect(highlight, color, highlight.get_rect())
        
        # Highlight
        self.screen.blit(highlight, (file_idx * self.square_size, rank_idx * self.square_size))
        
    def draw_board(self):
        for row in range(8):
            for col in range(8):
                # Calculate square color
                color = (240, 217, 181) if (row + col) % 2 == 0 else (181, 136, 99)
                
                # Draw square
                pygame.draw.rect(
                    self.screen,
                    color,
                    (col * self.square_size, row * self.square_size, 
                     self.square_size, self.square_size)
                )
                
                # Draw piece if present
                square = chess.square(col, 7-row)  # Flip row: chess ranks from bottom-to-top
                piece = self.board.piece_at(square)
                if piece:
                    symbol = piece.symbol()
                    piece_surface = self.pieces.get(symbol)
                    if piece_surface:
                        self.screen.blit(piece_surface, (col * self.square_size, row * self.square_size))
                
                # Rank (1-8) on the left edge of each row
                if col == 0:
                    rank_num = str(8 - row)
                    rank_font = self.small_font
                    rank_color = (80, 80, 80)
                    rank_surf, _ = rank_font.render(rank_num, fgcolor=rank_color)
                    self.screen.blit(rank_surf, (4, row * self.square_size + 4))
                #  File (a-h) on the bottom edge of each column
                if row == 7:
                    file_letter = chr(ord('a') + col)
                    file_font = self.small_font
                    file_color = (80, 80, 80)
                    file_surf, _ = file_font.render(file_letter, fgcolor=file_color)
                    self.screen.blit(file_surf, (col * self.square_size + self.square_size - 18, self.square_size * 8 - 20))
        
        # Highlight selected square
        if self.selected_square is not None:
            self.highlight_square(self.selected_square, (255, 255, 0, 128))  # Yellow highlight
            
            # Highlight valid moves
            for move in self.valid_moves:
                self.highlight_square(move.to_square, (0, 255, 0, 128))  # Green highlight
    
    def draw_right_panel(self):
        # Draw right panel background
        panel_x = self.square_size * 8
        panel_width = self.screen_size[0] - panel_x
        pygame.draw.rect(self.screen, (40, 40, 40), (panel_x, 0, panel_width, self.screen_size[1]))

        y_offset = 30
        # Draw avatar placeholder (circle with initials)
        avatar_center = (panel_x + panel_width // 2, y_offset + 40)
        pygame.draw.circle(self.screen, (200, 150, 100), avatar_center, 40)
        initials, _ = self.large_font.render('P', fgcolor=(255, 255, 255))
        initials_rect = initials.get_rect(center=avatar_center)
        self.screen.blit(initials, initials_rect)
        y_offset += 90

        # --- Enhanced Evaluation Bar ---
        bar_x = panel_x + panel_width // 2 - 20
        bar_y = y_offset
        bar_width = 40
        bar_height = 220
        radius = 12

        # Clamp and animate evaluation
        with self._analysis_lock:
            analysis = self.analysis_data
            pending = self.analysis_pending
        target_eval = analysis['current_evaluation'] if analysis else 0
        target_eval = max(min(target_eval, 5), -5)
        # Smooth animation
        self.displayed_eval += (target_eval - self.displayed_eval) * self.eval_animation_speed
        capped_eval = self.displayed_eval
        white_ratio = (capped_eval + 5) / 10  # 0 (all black) to 1 (all white)
        white_height = int(bar_height * white_ratio)

        # Create a surface for the bar (with per-pixel alpha)
        bar_surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)

        # Draw vertical gradient (white to black)
        for y in range(bar_height):
            t = y / bar_height
            # Interpolate color: white at top (t=0), black at bottom (t=1)
            color = (
                int(255 * (1 - t)),
                int(255 * (1 - t)),
                int(255 * (1 - t)),
                255
            )
            pygame.draw.rect(bar_surface, color, (0, y, bar_width, 1))

        # Draw rounded corners mask
        mask = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, bar_width, bar_height), border_radius=radius)
        bar_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Draw highlight/glow at the boundary
        boundary_y = white_height
        if 0 < boundary_y < bar_height:
            glow_color = (120, 200, 255, 120)
            pygame.draw.rect(bar_surface, glow_color, (0, boundary_y-2, bar_width, 4), border_radius=radius)

        # Draw border
        pygame.draw.rect(bar_surface, (200, 200, 200, 255), (0, 0, bar_width, bar_height), 2, border_radius=radius)

        # Blit the bar to the screen
        self.screen.blit(bar_surface, (bar_x, bar_y))

        # Draw numeric evaluation overlay (to the right of the bar, aligned with boundary)
        eval_text = f"{capped_eval:+.2f}"
        eval_render, _ = self.large_font.render(eval_text, fgcolor=(40, 120, 255))
        # Position: right of the bar, vertically at the boundary (clamp to bar edges)
        eval_y = bar_y + min(max(white_height, 0), bar_height - 1)
        eval_rect = eval_render.get_rect(midleft=(bar_x + bar_width + 16, eval_y))
        self.screen.blit(eval_render, eval_rect)

        # Draw W/B labels
        w_label, _ = self.small_font.render('W', fgcolor=(255, 255, 255))
        b_label, _ = self.small_font.render('B', fgcolor=(0, 0, 0))
        self.screen.blit(w_label, (bar_x + bar_width + 8, bar_y - 5))
        self.screen.blit(b_label, (bar_x + bar_width + 8, bar_y + bar_height - 15))
        y_offset += bar_height + 30

        if pending:
            pending_text, _ = self.small_font.render('Analyzing...', fgcolor=(160, 160, 160))
            self.screen.blit(pending_text, (bar_x + bar_width + 16, bar_y + bar_height + 6))

        # In-depth Analysis Information
        if analysis:
            # Material imbalance
            white_material = sum([
                len(self.board.pieces(pt, chess.WHITE)) * val
                for pt, val in self.enhanced_engine.material_values.items()
            ])
            black_material = sum([
                len(self.board.pieces(pt, chess.BLACK)) * val
                for pt, val in self.enhanced_engine.material_values.items()
            ])
            material_imbalance = white_material - black_material
            material_text = f"Material: W {white_material:.1f} / B {black_material:.1f} (Δ {material_imbalance:+.1f})"
            material_render, _ = self.font.render(material_text, fgcolor=(220, 220, 220))
            self.screen.blit(material_render, (panel_x + 20, y_offset))
            y_offset += 28

            # Mobility
            white_mobility = self.mobility(self.board, chess.WHITE)
            black_mobility = self.mobility(self.board, chess.BLACK)
            mobility_text = f"Mobility: W {white_mobility} / B {black_mobility}"
            mobility_render, _ = self.font.render(mobility_text, fgcolor=(200, 200, 200))
            self.screen.blit(mobility_render, (panel_x + 20, y_offset))
            y_offset += 24

            # King safety (distance from center)
            wk_sq = self.board.king(chess.WHITE)
            bk_sq = self.board.king(chess.BLACK)
            wk_dist = abs(3.5 - chess.square_file(wk_sq)) + abs(3.5 - chess.square_rank(wk_sq)) if wk_sq is not None else 0
            bk_dist = abs(3.5 - chess.square_file(bk_sq)) + abs(3.5 - chess.square_rank(bk_sq)) if bk_sq is not None else 0
            king_safety_text = f"King Center Dist: W {wk_dist:.1f} / B {bk_dist:.1f}"
            king_safety_render, _ = self.font.render(king_safety_text, fgcolor=(180, 180, 255))
            self.screen.blit(king_safety_render, (panel_x + 20, y_offset))
            y_offset += 24

            # Pawn structure (doubled pawns)
            doubled_white = sum([max(0, len(self.board.pieces(chess.PAWN, chess.WHITE) & chess.BB_FILES[file]) - 1) for file in range(8)])
            doubled_black = sum([max(0, len(self.board.pieces(chess.PAWN, chess.BLACK) & chess.BB_FILES[file]) - 1) for file in range(8)])
            pawn_structure_text = f"Doubled Pawns: W {doubled_white} / B {doubled_black}"
            pawn_structure_render, _ = self.font.render(pawn_structure_text, fgcolor=(200, 180, 180))
            self.screen.blit(pawn_structure_render, (panel_x + 20, y_offset))
            y_offset += 24

            # Game phase
            total_pieces = len(self.board.piece_map())
            if total_pieces > 24:
                phase = "Opening"
            elif total_pieces > 12:
                phase = "Middlegame"
            else:
                phase = "Endgame"
            phase_text = f"Game Phase: {phase}"
            phase_render, _ = self.font.render(phase_text, fgcolor=(180, 255, 180))
            self.screen.blit(phase_render, (panel_x + 20, y_offset))
            y_offset += 28

            # Human-readable position assessment
            eval_score = analysis['current_evaluation']
            game_over = self.game_over_text()
            if game_over:
                assessment = game_over
            elif abs(eval_score) > 3.0:
                assessment = "White is winning" if eval_score > 0 else "Black is winning"
            elif abs(eval_score) > 1.0:
                assessment = "White is better" if eval_score > 0 else "Black is better"
            else:
                assessment = "Equal position"
            assessment_text = f"Assessment: {assessment}"
            assessment_render, _ = self.font.render(assessment_text, fgcolor=(255, 220, 120))
            self.screen.blit(assessment_render, (panel_x + 20, y_offset))
            y_offset += 32

        # Move list in two columns, showing only the most recent pairs
        pairs = [(self.san_history[i], self.san_history[i + 1] if i + 1 < len(self.san_history) else '')
                 for i in range(0, len(self.san_history), 2)]
        first_pair = max(0, len(pairs) - MAX_VISIBLE_MOVE_PAIRS)
        col1_x = panel_x + 30
        col2_x = panel_x + panel_width // 2
        row_height = 32
        y_offset += 10
        for row, pair_idx in enumerate(range(first_pair, len(pairs))):
            move1, move2 = pairs[pair_idx]
            is_last_pair = pair_idx == len(pairs) - 1
            font1 = self.large_font if is_last_pair and not move2 else self.font
            font2 = self.large_font if is_last_pair and move2 else self.font
            y = y_offset + row * row_height
            move_num_text, _ = self.small_font.render(f'{pair_idx + 1}.', fgcolor=(180, 180, 180))
            self.screen.blit(move_num_text, (col1_x - 25, y))
            move1_text, _ = font1.render(move1, fgcolor=(255, 255, 255))
            self.screen.blit(move1_text, (col1_x, y))
            if move2:
                move2_text, _ = font2.render(move2, fgcolor=(255, 255, 255))
                self.screen.blit(move2_text, (col2_x, y))

        # Game-over banner across the board
        banner = self.game_over_text()
        if banner:
            overlay = pygame.Surface((self.square_size * 8, 60), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            self.screen.blit(overlay, (0, self.square_size * 4 - 30))
            text, _ = self.large_font.render(banner + "  (R to restart)", fgcolor=(255, 230, 120))
            self.screen.blit(text, text.get_rect(center=(self.square_size * 4, self.square_size * 4)))

    def handle_click(self, pos: tuple[int, int]) -> Optional[chess.Move]:
        if self.board.is_game_over():
            return None
        square = self.get_square_from_pos(pos)
        if square is None:
            return None
            
        # If a square is already selected
        if self.selected_square is not None:
            # Check if the clicked square is a valid move
            for move in self.valid_moves:
                if move.to_square == square:
                    # Make the move
                    self.san_history.append(self.board.san(move))
                    self.board.push(move)
                    self.move_history.append(move)
                    
                    # Reset selection
                    self.selected_square = None
                    self.valid_moves = []
                    
                    # Update analysis after move
                    self.update_analysis()
                    return move
                    
            # If clicked on a different piece of the same color, select that piece instead
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.selected_square = square
                self.valid_moves = self.get_valid_moves(square)
                return None
                
            # If clicked elsewhere, deselect
            self.selected_square = None
            self.valid_moves = []
            return None
            
        # If no square is selected, select the clicked square if it has a piece of the current player's color
        piece = self.board.piece_at(square)
        if piece and piece.color == self.board.turn:
            self.selected_square = square
            self.valid_moves = self.get_valid_moves(square)
            
        return None
        
    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Reset game with 'R' key
                        self.board = chess.Board()
                        self.selected_square = None
                        self.valid_moves = []
                        self.move_history = []
                        self.san_history = []
                        self.update_analysis()
                    elif event.key == pygame.K_u:  # Undo move with 'U' key
                        if self.move_history:
                            self.board.pop()
                            self.move_history.pop()
                            self.san_history.pop()
                            self.selected_square = None
                            self.valid_moves = []
                            self.update_analysis()
            
            # Clear screen
            self.screen.fill((30, 30, 30))
            
            # Draw the current state
            self.draw_board()
            self.draw_right_panel()
            
            pygame.display.flip()
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = ChessGame()
    game.run()
