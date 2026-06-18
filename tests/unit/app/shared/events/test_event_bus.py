import asyncio
from datetime import datetime
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from pytz import UTC

from app.shared.events.event_bus import DomainEvent, EventBus
from app.shared.utils import uuid_gen


class MyTestEvent(DomainEvent):
    __slots__ = ()


class OtherEvent(DomainEvent):
    __slots__ = ()


class TestDomainEvent:
    def test_event_id_is_uuid(self):
        event = MyTestEvent()
        assert isinstance(event.event_id, UUID)

    def test_occured_at_is_datetime_with_utc(self):
        event = MyTestEvent()
        assert isinstance(event.occured_at, datetime)
        assert event.occured_at.tzinfo == UTC

    def test_unique_ids(self):
        e1 = MyTestEvent()
        e2 = MyTestEvent()
        assert e1.event_id != e2.event_id

    def test_occured_at_close_to_now(self):
        before = datetime.now(UTC)
        event = MyTestEvent()
        after = datetime.now(UTC)
        assert before <= event.occured_at <= after

    def test_event_id_has_no_setter(self):
        event = MyTestEvent()
        with pytest.raises(AttributeError):
            event.event_id = uuid_gen()  # pyright: ignore

    def test_occured_at_has_no_setter(self):
        event = MyTestEvent()
        with pytest.raises(AttributeError):
            event.occured_at = datetime.now(UTC)  # pyright: ignore

    def test_cannot_set_arbitrary_attrs(self):
        event = MyTestEvent()
        with pytest.raises(AttributeError):
            event.foo = "bar"  # pyright: ignore


class TestEventBusSubscribe:
    def test_subscribe_adds_handler(self):
        bus = EventBus()
        handler = AsyncMock()
        bus.subscribe(MyTestEvent, handler)
        assert handler in bus._handlers[MyTestEvent]  # pyright: ignore


class TestEventBusPublish:
    async def test_publish_no_handlers(self):
        bus = EventBus()
        await bus.publish(MyTestEvent())

    async def test_publish_calls_handler(self):
        bus = EventBus()
        handler = AsyncMock()
        bus.subscribe(MyTestEvent, handler)
        event = MyTestEvent()
        await bus.publish(event)
        handler.assert_awaited_once_with(event)

    async def test_publish_calls_all_handlers(self):
        bus = EventBus()
        handler1 = AsyncMock()
        handler2 = AsyncMock()
        bus.subscribe(MyTestEvent, handler1)
        bus.subscribe(MyTestEvent, handler2)
        event = MyTestEvent()
        await bus.publish(event)
        handler1.assert_awaited_once_with(event)
        handler2.assert_awaited_once_with(event)

    async def test_publish_swallows_exception(self):
        bus = EventBus()

        async def failing_handler(event: DomainEvent):
            raise ValueError("oops")

        good_handler = AsyncMock()
        bus.subscribe(MyTestEvent, failing_handler)
        bus.subscribe(MyTestEvent, good_handler)
        await bus.publish(MyTestEvent())
        good_handler.assert_awaited_once()

    async def test_publish_only_correct_type(self):
        bus = EventBus()
        handler = AsyncMock()
        bus.subscribe(MyTestEvent, handler)
        await bus.publish(OtherEvent())
        handler.assert_not_awaited()


class TestEventBusConcurrency:
    async def test_handlers_run_concurrently(self):
        bus = EventBus()
        results: list[str] = []

        async def slow_handler(event: DomainEvent):
            await asyncio.sleep(0.05)
            results.append("slow")

        async def fast_handler(event: DomainEvent):
            results.append("fast")

        bus.subscribe(MyTestEvent, slow_handler)
        bus.subscribe(MyTestEvent, fast_handler)
        await bus.publish(MyTestEvent())
        assert "fast" in results
        assert "slow" in results
