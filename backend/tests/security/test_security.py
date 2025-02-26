import pytest
from fastapi.testclient import TestClient
from jose import jwt
from datetime import datetime, timedelta

from app.main import app
from app.core.security import create_access_token, verify_password, get_password_hash
from app.core.config import settings

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def test_user_data():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "StrongP@ssw0rd123"
    }

@pytest.fixture
def test_token_data():
    return {
        "sub": "testuser",
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }

class TestAuthentication:
    def test_password_hashing(self):
        """Testa a funcionalidade de hash de senha"""
        password = "StrongP@ssw0rd123"
        hashed = get_password_hash(password)
        
        # Verifica se o hash é diferente da senha original
        assert hashed != password
        
        # Verifica se a verificação funciona
        assert verify_password(password, hashed)
        
        # Verifica se uma senha errada falha
        assert not verify_password("WrongPassword", hashed)

    def test_token_creation(self, test_token_data):
        """Testa a criação de tokens JWT"""
        token = create_access_token(test_token_data)
        
        # Verifica se o token foi criado
        assert token is not None
        
        # Decodifica o token e verifica os claims
        decoded = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        assert decoded["sub"] == test_token_data["sub"]

    def test_token_expiration(self):
        """Testa a expiração de tokens"""
        # Cria um token que já expirou
        expired_data = {
            "sub": "testuser",
            "exp": datetime.utcnow() - timedelta(minutes=1)
        }
        token = create_access_token(expired_data)
        
        # Verifica se o token expirado é rejeitado
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )

class TestAuthorization:
    def test_protected_endpoint_without_token(self, test_client):
        """Testa acesso a endpoint protegido sem token"""
        response = test_client.get("/api/v1/protected")
        assert response.status_code == 401

    def test_protected_endpoint_with_invalid_token(self, test_client):
        """Testa acesso a endpoint protegido com token inválido"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = test_client.get("/api/v1/protected", headers=headers)
        assert response.status_code == 401

    def test_protected_endpoint_with_valid_token(self, test_client, test_token_data):
        """Testa acesso a endpoint protegido com token válido"""
        token = create_access_token(test_token_data)
        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.get("/api/v1/protected", headers=headers)
        assert response.status_code == 200

class TestRateLimit:
    def test_rate_limit(self, test_client):
        """Testa o rate limiting"""
        # Faz múltiplas requisições rápidas
        responses = []
        for _ in range(100):
            response = test_client.get("/api/v1/features")
            responses.append(response.status_code)

        # Verifica se alguma requisição foi limitada (429 Too Many Requests)
        assert 429 in responses

class TestInputValidation:
    def test_sql_injection(self, test_client):
        """Testa proteção contra SQL injection"""
        malicious_input = "'; DROP TABLE features; --"
        response = test_client.get(f"/api/v1/features?name={malicious_input}")
        assert response.status_code != 500  # Não deve causar erro interno

    def test_xss_protection(self, test_client):
        """Testa proteção contra XSS"""
        malicious_input = "<script>alert('xss')</script>"
        response = test_client.post("/api/v1/features", json={
            "name": "test",
            "description": malicious_input
        })
        data = response.json()
        assert "<script>" not in data["description"]

class TestDataPrivacy:
    def test_password_not_exposed(self, test_client, test_user_data):
        """Testa se senhas não são expostas nas respostas"""
        response = test_client.post("/api/v1/users", json=test_user_data)
        data = response.json()
        assert "password" not in data

    def test_sensitive_headers(self, test_client):
        """Testa se headers sensíveis não são expostos"""
        response = test_client.get("/api/v1/features")
        assert "X-Powered-By" not in response.headers
        assert "Server" not in response.headers
