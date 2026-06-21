from sqlalchemy import Dialect, String, TypeDecorator

from app.shared.domain.value_objects import Email, Url


class EmailType(TypeDecorator[Email]):
    impl = String(256)
    cache_ok = True

    def process_bind_param(  # pyright: ignore
        self,
        value: Email | None,
        dialect: Dialect,
    ) -> str | None:
        return str(value) if value else None

    def process_result_value(  # pyright: ignore
        self,
        value: str | None,
        dialect: Dialect,
    ) -> Email | None:
        return Email(value) if value else None


class UrlType(TypeDecorator[Url]):
    impl = String(512)
    cache_ok = True

    def process_bind_param(  # pyright: ignore
        self,
        value: Url | None,
        dialect: Dialect,
    ) -> str | None:
        return str(value) if value else None

    def process_result_value(  # pyright: ignore
        self,
        value: str | None,
        dialect: Dialect,
    ) -> Url | None:
        return Url(value) if value else None
