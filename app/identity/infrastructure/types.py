from sqlalchemy import Dialect, String, TypeDecorator

from app.identity.domain.value_objects import HashedPassword, Role, RoleEnum, UserName


class HashedPasswordType(TypeDecorator[HashedPassword]):
    impl = String(256)
    cache_ok = True

    def process_bind_param(  # pyright: ignore
        self, value: HashedPassword | None, dialect: Dialect
    ) -> str | None:
        return str(value) if value else None

    def process_result_value(  # pyright: ignore
        self, value: str | None, dialect: Dialect
    ) -> HashedPassword | None:
        return HashedPassword(value) if value else None


class UserNameType(TypeDecorator[UserName]):
    impl = String(64)
    cache_ok = True

    def process_bind_param(  # pyright: ignore
        self, value: UserName | None, dialect: Dialect
    ) -> str | None:
        return str(value) if value else None

    def process_result_value(  # pyright: ignore
        self, value: str | None, dialect: Dialect
    ) -> UserName | None:
        return UserName(value) if value else None


class RoleType(TypeDecorator[Role]):
    impl = String(16)
    cache_ok = True

    def process_bind_param(  # pyright: ignore
        self, value: Role | None, dialect: Dialect
    ) -> str | None:
        return str(value) if value else None

    def process_result_value(  # pyright: ignore
        self, value: str | None, dialect: Dialect
    ) -> Role | None:
        return Role(RoleEnum(value)) if value else None
