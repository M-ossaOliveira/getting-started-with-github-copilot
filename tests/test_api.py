import copy
from fastapi.testclient import TestClient
from src.app import app, activities


# Fixture to provide a TestClient and reset in-memory state between tests
import pytest

@pytest.fixture(autouse=True)
def client_and_reset():
    # Arrange: keep a deep copy of the original activities and provide TestClient
    original = copy.deepcopy(activities)
    client = TestClient(app)
    yield client
    # Teardown: restore original activities state
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_get_activities(client):
    # Arrange (handled by fixture)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success(client):
    # Arrange
    activity = "Chess Club"
    email = "test_signup_success@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert "Signed up" in response.json().get("message", "")

    # Verify the in-memory state changed
    resp2 = client.get("/activities")
    assert email in resp2.json()[activity]["participants"]


def test_signup_duplicate(client):
    # Arrange
    activity = "Chess Club"
    email = "duplicate@mergington.edu"

    # Act
    resp1 = client.post(f"/activities/{activity}/signup?email={email}")
    resp2 = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert resp1.status_code == 200
    assert resp2.status_code == 400


def test_remove_participant_success(client):
    # Arrange: sign up a participant first
    activity = "Chess Club"
    email = "to.remove@mergington.edu"
    r = client.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 200

    # Act: remove the participant
    r2 = client.delete(f"/activities/{activity}/participants?email={email}")

    # Assert
    assert r2.status_code == 200
    # Verify removal
    r3 = client.get("/activities")
    assert email not in r3.json()[activity]["participants"]


def test_remove_participant_not_found(client):
    # Arrange
    activity = "Chess Club"
    email = "notfound@mergington.edu"

    # Act
    r = client.delete(f"/activities/{activity}/participants?email={email}")

    # Assert
    assert r.status_code == 404
