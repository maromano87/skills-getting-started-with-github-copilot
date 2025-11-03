import copy

from fastapi.testclient import TestClient
import pytest

from src import app as appmod


# Keep a baseline copy of the in-memory activities so each test starts fresh
BASE_ACTIVITIES = copy.deepcopy(appmod.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    # Restore activities to baseline before each test
    appmod.activities = copy.deepcopy(BASE_ACTIVITIES)
    yield


client = TestClient(appmod.app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # sanity check some expected activities exist
    assert "Chess Club" in data


def test_signup_success():
    email = "testuser@example.com"
    activity = "Chess Club"
    assert email not in appmod.activities[activity]["participants"]

    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert email in appmod.activities[activity]["participants"]


def test_signup_duplicate():
    email = "dup@example.com"
    activity = "Chess Club"

    resp1 = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp1.status_code == 200

    resp2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp2.status_code == 400


def test_unregister_success_existing():
    activity = "Chess Club"
    email = "michael@mergington.edu"  # present in initial data
    assert email in appmod.activities[activity]["participants"]

    resp = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 200
    assert email not in appmod.activities[activity]["participants"]


def test_unregister_not_registered():
    activity = "Chess Club"
    email = "notthere@example.com"
    assert email not in appmod.activities[activity]["participants"]

    resp = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 400
