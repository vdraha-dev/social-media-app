from app.shared.domain.exceptions import DomainError


class UserProfileNotFound(DomainError): ...


class UserProfileIsAlreadyExists(DomainError): ...
