"""Generate labelled training positions for Scripts/train_engine.py.

Games are played by Stockfish at a shallow depth with random moves mixed in
(so the data covers blunders and lopsided positions, not just balanced
ones), and every position is labelled with a deeper Stockfish evaluation
from White's perspective in pawns. Without Stockfish the heuristic engine
plays and labels instead, which is far weaker but keeps the pipeline usable.

Run from the repo root:  python Scripts/generate_synthetic_data.py [--games N]
"""
import argparse
import csv
import os
import random
import sys
import time

import chess
import chess.engine

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Engine.chess_suggester import ChessSuggester  # noqa: E402
from Engine.evaluation import find_stockfish  # noqa: E402

OPENINGS = {
    "Ruy Lopez": ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5"],
    "Italian Game": ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4"],
    "Sicilian Defense": ["e2e4", "c7c5", "g1f3", "d7d6", "d2d4", "c5d4", "f3d4"],
    "French Defense": ["e2e4", "e7e6", "d2d4", "d7d5"],
    "Caro-Kann": ["e2e4", "c7c6", "d2d4", "d7d5"],
    "Queen's Gambit": ["d2d4", "d7d5", "c2c4"],
    "King's Indian": ["d2d4", "g8f6", "c2c4", "g7g6", "b1c3", "f8g7"],
    "English Opening": ["c2c4", "e7e5"],
    "London System": ["d2d4", "d7d5", "c1f4"],
    "Scandinavian": ["e2e4", "d7d5", "e4d5", "d8d5"],
}

FIELDNAMES = ['position_fen', 'move_played', 'move_evaluation', 'position_evaluation',
              'game_outcome', 'player_rating', 'time_control', 'opening_name']

EVAL_CLAMP = 10.0      # pawns; keeps mates from dominating a regression
MATE_SCORE = 10000


class StockfishLabeller:
    def __init__(self, path, label_depth=10, play_depth=4):
        self.engine = chess.engine.SimpleEngine.popen_uci(path)
        self.engine.configure({"Threads": 1, "Hash": 32})
        self.label_limit = chess.engine.Limit(depth=label_depth)
        self.play_limit = chess.engine.Limit(depth=play_depth)

    def evaluate(self, board):
        info = self.engine.analyse(board, self.label_limit)
        return info["score"].white().score(mate_score=MATE_SCORE) / 100.0

    def choose_move(self, board):
        return self.engine.play(board, self.play_limit).move

    def close(self):
        self.engine.quit()


class HeuristicLabeller:
    def __init__(self):
        self.engine = ChessSuggester()

    def evaluate(self, board):
        return self.engine.evaluate_position(board)

    def choose_move(self, board):
        return self.engine.suggest_moves(board, limit=1)[0][0]

    def close(self):
        pass


def clamp(value):
    return max(-EVAL_CLAMP, min(EVAL_CLAMP, value))


def play_game(labeller, rng, random_move_prob=0.2, max_plies=120):
    board = chess.Board()
    opening_name, opening = rng.choice(list(OPENINGS.items()))
    rows = []
    rating = rng.randint(1200, 2800)
    time_control = rng.choice([1, 3, 5, 10, 15])

    for ply in range(max_plies):
        if board.is_game_over(claim_draw=True):
            break

        if ply < len(opening) and chess.Move.from_uci(opening[ply]) in board.legal_moves:
            move = chess.Move.from_uci(opening[ply])
        elif rng.random() < random_move_prob:
            move = rng.choice(list(board.legal_moves))
        else:
            move = labeller.choose_move(board)

        fen = board.fen()
        position_eval = clamp(labeller.evaluate(board))
        board.push(move)
        move_eval = clamp(labeller.evaluate(board))

        rows.append({
            'position_fen': fen,
            'move_played': move.uci(),
            'move_evaluation': round(move_eval, 2),
            'position_evaluation': round(position_eval, 2),
            'game_outcome': None,  # filled once the game ends
            'player_rating': rating,
            'time_control': time_control,
            'opening_name': opening_name,
        })

    outcome = board.result(claim_draw=True)
    for row in rows:
        row['game_outcome'] = outcome
    return rows


def generate_dataset(num_games, seed=42, labeller=None):
    rng = random.Random(seed)
    rows = []
    started = time.time()
    for game_index in range(num_games):
        rows.extend(play_game(labeller, rng))
        if (game_index + 1) % 25 == 0:
            elapsed = time.time() - started
            print(f"  {game_index + 1}/{num_games} games, {len(rows)} positions, {elapsed:.0f}s")
    return rows


def save_to_csv(rows, filename='Data/training_data.csv'):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--games", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="Data/training_data.csv")
    args = parser.parse_args()

    stockfish = find_stockfish()
    if stockfish:
        print(f"Labelling with Stockfish at {stockfish}")
        labeller = StockfishLabeller(stockfish)
    else:
        print("Stockfish not found - labelling with the heuristic engine (much weaker labels)")
        labeller = HeuristicLabeller()

    try:
        rows = generate_dataset(args.games, seed=args.seed, labeller=labeller)
    finally:
        labeller.close()

    save_to_csv(rows, args.output)
    print(f"Generated {len(rows)} positions from {args.games} games -> {args.output}")


if __name__ == "__main__":
    main()
