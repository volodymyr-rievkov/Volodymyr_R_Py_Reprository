from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from .lcg import *

router = APIRouter()

@router.get("/generate")
async def generate(n: int = Query(..., gt=0)):
    return StreamingResponse(
        lcg_stream(n, chunk_size=10000),
        media_type="text/plain"
    )

@router.get("/params")
async def get_params():
    """Повертає параметри генератора для фронту"""
    return get_lcg_params()

@router.get("/period")
async def get_period():
    return {"period": find_period()}

@router.get("/cesaro")
async def run_cesaro(n: int = Query(..., gt=0)):
    if n % 2 != 0:
        raise HTTPException(400, "N must be even for Cesaro test")
    pi_est = cesaro_test_stream(n)
    return {"estimated_pi": pi_est}