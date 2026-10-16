from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_investigate_success():
    fake_message = MagicMock()
    fake_message.text.return_value = "Your bill increased by $57.60."

    fake_result = {
        "messages": [fake_message]
    }

    with patch("app.api.routes.chat.agent") as mock_agent:
        mock_agent.invoke.return_value = fake_result

        response = client.post(
            "/investigate",
            json={
                "customer_id": "C001",
                "query": "Why did my bill increase?"
            }
        )

        assert response.status_code == 200

        assert response.json() == {
            "customer_id": "C001",
            "answer": "Your bill increased by $57.60."
        }

        mock_agent.invoke.assert_called_once()

def test_investigate_missing_query():
    response = client.post(
        "/investigate",
        json={
            "customer_id": "C001"
        }
    )

    assert response.status_code == 422

def test_investigate_missing_customer_id():
    response = client.post(
        "/investigate",
        json={
            "query": "Why did my bill increase?"
        }
    )

    assert response.status_code == 422

def test_investigate_agent_failure():
    with patch("app.api.routes.chat.agent") as mock_agent:
        mock_agent.invoke.side_effect = RuntimeError(
            "Internal LLM provider error"
        )

        response = client.post(
            "/investigate",
            json={
                "customer_id": "C001",
                "query": "Why did my bill increase?"
            }
        )

        assert response.status_code == 503
        assert response.json() == {
            "detail": "Billing investigation service unavailable"
        }