import chess
import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from API import create_app  # noqa: E402
from API import endpoints  # noqa: E402

PREFIX = "/api/v1"


@pytest.fixture
def client():
    endpoints.board.reset()
    with TestClient(create_app()) as client:
        yield client
    endpoints.board.reset()


def test_initial_state(client):
    body = client.get(f"{PREFIX}/state").json()
    assert body["fen"] == chess.STARTING_FEN
    assert body["turn"] == "white"
    assert body["is_game_over"] is False
    assert len(body["legal_moves"]) == 20


def test_move_then_reset_actually_resets(client):
    assert client.post(f"{PREFIX}/move", json={"move": "e2e4"}).status_code == 200
    assert client.get(f"{PREFIX}/state").json()["turn"] == "black"

    body = client.post(f"{PREFIX}/reset").json()
    assert body["fen"] == chess.STARTING_FEN
    assert client.get(f"{PREFIX}/state").json()["fen"] == chess.STARTING_FEN


def test_illegal_and_malformed_moves(client):
    assert client.post(f"{PREFIX}/move", json={"move": "e2e5"}).status_code == 400
    assert client.post(f"{PREFIX}/move", json={"move": "nope"}).status_code == 400


def test_promotion_accepted(client):
    endpoints.board.board.set_fen("8/P7/8/8/8/8/8/k6K w - - 0 1")
    body = client.post(f"{PREFIX}/move", json={"move": "a7a8q"}).json()
    assert chess.Board(body["fen"]).piece_at(chess.A8) == chess.Piece(chess.QUEEN, chess.WHITE)


def test_undo(client):
    client.post(f"{PREFIX}/move", json={"move": "e2e4"})
    assert client.post(f"{PREFIX}/undo").json()["fen"] == chess.STARTING_FEN
    assert client.post(f"{PREFIX}/undo").status_code == 400


def test_best_move(client):
    body = client.get(f"{PREFIX}/best-move", params={"depth": 4}).json()
    assert chess.Move.from_uci(body["move"]) in chess.Board().legal_moves
    assert "san" in body and "evaluation" in body
