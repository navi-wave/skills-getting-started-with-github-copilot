import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirect():
    """Test that root endpoint redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    """Test retrieving all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0
    # Check that activities have required fields
    for activity_name, activity_details in activities.items():
        assert "description" in activity_details
        assert "schedule" in activity_details
        assert "max_participants" in activity_details
        assert "participants" in activity_details
        assert isinstance(activity_details["participants"], list)


def test_signup_for_activity():
    """Test signing up for an activity"""
    email = "test@mergington.edu"
    activity_name = "Robotics Club"
    
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert email in result["message"]


def test_signup_duplicate_student():
    """Test that a student cannot sign up twice"""
    email = "duplicate@mergington.edu"
    activity_name = "Programming Class"
    
    # First signup should succeed
    response1 = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )
    assert response1.status_code == 200
    
    # Second signup should fail
    response2 = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )
    assert response2.status_code == 400
    assert "already signed up" in response2.json()["detail"]


def test_signup_nonexistent_activity():
    """Test signing up for a non-existent activity"""
    response = client.post(
        "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
    )
    assert response.status_code == 404


def test_remove_participant():
    """Test removing a participant from an activity"""
    email = "remove@mergington.edu"
    activity_name = "Gym Class"
    
    # First, sign up
    signup_response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )
    assert signup_response.status_code == 200
    
    # Then remove
    remove_response = client.delete(
        f"/activities/{activity_name}/participants/{email}"
    )
    assert remove_response.status_code == 200
    result = remove_response.json()
    assert "message" in result
    assert email in result["message"]


def test_remove_nonexistent_participant():
    """Test removing a non-existent participant"""
    response = client.delete(
        "/activities/Robotics Club/participants/nonexistent@mergington.edu"
    )
    assert response.status_code == 404
