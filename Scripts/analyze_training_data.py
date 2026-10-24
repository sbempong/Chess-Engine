import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import chess
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Engine.evaluation import evaluate_position  # noqa: E402

def load_training_data(file_path='Data/training_data.csv'):
    try:
        data = pd.read_csv(file_path)
        print(f"Loaded {len(data)} positions from training data")
        return data
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
        return None

def analyze_openings(data):
    if data is None or 'opening_name' not in data.columns:
        print("No opening data available")
        return
    
    opening_counts = data['opening_name'].value_counts()
    
    plt.figure(figsize=(12, 6))
    opening_counts.plot(kind='bar')
    plt.title('Distribution of Openings in Training Data')
    plt.xlabel('Opening')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig('Data/opening_distribution.png')
    plt.close()
    
    print("\nTop 5 openings:")
    for opening, count in opening_counts.head().items():
        print(f"{opening}: {count} positions")

def analyze_evaluations(data):
    if data is None:
        return
    
    # Create a histogram of position evaluations
    plt.figure(figsize=(12, 6))
    sns.histplot(data['position_evaluation'], bins=50)
    plt.title('Distribution of Position Evaluations')
    plt.xlabel('Evaluation')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig('Data/evaluation_distribution.png')
    plt.close()
    
    # Calculate statistics
    print("\nPosition Evaluation Statistics:")
    print(f"Mean: {data['position_evaluation'].mean():.2f}")
    print(f"Median: {data['position_evaluation'].median():.2f}")
    print(f"Std Dev: {data['position_evaluation'].std():.2f}")
    print(f"Min: {data['position_evaluation'].min():.2f}")
    print(f"Max: {data['position_evaluation'].max():.2f}")

def analyze_game_outcomes(data):
    if data is None or 'game_outcome' not in data.columns:
        print("No game outcome data available")
        return
    
    outcome_counts = data['game_outcome'].value_counts()
    
    plt.figure(figsize=(8, 8))
    plt.pie(outcome_counts, labels=outcome_counts.index, autopct='%1.1f%%')
    plt.title('Distribution of Game Outcomes')
    plt.tight_layout()
    plt.savefig('Data/outcome_distribution.png')
    plt.close()
    
    print("\nGame Outcome Distribution:")
    for outcome, count in outcome_counts.items():
        print(f"{outcome}: {count} games ({count/len(data)*100:.1f}%)")

def analyze_player_ratings(data):
    if data is None or 'player_rating' not in data.columns:
        print("No player rating data available")
        return
    
    plt.figure(figsize=(12, 6))
    sns.histplot(data['player_rating'], bins=50)
    plt.title('Distribution of Player Ratings')
    plt.xlabel('Rating')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig('Data/rating_distribution.png')
    plt.close()
    
    print("\nPlayer Rating Statistics:")
    print(f"Mean: {data['player_rating'].mean():.1f}")
    print(f"Median: {data['player_rating'].median():.1f}")
    print(f"Std Dev: {data['player_rating'].std():.1f}")
    print(f"Min: {data['player_rating'].min():.1f}")
    print(f"Max: {data['player_rating'].max():.1f}")

def compare_engine_with_training_data(data):
    if data is None:
        return
    
    # Sample 100 positions to compare
    sample_data = data.sample(min(100, len(data)))
    
    engine_evaluations = []
    training_evaluations = []
    
    for _, row in sample_data.iterrows():
        try:
            board = chess.Board(row['position_fen'])
            engine_eval = evaluate_position(board)
            engine_evaluations.append(engine_eval)
            training_evaluations.append(row['position_evaluation'])
        except Exception as e:
            print(f"Error processing position: {str(e)}")
    
    # Calculate correlation
    correlation = np.corrcoef(engine_evaluations, training_evaluations)[0, 1]
    print(f"\nCorrelation between engine and training evaluations: {correlation:.2f}")
    
    # Create scatter plot
    plt.figure(figsize=(10, 10))
    plt.scatter(training_evaluations, engine_evaluations, alpha=0.5)
    plt.plot([min(training_evaluations), max(training_evaluations)], 
             [min(training_evaluations), max(training_evaluations)], 'r--')
    plt.title('Engine vs Training Evaluations')
    plt.xlabel('Training Evaluation')
    plt.ylabel('Engine Evaluation')
    plt.tight_layout()
    plt.savefig('Data/evaluation_correlation.png')
    plt.close()

def main():
    print("Analyzing chess training data...")
    
    # Load the data
    data = load_training_data()
    if data is None:
        return
    
    # Run analyses
    analyze_openings(data)
    analyze_evaluations(data)
    analyze_game_outcomes(data)
    analyze_player_ratings(data)
    compare_engine_with_training_data(data)
    
    print("\nAnalysis complete. Results saved to Data/ directory.")

if __name__ == "__main__":
    main() 