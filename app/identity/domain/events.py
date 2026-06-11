from dataclasses import dataclass
from uuid import UUID

from app.shared.events.event_bus import DomainEvent


@dataclass(frozen=True, slots=True)
class UserRegistered(DomainEvent):
    user_id: UUID
    username: str
    email: str


@dataclass(frozen=True, slots=True)
class UserLogedIn(DomainEvent):
    user_id: UUID


@dataclass(frozen=True, slots=True)
class UserLoggedOut(DomainEvent):
    user_id: UUID
