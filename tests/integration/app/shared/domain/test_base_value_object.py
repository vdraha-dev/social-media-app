from dataclasses import dataclass

import pytest

from app.shared.domain.base_value_object import BaseValueObject
from app.shared.domain.value_objects import Email


@dataclass
class ConcreteVo(BaseValueObject):
    value: str

    def _validate(self):
        if not self.value:
            raise ValueError("value cannot be empty")


class TestBaseValueObject:
    def test_validation_called_on_init(self):
        with pytest.raises(ValueError, match="value cannot be empty"):
            ConcreteVo("")

    def test_validation_passes_with_valid_value(self):
        vo = ConcreteVo("hello")
        assert vo.value == "hello"

    def test_inherits_validate_contract(self):
        assert hasattr(BaseValueObject, "_validate")

    def test_post_init_triggers_validate(self):
        class TrackingVo(BaseValueObject):
            def __init__(self, x: int):
                self.x = x
                self.validated = False
                self.__post_init__()

            def _validate(self):
                self.validated = True
                if self.x < 0:
                    raise ValueError("negative")

        vo = TrackingVo(5)
        assert vo.validated

    def test_validation_error_inherits_from_value_error(self):
        with pytest.raises(ValueError):
            ConcreteVo("")

    def test_can_create_value_object_directly(self):
        vo = ConcreteVo("valid")
        assert vo.value == "valid"

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="value cannot be empty"):
            ConcreteVo("")


class TestBaseValueObjectWithEmail:
    def test_base_value_object_is_parent_of_email(self):
        assert issubclass(Email, BaseValueObject)
