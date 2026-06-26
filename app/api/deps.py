from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.database.models import User


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session from the application container."""
    from app.core.container import AppContainer

    container: AppContainer = request.app.state.container
    async with container.session_factory() as session:
        yield session


_bearer = HTTPBearer()


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
) -> User:
    from app.core.container import AppContainer
    from app.services.auth import AuthService

    container: AppContainer = request.app.state.container
    async with container.session_factory() as session:
        svc = AuthService(session)
        user = await svc.get_user_from_access_token(credentials.credentials)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
