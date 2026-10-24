import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import chess
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Engine.chess_suggester import ChessSuggester  # noqa: E402
from Engine.enhanced_engine import EnhancedChessSuggester  # noqa: E402

def load_training_data(file_path='Data/training_data.csv'):
    try:
        df = pd.read_csv(file_path)
        print(f"Loaded {len(df)} positions from {file_path}")
        return df
    except FileNotFoundError:
        print(f"Training data file {file_path} not found")
        return None

def plot_opening_distribution(df, top_n=10):
    plt.figure(figsize=(12, 6))
    
    opening_counts = df['opening_name'].value_counts().head(top_n)
    
    sns.barplot(x=opening_counts.values, y=opening_counts.index)
    plt.title(f'Top {top_n} Openings in Training Data')
    plt.xlabel('Number of Games')
    plt.ylabel('Opening')
    
    plt.tight_layout()
    plt.savefig('Data/plots/opening_distribution.png')
    plt.close()

def plot_evaluation_distribution(df):
    plt.figure(figsize=(10, 6))
    
    sns.histplot(data=df, x='position_evaluation', bins=50)
    plt.title('Distribution of Position Evaluations')
    plt.xlabel('Evaluation Score')
    plt.ylabel('Count')
    
    plt.axvline(x=0, color='r', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig('Data/plots/evaluation_distribution.png')
    plt.close()

def plot_game_outcomes(df):
    plt.figure(figsize=(8, 8))
    
    outcome_counts = df['game_outcome'].value_counts()
    
    plt.pie(outcome_counts.values, labels=outcome_counts.index, autopct='%1.1f%%')
    plt.title('Distribution of Game Outcomes')
    
    plt.tight_layout()
    plt.savefig('Data/plots/game_outcomes.png')
    plt.close()

def plot_player_ratings(df):
    plt.figure(figsize=(10, 5))
    sns.histplot(data=df, x='player_rating', bins=30)
    plt.title('Distribution of Player Ratings')
    plt.xlabel('Rating')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig('Data/plots/player_ratings.png')
    plt.close()

def plot_engine_comparison(df, num_positions=100):
    original_engine = ChessSuggester()
    enhanced_engine = EnhancedChessSuggester()
    
    sample_positions = df.sample(min(num_positions, len(df)))
    
    # Get evaluations from both engines
    original_evals = []
    enhanced_evals = []
    training_evals = []
    
    for _, row in sample_positions.iterrows():
        board = chess.Board(row['position_fen'])
        original_evals.append(original_engine.evaluate_position(board))
        enhanced_evals.append(enhanced_engine.evaluate_position(board))
        training_evals.append(row['position_evaluation'])
    
    plt.figure(figsize=(10, 10))
    
    plt.scatter(training_evals, original_evals, alpha=0.5, label='Original Engine')
    plt.scatter(training_evals, enhanced_evals, alpha=0.5, label='Enhanced Engine')
    
    min_val = min(min(training_evals), min(original_evals), min(enhanced_evals))
    max_val = max(max(training_evals), max(original_evals), max(enhanced_evals))
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.5)
    
    plt.title('Engine Evaluations vs Training Data')
    plt.xlabel('Training Data Evaluation')
    plt.ylabel('Engine Evaluation')
    plt.legend()
    
    # Save plot
    plt.tight_layout()
    plt.savefig('Data/plots/engine_comparison.png')
    plt.close()

def plot_evaluation_correlation(df):
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    corr_matrix = df[numeric_cols].corr()
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
    plt.title('Feature Correlation Matrix')

    plt.tight_layout()
    plt.savefig('Data/plots/feature_correlation.png')
    plt.close()

def create_plots_directory():
    plots_dir = Path('Data/plots')
    plots_dir.mkdir(parents=True, exist_ok=True)
    return plots_dir

def main():
    print("Generating visualizations for training data analysis...")
    
    plots_dir = create_plots_directory()
    print(f"Created plots directory at {plots_dir}")
    
    df = load_training_data()
    if df is None:
        return
    
    print("\nGenerating plots...")
    plot_opening_distribution(df)
    plot_evaluation_distribution(df)
    plot_game_outcomes(df)
    plot_player_ratings(df)
    plot_engine_comparison(df)
    plot_evaluation_correlation(df)
    
    print("\nAll plots have been saved to the Data/plots directory.")
    print("Generated the following visualizations:")
    print("1. Opening distribution (top 10 openings)")
    print("2. Position evaluation distribution")
    print("3. Game outcome distribution")
    print("4. Player rating distributions")
    print("5. Engine evaluation comparison")
    print("6. Feature correlation matrix")

if __name__ == "__main__":
    main() 