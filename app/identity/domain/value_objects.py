from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HashedPassword:
    value: str

    def _validation(self):
        if not self.value:
            raise ValueError("Invalid password. Password cannot be empty.")
