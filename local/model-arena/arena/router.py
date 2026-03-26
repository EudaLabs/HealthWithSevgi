"""Model Arena REST endpoints."""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import Response

from .schemas import (
    ArenaCompareRequest,
    ArenaCompareResponse,
    ArenaRun,
    BatchTrainRequest,
    BatchTrainResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/arena", tags=["arena"])


def _get_arena_service(request: Request):
    return request.app.state.arena_service


@router.post("/batch-train", response_model=BatchTrainResponse)
def batch_train(request: Request, body: BatchTrainRequest) -> BatchTrainResponse:
    """Train multiple models in one request."""
    arena = _get_arena_service(request)
    logger.info("Arena batch_train: session=%s models=%d", body.session_id, len(body.models))
    try:
        result = arena.batch_train(body)
        completed = sum(1 for r in result.runs if r.status == "completed")
        logger.info("Arena batch_train done: %d/%d completed", completed, len(result.runs))
        return result
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception as exc:
        logger.exception("Batch training failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get("/runs/{session_id}", response_model=list[ArenaRun])
def get_runs(request: Request, session_id: str) -> list[ArenaRun]:
    """Get all arena runs for a session."""
    arena = _get_arena_service(request)
    # Return empty list if session has no arena runs yet but ML session exists
    ml_service = request.app.state.ml_service
    if not arena.has_session(session_id) and ml_service.get_session(session_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found",
        )
    return arena.get_runs(session_id)


@router.post("/compare/{session_id}", response_model=ArenaCompareResponse)
def compare_runs(
    request: Request, session_id: str, body: ArenaCompareRequest
) -> ArenaCompareResponse:
    """Compare selected runs."""
    arena = _get_arena_service(request)
    try:
        return arena.compare_runs(session_id, body.run_ids)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.delete("/runs/{session_id}", status_code=204)
def clear_runs(request: Request, session_id: str):
    """Clear all arena runs for a session."""
    _get_arena_service(request).clear_runs(session_id)
    return Response(status_code=204)
