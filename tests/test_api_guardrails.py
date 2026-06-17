import pytest

pytest.importorskip("fastapi", reason="fastapi required: pip install feldtheorie[api]")
from api.server import BETA_TARGET, KAPPA_BOUNDS, app
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_health_guardrails_exposed():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"

    guardrails = payload["guardrails"]
    assert guardrails["beta_target"] == pytest.approx(BETA_TARGET)
    assert guardrails["kappa_bounds"] == list(KAPPA_BOUNDS)
    assert "tau_star_rule" in guardrails


def test_telemetry_guardrail_handshake_tau_star():
    client = TestClient(app)

    with client.websocket_connect("/ws/telemetry?zeta=-0.5&delta_r=2.0") as websocket:
        guardrail_message = websocket.receive_json()

    assert guardrail_message["type"] == "guardrail"
    assert guardrail_message["beta_target"] == BETA_TARGET
    assert guardrail_message["kappa_bounds"] == list(KAPPA_BOUNDS)
    assert guardrail_message["tau_star"] == pytest.approx(0.2)
