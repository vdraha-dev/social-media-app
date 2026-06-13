import pytest

from app.identity.domain.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
    UserAlreadyExistsError,
)
from app.shared.domain.exceptions import DomainError


class TestTokenExpiredError:
    def test_is_domain_error(self):
        assert issubclass(TokenExpiredError, DomainError)

    def test_can_be_raised(self):
        with pytest.raises(TokenExpiredError):
            raise TokenExpiredError()

    def test_with_message(self):
        with pytest.raises(TokenExpiredError, match="expired"):
            raise TokenExpiredError("Token expired")


class TestInvalidTokenError:
    def test_is_domain_error(self):
        assert issubclass(InvalidTokenError, DomainError)

    def test_can_be_raised(self):
        with pytest.raises(InvalidTokenError):
            raise InvalidTokenError()


class TestUserAlreadyExistsError:
    def test_is_domain_error(self):
        assert issubclass(UserAlreadyExistsError, DomainError)

    def test_can_be_raised(self):
        with pytest.raises(UserAlreadyExistsError):
            raise UserAlreadyExistsError("User exists")


class TestInvalidCredentialsError:
    def test_is_domain_error(self):
        assert issubclass(InvalidCredentialsError, DomainError)

    def test_can_be_raised(self):
        with pytest.raises(InvalidCredentialsError):
            raise InvalidCredentialsError("Bad credentials")


class TestExceptionHierarchy:
    @pytest.mark.parametrize(
        "exc_type",
        [
            TokenExpiredError,
            InvalidTokenError,
            UserAlreadyExistsError,
            InvalidCredentialsError,
        ],
    )
    def test_all_caught_by_domain_error(self, exc_type):
        with pytest.raises(DomainError):
            raise exc_type()
