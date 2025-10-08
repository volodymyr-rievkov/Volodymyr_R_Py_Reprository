from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from io import StringIO
from .lcg import *

router = APIRouter()

@router.get("/generate")
async def generate(n: int = Query(..., gt=0)):
    return StreamingResponse(
        lcg_stream(n, chunk_size=10000),
        media_type="text/plain",
        headers={"Content-Disposition": "attachment; filename=output.txt"}
    )

@router.get("/period")
async def get_period():
    period = find_period()
    return {"period": period}

@router.get("/cesaro")
async def run_cesaro(n: int = Query(..., gt=0)):
    if n % 2 != 0:
        raise HTTPException(400, "N must be even for Cesaro test")
    sequence = lcg_generate(n)
    pi_est = cesaro_test(sequence)
    return {"estimated_pi": pi_est}