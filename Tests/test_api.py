import chess
import pytest

from app import app

START = chess.STARTING_FEN
PROMOTION_FEN = "8/P7/8/8/8/8/8/k6K w - - 0 1"


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"<title>" in response.data


def test_legal_move(client):
    response = client.post("/move", json={"fen": START, "move": "e2e4"})
    body = response.get_json()
    assert response.status_code == 200
    assert body["status"] == "ok"
    assert body["fen"].startswith("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b")
    assert body["turn"] == "black"


def test_illegal_move(client):
    response = client.post("/move", json={"fen": START, "move": "e2e5"})
    assert response.status_code == 200
    assert response.get_json()["status"] == "illegal"


def test_promotion_move_accepted(client):
    response = client.post("/move", json={"fen": PROMOTION_FEN, "move": "a7a8q"})
    body = response.get_json()
    assert body["status"] == "ok"
    assert chess.Board(body["fen"]).piece_at(chess.A8) == chess.Piece(chess.QUEEN, chess.WHITE)


def test_malformed_move_is_400(client):
    response = client.post("/move", json={"fen": START, "move": "zz"})
    assert response.status_code == 400


def test_missing_json_is_400(client):
    response = client.post("/move", data="not json", content_type="text/plain")
    assert response.status_code == 400


def test_invalid_fen_is_400(client):
    response = client.post("/suggest", json={"fen": "this is not a fen"})
    assert response.status_code == 400


def test_reset(client):
    response = client.post("/reset")
    body = response.get_json()
    assert body["status"] == "reset"
    assert body["fen"] == START


def test_suggest_returns_moves(client):
    response = client.post("/suggest", json={"fen": START})
    body = response.get_json()
    assert response.status_code == 200
    assert "current_evaluation" in body
    assert 1 <= len(body["suggested_moves"]) <= 5
    assert all({"move", "san", "evaluation"} <= set(m) for m in body["suggested_moves"])


def test_suggest_defaults_to_start_position(client):
    response = client.post("/suggest", json={})
    assert response.status_code == 200
    assert response.get_json()["suggested_moves"]


def test_position_reflects_query_fen(client):
    mate = "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3"
    response = client.get("/position", query_string={"fen": mate})
    body = response.get_json()
    assert body["is_checkmate"] is True
    assert body["is_game_over"] is True
    assert body["turn"] == "white"
