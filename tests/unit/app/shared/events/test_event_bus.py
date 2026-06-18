import asyncio
from datetime import datetime
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from pytz import UTC

from app.shared.events.event_bus import DomainEvent, EventBus
from app.shared.utils import uuid_gen


class TestEvent(DomainEvent):
    pass


class OtherEvent(DomainEvent):
    pass


class TestDomainEvent:
    def test_event_id_is_uuid(self):
        event = TestEvent()
        assert isinstance(event.event_id, UUID)

    def test_occured_at_is_datetime_with_utc(self):
        event = TestEvent()
        assert isinstance(event.occured_at, datetime)
        assert event.occured_at.tzinfo == UTC

    def test_unique_ids(self):
        e1 = TestEvent()
        e2 = TestEvent()
        assert e1.event_id != e2.event_id

    def test_occured_at_close_to_now(self):
        before = datetime.now(UTC)
        event = TestEvent()
        after = datetime.now(UTC)
        assert before <= event.occured_at <= after

    def test_event_id_has_no_setter(self):
        event = TestEvent()
        with pytest.raises(AttributeError):
            event.event_id = uuid_gen()

    def test_occured_at_has_no_setter(self):
        event = TestEvent()
        with pytest.raises(AttributeError):
            event.occured_at = datetime.now(UTC)

    def test_cannot_set_arbitrary_attrs(self):
        event = TestEvent()
        with pytest.raises(AttributeError):
            event.foo = "bar"


class TestEventBusSubscribe:
    def test_subscribe_adds_handler(self):
        bus = EventBus()
        handler = AsyncMock()
        bus.subscribe(TestEvent, handler)
        assert handler in bus._handlers[TestEvent]


class TestEventBusPublish:
    async def test_publish_no_handlers(self):
        bus = EventBus()
        await bus.publish(TestEvent())

    async def test_publish_calls_handler(self):
        bus = EventBus()
        handler = AsyncMock()
        bus.subscribe(TestEvent, handler)
        event = TestEvent()
        await bus.publish(event)
        handler.assert_awaited_once_with(event)

    async def test_publish_calls_all_handlers(self):
        bus = EventBus()
        handler1 = AsyncMock()
        handler2 = AsyncMock()
        bus.subscribe(TestEvent, handler1)
        bus.subscribe(TestEvent, handler2)
        event = TestEvent()
        await bus.publish(event)
        handler1.assert_awaited_once_with(event)
        handler2.assert_awaited_once_with(event)

    async def test_publish_swallows_exception(self):
        bus = EventBus()

        async def failing_handler(event):
            raise ValueError("oops")

        good_handler = AsyncMock()
        bus.subscribe(TestEvent, failing_handler)
        bus.subscribe(TestEvent, good_handler)
        await bus.publish(TestEvent())
        good_handler.assert_awaited_once()

    async def test_publish_only_correct_type(self):
        bus = EventBus()
        handler = AsyncMock()
        bus.subscribe(TestEvent, handler)
        await bus.publish(OtherEvent())
        handler.assert_not_awaited()


class TestEventBusConcurrency:
    async def test_handlers_run_concurrently(self):
        bus = EventBus()
        results = []

        async def slow_handler(event):
            await asyncio.sleep(0.05)
            results.append("slow")

        async def fast_handler(event):
            results.append("fast")

        bus.subscribe(TestEvent, slow_handler)
        bus.subscribe(TestEvent, fast_handler)
        await bus.publish(TestEvent())
        assert "fast" in results
        assert "slow" in results
