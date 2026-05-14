"""
Test suite for Mergington High School API using the AAA (Arrange-Act-Assert) pattern.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to a known state before each test."""
    # Store original state
    original = {k: v.copy() for k, v in activities.items()}
    yield
    # Restore original state after test
    activities.clear()
    activities.update(original)


class TestGetActivities:
    """Test suite for the GET /activities endpoint."""
    
    def test_get_activities_returns_dict(self, client, reset_activities):
        """
        Arrange: Create a test client
        Act: Send a GET request to /activities
        Assert: Verify response status is 200 and returns a dict
        """
        # Arrange
        # Already done via fixtures
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
    
    def test_get_activities_contains_chess_club(self, client, reset_activities):
        """
        Arrange: Create a test client
        Act: Send a GET request to /activities
        Assert: Verify Chess Club is in the returned activities
        """
        # Arrange
        # Already done via fixtures
        
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        assert "Chess Club" in activities_data
        assert "description" in activities_data["Chess Club"]


class TestSignupForActivity:
    """Test suite for the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_new_student_success(self, client, reset_activities):
        """
        Arrange: Prepare test data with an activity and new email
        Act: Send POST request to signup endpoint
        Assert: Verify success response and participant was added
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert new_email in activities[activity_name]["participants"]
    
    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """
        Arrange: Prepare a non-existent activity name
        Act: Send POST request for signup with invalid activity
        Assert: Verify 404 error is returned
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_duplicate_student_returns_400(self, client, reset_activities):
        """
        Arrange: Use an email already signed up for an activity
        Act: Send POST request to signup with duplicate email
        Assert: Verify 400 error is returned
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = activities[activity_name]["participants"][0]
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()


class TestRemoveParticipant:
    """Test suite for the DELETE /activities/{activity_name}/participants endpoint."""
    
    def test_remove_existing_participant_success(self, client, reset_activities):
        """
        Arrange: Prepare an activity with a known participant
        Act: Send DELETE request to remove that participant
        Assert: Verify success response and participant was removed
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = activities[activity_name]["participants"][0]
        original_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email_to_remove}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        assert len(activities[activity_name]["participants"]) == original_count - 1
        assert email_to_remove not in activities[activity_name]["participants"]
    
    def test_remove_from_nonexistent_activity_returns_404(self, client, reset_activities):
        """
        Arrange: Prepare a non-existent activity name
        Act: Send DELETE request for non-existent activity
        Assert: Verify 404 error is returned
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_remove_nonexistent_participant_returns_404(self, client, reset_activities):
        """
        Arrange: Prepare an email not in the activity
        Act: Send DELETE request to remove non-existent participant
        Assert: Verify 404 error is returned
        """
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
