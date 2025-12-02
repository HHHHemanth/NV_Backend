# parameter.py (paste into file)
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import httpx
import logging
import traceback

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger("parameter_proxy")
logger.setLevel(logging.DEBUG)  # ensure logger prints in uvicorn debug

class ParameterTrendsRequest(BaseModel):
    assetId: str
    assetPartId: str
    axis: str
    days: int
    type: str

@router.post("/api/assetpart/ParameterTrends")
async def get_parameter_trends(
    payload: ParameterTrendsRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request = None
):
    token = credentials.credentials
    logger.info(f"[ParameterTrends] called assetPart={payload.assetPartId} axis={payload.axis} days={payload.days}")

    upstream_url = "https://iotapi.enmaz.com/api/assetpart/ParameterTrends"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                upstream_url,
                headers={"Authorization": f"Bearer {token}"},
                json=payload.model_dump()
            )
    except Exception as exc:
        # Network / DNS / SSL / timeout / other httpx exceptions
        tb = traceback.format_exc()
        logger.error("[ParameterTrends] httpx request failed: %s\n%s", str(exc), tb)
        raise HTTPException(status_code=502, detail=f"Upstream request failed: {str(exc)}")

    # If upstream returned non-200, return its status & body for debugging (trimmed)
    if resp.status_code != 200:
        body = resp.text or "<no body>"
        short = body if len(body) < 2000 else body[:2000] + "...(truncated)"
        logger.error("[ParameterTrends] upstream returned %s body:%s", resp.status_code, short[:1000])
        # return upstream status + body
        raise HTTPException(status_code=resp.status_code, detail=short)

    # upstream returned 200; try parse JSON
    try:
        data = resp.json()
    except Exception as exc:
        tb = traceback.format_exc()
        logger.error("[ParameterTrends] failed to parse JSON: %s\n%s", str(exc), tb)
        # supply a trimmed preview of the body
        sample = (resp.text or "")[:2000]
        raise HTTPException(status_code=502, detail=f"Upstream returned invalid JSON. Preview: {sample}")

    return data
