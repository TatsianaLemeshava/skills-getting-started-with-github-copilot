import copy
import os
import sys

# Ensure the "src" directory is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from fastapi.testclient import TestClient
import pytest

from app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities dict after each test to avoid state leakage."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_remove_participant():
    activity = "Basketball Team"
    email = "testuser@example.com"

    # Sign up
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in resp.json().get("message", "")

    # Confirm participant is listed
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email in resp.json()[activity]["participants"]

    # Remove participant
    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp.status_code == 200
    assert "Removed" in resp.json().get("message", "")

    # Confirm removal
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email not in resp.json()[activity]["participants"]


def test_signup_existing_returns_400():
    activity = "Basketball Team"
    existing = "alex@mergington.edu"

    resp = client.post(f"/activities/{activity}/signup", params={"email": existing})
    assert resp.status_code == 400


def test_remove_nonexistent_returns_404():
    activity = "Basketball Team"
    nonexist = "noone@example.com"

    resp = client.delete(f"/activities/{activity}/participants", params={"email": nonexist})
    assert resp.status_code == 404


def test_activity_not_found():
    resp = client.post("/activities/NoSuchActivity/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404

    resp = client.delete("/activities/NoSuchActivity/participants", params={"email": "a@b.com"})
    assert resp.status_code == 404
