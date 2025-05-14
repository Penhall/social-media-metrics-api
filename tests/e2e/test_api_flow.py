import pytest
from datetime import datetime, timedelta

def test_full_metric_flow(client):
    """Testa o fluxo completo de obtenção de métricas"""
    # 1. Autenticação
    auth_response = client.post(
        "/auth/token",
        data={"username": "test", "password": "test"}
    )
    assert auth_response.status_code == 200
    token = auth_response.json()["access_token"]

    # 2. Obtenção de métricas
    headers = {"Authorization": f"Bearer {token}"}
    metrics_response = client.get(
        "/metrics",
        headers=headers,
        params={
            "platforms": "facebook,instagram",
            "date_from": (datetime.now() - timedelta(days=7)).isoformat(),
            "date_to": datetime.now().isoformat()
        }
    )
    assert metrics_response.status_code == 200
    data = metrics_response.json()
    assert "facebook" in data["platforms"]
    assert "instagram" in data["platforms"]

    # 3. Verificação no banco de dados
    db_response = client.get(
        "/metrics/history",
        headers=headers
    )
    assert db_response.status_code == 200
    assert len(db_response.json()) > 0

def test_database_persistence(client):
    """Testa se os dados são persistidos corretamente"""
    # 1. Criar métricas
    response = client.post(
        "/metrics",
        json={
            "platform": "twitter",
            "metrics": {"followers": 1000, "likes": 500}
        },
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 201

    # 2. Verificar persistência
    db_response = client.get("/metrics/twitter")
    assert db_response.status_code == 200
    assert db_response.json()["metrics"]["followers"] == 1000