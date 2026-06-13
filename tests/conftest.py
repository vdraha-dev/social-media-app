from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def session():
    s = AsyncMock()
    s.add = MagicMock()
    return s


@pytest.fixture
def secret_key():
    return "1111111111111111111111111111111111111111111111111111111111111111"
