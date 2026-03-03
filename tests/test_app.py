import copy
import pytest

from fastapi.testclient import TestClient
from src.app import app, activities


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Reset the in-memory activities dict before each test.
    
    Arrange: save original state
    Yield: test runs
    Cleanup: restore original state
    """
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities():
    """Test that /activities endpoint returns the activities dictionary."""
    # Arrange - client is ready
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success():
    """Test that a new student can successfully sign up for an activity."""
    # Arrange
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in activities[activity]["participants"]


def test_signup_duplicate():
    """Test that signing up an already-registered student returns 400."""
    # Arrange
    activity = "Chess Club"
    existing = activities[activity]["participants"][0]
    
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": existing})
    
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_activity_not_found():
    """Test that signing up for a non-existent activity returns 404."""
    # Arrange
    email = "x@x.com"
    
    # Act
    response = client.post("/activities/Nonexistent/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_success():
    """Test that removing an existing participant succeeds."""
    # Arrange
    activity = "Chess Club"
    email = "tempstudent@mergington.edu"
    # First add the student
    client.post(f"/activities/{activity}/signup", params={"email": email})
    
    # Act
    response = client.post(f"/activities/{activity}/remove", params={"email": email})
    
    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity}"}
    assert email not in activities[activity]["participants"]


def test_remove_not_registered():
    """Test that removing someone not registered returns 400."""
    # Arrange
    activity = "Chess Club"
    email = "not@here.com"
    
    # Act
    response = client.post(f"/activities/{activity}/remove", params={"email": email})
    
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student not registered for this activity"


def test_remove_activity_not_found():
    """Test that removing from a nonexistent activity returns 404."""
    # Arrange
    email = "x@x.com"
    
    # Act
    response = client.post("/activities/Nonexistent/remove", params={"email": email})
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
