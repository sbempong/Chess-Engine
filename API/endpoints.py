from typing import List, Optional

import chess
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from Engine.board import Board
from Engine.evaluation import evaluate_position
from Engine.evaluation import get_best_move as engine_get_best_move

router = APIRouter()
board = Board()


class MoveRequest(BaseModel):
    move: str  # UCI format (e.g., "e2e4", "e7e8q")


class GameState(BaseModel):
    fen: str
    turn: str
    is_check: bool
    is_game_over: bool
    result: Optional[str]
    evaluation: float
    legal_moves: List[str]


def current_state() -> GameState:
    return GameState(
        fen=board.get_fen(),
        turn="white" if board.get_turn() else "black",
        is_check=board.is_check(),
        is_game_over=board.is_game_over(),
        result=board.get_game_result(),
        evaluation=evaluate_position(board.board),
        legal_moves=[move.uci() for move in board.get_legal_moves()],
    )


@router.post("/move", response_model=GameState)
async def make_move(move_request: MoveRequest):
    try:
        move = chess.Move.from_uci(move_request.move)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid move format")
    if not board.make_move(move):
        raise HTTPException(status_code=400, detail="Illegal move")
    return current_state()


@router.post("/undo", response_model=GameState)
async def undo_move():
    if board.undo_move() is None:
        raise HTTPException(status_code=400, detail="No moves to undo")
    return current_state()


@router.get("/state", response_model=GameState)
async def get_state():
    return current_state()


@router.get("/best-move")
async def get_best_move_endpoint(depth: int = Query(15, ge=1, le=30)):
    move, score = engine_get_best_move(board.board, depth)
    if move is None:
        raise HTTPException(status_code=404, detail="No legal moves available")
    return {"move": move.uci(), "san": board.board.san(move), "evaluation": score}


@router.post("/reset", response_model=GameState)
async def reset_game():
    board.reset()
    return current_state()
