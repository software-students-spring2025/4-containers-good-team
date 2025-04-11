import json
import datetime
import pytest
from web_app.app import app, generate_password_hash

def test_example():
    assert True

# simulate MongoDB operations.
class DummyCollection:
    def __init__(self):
        self.data = []
    def find_one(self, query):
        for item in self.data:
            if all(item.get(k) == v for k, v in query.items()):
                return item
        return None
    def insert_one(self, document):
        document["_id"] = "dummy_id"
        self.data.append(document)
        class DummyInsert:
            inserted_id = "dummy_id"
        return DummyInsert()
    def find(self, query):
        return self.data

@pytest.fixture
def client(monkeypatch):
    app.config["TESTING"] = True

    monkeypatch.setattr(app, "render_template", lambda template, **kwargs: f"Rendered {template}")

    # MongoDB collections.
    dummy_users = DummyCollection()
    dummy_sensor_data = DummyCollection()

    # mongo attributes
    monkeypatch.setattr(app, "users_collection", dummy_users)
    dummy_db = {"users": dummy_users, "sensor_data": dummy_sensor_data}
    monkeypatch.setattr(app, "mongo", type("DummyMongo", (), {"db": dummy_db})())

    with app.test_client() as client:
        yield client

def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Rendered index.html" in response.get_data(as_text=True)

def test_translator_not_logged(client):
    response = client.get("/translator", follow_redirects=False)
    # redirect to /login if not logged in
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

def test_register_get(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert "Rendered register.html" in response.get_data(as_text=True)

def test_register_post_missing_fields(client):
    # post - missing required fields.
    response = client.post("/register", data={"first_name": "John"})
    assert response.status_code == 302
    assert "/register" in response.headers["Location"]

def test_register_post_password_mismatch(client):
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password": "secret",
        "confirm_password": "password123"
    }
    response = client.post("/register", data=data)
    assert response.status_code == 302
    assert "/register" in response.headers["Location"]

def test_register_post_existing_user(client):
    # user registration
    data = {
        "first_name": "Person",
        "last_name": "Doe",
        "email": "person@example.com",
        "password": "password",
        "confirm_password": "password"
    }
    response = client.post("/register", data=data)
    assert response.status_code == 302
    # registering
    response = client.post("/register", data=data)
    assert response.status_code == 302
    assert "/register" in response.headers["Location"]

def test_register_post_success(client):
    # non-existing username
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
    assert "/login" in response.headers["Location"]

def test_login_get(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert "Rendered login.html" in response.get_data(as_text=True)

def test_login_post_success(client):
    # user to collection
    password = "securepass"
    hashed = generate_password_hash(password)
    user = {
        "first_name": "Bob",
        "last_name": "Builder",
        "email": "bob@example.com",
        "password": hashed,
        "created_at": datetime.datetime.utcnow()
    }
    app.users_collection.insert_one(user)
    data = {"email": "bob@example.com", "password": password}
    response = client.post("/login", data=data)
    assert response.status_code == 302
    # success login, redirect to translator 
    assert "/translator" in response.headers["Location"]

def test_login_post_invalid(client):
    # attempt to log in with a non-existent user.
    data = {"email": "nonexistent@example.com", "password": "password"}
    response = client.post("/login", data=data)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

def test_logout(client):
    with client.session_transaction() as sess:
        sess["username"] = "test@example.com"
    response = client.post("/logout", follow_redirects=False)
    assert response.status_code == 302
    assert "/" in response.headers["Location"]

def test_get_sensor_data(client):
    # dummy sensor_data collection with a test document.
    test_docu = {
        "input_text": "Test",
        "target_language": "en",
        "timestamp": datetime.datetime.utcnow()
    }
    app.mongo.db["sensor_data"].insert_one(test_docu)
    response = client.get("/api/sensor_data")
    assert response.status_code == 200
    json_data = json.loads(response.get_data(as_text=True))
    assert isinstance(json_data, list)
    if json_data:
        assert "timestamp" in json_data[0]
        assert isinstance(json_data[0]["_id"], str)

def test_simulate_input(client):
    response = client.get("/simulate_input")
    assert response.status_code == 200
    json_data = json.loads(response.get_data(as_text=True))
    assert json_data.get("message") == "Test document inserted"
    assert "id" in json_data

def test_submit_text_missing_input(client):
    response = client.post("/submit_text", json={})
    assert response.status_code == 400
    json_data = json.loads(response.get_data(as_text=True))
    assert json_data.get("error") == "Input text is required"

def test_submit_text_success(client):
    data = {"input_text": "Hello", "target_language": "fr"}
    response = client.post("/submit_text", json=data)
    assert response.status_code == 200
    json_data = json.loads(response.get_data(as_text=True))
    assert json_data.get("message") == "Text submitted successfully"
    assert "id" in json_data

