import pytest
from fastapi.testclient import TestClient

from app.api import create_app
from app.storage import Storage

CRITERIA = [{"type": "experience", "min_years": 2, "weight": 1.0}]
CANDIDATE = {"name": "Jonas Jonaitis", "skills": {}, "experience_years": 3}


@pytest.fixture
def storage() -> Storage:
    return Storage(":memory:")


@pytest.fixture
def first(storage) -> dict:
    organization_id = storage.add_organization("Pirma organizacija")
    position_id = storage.add_position(organization_id, "Pirmos organizacijos pozicija", [], CRITERIA)
    return {"headers": {"X-Organization": str(organization_id)}, "position_id": position_id}


@pytest.fixture
def second(storage) -> dict:
    organization_id = storage.add_organization("Antra organizacija")
    position_id = storage.add_position(organization_id, "Antros organizacijos pozicija", [], CRITERIA)
    return {"headers": {"X-Organization": str(organization_id)}, "position_id": position_id}


@pytest.fixture
def client(storage) -> TestClient:
    return TestClient(create_app(storage))


def test_organization_cannot_read_candidates_of_another_organization(client, first, second):
    url = f"/api/positions/{first['position_id']}/candidates"
    client.post(url, json=CANDIDATE, headers=first["headers"])

    own_response = client.get(url, headers=first["headers"])
    foreign_response = client.get(url, headers=second["headers"])

    assert [candidate["name"] for candidate in own_response.json()] == ["Jonas Jonaitis"]
    assert foreign_response.status_code == 404
