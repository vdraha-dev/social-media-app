from sqlalchemy import Dialect, String, TypeDecorator
from sqlalchemy.dialects.postgresql import JSON

from app.profiles.domain.value_objects import Bio, DisplayedName, SocialLink


class BioType(TypeDecorator[Bio]):
    impl = String(512)
    cache_ok = True

    def process_bind_param(  # pyright: ignore
        self, value: Bio | None, dialect: Dialect
    ) -> str | None:
        return value.value if value else None

    def process_result_value(  # pyright: ignore
        self, value: str | None, dialect: Dialect
    ) -> Bio | None:
        return Bio(value) if value else None


class SocialLinkType(TypeDecorator[SocialLink]):
    impl = JSON
    cache_ok = True

    def process_bind_param(  # pyright: ignore
        self, value: SocialLink | None, dialect: Dialect
    ) -> dict[str, str] | None:
        return value.to_dict() if value else None

    def process_result_value(  # pyright: ignore
        self, value: dict[str, str] | None, dialect: Dialect
    ) -> SocialLink | None:
        return SocialLink.from_dict(value) if value else None


class DisplayedNameType(TypeDecorator[DisplayedName]):
    impl = String(64)
    cache_ok = True

    def process_bind_param(  # pyright: ignore
        self, value: DisplayedName | None, dialect: Dialect
    ) -> str | None:
        return value.value if value else None

    def process_result_value(  # pyright: ignore
        self, value: str | None, dialect: Dialect
    ) -> DisplayedName | None:
        return DisplayedName(value) if value else None
