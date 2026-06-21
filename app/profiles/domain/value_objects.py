from dataclasses import dataclass

from app.shared.domain.base_value_object import BaseValueObject
from app.shared.domain.value_objects import Url


@dataclass(frozen=True, slots=True)
class Bio(BaseValueObject):
    value: str

    def _validate(self):
        if len(self.value) > 512:
            raise ValueError("Bio must be less than 512 characters")

    def __str__(self):
        return self.value


@dataclass(frozen=True, slots=True)
class SocialLink(BaseValueObject):
    platform: str
    url: Url

    def __str__(self):
        return str(self.url)

    def to_dict(self) -> dict[str, str]:
        return {
            "platform": self.platform,
            "url": str(self.url),
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> SocialLink:
        return cls(platform=data["platform"], url=Url(data["url"]))


@dataclass(frozen=True, slots=True)
class DisplayedName(BaseValueObject):
    value: str

    def _validate(self): ...

    def __str__(self):
        return self.value
