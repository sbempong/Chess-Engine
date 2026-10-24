"""Generate data -> analyse -> train -> test. Run from the repo root."""
import subprocess
import sys
import time


def run_step(command, description):
    print(f"\n{'=' * 80}\nRunning: {description}\n{'=' * 80}\n")
    start = time.time()
    result = subprocess.run([sys.executable, *command], text=True, capture_output=True)
    print(result.stdout)
    if result.stderr:
        print("Errors/Warnings:")
        print(result.stderr)
    status = "Completed" if result.returncode == 0 else f"Failed (exit {result.returncode})"
    print(f"\n{status} in {time.time() - start:.2f} seconds")
    return result.returncode == 0


def main():
    print("Starting Chess Engine Training Pipeline")

    if not run_step(["Scripts/generate_synthetic_data.py"], "Generating training data"):
        print("Failed to generate data. Aborting pipeline.")
        return 1

    if not run_step(["Scripts/analyze_training_data.py"], "Analyzing training data"):
        print("Analysis failed. Continuing with training...")

    if not run_step(["Scripts/train_engine.py"], "Training the chess engine"):
        print("Failed to train the engine. Aborting pipeline.")
        return 1

    if not run_step(["-m", "pytest"], "Running the test suite"):
        print("Some tests failed. Please check the test output.")
        return 1

    print("\nPipeline completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
