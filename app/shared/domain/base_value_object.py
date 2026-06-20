from abc import ABC, abstractmethod


class BaseValueObject(ABC):
    def __post_init__(self):
        self._validate()

    @abstractmethod
    def _validate(self): ...
