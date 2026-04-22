import inspect
import os
import sys

from fastapi.testclient import TestClient

from app.main import app
from app.routes.userInput import get_current_user as route_get_current_user
from app.routes.userInput import get_current_user_optional

# Add root directory to Python path
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../../../')))

class TestUser():
    user_id = 1
    username = "test"
    
#Helper function to override the current user in tests  
def override_current_user():
    return TestUser()


app.dependency_overrides[get_current_user_optional] = override_current_user

client = TestClient(app)


def test_post_api_submit_user_input():
    response = client.post("/userinput", json={
        "text": "This is a test input",
        "uploadedFiles": [""]
    })
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Sentiment analysis completed successfully."
    assert "results" in data and isinstance(data["results"], list)
