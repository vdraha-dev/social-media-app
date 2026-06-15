from dataclasses import dataclass

from app.shared.domain.base_value_object import BaseValueObject
from app.shared.domain.value_objects import Url


@dataclass(frozen=True, slots=True)
class Bio(BaseValueObject):
    value: str

    def _validate(self):
        if len(self.value) > 500:
            raise ValueError("Bio must be less than 500 characters")

    def __str__(self):
        return self.value


@dataclass(frozen=True, slots=True)
class SocialLink(BaseValueObject):
    platform: str
    url: Url

    def __str__(self):
        return str(self.url)


@dataclass(frozen=True, slots=True)
class DisplayedName(BaseValueObject):
    value: str

    def __str__(self):
        return self.value
