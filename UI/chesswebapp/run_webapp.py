import os
import sys
import webbrowser
import time
from threading import Timer

def main():
    print("♔ Foundation Chess Engine Webapp ♔")
    print("=" * 50)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    
    os.chdir(project_root)
    print(f"Working directory: {os.getcwd()}")
    
    # Check if required files exist
    required_files = [
        'app.py',
        'UI/chesswebapp/templates/index.html',
        'UI/chesswebapp/static/style.css',
        'Engine/chess_suggester.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("Error: Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("\nPlease ensure all files are present before running the webapp.")
        return 1
    
    print("All required files found")
    
    import importlib.util
    for module, package in (("flask", "Flask"), ("chess", "chess")):
        if importlib.util.find_spec(module) is None:
            print(f"{package} is not installed. Please run: pip install -r requirements.txt")
            return 1
    print("Flask and chess are installed")
    
    print("\nStarting the chess webapp...")
    print("The webapp will be available at: http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    def open_browser():
        time.sleep(2)  
        try:
            webbrowser.open('http://localhost:5001')
            print("Browser opened automatically")
        except:
            print("Please open your browser and navigate to: http://localhost:5001")
    
    Timer(2, open_browser).start()
    
    # Import and run Flask app
    try:
        # Add the project root to Python path
        sys.path.insert(0, project_root)
        from app import app
        # Run without debug mode to avoid restart issues
        app.run(debug=False, host='0.0.0.0', port=5001, threaded=True)
    except KeyboardInterrupt:
        print("\n\nWebapp stopped. Goodbye!")
    except Exception as e:
        print(f"\nError starting webapp: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
