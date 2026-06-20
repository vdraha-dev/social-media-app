from abc import ABC
from dataclasses import FrozenInstanceError, dataclass

import pytest

from app.shared.domain.base_value_object import BaseValueObject


@dataclass(frozen=True)
class ConcreteValueObject(BaseValueObject):
    value: str

    def _validate(self):
        if not self.value:
            raise ValueError("value cannot be empty")


class TestBaseValueObject:
    def test_is_abstract(self):
        assert issubclass(BaseValueObject, ABC)

    def test_cannot_instantiate_abstract(self):
        with pytest.raises(TypeError):
            BaseValueObject()  # pyright: ignore

    def test_calls_validate_on_init(self):
        obj = ConcreteValueObject(value="hello")
        assert obj.value == "hello"

    def test_validation_error_on_init(self):
        with pytest.raises(ValueError, match="value cannot be empty"):
            ConcreteValueObject(value="")

    def test_validate_called_by_post_init(self):
        call_count = 0

        @dataclass(frozen=True)
        class TrackingValueObject(BaseValueObject):
            value: str = ""

            def _validate(self):
                nonlocal call_count
                call_count += 1

        TrackingValueObject()
        assert call_count == 1

    def test_frozen(self):
        obj = ConcreteValueObject(value="hello")
        with pytest.raises(FrozenInstanceError):
            obj.value = "world"  # pyright: ignore
