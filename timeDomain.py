from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, RootModel
from typing import List
import httpx
from fastapi import APIRouter

router = APIRouter()
security = HTTPBearer()

class TimeSeriesRequest(BaseModel):
    assetId: str
    assetPartId: str
    axis: str
    dateTime: int
    type: str

class TimeSeriesPoint(RootModel[List[float]]):
    pass

class TimeSeriesResponse(BaseModel):
    SR: float
    twf_min: float
    twf_max: float
    Timeseries: List[TimeSeriesPoint]


@router.post("/api/assetpart/timeseries", response_model=TimeSeriesResponse)
async def get_timeseries(
    payload: TimeSeriesRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://iotapi.enmaz.com/api/assetpart/timeseries",
            headers={"Authorization": f"Bearer {token}"},
            json=payload.model_dump(),
        )

    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)

    return r.json()   # full data from Enmaz
