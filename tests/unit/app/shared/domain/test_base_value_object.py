from dataclasses import dataclass

import pytest

from app.shared.domain.base_value_object import BaseValueObject


class TestBaseValueObject:
    def test_calls_validate_on_init_when_dataclass(self):
        @dataclass
        class ValidVO(BaseValueObject):
            def _validate(self):
                pass

        instance = ValidVO()
        assert isinstance(instance, BaseValueObject)

    def test_raises_when_validate_raises_with_dataclass(self):
        @dataclass
        class InvalidVO(BaseValueObject):
            def _validate(self):
                raise ValueError("invalid")

        with pytest.raises(ValueError, match="invalid"):
            InvalidVO()

    def test_validate_not_auto_called_without_dataclass(self):
        class PlainVO(BaseValueObject):
            def _validate(self):
                raise ValueError("should not be called")

        instance = PlainVO()
        assert isinstance(instance, BaseValueObject)

    def test_abstract_validate_returns_none_when_not_overridden(self):
        @dataclass
        class NoValidateVO(BaseValueObject):
            pass

        instance = NoValidateVO()
        assert instance._validate() is None

    def test_custom_validate_inherits_with_dataclass(self):
        called = False

        @dataclass
        class CustomVO(BaseValueObject):
            def _validate(self):
                nonlocal called
                called = True

        CustomVO()
        assert called
