import os

import chess
from flask import Flask, jsonify, render_template, request

from Engine.chess_suggester import ChessSuggester

try:
    from Engine.enhanced_engine import EnhancedChessSuggester
except ImportError:  # numpy / scikit-learn not installed (e.g. minimal deploy)
    EnhancedChessSuggester = None

app = Flask(__name__,
            static_folder='UI/chesswebapp/static',
            template_folder='UI/chesswebapp/templates')


def build_suggester():
    if EnhancedChessSuggester is not None:
        enhanced = EnhancedChessSuggester()
        if enhanced.use_model:
            return enhanced
    return ChessSuggester()


# Stateless: every request carries its own FEN, so one shared suggester is safe.
chess_suggester = build_suggester()


@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response


def board_from_request(payload):
    fen = payload.get('fen') or chess.STARTING_FEN
    try:
        return chess.Board(fen), None
    except ValueError as exc:
        return None, (jsonify({'status': 'error', 'message': f'Invalid FEN: {exc}'}), 400)


def position_payload(board):
    return {
        'fen': board.fen(),
        'is_check': board.is_check(),
        'is_checkmate': board.is_checkmate(),
        'is_stalemate': board.is_stalemate(),
        'is_insufficient_material': board.is_insufficient_material(),
        'is_game_over': board.is_game_over(),
        'turn': 'white' if board.turn else 'black',
    }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/move', methods=['POST'])
def move():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({'status': 'error', 'message': 'Invalid or missing JSON'}), 400

    move_uci = payload.get('move')
    if not move_uci:
        return jsonify({'status': 'error', 'message': 'No move provided'}), 400

    board, error = board_from_request(payload)
    if error:
        return error

    try:
        move = chess.Move.from_uci(move_uci)
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Invalid move format'}), 400

    if move not in board.legal_moves:
        return jsonify({'status': 'illegal', 'fen': board.fen()})

    board.push(move)
    return jsonify({'status': 'ok', **position_payload(board)})


@app.route('/reset', methods=['POST'])
def reset():
    return jsonify({'status': 'reset', **position_payload(chess.Board())})


@app.route('/suggest', methods=['POST'])
def suggest_moves():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({'status': 'error', 'message': 'Invalid or missing JSON'}), 400

    board, error = board_from_request(payload)
    if error:
        return error

    return jsonify(chess_suggester.get_move_suggestions(board))


@app.route('/position', methods=['GET'])
def get_position():
    board, error = board_from_request(request.args)
    if error:
        return error
    return jsonify(position_payload(board))


if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug, host='127.0.0.1', port=int(os.environ.get('PORT', 5001)), threaded=True)
