# realtimedata.py
from fastapi import APIRouter, HTTPException, Query
import httpx

router = APIRouter(prefix="/realtime", tags=["realtime"])

LOGIN_URL = "https://iotapi.enmaz.com/api/login"
REALTIME_URL = "https://iotapi.enmaz.com/api/assets/RealTimeValue"

EMAIL = "cmti@enmaz.com"
PASSWORD = "Password@123"   # you can move this to .env


async def get_token():
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            LOGIN_URL,
            json={"email": EMAIL, "password": PASSWORD}
        )
        if resp.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail="Failed to auto-login to Enmaz API"
            )
        return resp.json().get("token")


@router.get("/")
async def realtime(assetId: str = Query(...)):
    """
    Frontend does NOT send Authorization.
    FastAPI logs in automatically and fetches realtime data.
    """
    token = await get_token()  # auto login

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                REALTIME_URL,
                params={"assetId": assetId},
                headers={"Authorization": f"Bearer {token}"}
            )

        if resp.status_code != 200:
            raise HTTPException(
                status_code=resp.status_code,
                detail=f"Upstream error: {resp.text}"
            )

        return resp.json()

    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=str(e))
