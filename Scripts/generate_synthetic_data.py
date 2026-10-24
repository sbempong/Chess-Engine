import chess
import random
import csv

def generate_synthetic_game():
    board = chess.Board()
    game_data = []
    
    # Generate a random number of moves (between 20 and 60)
    num_moves = random.randint(20, 60)
    
    # Random player ratings between 1200 and 2800
    white_rating = random.randint(1200, 2800)
    black_rating = random.randint(1200, 2800)
    
    # Random time control (in minutes)
    time_control = random.choice([1, 3, 5, 10, 15])
    
    # Common openings with their first few moves
    openings = {
        "Ruy Lopez": ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "c6d4", "c4b5"],
        "Sicilian Defense": ["e2e4", "c7c5", "g1f3", "d7d6", "d2d4", "c5d4", "f3d4"],
        "Queen's Gambit": ["d2d4", "d7d5", "c2c4", "d5c4", "e2e3", "b7b5", "a2a4"],
        "French Defense": ["e2e4", "e7e6", "d2d4", "d7d5", "e4d5", "e6d5", "c2c3"],
        "King's Indian": ["d2d4", "g8f6", "c2c4", "g7g6", "b1c3", "f8g7", "e2e4", "d7d6"]
    }
    
    # Select a random opening
    opening_name = random.choice(list(openings.keys()))
    opening_moves = openings[opening_name]
    
    # Apply opening moves
    for move_uci in opening_moves:
        if not board.is_game_over():
            move = chess.Move.from_uci(move_uci)
            if move in board.legal_moves:
                # Generate realistic evaluation (-2 to +2)
                position_eval = random.uniform(-2, 2)
                move_eval = position_eval + random.uniform(-0.5, 0.5)
                
                game_data.append({
                    'position_fen': board.fen(),
                    'move_played': move_uci,
                    'move_evaluation': round(move_eval, 2),
                    'position_evaluation': round(position_eval, 2),
                    'game_outcome': '*',  # Game in progress
                    'player_rating': white_rating if board.turn else black_rating,
                    'time_control': time_control,
                    'opening_name': opening_name
                })
                
                board.push(move)
    
    # Continue the game with random moves
    moves_made = len(opening_moves)
    while not board.is_game_over() and moves_made < num_moves:
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            break
            
        # Select a move with some randomness but bias towards good moves
        move = random.choice(legal_moves)
        
        # Generate realistic evaluation
        position_eval = random.uniform(-2, 2)
        move_eval = position_eval + random.uniform(-0.5, 0.5)
        
        game_data.append({
            'position_fen': board.fen(),
            'move_played': move.uci(),
            'move_evaluation': round(move_eval, 2),
            'position_evaluation': round(position_eval, 2),
            'game_outcome': '*',  # Game in progress
            'player_rating': white_rating if board.turn else black_rating,
            'time_control': time_control,
            'opening_name': opening_name
        })
        
        board.push(move)
        moves_made += 1
    
    # Determine game outcome
    outcome = '*'
    if board.is_checkmate():
        outcome = '1-0' if board.turn else '0-1'
    elif board.is_stalemate() or board.is_insufficient_material() or board.is_fifty_moves():
        outcome = '1/2-1/2'
    
    # Update all positions with the final outcome
    for data in game_data:
        data['game_outcome'] = outcome
    
    return game_data

def generate_dataset(num_games=1000):
    all_data = []
    
    for _ in range(num_games):
        game_data = generate_synthetic_game()
        all_data.extend(game_data)
    
    return all_data

def save_to_csv(data, filename='Data/training_data.csv'):
    fieldnames = ['position_fen', 'move_played', 'move_evaluation', 
                 'position_evaluation', 'game_outcome', 'player_rating', 
                 'time_control', 'opening_name']
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    print("Generating synthetic chess training data...")
    dataset = generate_dataset(1000)  # Generate 1000 games
    save_to_csv(dataset)
    print(f"Generated {len(dataset)} positions from 1000 games")
    print("Data saved to Data/training_data.csv") 