# ♟️ Foundation Chess Engine

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Chess](https://img.shields.io/badge/Chess-Engine-black.svg)
![ML](https://img.shields.io/badge/ML-Enhanced-orange.svg)
![Web](https://img.shields.io/badge/Web-App-Complete-brightgreen.svg)

**A comprehensive Python chess engine with machine learning-powered analysis, multiple interfaces, and real-time evaluation**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Architecture](#-architecture) • [API](#-api) • [Contributing](#-contributing)

</div>

---

## 🚀 Features

### 🧠 **Machine Learning Enhanced Analysis**
- **ML-Powered Evaluation**: Combines traditional chess evaluation with trained machine learning models
- **Feature Extraction**: Advanced position analysis including material, mobility, king safety, and pawn structure
- **Predictive Move Suggestions**: AI-driven move recommendations with confidence scores
- **Real-time Learning**: Continuously improves analysis through synthetic data training

### 🎮 **Multiple User Interfaces**
- **🌐 Modern Web Application**: Beautiful, responsive web interface
- **🎨 Pygame GUI**: Beautiful graphical interface with real-time evaluation bar and move history
- **💻 Command Line Interface**: Lightweight CLI for quick analysis and scripting
- **🌐 Web API**: RESTful API for integration with web applications
- **📊 Analysis Dashboard**: Comprehensive position analysis and visualization tools

### ♟️ **Advanced Chess Features**
- **Real-time Position Evaluation**: Live analysis with numerical and visual feedback
- **Blunder Detection**: Identifies poor moves and suggests improvements
- **Move Suggestion Engine**: Top 5 best moves with detailed explanations
- **Game State Analysis**: Check, checkmate, stalemate, and draw detection
- **Opening Database**: Support for opening theory and analysis
- **Interactive Chess Board**: Drag-and-drop piece movement with legal move validation

### 🎨 **Modern Web Interface**
- **Ghana Flag-Inspired Design**: Dark theme with red, gold, and green color scheme
- **Responsive Layout**: Works seamlessly on desktop, tablet, and mobile devices
- **Real-time Updates**: Live game state, evaluation, and move suggestions
- **Interactive Elements**: Click-to-play move suggestions, board flipping, game reset
- **Beautiful Animations**: Smooth transitions and gradient animations
- **Professional UI**: Glassmorphism effects and modern design principles

### 🔧 **Developer Tools**
- **Training Pipeline**: Complete ML model training and validation system
- **Data Analysis**: Comprehensive training data analysis and visualization
- **Testing Suite**: Extensive unit tests and integration tests
- **Performance Monitoring**: Real-time engine performance metrics

---

## 📦 Installation

### Prerequisites
- **Python 3.11+** (3.13 supported)
- **Stockfish** (optional; used by `Engine/evaluation.py`, the CLI, the Tkinter GUI and the FastAPI service when found on `PATH`, in `/opt/homebrew/bin`, `/usr/local/bin`, or via `STOCKFISH_PATH`). `brew install stockfish` on macOS.

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Bempong-Sylvester-Obese/Chess-Engine.git
   cd Chess-Engine
   ```

2. **Create a virtual environment and install dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements-dev.txt   # everything: desktop UIs, API, ML, tests
   # or, for just the web app:
   pip install -r requirements.txt
   ```

3. **Train the ML model** (optional — a trained model is already committed)
   ```bash
   python Scripts/train_engine.py
   ```

4. **Run the web application** (recommended)
   ```bash
   python app.py            # http://127.0.0.1:5001
   ```

---

## 🎯 Usage

### 🌐 Web Application (Recommended)
Launch the web interface from the repo root:
```bash
python app.py                        # http://127.0.0.1:5001
FLASK_DEBUG=1 python app.py          # with auto-reload
python UI/chesswebapp/run_webapp.py  # same, and opens your browser
```
The server is stateless: the browser holds the game and sends a FEN with every request, so several tabs can play independently.

**Features:**
- **Beautiful Dark Theme**: Ghana flag-inspired design with red, gold, and green accents
- **Interactive Chess Board**: Drag-and-drop piece movement with legal move validation
- **Real-time Analysis**: Live position evaluation with visual evaluation bar
- **Move Suggestions**: Click-to-play top 5 best moves with evaluations
- **Game Controls**: New game, board flip, and game reset functionality
- **Move History**: Complete game history with move notation

**Access**: Open your browser and go to `http://localhost:5001`

### 🎮 Graphical Interface (Pygame)
Launch Pygame-based chess interface:
```bash
python main.py
```

**Features:**
- Interactive chessboard with piece highlighting
- Real-time evaluation bar showing position strength
- Move history with last move highlighting
- Keyboard shortcuts (R: Reset, U: Undo)

### 🖼️ Graphical Interface (Tkinter)
```bash
python -m UI.gui
```
Requires a Python build with `tkinter` (`brew install python-tk@3.13` on macOS Homebrew).

### 💻 Command Line Interface
For quick analysis and scripting:
```bash
python -m UI.cli
```

**Features:**
- ASCII chessboard display
- UCI move input format
- Position evaluation output
- Game state tracking

### 🌐 Web API
Start the FastAPI server from the repo root:
```bash
uvicorn API.server:app --reload      # http://127.0.0.1:8000/docs
```

**Available Endpoints** (prefix `/api/v1`):
- `POST /move` - Make a move (`{"move": "e2e4"}`, promotions as `e7e8q`)
- `POST /undo` - Undo the last move
- `GET /state` - Current FEN, turn, evaluation, legal moves
- `GET /best-move?depth=15` - Engine's best move
- `POST /reset` - Reset the game

### 🔬 Advanced Analysis
Run comprehensive analysis tools:
```bash
# Train ML model
python Scripts/train_engine.py

# Analyze training data
python Scripts/analyze_training_data.py

# Generate synthetic data
python Scripts/generate_synthetic_data.py

# Visualize analysis
python Scripts/visualize_analysis.py
```

---

## 🏗️ Architecture

### System Overview

```mermaid
graph TB
    subgraph "User Interfaces"
        WEB[🌐 Web Application]
        GUI[🎨 Pygame GUI]
        CLI[💻 Command Line]
        API[🌐 Web API]
    end
    
    subgraph "Core Engine"
        ENGINE[🧠 Enhanced Engine]
        EVAL[📊 Evaluation]
        SUGGEST[💡 Move Suggester]
        BOARD[♟️ Board Logic]
    end
    
    subgraph "Machine Learning"
        ML[🤖 ML Model]
        FEATURES[🔍 Feature Extraction]
        TRAINING[📈 Training Pipeline]
        DATA[📊 Data Analysis]
    end
    
    subgraph "Data & Storage"
        MODEL[💾 Trained Model]
        DATASET[📁 Training Data]
        PLOTS[📈 Analysis Plots]
    end
    
    WEB --> ENGINE
    GUI --> ENGINE
    CLI --> ENGINE
    API --> ENGINE
    
    ENGINE --> EVAL
    ENGINE --> SUGGEST
    ENGINE --> BOARD
    
    EVAL --> ML
    SUGGEST --> ML
    ML --> FEATURES
    FEATURES --> TRAINING
    TRAINING --> DATA
    
    ML --> MODEL
    TRAINING --> DATASET
    DATA --> PLOTS
    
    style WEB fill:#e1f5fe
    style GUI fill:#f3e5f5
    style CLI fill:#e8f5e8
    style API fill:#fff3e0
    style ENGINE fill:#ffebee
    style ML fill:#f1f8e9
```

### Web Application Architecture

```mermaid
graph LR
    subgraph "Frontend"
        HTML[HTML5]
        CSS[CSS3 - Ghana Theme]
        JS[JavaScript]
        CHESSBOARD[Chessboard.js]
    end
    
    subgraph "Backend"
        FLASK[Flask Server]
        CHESS_JS[Chess.js]
        ENGINE[Python Engine]
    end
    
    subgraph "API"
        MOVE[/move]
        SUGGEST[/suggest]
        RESET[/reset]
        ANALYZE[/analyze]
    end
    
    HTML --> FLASK
    CSS --> FLASK
    JS --> FLASK
    CHESSBOARD --> FLASK
    
    FLASK --> MOVE
    FLASK --> SUGGEST
    FLASK --> RESET
    FLASK --> ANALYZE
    
    MOVE --> ENGINE
    SUGGEST --> ENGINE
    RESET --> ENGINE
    ANALYZE --> ENGINE
    
    style HTML fill:#e8f5e8
    style CSS fill:#fff3e0
    style JS fill:#ffebee
    style FLASK fill:#e1f5fe
```

### Data Flow

```mermaid
flowchart LR
    subgraph "Input"
        POSITION[Chess Position]
        MOVE[Player Move]
    end
    
    subgraph "Processing"
        FEATURES[Extract Features]
        EVAL[Evaluate Position]
        ML[ML Analysis]
        SUGGEST[Generate Suggestions]
    end
    
    subgraph "Output"
        EVAL_BAR[Evaluation Bar]
        MOVES[Best Moves]
        ANALYSIS[Position Analysis]
    end
    
    POSITION --> FEATURES
    MOVE --> FEATURES
    
    FEATURES --> EVAL
    FEATURES --> ML
    
    EVAL --> SUGGEST
    ML --> SUGGEST
    
    SUGGEST --> MOVES
    EVAL --> EVAL_BAR
    ML --> ANALYSIS
    
    style POSITION fill:#e3f2fd
    style MOVE fill:#e3f2fd
    style FEATURES fill:#f3e5f5
    style EVAL fill:#e8f5e8
    style ML fill:#fff3e0
    style SUGGEST fill:#ffebee
    style EVAL_BAR fill:#e1f5fe
    style MOVES fill:#f1f8e9
    style ANALYSIS fill:#fce4ec
```

### Training Pipeline

```mermaid
flowchart TD
    subgraph "Data Collection"
        GAMES[Chess Games]
        SYNTHETIC[Synthetic Data]
        ANALYSIS[Position Analysis]
    end
    
    subgraph "Feature Engineering"
        MATERIAL[Material Count]
        MOBILITY[Piece Mobility]
        KING_SAFETY[King Safety]
        PAWN_STRUCT[Pawn Structure]
    end
    
    subgraph "Model Training"
        FEATURES[Feature Matrix]
        LABELS[Position Labels]
        TRAIN[Train Model]
        VALIDATE[Validate Model]
    end
    
    subgraph "Deployment"
        SAVE[Save Model]
        INTEGRATE[Integrate with Engine]
        MONITOR[Monitor Performance]
    end
    
    GAMES --> FEATURES
    SYNTHETIC --> FEATURES
    ANALYSIS --> FEATURES
    
    MATERIAL --> FEATURES
    MOBILITY --> FEATURES
    KING_SAFETY --> FEATURES
    PAWN_STRUCT --> FEATURES
    
    FEATURES --> TRAIN
    LABELS --> TRAIN
    TRAIN --> VALIDATE
    VALIDATE --> SAVE
    SAVE --> INTEGRATE
    INTEGRATE --> MONITOR
    
    style GAMES fill:#e8f5e8
    style SYNTHETIC fill:#e8f5e8
    style ANALYSIS fill:#e8f5e8
    style FEATURES fill:#fff3e0
    style TRAIN fill:#ffebee
    style SAVE fill:#e1f5fe
```

### Component Interaction

```mermaid
sequenceDiagram
    participant User
    participant Web
    participant Engine
    participant ML
    participant Board
    
    User->>Web: Make Move
    Web->>Engine: Process Move
    Engine->>Board: Update Position
    Board->>Engine: New Position
    
    Engine->>ML: Request Analysis
    ML->>Engine: Evaluation & Suggestions
    
    Engine->>Web: Return Results
    Web->>User: Display Analysis
    
    Note over Engine,ML: Real-time evaluation
    Note over Web,User: Visual feedback
```

```
Chess-Engine/
├── app.py                    # Flask web app (entry point for the web UI and Vercel)
├── wsgi.py / vercel.json     # Vercel deployment
├── main.py                   # Pygame desktop UI with live analysis panel
├── requirements.txt          # Runtime deps for the web app
├── requirements-dev.txt      # Desktop UIs, API, ML pipeline, tests
├── pytest.ini / conftest.py  # Test configuration
├── Engine/                   # Core engine
│   ├── chess_suggester.py    # Material eval + 2-ply move ranking
│   ├── enhanced_engine.py    # Adds the trained regression model
│   ├── features.py           # Feature extraction shared with training
│   ├── evaluation.py         # Stockfish (if available) / material evaluation
│   └── board.py              # Board wrapper used by the API and UIs
├── API/                      # FastAPI service (uvicorn API.server:app)
├── UI/
│   ├── cli.py                # Command-line interface
│   ├── gui.py                # Tkinter interface
│   └── chesswebapp/          # Flask templates and static assets
├── Scripts/                  # Data generation, training, analysis
├── Data/                     # training_data.csv, trained_model.pkl, plots/
├── Tests/                    # pytest suite
└── Docs/
```

---

## 🔌 API Reference

### Core Engine API
```python
from Engine.enhanced_engine import EnhancedChessSuggester

# Initialize engine
engine = EnhancedChessSuggester()

# Get move suggestions
suggestions = engine.get_move_suggestions(board)
print(f"Evaluation: {suggestions['current_evaluation']}")
print(f"Best moves: {suggestions['suggested_moves']}")
```

### Web Application API
```bash
# Make a move
curl -X POST "http://localhost:5001/move" \
     -H "Content-Type: application/json" \
     -d '{"move": "e2e4"}'

# Get move suggestions
curl -X POST "http://localhost:5001/suggest" \
     -H "Content-Type: application/json" \
     -d '{"fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"}'

# Reset game
curl -X POST "http://localhost:5001/reset"
```

### Web API Endpoints
```bash
# Make a move
curl -X POST "http://localhost:8000/move" \
     -H "Content-Type: application/json" \
     -d '{"move": "e2e4"}'

# Get game state
curl "http://localhost:8000/state"

# Get best move
curl "http://localhost:8000/best-move?depth=15"
```

---

## 🧪 Testing

### Test Architecture

```mermaid
graph LR
    subgraph "Test Types"
        UNIT[Unit Tests]
        INTEGRATION[Integration Tests]
        API[API Tests]
        WEB[Web Tests]
        ML[ML Tests]
    end
    
    subgraph "Test Coverage"
        ENGINE[Engine Logic]
        EVAL[Evaluation]
        SUGGEST[Move Suggestions]
        WEB_UI[Web Interface]
        GUI[User Interface]
    end
    
    UNIT --> ENGINE
    INTEGRATION --> EVAL
    API --> SUGGEST
    WEB --> WEB_UI
    ML --> GUI
    
    style UNIT fill:#e8f5e8
    style INTEGRATION fill:#fff3e0
    style API fill:#ffebee
    style WEB fill:#e1f5fe
    style ML fill:#f3e5f5
```

Run the test suite from the repo root:
```bash
python -m pytest                      # all tests (~5s)
python -m pytest Tests/test_api.py    # one module
```
Stockfish-dependent tests are skipped automatically when it isn't installed.

---

## 📈 Performance

### Performance Metrics

```mermaid
graph LR
    subgraph "Speed"
        EVAL_TIME[< 1s Evaluation]
        MOVE_GEN[Fast Move Generation]
        ML_INFERENCE[Quick ML Inference]
        WEB_RESPONSE[< 100ms Web Response]
    end
    
    subgraph "Accuracy"
        ML_ACCURACY[70% ML Weight]
        TRADITIONAL[30% Traditional]
        COMBINED[Combined Analysis]
    end
    
    subgraph "Efficiency"
        MEMORY[Memory Optimized]
        SCALABLE[Scalable Design]
        MODULAR[Modular Architecture]
        RESPONSIVE[Responsive Web UI]
    end
    
    EVAL_TIME --> COMBINED
    MOVE_GEN --> COMBINED
    ML_INFERENCE --> COMBINED
    WEB_RESPONSE --> COMBINED
    
    ML_ACCURACY --> COMBINED
    TRADITIONAL --> COMBINED
    
    COMBINED --> MEMORY
    COMBINED --> SCALABLE
    COMBINED --> MODULAR
    COMBINED --> RESPONSIVE
    
    style EVAL_TIME fill:#e8f5e8
    style ML_ACCURACY fill:#fff3e0
    style MEMORY fill:#ffebee
    style WEB_RESPONSE fill:#e1f5fe
```

The engine features:
- **Real-time Analysis**: Sub-second position evaluation
- **ML Enhancement**: 70% ML + 30% traditional evaluation
- **Memory Efficient**: Optimized for large game trees
- **Scalable Architecture**: Modular design for easy extension
- **Fast Web Interface**: Responsive web application with < 100ms response times

---

## 🎨 Design System

### Ghana Flag-Inspired Theme

The web application features a beautiful dark theme inspired by the Ghana flag:

- **🇬🇭 Ghana Red** (`#ce1126`): Primary buttons and accents
- **🇬🇭 Ghana Gold** (`#fcd116`): Icons, highlights, and interactive elements
- **🇬🇭 Ghana Green** (`#006b3f`): Success states and background accents
- **Pure Black** (`#000000`): Main backgrounds for mysterious atmosphere
- **Animated Gradients**: Flowing background animations through Ghana colors

### Design Features
- **Glassmorphism Effects**: Modern blur and transparency effects
- **Smooth Animations**: Gradient shifts and hover transitions
- **Responsive Design**: Works perfectly on all device sizes
- **Professional UI**: Clean, modern interface with excellent UX

---

## 🤝 Contributing

### Contribution Workflow

```mermaid
flowchart TD
    A[Fork Repository] --> B[Create Feature Branch]
    B --> C[Make Changes]
    C --> D[Run Tests]
    D --> E{Tests Pass?}
    E -->|No| F[Fix Issues]
    F --> D
    E -->|Yes| G[Commit Changes]
    G --> H[Push to Branch]
    H --> I[Create Pull Request]
    I --> J[Code Review]
    J --> K{Approved?}
    K -->|No| L[Address Feedback]
    L --> J
    K -->|Yes| M[Merge to Main]
    
    style A fill:#e8f5e8
    style M fill:#e8f5e8
    style E fill:#ffebee
    style K fill:#ffebee
```

We welcome contributions! Please see our contributing guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup
```bash
pip install -r requirements-dev.txt

python -m pyflakes Engine Scripts API UI Tests app.py main.py   # lint
python -m pytest                                                # tests
FLASK_DEBUG=1 python app.py                                     # web dev server
```

Branches follow `fix/…`, `feat/…`, `refactor/…`, `docs/…`; open a PR against `main` and reference the issue it closes.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


<div align="center">

**Made with ♟️ and ❤️ by the Foundation Chess Engine Team**

</div>

