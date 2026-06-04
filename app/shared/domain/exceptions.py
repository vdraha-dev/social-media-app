class DomainError(Exception): ...


class NotFoundError(DomainError):
    """
    Raised when an entity is not found.
    """

    def __init__(self, entity: str, identifier: object):
        super.__init__(f"{entity} not found with identifier {identifier}")
        self.entity = entity
        self.identifier = identifier


class AlreadyExistsError(DomainError):
    """
    Raised when an entity already exists.
    """

    def __init__(self, entity: str, field: str, value: object):
        super.__init__(f"{entity} with {field}={value!r} already exists")
        self.entity = entity
        self.field = field
        self.value = value


class PermissionDeniedError(DomainError):
    """
    Raised when a user does not have the necessary permissions to perform an action.
    """

    def __init__(self, action: str, reason: str = ""):
        msg = f"Acess denied for {action}"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)
        self.action = action


class ValidationError(DomainError):
    """
    Raised when a validation error occurs.
    """

    ...


class ConflictError(DomainError):
    """
    Raised when a state conflict occurs.
    """

    ...
