from unittest.mock import AsyncMock, MagicMock

import pytest

from app.shared.events.event_bus import DomainEvent, EventBus, event_bus


class TestDomainEvent:
    def test_event_id_is_field_descriptor_not_uuid(self):
        from dataclasses import Field

        e = DomainEvent()
        assert isinstance(e.event_id, Field)

    def test_occurred_at_is_field_descriptor(self):
        from dataclasses import Field

        e = DomainEvent()
        assert isinstance(e.occurred_at, Field)

    def test_can_create_instance(self):
        e = DomainEvent()
        assert isinstance(e, DomainEvent)

    def test_two_instances_have_same_field_descriptors(self):
        e1 = DomainEvent()
        e2 = DomainEvent()
        assert e1.event_id is e2.event_id


class TestEventBus:
    def test_subscribe_adds_handler(self):
        bus = EventBus()
        handler = AsyncMock()
        bus.subscribe(DomainEvent, handler)
        assert handler in bus._handlers[DomainEvent]

    def test_subscribe_multiple_handlers(self):
        bus = EventBus()
        h1 = AsyncMock()
        h2 = AsyncMock()
        bus.subscribe(DomainEvent, h1)
        bus.subscribe(DomainEvent, h2)
        assert len(bus._handlers[DomainEvent]) == 2

    @pytest.mark.asyncio
    async def test_publish_calls_handler(self):
        bus = EventBus()
        handler = MagicMock()
        bus.subscribe(DomainEvent, handler)
        event = DomainEvent()
        await bus.publish(event)
        handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_no_handlers_does_nothing(self):
        bus = EventBus()
        event = DomainEvent()
        await bus.publish(event)

    @pytest.mark.asyncio
    async def test_publish_multiple_handlers(self):
        bus = EventBus()
        h1 = MagicMock()
        h2 = MagicMock()
        bus.subscribe(DomainEvent, h1)
        bus.subscribe(DomainEvent, h2)
        event = DomainEvent()
        await bus.publish(event)
        h1.assert_called_once()
        h2.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_only_calls_subscribed_type(self):
        bus = EventBus()

        class EventA(DomainEvent):
            pass

        class EventB(DomainEvent):
            pass

        handler_a = MagicMock()
        handler_b = MagicMock()
        bus.subscribe(EventA, handler_a)
        bus.subscribe(EventB, handler_b)

        await bus.publish(EventA())
        handler_a.assert_called_once()
        handler_b.assert_not_called()

    @pytest.mark.asyncio
    async def test_publish_with_return_exceptions_does_not_raise(self):
        bus = EventBus()

        class EventA(DomainEvent):
            pass

        handler = MagicMock(side_effect=ValueError("fail"))
        bus.subscribe(EventA, handler)

        await bus.publish(EventA())
        handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_handle_silently_catches_exception(self):
        bus = EventBus()

        class EventA(DomainEvent):
            pass

        failing_handler = MagicMock(side_effect=RuntimeError("boom"))
        event = EventA()
        await bus._save_handle(failing_handler, event)
        failing_handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_handle_calls_handler(self):
        bus = EventBus()

        class EventA(DomainEvent):
            pass

        handler = MagicMock()
        event = EventA()
        await bus._save_handle(handler, event)
        handler.assert_called_once_with(event)

    def test_singleton_event_bus(self):
        assert isinstance(event_bus, EventBus)

    def test_singleton_is_same_instance(self):
        from app.shared.events.event_bus import event_bus as eb2

        assert event_bus is eb2
