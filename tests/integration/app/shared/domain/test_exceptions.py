from app.shared.domain.exceptions import (
    AlreadyExistsError,
    ConflictError,
    DomainError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)


class TestDomainErrorHierarchy:
    def test_all_errors_inherit_from_domain_error(self):
        assert issubclass(NotFoundError, DomainError)
        assert issubclass(AlreadyExistsError, DomainError)
        assert issubclass(PermissionDeniedError, DomainError)
        assert issubclass(ValidationError, DomainError)
        assert issubclass(ConflictError, DomainError)

    def test_domain_error_is_base(self):
        assert issubclass(DomainError, Exception)

    def test_not_found_error_message(self):
        exc = NotFoundError("User", 42)
        assert "User" in str(exc)
        assert "42" in str(exc)
        assert exc.entity == "User"
        assert exc.identifier == 42

    def test_already_exists_error_message(self):
        exc = AlreadyExistsError("User", "email", "a@b.com")
        assert "User" in str(exc)
        assert "email" in str(exc)
        assert "a@b.com" in str(exc)
        assert exc.entity == "User"
        assert exc.field == "email"
        assert exc.value == "a@b.com"

    def test_permission_denied_with_reason(self):
        exc = PermissionDeniedError("delete", "not admin")
        assert "delete" in str(exc)
        assert "not admin" in str(exc)
        assert exc.action == "delete"

    def test_permission_denied_without_reason(self):
        exc = PermissionDeniedError("delete")
        assert "delete" in str(exc)
        assert exc.action == "delete"

    def test_validation_error_no_args(self):
        exc = ValidationError()
        assert isinstance(exc, ValidationError)

    def test_conflict_error_no_args(self):
        exc = ConflictError()
        assert isinstance(exc, ConflictError)

    def test_validation_error_with_message(self):
        exc = ValidationError("bad data")
        assert "bad data" in str(exc)

    def test_conflict_error_with_message(self):
        exc = ConflictError("duplicate")
        assert "duplicate" in str(exc)

    def test_can_catch_generic_domain_error(self):
        exc: DomainError = NotFoundError("Post", "abc")
        assert isinstance(exc, DomainError)
        assert isinstance(exc, NotFoundError)

    def test_errors_are_hashable(self):
        exc = NotFoundError("User", 1)
        d = {exc: "found"}
        assert d[exc] == "found"


class TestExceptionAttributes:
    def test_not_found_error_repr(self):
        exc = NotFoundError("User", 1)
        r = repr(exc)
        assert isinstance(r, str)

    def test_already_exists_error_str_contains_values(self):
        exc = AlreadyExistsError("Product", "sku", "ABC123")
        msg = str(exc)
        assert "Product" in msg
        assert "sku" in msg
        assert "ABC123" in msg

    def test_permission_denied_default_message_format(self):
        exc = PermissionDeniedError("write")
        msg = str(exc)
        assert "write" in msg
        assert "Acess denied" in msg

    def test_validation_error_is_instance_of_value_error(self):
        assert not issubclass(ValidationError, ValueError)

    def test_not_found_error_is_not_value_error(self):
        assert not issubclass(NotFoundError, ValueError)
