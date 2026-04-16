import uuid

from fastapi.testclient import TestClient


def _unique_email() -> str:
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


class TestRegister:
    def test_returns_201(self, client: TestClient):
        response = client.post("/auth/register", json={
            "name": "Test User",
            "email": _unique_email(),
            "password": "senha123",
        })
        assert response.status_code == 201

    def test_response_shape(self, client: TestClient):
        data = client.post("/auth/register", json={
            "name": "Test User",
            "email": _unique_email(),
            "password": "senha123",
        }).json()
        assert "access_token" in data
        assert "token_type" in data
        assert "user" in data
        assert data["token_type"] == "bearer"

    def test_user_fields(self, client: TestClient):
        email = _unique_email()
        user = client.post("/auth/register", json={
            "name": "Maria Silva",
            "email": email,
            "password": "senha123",
        }).json()["user"]
        assert user["name"] == "Maria Silva"
        assert user["email"] == email
        assert "id" in user

    def test_duplicate_email_returns_409(self, client: TestClient):
        email = _unique_email()
        payload = {"name": "Dup User", "email": email, "password": "senha123"}
        client.post("/auth/register", json=payload)
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 409

    def test_short_password_returns_422(self, client: TestClient):
        response = client.post("/auth/register", json={
            "name": "User",
            "email": _unique_email(),
            "password": "123",
        })
        assert response.status_code == 422

    def test_invalid_email_returns_422(self, client: TestClient):
        response = client.post("/auth/register", json={
            "name": "User",
            "email": "not-an-email",
            "password": "senha123",
        })
        assert response.status_code == 422

    def test_short_name_returns_422(self, client: TestClient):
        response = client.post("/auth/register", json={
            "name": "A",
            "email": _unique_email(),
            "password": "senha123",
        })
        assert response.status_code == 422


class TestLogin:
    def _register(self, client: TestClient) -> tuple[str, str]:
        email = _unique_email()
        password = "senha123"
        client.post("/auth/register", json={"name": "Login User", "email": email, "password": password})
        return email, password

    def test_returns_200(self, client: TestClient):
        email, password = self._register(client)
        response = client.post("/auth/login", json={"email": email, "password": password})
        assert response.status_code == 200

    def test_response_shape(self, client: TestClient):
        email, password = self._register(client)
        data = client.post("/auth/login", json={"email": email, "password": password}).json()
        assert "access_token" in data
        assert "token_type" in data
        assert "user" in data
        assert data["token_type"] == "bearer"

    def test_user_fields(self, client: TestClient):
        email, password = self._register(client)
        user = client.post("/auth/login", json={"email": email, "password": password}).json()["user"]
        assert user["email"] == email
        assert "id" in user
        assert "name" in user

    def test_wrong_password_returns_401(self, client: TestClient):
        email, _ = self._register(client)
        response = client.post("/auth/login", json={"email": email, "password": "errada"})
        assert response.status_code == 401

    def test_unknown_email_returns_401(self, client: TestClient):
        response = client.post("/auth/login", json={"email": "nobody@example.com", "password": "senha123"})
        assert response.status_code == 401

    def test_token_is_non_empty_string(self, client: TestClient):
        email, password = self._register(client)
        token = client.post("/auth/login", json={"email": email, "password": password}).json()["access_token"]
        assert isinstance(token, str)
        assert len(token) > 20
