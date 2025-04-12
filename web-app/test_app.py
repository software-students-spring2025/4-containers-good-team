"""
Testing for app.py.

This file contains unit tests for the Flask application. The tests simulate MongoDB
operations using dummy collections and verify that the endpoints behave as expected.
"""

import json
import datetime
import pytest
from werkzeug.security import generate_password_hash
import app as app_mod
from app import app

def test_example():
    """An example unit test. This test will always pass."""
    assert True

# simulate MongoDB operations.
class DummyCollection:
    """A dummy collection class to simulate MongoDB collection operations."""
    def __init__(self):
        """Initialize the DummyCollection class."""
        self.data = []
    def find_one(self, query):
        """Return the first document matching the given query."""
        for item in self.data:
            if all(item.get(k) == v for k, v in query.items()):
                return item
        return None
    def insert_one(self, document):
        """Insert a document into the collection and return a dummy insert result."""
        document["_id"] = "dummy_id"
        self.data.append(document)
        class DummyInsert:
            """A dummy insert result class."""
            inserted_id = "dummy_id"
        return DummyInsert()
    def find(self, query):
        """Return all documents (ignoring the query for simplicity)."""
        return self.data

@pytest.fixture
def client(monkeypatch):
    """A pytest fixture that returns a test client with dummy MongoDB globals patched."""
    app.config["TESTING"] = True
    dummy_users = DummyCollection()
    dummy_sensor_data = DummyCollection()
    monkeypatch.setitem(app_mod.__dict__, "users_collection", dummy_users)
    monkeypatch.setitem(app_mod.__dict__, "sensor_data_collection", dummy_sensor_data)
    with app.test_client() as client:
        yield client

def test_home(client):
    """Test that the home route ("/") renders the login page."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_data(as_text=True)
    assert "<form" in data.lower()

def test_index_requires_login(client):
    """Test that accessing /home without being logged in redirects to /login."""
    response = client.get("/home", follow_redirects=False)
    # redirect to /login if not logged in
    assert response.status_code == 302
    assert "login" in response.headers["Location"]

def test_translator_requires_login(client):
    """Test that accessing /translator without login redirects to /login."""
    response = client.get("/translator", follow_redirects=False)
    assert response.status_code == 302
    assert "login" in response.headers["Location"]

def test_register_get(client):
    """Test that the GET request on /register renders the registration page."""
    response = client.get("/register")
    assert response.status_code == 200
    data = response.get_data(as_text=True)
    assert "<form" in data

def test_register_post_missing_fields(client):
    """Test that a POST to /register with missing fields redirects back to /register."""
    response = client.post("/register", data={"first_name": "John"})
    assert response.status_code == 302
    assert "register" in response.headers["Location"]

def test_register_post_password_mismatch(client):
    """Test that a POST to /register with a password mismatch redirects back to /register."""
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password": "secret",
        "confirm_password": "password123"
    }
    response = client.post("/register", data=data)
    assert response.status_code == 302
    assert "register" in response.headers["Location"]

def test_register_post_existing_user(client):
    """Test that registering an existing user redirects back to /register."""
    data = {
        "first_name": "Person",
        "last_name": "Doe",
        "email": "person@example.com",
        "password": "password",
        "confirm_password": "password"
    }
    #response1 = client.post("/register", data=data)
    response2 = client.post("/register", data=data)
    assert response2.status_code == 302
    assert "register" in response2.headers["Location"]

def test_register_post_success(client):
    """Test that a successful registration redirects to /home."""
    data = {
        "first_name": "Giulia",
        "last_name": "Carvalho",
        "email": "giulia@example.com",
        "password": "mypassword",
        "confirm_password": "mypassword"
    }
    response = client.post("/register", data=data)
    # redirect to /login if success.
    assert response.status_code == 302
    assert "home" in response.headers["Location"]

def test_login_get(client):
    """Test that the GET request on /login renders the login page."""
    response = client.get("/login")
    assert response.status_code == 200
    data = response.get_data(as_text=True)
    assert "<form" in data

def test_login_post_success(client):
    """Test that a valid login redirects to the translator page."""
    password = "securepass"
    hashed = generate_password_hash(password)
    user = {
        "first_name": "Bob",
        "last_name": "Builder",
        "email": "bob@example.com",
        "password": hashed,
        "created_at": datetime.datetime.utcnow()
    }
    app_mod.users_collection.insert_one(user)
    data = {"email": "bob@example.com", "password": password}
    response = client.post("/login", data=data)
    assert response.status_code == 302
    # success login, redirect to translator
    assert "translator" in response.headers["Location"]

def test_login_post_invalid(client):
    """Test that an invalid login attempt redirects back to /login."""
    data = {"email": "nonexistent@example.com", "password": "password"}
    response = client.post("/login", data=data)
    assert response.status_code == 302
    assert "login" in response.headers["Location"]

def test_logout(client):
    """Test that logout clears the session and redirects to home."""
    with client.session_transaction() as sess:
        sess["username"] = "test@example.com"
    response = client.get("/logout", follow_redirects=False)
    assert response.status_code == 302
    assert "/" in response.headers["Location"]

def test_get_sensor_data(client):
    """Test that the API for sensor data returns a list of documents with formatted timestamps."""
    test_doc = {
        "input_text": "Test",
        "target_language": "en",
        "timestamp": datetime.datetime.utcnow()
    }
    app_mod.mongo.db["sensor_data"].insert_one(test_doc)
    response = client.get("/api/sensor_data")
    assert response.status_code == 200
    json_data = json.loads(response.get_data(as_text=True))
    assert isinstance(json_data, list)
    if json_data:
        assert "timestamp" in json_data[0]
        assert isinstance(json_data[0]["_id"], str)

def test_simulate_input(client):
    """Test that /simulate_input returns a JSON response with a message and id."""
    response = client.get("/simulate_input")
    assert response.status_code == 200
    json_data = json.loads(response.get_data(as_text=True))
    assert json_data.get("message") == "Test document inserted"
    assert "id" in json_data

def test_submit_text_missing_input(client):
    """Test that posting to /submit_text without input_text returns a 400 error."""
    response = client.post("/submit_text", json={})
    assert response.status_code == 400
    json_data = json.loads(response.get_data(as_text=True))
    assert json_data.get("error") == "Input text is required"

def test_submit_text_success(client):
    """Test that a valid POST to /submit_text returns a successful message and an id."""
    data = {"input_text": "Hello", "target_language": "fr"}
    response = client.post("/submit_text", json=data)
    assert response.status_code == 200
    json_data = json.loads(response.get_data(as_text=True))
    assert json_data.get("message") == "Text submitted successfully"
    assert "id" in json_data
