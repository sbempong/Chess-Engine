import os
import pickle
import sys

import chess
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Engine.features import extract_features  # noqa: E402


def prepare_training_data(data, max_samples=10000):
    if data is None:
        return None, None
    
    if len(data) > max_samples:
        data = data.sample(max_samples, random_state=42) # Limit to max_samples
    
    X = []
    y = []
    
    for _, row in data.iterrows():
        try:
            board = chess.Board(row['position_fen'])
            features = extract_features(board)
            X.append(features)
            y.append(row['position_evaluation'])
        except Exception as e:
            print(f"Error processing position: {str(e)}")
    
    return np.array(X), np.array(y)

def train_model(X, y):
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_val)
    mse = mean_squared_error(y_val, y_pred)
    r2 = r2_score(y_val, y_pred)
    
    print(f"Mean Squared Error: {mse:.4f}")
    print(f"R² Score: {r2:.4f}")
    
    return model

def save_model(model, file_path='Data/trained_model.pkl'):
    with open(file_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"Model saved to {file_path}")

def main():
    print("Training chess engine using synthetic data...")
    
    data = pd.read_csv('Data/training_data.csv')
    if data is None:
        return
    
    X, y = prepare_training_data(data)
    if X is None or y is None:
        return
    
    model = train_model(X, y)
    
    save_model(model)
    
    print("Training complete.")

if __name__ == "__main__":
    main() 