import sys
import subprocess
import time

def run_script(script_name, description):
    print(f"\n{'='*80}")
    print(f"Running: {description}")
    print(f"{'='*80}\n")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            text=True,
            capture_output=True
        )
        print(result.stdout)
        
        if result.stderr:
            print("Errors/Warnings:")
            print(result.stderr)
            
        elapsed_time = time.time() - start_time
        print(f"\nCompleted in {elapsed_time:.2f} seconds")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}:")
        print(e.stdout)
        print(e.stderr)
        return False

def main():
    print("Starting Chess Engine Training Pipeline")
    print("==========")
    
    if not run_script("Scripts/generate_synthetic_data.py", "Generating synthetic chess training data"):
        print("Failed to generate synthetic data. Aborting pipeline.")
        return
    
    if not run_script("Scripts/analyze_training_data.py", "Analyzing training data"):
        print("Failed to analyze training data. Continuing with training...")
    
    if not run_script("Scripts/train_engine.py", "Training the chess engine"):
        print("Failed to train the engine. Aborting pipeline.")
        return
    
    if not run_script("Tests/test_engine.py", "Running engine tests"):
        print("Some tests failed. Please check the test output.")
    
    print("\nPipeline completed successfully!")
    print("You can now use the trained model in your chess engine.")

if __name__ == "__main__":
    main() 