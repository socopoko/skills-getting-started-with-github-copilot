import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def api(monkeypatch):
    activities = {
        "Chess Club": {
            "description": "Learn chess strategies",
            "schedule": "Fridays, 3:30 PM",
            "max_participants": 12,
            "participants": ["student@example.com"],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)

    with TestClient(app_module.app) as client:
        yield client, activities


def test_get_activities_returns_all_activity_data(api):
    # Arrange
    client, activities = api

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == activities


def test_signup_adds_participant(api):
    # Arrange
    client, activities = api
    activity_name = "Chess Club"
    email = "new-student@example.com"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(api):
    # Arrange
    client, activities = api
    activity_name = "Chess Club"
    email = "student@example.com"
    original_participants = activities[activity_name]["participants"].copy()

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert activities[activity_name]["participants"] == original_participants


def test_signup_returns_not_found_for_unknown_activity(api):
    # Arrange
    client, _ = api

    # Act
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "student@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant_removes_signup(api):
    # Arrange
    client, activities = api
    activity_name = "Chess Club"
    email = "student@example.com"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_remove_participant_returns_not_found_for_unknown_activity(api):
    # Arrange
    client, _ = api

    # Act
    response = client.delete(
        "/activities/Unknown Club/signup",
        params={"email": "student@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant_returns_not_found_when_not_signed_up(api):
    # Arrange
    client, activities = api
    activity_name = "Chess Club"
    email = "not-enrolled@example.com"
    original_participants = activities[activity_name]["participants"].copy()

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
    assert activities[activity_name]["participants"] == original_participants