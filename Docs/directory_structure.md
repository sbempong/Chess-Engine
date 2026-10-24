# Project Directory Structure

```
Chess-Engine/
├── app.py                     # Flask web app: serves UI/chesswebapp and the /move, /suggest, /position, /reset JSON routes
├── wsgi.py                    # WSGI entry point for Vercel / gunicorn
├── vercel.json, runtime.txt   # Vercel deployment config
├── main.py                    # Pygame desktop UI with evaluation bar and analysis panel
├── requirements.txt           # Runtime deps for the web app (chess, Flask, gunicorn)
├── requirements-dev.txt       # Everything else: pygame, numpy/sklearn/pandas, fastapi, pytest
├── pytest.ini, conftest.py    # Test config; conftest puts the repo root on sys.path
│
├── Engine/
│   ├── chess_suggester.py     # ChessSuggester: material evaluation + 2-ply move ranking
│   ├── enhanced_engine.py     # EnhancedChessSuggester: blends the trained model with material
│   ├── features.py            # extract_features() — the only definition, shared with training
│   ├── evaluation.py          # PositionEvaluator: Stockfish when available, material otherwise
│   └── board.py               # Board wrapper (history, PGN, result) used by API/ and UI/
│
├── API/                       # FastAPI service — run with: uvicorn API.server:app
│   ├── server.py              # create_app(), CORS
│   └── endpoints.py           # /api/v1/{move,undo,state,best-move,reset}
│
├── UI/
│   ├── cli.py                 # python -m UI.cli
│   ├── gui.py                 # python -m UI.gui (needs tkinter)
│   └── chesswebapp/
│       ├── run_webapp.py      # Launches app.py and opens a browser
│       ├── templates/index.html
│       └── static/
│           ├── app.js         # Front-end logic (chess.js 0.10 + chessboard.js 1.0)
│           ├── style.css
│           └── chessboardjs-1/   # Vendored chessboard.js, CSS and piece images
│
├── Scripts/                   # Run from the repo root, e.g. python Scripts/train_engine.py
│   ├── generate_synthetic_data.py
│   ├── analyze_training_data.py
│   ├── visualize_analysis.py
│   ├── train_engine.py        # Trains Data/trained_model.pkl
│   ├── run_pipeline.py        # generate → analyze → train → test
│   └── setup.py               # venv + requirements-dev + Stockfish check
│
├── Data/
│   ├── training_data.csv
│   ├── trained_model.pkl
│   └── plots/
│
├── Tests/                     # python -m pytest
│   ├── test_move_ranking.py   # Engine ranks the best move first for both colours
│   ├── test_evaluation.py     # PositionEvaluator, Stockfish discovery (skipped if absent)
│   ├── test_engine.py         # Material eval, draws, Board wrapper, training-data smoke test
│   ├── test_analysis_integration.py
│   ├── test_api.py            # Flask routes
│   ├── test_fastapi.py        # FastAPI routes
│   └── test_blunder.py        # Stockfish-based blunder detection (skipped if absent)
│
└── Docs/
    ├── README.md
    ├── ANALYSIS_FEATURES.md
    └── directory_structure.md
```

## Conventions

- Evaluations everywhere are **pawns from White's perspective**: positive favours White.
- The Flask app is stateless; the browser sends a FEN with each request.
- `Scripts/` and `Tests/` import `Engine` from the repo root — run them from there.
