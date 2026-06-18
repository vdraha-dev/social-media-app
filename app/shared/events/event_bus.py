import asyncio
from collections import defaultdict
from collections.abc import Awaitable
from datetime import datetime
from typing import Protocol
from uuid import UUID

from pytz import UTC

from app.shared.utils import uuid_gen


class DomainEvent:
    __slots__ = ("_event_id", "_occured_at")

    def __init__(self):
        self._event_id: UUID = uuid_gen()
        self._occured_at: datetime = datetime.now(tz=UTC)

    @property
    def event_id(self) -> UUID:
        return self._event_id

    @property
    def occured_at(self) -> datetime:
        return self._occured_at


class EventHandler(Protocol):
    def __call__(self, event: DomainEvent) -> Awaitable[None]: ...


class EventBus:
    def __init__(self):
        self._handlers: dict[type[DomainEvent], list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent):
        handlers = self._handlers.get(type(event), None)
        if not handlers:
            return

        await asyncio.gather(
            *[self._save_handle(handler, event) for handler in handlers],
            return_exceptions=True,
        )

    async def _save_handle(self, handler: EventHandler, event: DomainEvent) -> None:
        try:
            await handler(event)
        except Exception:
            ...
            # TODO: logging


event_bus = EventBus()
