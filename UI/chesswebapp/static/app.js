/* global Chess, Chessboard, $ */
// chess.js 0.10.x API (snake_case): game_over(), in_check(), in_checkmate(),
// in_stalemate(), in_draw(), in_threefold_repetition(), insufficient_material().

(function () {
    'use strict';

    const EVAL_CLAMP = 5; // pawns; bar is full at ±5

    let board = null;
    let game = new Chess();
    let gameStartTime = Date.now();
    let moveHistory = [];
    let isGameOver = false;
    let suggestRequestId = 0;

    const $id = (id) => document.getElementById(id);
    const pieceTheme = window.CHESS_PIECE_THEME || 'img/chesspieces/wikipedia/{piece}.png';

    // ---------- board highlighting (chessboard.js 1.0 has no addCircle) ----------

    function highlightSquares(squares, cls) {
        squares.forEach((sq) => $('#board .square-' + sq).addClass(cls));
    }

    function clearHighlights() {
        $('#board .square-55d63').removeClass('highlight-move highlight-capture highlight-source');
    }

    // ---------- chessboard.js config ----------

    function onDragStart(source, piece) {
        if (isGameOver) return false;
        if ((game.turn() === 'w' && piece.charAt(0) === 'b') ||
            (game.turn() === 'b' && piece.charAt(0) === 'w')) {
            return false;
        }
        clearHighlights();
        highlightSquares([source], 'highlight-source');
        const moves = game.moves({ square: source, verbose: true });
        highlightSquares(moves.filter((m) => !m.captured).map((m) => m.to), 'highlight-move');
        highlightSquares(moves.filter((m) => m.captured).map((m) => m.to), 'highlight-capture');
        return true;
    }

    function onDrop(source, target) {
        clearHighlights();
        if (source === target) return 'snapback';
        return makeMove(source, target) ? undefined : 'snapback';
    }

    function onSnapEnd() {
        board.position(game.fen());
    }

    function initializeBoard() {
        board = Chessboard('board', {
            draggable: true,
            position: 'start',
            pieceTheme: pieceTheme,
            onDragStart: onDragStart,
            onDrop: onDrop,
            onSnapEnd: onSnapEnd,
        });
    }

    // ---------- game flow ----------

    function makeMove(source, target) {
        if (isGameOver) return false;
        const move = game.move({ from: source, to: target, promotion: 'q' });
        if (move === null) return false;

        board.position(game.fen());
        moveHistory.push(move);
        renderMoveHistory();
        updateGameState();
        requestAnalysis();
        return true;
    }

    function playSuggestion(uci) {
        const move = game.moves({ verbose: true }).find((m) => m.from + m.to + (m.promotion || '') === uci);
        if (move) makeMove(move.from, move.to);
    }

    function resetGame() {
        clearHighlights();
        game = new Chess();
        board.position('start');
        moveHistory = [];
        gameStartTime = Date.now();
        isGameOver = false;
        renderMoveHistory();
        updateGameState();
        requestAnalysis();
        showNotification('New game started', 'success');
    }

    function flipBoard() {
        board.flip();
    }

    // ---------- engine analysis ----------

    function requestAnalysis() {
        const requestId = ++suggestRequestId;
        $id('move-suggestions').innerHTML = '<div class="loading">Analyzing position...</div>';

        fetch('/suggest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fen: game.fen() }),
        })
            .then((r) => r.json())
            .then((data) => {
                if (requestId !== suggestRequestId) return; // stale response
                if (typeof data.current_evaluation === 'number') {
                    updateEvaluation(data.current_evaluation);
                }
                renderSuggestions(data.suggested_moves || []);
            })
            .catch((err) => {
                console.error('Error getting suggestions:', err);
                renderSuggestions([]);
            });
    }

    function formatEval(value) {
        if (Math.abs(value) >= 1000) return value > 0 ? 'M (White)' : 'M (Black)';
        return (value > 0 ? '+' : '') + value.toFixed(2);
    }

    function updateEvaluation(evaluation) {
        const text = $id('evaluation-text');
        const fill = $id('eval-bar-fill');
        const clamped = Math.max(-EVAL_CLAMP, Math.min(EVAL_CLAMP, evaluation));
        const whitePercent = ((clamped + EVAL_CLAMP) / (2 * EVAL_CLAMP)) * 100;

        text.textContent = formatEval(evaluation);
        text.className = 'evaluation-text ' + (evaluation > 0.05 ? 'positive' : evaluation < -0.05 ? 'negative' : 'neutral');
        fill.style.width = whitePercent + '%';
        fill.className = 'eval-bar-fill ' + (evaluation >= 0 ? 'positive' : 'negative');
    }

    function renderSuggestions(moves) {
        const container = $id('move-suggestions');
        if (!moves.length) {
            container.innerHTML = '<div class="no-suggestions"><p>No suggestions available</p></div>';
            return;
        }
        container.innerHTML = '';
        moves.slice(0, 5).forEach((m, i) => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            item.innerHTML =
                '<div class="suggestion-rank">' + (i + 1) + '</div>' +
                '<div class="suggestion-move"></div>' +
                '<div class="suggestion-eval ' + (m.evaluation >= 0 ? 'positive' : 'negative') + '">' +
                formatEval(m.evaluation) + '</div>';
            item.querySelector('.suggestion-move').textContent = m.san;
            item.addEventListener('click', () => playSuggestion(m.move));
            container.appendChild(item);
        });
    }

    // ---------- status panels ----------

    function updateGameState() {
        const inCheck = game.in_check();
        const over = game.game_over();

        $id('check-status').textContent = inCheck ? 'Yes' : 'No';
        $id('check-status').className = 'info-value' + (inCheck ? ' warning' : '');
        $id('game-over-status').textContent = over ? 'Yes' : 'No';
        $id('game-over-status').className = 'info-value' + (over ? ' error' : '');
        $id('turn-indicator').textContent = game.turn() === 'w' ? 'White' : 'Black';

        const status = $id('status-text');
        if (game.in_checkmate()) {
            status.textContent = 'Checkmate — ' + (game.turn() === 'w' ? 'Black' : 'White') + ' wins';
            status.className = 'status-text checkmate';
        } else if (game.in_stalemate()) {
            status.textContent = 'Stalemate';
            status.className = 'status-text stalemate';
        } else if (game.in_draw()) {
            status.textContent = 'Draw';
            status.className = 'status-text draw';
        } else if (inCheck) {
            status.textContent = (game.turn() === 'w' ? 'White' : 'Black') + ' is in check';
            status.className = 'status-text check';
        } else {
            status.textContent = game.turn() === 'w' ? 'White to move' : 'Black to move';
            status.className = 'status-text';
        }

        if (over && !isGameOver) {
            isGameOver = true;
            showNotification(gameOverMessage(), 'info');
        }
    }

    function gameOverMessage() {
        if (game.in_checkmate()) return 'Checkmate! ' + (game.turn() === 'w' ? 'Black' : 'White') + ' wins.';
        if (game.in_stalemate()) return 'Draw by stalemate.';
        if (game.in_threefold_repetition()) return 'Draw by threefold repetition.';
        if (game.insufficient_material()) return 'Draw by insufficient material.';
        return 'Draw.';
    }

    function renderMoveHistory() {
        const container = $id('move-history');
        $id('move-count').textContent = String(moveHistory.length);

        if (!moveHistory.length) {
            container.innerHTML = '<div class="history-placeholder"><p>No moves played yet</p></div>';
            return;
        }
        let html = '';
        for (let i = 0; i < moveHistory.length; i += 2) {
            const white = moveHistory[i];
            const black = moveHistory[i + 1];
            html += '<div class="history-move"><span class="move-number">' + (i / 2 + 1) + '.</span>' +
                '<span class="move-text">' + white.san + '</span>' +
                (black ? '<span class="move-text">' + black.san + '</span>' : '') + '</div>';
        }
        container.innerHTML = html;
        container.scrollTop = container.scrollHeight;
    }

    function showNotification(message, type) {
        const container = $id('notifications');
        const el = document.createElement('div');
        el.className = 'notification ' + type;
        el.textContent = message;
        container.appendChild(el);
        setTimeout(() => {
            el.classList.add('fade-out');
            setTimeout(() => el.remove(), 300);
        }, 3000);
    }

    function updateTimer() {
        const elapsed = Date.now() - gameStartTime;
        const minutes = Math.floor(elapsed / 60000);
        const seconds = Math.floor((elapsed % 60000) / 1000);
        $id('game-timer').textContent = String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');
    }

    // ---------- bootstrap ----------

    document.addEventListener('DOMContentLoaded', () => {
        initializeBoard();
        updateGameState();
        requestAnalysis();
        setInterval(updateTimer, 1000);
        window.addEventListener('resize', () => board && board.resize());
        document.querySelectorAll('[data-action="new-game"]').forEach((b) => b.addEventListener('click', resetGame));
        document.querySelectorAll('[data-action="flip"]').forEach((b) => b.addEventListener('click', flipBoard));
    });
})();
