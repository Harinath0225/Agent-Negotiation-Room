"""
Simulation API routes for Nexus Deal Room.
"""
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
import logging

from ..services.simulation_service import (
    SimulationRequest,
    SimulationOutcome,
    SimulationErrorResponse,
    run_tradeoff_simulation,
)

logger = logging.getLogger("simulation_routes")
router = APIRouter(prefix="/simulations", tags=["simulations"])


@router.post(
    "/tradeoff",
    response_model=SimulationOutcome,
    responses={
        200: {"model": SimulationOutcome, "description": "Simulation completed successfully"},
        422: {"description": "Validation error in request parameters"},
        500: {"model": SimulationErrorResponse, "description": "Simulation execution failed"},
    },
)
async def simulate_tradeoff_endpoint(request: SimulationRequest):
    """
    Executes a tradeoff simulation using the shared Decision Twin service.
    """
    try:
        outcome = run_tradeoff_simulation(request)
        return outcome
    except ValueError as val_err:
        logger.warning(f"[Simulation Validation Error] request_id={request.request_id}: {val_err}")
        raise HTTPException(
            status_code=422,
            detail=str(val_err),
        )
    except Exception as exc:
        logger.error(f"[Simulation Internal Error] request_id={request.request_id}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "request_id": request.request_id,
                "detail": "The tradeoff simulation could not be completed. Try again.",
            },
        )
