from __future__ import annotations

from httpx import AsyncClient

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
REFRESH_URL = "/api/v1/auth/refresh"
LOGOUT_URL = "/api/v1/auth/logout"
ME_URL = "/api/v1/users/me"

EMAIL = "user@example.com"
PASSWORD = "strongpassword123"


async def _register_and_login(client: AsyncClient) -> dict[str, str]:
    await client.post(REGISTER_URL, json={"email": EMAIL, "password": PASSWORD})
    resp = await client.post(LOGIN_URL, json={"email": EMAIL, "password": PASSWORD})
    data: dict[str, str] = resp.json()
    return data


async def test_register_creates_user(client: AsyncClient) -> None:
    resp = await client.post(REGISTER_URL, json={"email": EMAIL, "password": PASSWORD})
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == EMAIL
    assert body["is_active"] is True
    assert "id" in body


async def test_register_duplicate_email_returns_409(client: AsyncClient) -> None:
    await client.post(REGISTER_URL, json={"email": EMAIL, "password": PASSWORD})
    resp = await client.post(REGISTER_URL, json={"email": EMAIL, "password": PASSWORD})
    assert resp.status_code == 409


async def test_register_short_password_returns_422(client: AsyncClient) -> None:
    resp = await client.post(REGISTER_URL, json={"email": EMAIL, "password": "short"})
    assert resp.status_code == 422


async def test_login_returns_tokens(client: AsyncClient) -> None:
    await client.post(REGISTER_URL, json={"email": EMAIL, "password": PASSWORD})
    resp = await client.post(LOGIN_URL, json={"email": EMAIL, "password": PASSWORD})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


async def test_login_wrong_password_returns_401(client: AsyncClient) -> None:
    await client.post(REGISTER_URL, json={"email": EMAIL, "password": PASSWORD})
    resp = await client.post(LOGIN_URL, json={"email": EMAIL, "password": "wrongpassword"})
    assert resp.status_code == 401


async def test_login_unknown_email_returns_401(client: AsyncClient) -> None:
    resp = await client.post(LOGIN_URL, json={"email": "nobody@example.com", "password": PASSWORD})
    assert resp.status_code == 401


async def test_refresh_returns_new_access_token(client: AsyncClient) -> None:
    tokens = await _register_and_login(client)
    resp = await client.post(REFRESH_URL, json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


async def test_refresh_with_invalid_token_returns_401(client: AsyncClient) -> None:
    resp = await client.post(REFRESH_URL, json={"refresh_token": "invalid-token"})
    assert resp.status_code == 401


async def test_logout_revokes_token(client: AsyncClient) -> None:
    tokens = await _register_and_login(client)
    resp = await client.post(LOGOUT_URL, json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 204
    resp2 = await client.post(REFRESH_URL, json={"refresh_token": tokens["refresh_token"]})
    assert resp2.status_code == 401


async def test_get_me_returns_current_user(client: AsyncClient) -> None:
    tokens = await _register_and_login(client)
    resp = await client.get(ME_URL, headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == EMAIL


async def test_get_me_without_token_returns_401(client: AsyncClient) -> None:
    resp = await client.get(ME_URL)
    assert resp.status_code == 401


async def test_get_me_with_invalid_token_returns_401(client: AsyncClient) -> None:
    resp = await client.get(ME_URL, headers={"Authorization": "Bearer invalid.token.here"})
    assert resp.status_code == 401
