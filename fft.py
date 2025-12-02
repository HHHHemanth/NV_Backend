from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, RootModel
from typing import List
import httpx

from fastapi import APIRouter

router = APIRouter()
security = HTTPBearer()

# ---------- REQUEST MODEL (same structure as timeseries) ----------
class FFTRequest(BaseModel):
    assetId: str
    assetPartId: str
    axis: str
    dateTime: int     # timestamp
    type: str

# ---------- RESPONSE MODELS ----------
# One FFT point: [frequency, value]
class FFTPoint(RootModel[List[float]]):
    pass

class FFTResponse(BaseModel):
    SR: float
    fft_min: float
    fft_max: float
    FFT: List[FFTPoint]


# ---------- ENDPOINT ----------
@router.post("/api/assetpart/fft", response_model=FFTResponse)
async def get_fft(
    payload: FFTRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # JWT token without "Bearer "
    token = credentials.credentials

    # Call the real Enmaz API and proxy the response
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(
            "https://iotapi.enmaz.com/api/assetpart/fft",
            headers={"Authorization": f"Bearer {token}"},
            json=payload.model_dump(),
        )

    if resp.status_code != 200:
        # bubble up error from upstream API
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    # Return full FFT data from Enmaz
    return resp.json()
