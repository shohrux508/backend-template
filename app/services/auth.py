from __future__ import annotations

import secrets
import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt  # type: ignore[import-untyped]
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database.models import RefreshToken, User


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def hash_password(plain: str) -> str:
        hashed: bytes = bcrypt.hashpw(plain.encode(), bcrypt.gensalt())
        return hashed.decode()

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())

    @staticmethod
    def create_access_token(subject: str) -> str:
        expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
        payload = {"sub": subject, "exp": expire}
        result: str = jwt.encode(
            payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
        )
        return result

    @staticmethod
    def create_refresh_token() -> tuple[str, datetime]:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
        return token, expires_at

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create_user(self, email: str, password: str) -> User:
        user = User(
            id=uuid.uuid4(),
            email=email,
            hashed_password=self.hash_password(password),
        )
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def store_refresh_token(
        self, user_id: uuid.UUID, token: str, expires_at: datetime
    ) -> None:
        rt = RefreshToken(
            id=uuid.uuid4(),
            token=token,
            user_id=user_id,
            expires_at=expires_at,
        )
        self._session.add(rt)
        await self._session.commit()

    async def get_valid_refresh_token(self, token: str) -> RefreshToken | None:
        now = datetime.now(UTC)
        result = await self._session.execute(
            select(RefreshToken).where(
                RefreshToken.token == token,
                RefreshToken.revoked.is_(False),
                RefreshToken.expires_at > now,
            )
        )
        return result.scalar_one_or_none()

    async def revoke_refresh_token(self, token: str) -> None:
        result = await self._session.execute(
            select(RefreshToken).where(RefreshToken.token == token)
        )
        rt = result.scalar_one_or_none()
        if rt is not None:
            rt.revoked = True
            await self._session.commit()

    async def get_user_from_access_token(self, token: str) -> User | None:
        try:
            payload: dict[str, object] = jwt.decode(
                token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
            )
            sub = payload.get("sub")
            if not isinstance(sub, str):
                return None
        except JWTError:
            return None

        result = await self._session.execute(
            select(User).where(User.id == uuid.UUID(sub), User.is_active.is_(True))
        )
        return result.scalar_one_or_none()
