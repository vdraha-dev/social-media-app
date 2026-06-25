import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.shared.domain.exceptions import (
    AlreadyExistsError,
    ConflictError,
    DomainError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from app.shared.presentation.exception_handlers import register_exception_handlers


@pytest.fixture
def app():
    application = FastAPI()
    register_exception_handlers(application)

    @application.get("/test/not-found")
    async def raise_not_found():  # pyright: ignore
        raise NotFoundError("User", "123")

    @application.get("/test/already-exists")
    async def raise_already_exists():  # pyright: ignore
        raise AlreadyExistsError("User", "email", "taken@test.com")

    @application.get("/test/permission-denied")
    async def raise_permission_denied():  # pyright: ignore
        raise PermissionDeniedError("access resource", "Access denied")

    @application.get("/test/validation")
    async def raise_validation():  # pyright: ignore
        raise ValidationError("Invalid input")

    @application.get("/test/conflict")
    async def raise_conflict():  # pyright: ignore
        raise ConflictError("Resource conflict")

    class _CustomDomainError(DomainError):
        pass

    @application.get("/test/domain-error")
    async def raise_domain():  # pyright: ignore
        raise _CustomDomainError("Generic domain error")

    return application


@pytest.fixture
def client(app: FastAPI):
    return TestClient(app)


class TestNotFoundHandler:
    def test_returns_404(self, client: TestClient):
        response = client.get("/test/not-found")
        assert response.status_code == 404

    def test_returns_detail(self, client: TestClient):
        response = client.get("/test/not-found")
        assert response.json()["detail"] == "User not found with identifier 123"

    def test_returns_not_found_code(self, client: TestClient):
        response = client.get("/test/not-found")
        assert response.json()["code"] == "NOT_FOUND"


class TestAlreadyExistsHandler:
    def test_returns_409(self, client: TestClient):
        response = client.get("/test/already-exists")
        assert response.status_code == 409

    def test_returns_detail(self, client: TestClient):
        response = client.get("/test/already-exists")
        assert (
            response.json()["detail"]
            == "User with email='taken@test.com' already exists"
        )

    def test_returns_already_exists_code(self, client: TestClient):
        response = client.get("/test/already-exists")
        assert response.json()["code"] == "ALREADY_EXISTS"


class TestPermissionDeniedHandler:
    def test_returns_403(self, client: TestClient):
        response = client.get("/test/permission-denied")
        assert response.status_code == 403

    def test_returns_detail(self, client: TestClient):
        response = client.get("/test/permission-denied")
        assert (
            response.json()["detail"]
            == "Access denied for access resource: Access denied"
        )

    def test_returns_permission_denied_code(self, client: TestClient):
        response = client.get("/test/permission-denied")
        assert response.json()["code"] == "PERMISSION_DENIED"


class TestValidationHandler:
    def test_returns_422(self, client: TestClient):
        response = client.get("/test/validation")
        assert response.status_code == 422

    def test_returns_detail(self, client: TestClient):
        response = client.get("/test/validation")
        assert response.json()["detail"] == "Invalid input"

    def test_returns_validation_code(self, client: TestClient):
        response = client.get("/test/validation")
        assert response.json()["code"] == "VALIDATION_ERROR"


class TestConflictHandler:
    def test_returns_409(self, client: TestClient):
        response = client.get("/test/conflict")
        assert response.status_code == 409

    def test_returns_detail(self, client: TestClient):
        response = client.get("/test/conflict")
        assert response.json()["detail"] == "Resource conflict"

    def test_returns_conflict_code(self, client: TestClient):
        response = client.get("/test/conflict")
        assert response.json()["code"] == "CONFLICT"


class TestDomainErrorHandler:
    def test_returns_400(self, client: TestClient):
        response = client.get("/test/domain-error")
        assert response.status_code == 400

    def test_returns_detail(self, client: TestClient):
        response = client.get("/test/domain-error")
        assert response.json()["detail"] == "Generic domain error"

    def test_returns_domain_error_code(self, client: TestClient):
        response = client.get("/test/domain-error")
        assert response.json()["code"] == "DOMAIN_ERROR"
