import pytest

from app.shared.domain.exceptions import (
    AlreadyExistsError,
    ConflictError,
    DomainError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)


class TestDomainError:
    def test_is_exception(self):
        assert issubclass(DomainError, Exception)

    def test_can_be_raised(self):
        with pytest.raises(DomainError):
            raise DomainError()


class TestNotFoundError:
    def test_is_subclass_of_domain_error(self):
        assert issubclass(NotFoundError, DomainError)

    def test_has_entity_and_identifier_attributes(self):
        assert hasattr(NotFoundError, "__init__")


class TestAlreadyExistsError:
    def test_is_subclass_of_domain_error(self):
        assert issubclass(AlreadyExistsError, DomainError)

    def test_has_entity_field_value_attributes(self):
        assert hasattr(AlreadyExistsError, "__init__")


class TestPermissionDeniedError:
    def test_initializes_fields(self):
        exc = PermissionDeniedError("delete_post")
        assert exc.action == "delete_post"

    def test_default_message_without_reason(self):
        exc = PermissionDeniedError("delete_post")
        assert str(exc) == "Acess denied for delete_post"

    def test_message_with_reason(self):
        exc = PermissionDeniedError("delete_post", "not an admin")
        assert str(exc) == "Acess denied for delete_post: not an admin"

    def test_empty_reason(self):
        exc = PermissionDeniedError("view", "")
        assert str(exc) == "Acess denied for view"

    def test_inherits_from_domain_error(self):
        assert issubclass(PermissionDeniedError, DomainError)


class TestValidationError:
    def test_is_domain_error(self):
        assert issubclass(ValidationError, DomainError)

    def test_can_be_raised_with_message(self):
        with pytest.raises(ValidationError) as excinfo:
            raise ValidationError("invalid data")
        assert str(excinfo.value) == "invalid data"


class TestConflictError:
    def test_is_domain_error(self):
        assert issubclass(ConflictError, DomainError)

    def test_can_be_raised(self):
        with pytest.raises(ConflictError):
            raise ConflictError()


class TestExceptionHierarchy:
    @pytest.mark.parametrize(
        "exc_type, args",
        [
            (PermissionDeniedError, ("a",)),
            (ValidationError, ()),
            (ConflictError, ()),
        ],
    )
    def test_subclasses_caught_by_domain_error(self, exc_type, args):
        with pytest.raises(DomainError):
            raise exc_type(*args)
