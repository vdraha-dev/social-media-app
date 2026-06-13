import re
from dataclasses import dataclass

from app.shared.domain.base_value_object import BaseValueObject


@dataclass(frozen=True, slots=True)
class Email(BaseValueObject):
    value: str

    def _validate(self) -> None:
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, self.value):
            raise ValueError(f"Unvalid email address: {self.value!r}")

    def __str__(self) -> str:
        return self.value

    def __repr__(self):
        return f"Email(value={self.value!r})"

    @property
    def domain(self) -> str:
        return self.value.split("@")[1]


@dataclass(frozen=True, slots=True)
class Url(BaseValueObject):
    value: str

    def _validate(self):
        if not self.value.startswith(("http://", "https://")):
            raise ValueError(f"Invalid URL: {self.value!r}")

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"Url(value={self.value!r})"


@dataclass(frozen=True, slots=True)
class Pagination(BaseValueObject):
    page_number: int = 1
    page_size: int = 20

    def _validate(self):
        if self.page_number < 1:
            raise ValueError(
                f"Invalid page number: {self.page_number} | The page must be >= 1"
            )
        if not (1 <= self.page_size <= 100):
            raise ValueError(
                f"Invalid page size: {self.page_size}"
                " | The page size must be between 1 and 100"
            )

    @property
    def offset(self) -> int:
        return (self.page_number - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size
