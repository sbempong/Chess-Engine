import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    min_version = (3, 8)
    if sys.version_info < min_version:
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)

def create_virtual_env():
    venv_path = Path("venv")
    if not venv_path.exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"])
        
    if platform.system() == "Windows":
        activate_script = venv_path / "Scripts" / "activate.bat"
    else:
        activate_script = venv_path / "bin" / "activate"
        
    if not activate_script.exists():
        print(f"Error: Virtual environment activation script not found at {activate_script}")
        sys.exit(1)
        
    print(f"Virtual environment created at {venv_path}")
    print(f"To activate, run: source {activate_script}")

def install_dependencies():
    print("Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"])

def check_stockfish():
    try:
        import chess.engine
        engine = chess.engine.SimpleEngine.popen_uci("stockfish")
        engine.quit()
        print("Stockfish is properly installed and accessible")
    except Exception:
        print("Warning: Stockfish not found or not accessible")
        print("Please install Stockfish:")
        if platform.system() == "Darwin":  # macOS
            print("  brew install stockfish")
        elif platform.system() == "Linux":
            print("  sudo apt-get install stockfish")
        else:
            print("  Download from https://stockfishchess.org/download/")

def main():
    print("Setting up Chess Engine project...")
    
    check_python_version()
    create_virtual_env()
    install_dependencies()
    check_stockfish()
    
    print("\nSetup completed successfully!")
    print("\nNext steps:")
    print("1. Activate the virtual environment")
    print("2. Run the chess engine: python main.py")
    print("3. Or start the API server: uvicorn API.server:app --reload")

if __name__ == "__main__":
    main()
