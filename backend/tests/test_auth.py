"""Integration tests for `/auth/*` (ZD-M1-03), against real Postgres +
Redis. Needs `docker compose up -d db redis` first; see backend/README.md.
"""

import pytest
import sqlalchemy as sa
from httpx import ASGITransport, AsyncClient

from app.main import app
from tests.conftest import SYNC_DATABASE_URL

pytestmark = pytest.mark.db


async def _client() -> AsyncClient:
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


async def test_anonymous_creates_a_user_and_issues_a_token(clean_redis):
    async with await _client() as client:
        response = await client.post("/auth/anonymous", json={"device_id": "device-1"})

    assert response.status_code == 200
    body = response.json()
    assert body["identity_type"] == "ANONYMOUS"
    assert body["access_token"]


async def test_anonymous_is_idempotent_per_device(clean_redis):
    async with await _client() as client:
        first = await client.post("/auth/anonymous", json={"device_id": "device-2"})
        second = await client.post("/auth/anonymous", json={"device_id": "device-2"})

    assert first.json()["user_id"] == second.json()["user_id"]

    engine = sa.create_engine(SYNC_DATABASE_URL)
    with engine.connect() as conn:
        count = conn.execute(
            sa.text("SELECT COUNT(*) FROM iam.users WHERE device_id = 'device-2'")
        ).scalar_one()
    assert count == 1


async def test_anonymous_is_rate_limited(clean_redis):
    async with await _client() as client:
        responses = [
            await client.post("/auth/anonymous", json={"device_id": f"device-rl-{i}"})
            for i in range(6)  # settings.anonymous_auth_rate_limit defaults to 5
        ]

    assert [r.status_code for r in responses] == [200, 200, 200, 200, 200, 429]


async def test_register_upgrades_the_same_row_to_named(clean_redis):
    async with await _client() as client:
        anon = await client.post("/auth/anonymous", json={"device_id": "device-3"})
        token = anon.json()["access_token"]
        user_id = anon.json()["user_id"]

        response = await client.post(
            "/auth/register",
            json={"phone_number": "+263771234567", "password": "correct horse"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["identity_type"] == "NAMED"
    # Same row upgraded in place (database_design.md Section 2.1) — not a
    # second account.
    assert body["user_id"] == user_id


async def test_register_rejects_an_already_named_account(clean_redis):
    async with await _client() as client:
        anon = await client.post("/auth/anonymous", json={"device_id": "device-4"})
        token = anon.json()["access_token"]
        await client.post(
            "/auth/register",
            json={"phone_number": "+263771234568", "password": "correct horse"},
            headers={"Authorization": f"Bearer {token}"},
        )

        response = await client.post(
            "/auth/register",
            json={"phone_number": "+263771234569", "password": "another password"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 409


async def test_register_rejects_a_phone_number_already_in_use(clean_redis):
    async with await _client() as client:
        first = await client.post("/auth/anonymous", json={"device_id": "device-5a"})
        await client.post(
            "/auth/register",
            json={"phone_number": "+263771234570", "password": "correct horse"},
            headers={"Authorization": f"Bearer {first.json()['access_token']}"},
        )

        second = await client.post("/auth/anonymous", json={"device_id": "device-5b"})
        response = await client.post(
            "/auth/register",
            json={"phone_number": "+263771234570", "password": "another password"},
            headers={"Authorization": f"Bearer {second.json()['access_token']}"},
        )

    assert response.status_code == 409


async def test_login_succeeds_with_the_right_password(clean_redis):
    async with await _client() as client:
        anon = await client.post("/auth/anonymous", json={"device_id": "device-6"})
        await client.post(
            "/auth/register",
            json={"phone_number": "+263771234571", "password": "correct horse"},
            headers={"Authorization": f"Bearer {anon.json()['access_token']}"},
        )

        response = await client.post(
            "/auth/login", json={"phone_number": "+263771234571", "password": "correct horse"}
        )

    assert response.status_code == 200
    assert response.json()["identity_type"] == "NAMED"


async def test_login_rejects_the_wrong_password(clean_redis):
    async with await _client() as client:
        anon = await client.post("/auth/anonymous", json={"device_id": "device-7"})
        await client.post(
            "/auth/register",
            json={"phone_number": "+263771234572", "password": "correct horse"},
            headers={"Authorization": f"Bearer {anon.json()['access_token']}"},
        )

        response = await client.post(
            "/auth/login", json={"phone_number": "+263771234572", "password": "wrong password"}
        )

    assert response.status_code == 401


async def test_login_rejects_an_unknown_phone_number(clean_redis):
    async with await _client() as client:
        response = await client.post(
            "/auth/login", json={"phone_number": "+263779999999", "password": "whatever"}
        )

    assert response.status_code == 401


async def test_me_returns_the_current_user(clean_redis):
    async with await _client() as client:
        anon = await client.post("/auth/anonymous", json={"device_id": "device-8"})
        response = await client.get(
            "/auth/me", headers={"Authorization": f"Bearer {anon.json()['access_token']}"}
        )

    assert response.status_code == 200
    assert response.json()["device_id"] == "device-8"


async def test_me_rejects_a_missing_token(clean_redis):
    async with await _client() as client:
        response = await client.get("/auth/me")

    assert response.status_code == 401  # HTTPBearer's own response for no credentials at all


async def test_me_rejects_a_garbage_token(clean_redis):
    async with await _client() as client:
        response = await client.get("/auth/me", headers={"Authorization": "Bearer not-a-jwt"})

    assert response.status_code == 401
