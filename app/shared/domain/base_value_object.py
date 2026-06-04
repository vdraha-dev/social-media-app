from abc import abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BaseValueObject:
    def __post_init__(self):
        self._validate()

    @abstractmethod
    def _validate(self): ...
