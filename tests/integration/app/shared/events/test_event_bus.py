import asyncio
from dataclasses import dataclass
from unittest.mock import MagicMock
from uuid import UUID

import pytest

from app.shared.events.event_bus import DomainEvent, EventBus, event_bus


@dataclass
class UserCreated:
    user_id: UUID | None = None


@dataclass
class OrderPlaced:
    order_id: str = ""


class TestEventBusSubscription:
    def test_subscribe_adds_handler(self, event_bus):
        handler = MagicMock()
        event_bus.subscribe(UserCreated, handler)
        assert handler in event_bus._handlers[UserCreated]

    def test_subscribe_multiple_handlers_same_event(self, event_bus):
        h1 = MagicMock()
        h2 = MagicMock()
        event_bus.subscribe(UserCreated, h1)
        event_bus.subscribe(UserCreated, h2)
        assert len(event_bus._handlers[UserCreated]) == 2

    def test_subscribe_different_events_have_separate_handlers(self, event_bus):
        h1 = MagicMock()
        h2 = MagicMock()
        event_bus.subscribe(UserCreated, h1)
        event_bus.subscribe(OrderPlaced, h2)
        assert h1 in event_bus._handlers[UserCreated]
        assert h2 in event_bus._handlers[OrderPlaced]
        assert len(event_bus._handlers[UserCreated]) == 1


class TestEventBusPublish:
    @pytest.mark.asyncio
    async def test_publish_calls_handler(self, event_bus):
        handler = MagicMock()
        event_bus.subscribe(UserCreated, handler)
        event = UserCreated()
        await event_bus.publish(event)
        handler.assert_called_once_with(event)

    @pytest.mark.asyncio
    async def test_publish_no_handlers_does_nothing(self, event_bus):
        event = UserCreated()
        await event_bus.publish(event)

    @pytest.mark.asyncio
    async def test_publish_calls_all_handlers(self, event_bus):
        results = []

        async def handler1(event):
            results.append("h1")

        async def handler2(event):
            results.append("h2")

        event_bus.subscribe(UserCreated, handler1)
        event_bus.subscribe(UserCreated, handler2)

        await event_bus.publish(UserCreated())
        assert results == ["h1", "h2"]

    @pytest.mark.asyncio
    async def test_publish_only_notifies_subscribed_type(self, event_bus):
        handler = MagicMock()
        event_bus.subscribe(UserCreated, handler)

        await event_bus.publish(OrderPlaced())
        handler.assert_not_called()

    @pytest.mark.asyncio
    async def test_publish_handler_exception_does_not_propagate(self, event_bus):
        handler = MagicMock(side_effect=ValueError("fail"))
        event_bus.subscribe(UserCreated, handler)

        await event_bus.publish(UserCreated())
        handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_one_failing_does_not_block_others(self, event_bus):
        results = []

        async def good_handler(event):
            results.append("ok")

        failing_handler = MagicMock(side_effect=RuntimeError("boom"))
        event_bus.subscribe(UserCreated, good_handler)
        event_bus.subscribe(UserCreated, failing_handler)

        await event_bus.publish(UserCreated())
        assert "ok" in results
        failing_handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_multiple_events(self, event_bus):
        handler = MagicMock()
        event_bus.subscribe(UserCreated, handler)

        await event_bus.publish(UserCreated())
        await event_bus.publish(UserCreated())
        assert handler.call_count == 2

    @pytest.mark.asyncio
    async def test_publish_with_multiple_event_types(self, event_bus):
        user_handler = MagicMock()
        order_handler = MagicMock()

        event_bus.subscribe(UserCreated, user_handler)
        event_bus.subscribe(OrderPlaced, order_handler)

        await event_bus.publish(UserCreated())
        user_handler.assert_called_once()
        order_handler.assert_not_called()

        await event_bus.publish(OrderPlaced())
        order_handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_concurrent_publishes(self, event_bus):
        handler = MagicMock()
        event_bus.subscribe(UserCreated, handler)

        async def publish_many():
            for _ in range(10):
                await event_bus.publish(UserCreated())
                await asyncio.sleep(0)

        await asyncio.gather(publish_many(), publish_many())
        assert handler.call_count == 20


class TestEventBusSingleton:
    def test_event_bus_is_singleton(self):
        from app.shared.events.event_bus import event_bus as eb2

        assert event_bus is eb2

    def test_singleton_is_event_bus_instance(self):
        assert isinstance(event_bus, EventBus)

    def test_singleton_handlers_are_shared(self):
        from app.shared.events.event_bus import event_bus as eb2

        handler = MagicMock()
        event_bus.subscribe(UserCreated, handler)
        assert handler in eb2._handlers[UserCreated]


class TestDomainEvent:
    def test_domain_event_can_be_instantiated(self):
        e = DomainEvent()
        assert isinstance(e, DomainEvent)

    def test_event_id_is_uuid_field(self):
        e = DomainEvent()
        from dataclasses import Field

        assert isinstance(e.event_id, Field)

    def test_occurred_at_is_datetime_field(self):
        e = DomainEvent()
        from dataclasses import Field

        assert isinstance(e.occurred_at, Field)
