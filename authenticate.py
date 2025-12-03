# authenticate.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import httpx

router = APIRouter(prefix="/auth", tags=["auth"])

LOGIN_URL = "https://iotapi.enmaz.com/api/login"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/login")
async def login(body: LoginRequest):
    """
    Proxy login to Enmaz IoT API and return the token response.
    Frontend should send:
    {
        "email": "cmti@enmaz.com",
        "password": "Password@123"
    }
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(LOGIN_URL, json=body.model_dump())

        # Raise HTTPException if Enmaz returns non-200
        if resp.status_code != 200:
            raise HTTPException(
                status_code=resp.status_code,
                detail=f"Login failed: {resp.text}",
            )

        data = resp.json()
        # If you only care about token, you can return `data["token"]`
        return data

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Error contacting auth server: {exc}",
        )
