from abc import abstractmethod


class BaseValueObject:
    def __post_init__(self):
        self._validate()

    @abstractmethod
    def _validate(self): ...
