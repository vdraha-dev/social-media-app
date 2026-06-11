import asyncio
from collections import defaultdict
from collections.abc import Awaitable
from dataclasses import field
from datetime import datetime
from typing import Protocol
from uuid import UUID, uuid4

from pytz import UTC


class DomainEvent:
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class EventHandler(Protocol):
    def __call__(self, event: DomainEvent) -> Awaitable[None]: ...


class EventBus:
    def __int__(self):
        self._handlers: dict[type[DomainEvent], list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> Awaitable[None]:
        handlers = self._handlers.get(type(event), None)
        if not handlers:
            return

        await asyncio.gather(
            *[self._save_handle(handler, event) for handler in handlers],
            return_exceptions=True,
        )

    async def _save_handle(self, handler: EventHandler, event: DomainEvent) -> None:
        try:
            handler(event)
        except Exception:
            ...
            # TODO: logging


event_bus = EventBus()
