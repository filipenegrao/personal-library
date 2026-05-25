from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.auth import create_access_token, hash_password, verify_password
from app.config import settings
from app.deps import get_current_user

router = APIRouter()

_hashed_password: str | None = None


def _get_hashed() -> str:
    global _hashed_password
    if _hashed_password is None:
        _hashed_password = hash_password(settings.library_password)
    return _hashed_password


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest) -> TokenResponse:
    if body.username != settings.library_username or not verify_password(
        body.password, _get_hashed()
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenResponse(access_token=create_access_token(body.username))


@router.get("/me")
async def me(username: str = Depends(get_current_user)):
    return {"username": username}
