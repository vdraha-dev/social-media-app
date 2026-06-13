from app.identity.domain.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
    UserAlreadyExistsError,
)
from app.shared.domain.exceptions import DomainError


class TestIdentityExceptions:
    def test_all_inherit_from_domain_error(self):
        assert issubclass(TokenExpiredError, DomainError)
        assert issubclass(InvalidTokenError, DomainError)
        assert issubclass(UserAlreadyExistsError, DomainError)
        assert issubclass(InvalidCredentialsError, DomainError)

    def test_can_instantiate_with_message(self):
        exc = TokenExpiredError("Token has expired")
        assert str(exc) == "Token has expired"

        exc = InvalidTokenError("Bad token")
        assert str(exc) == "Bad token"

        exc = UserAlreadyExistsError("User exists")
        assert str(exc) == "User exists"

        exc = InvalidCredentialsError("Wrong email or password")
        assert str(exc) == "Wrong email or password"

    def test_can_instantiate_without_message(self):
        exc = TokenExpiredError()
        assert isinstance(exc, TokenExpiredError)

    def test_can_be_caught_by_domain_error(self):
        errors = [
            TokenExpiredError(),
            InvalidTokenError(),
            UserAlreadyExistsError(),
            InvalidCredentialsError(),
        ]
        for exc in errors:
            assert isinstance(exc, DomainError)

    def test_exceptions_are_hashable(self):
        exc = InvalidCredentialsError("bad")
        d = {exc: "found"}
        assert d[exc] == "found"
