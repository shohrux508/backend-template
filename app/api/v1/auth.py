from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.schemas.auth import (
    AccessTokenResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def _get_auth_service(session: Annotated[AsyncSession, Depends(get_session)]) -> AuthService:
    return AuthService(session)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    svc: Annotated[AuthService, Depends(_get_auth_service)],
) -> UserResponse:
    existing = await svc.get_user_by_email(body.email)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )
    user = await svc.create_user(body.email, body.password)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    svc: Annotated[AuthService, Depends(_get_auth_service)],
) -> TokenResponse:
    user = await svc.get_user_by_email(body.email)
    if user is None or not svc.verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    access_token = svc.create_access_token(str(user.id))
    refresh_token, expires_at = svc.create_refresh_token()
    await svc.store_refresh_token(user.id, refresh_token, expires_at)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(
    body: RefreshRequest,
    svc: Annotated[AuthService, Depends(_get_auth_service)],
) -> AccessTokenResponse:
    rt = await svc.get_valid_refresh_token(body.refresh_token)
    if rt is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token"
        )
    access_token = svc.create_access_token(str(rt.user_id))
    return AccessTokenResponse(access_token=access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    body: LogoutRequest,
    svc: Annotated[AuthService, Depends(_get_auth_service)],
) -> None:
    await svc.revoke_refresh_token(body.refresh_token)
