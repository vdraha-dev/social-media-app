from app.shared.domain.errors import ApplicationError


class TokenExpiredError(ApplicationError): ...


class InvalidTokenError(ApplicationError): ...
