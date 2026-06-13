from unittest.mock import patch

from app.shared.config import Settings


class TestSettingsDefaults:
    def test_default_values(self):
        s = Settings(_env_file=None)
        assert s.DATABASE_URL == ""
        assert s.SYNC_DATABASE_URL == ""
        assert s.DB_POOL_SIZ == 10
        assert s.DB_MAX_OVERFLOW == 20
        assert s.SECRET_KEY == "change-me-in-production"
        assert s.ALGORITHM == "HS256"
        assert s.ACCESS_TOKEN_TTL_HOURS == 24
        assert s.HASH_ALGORITHMS == ["argon2"]
        assert s.DEBUG is False

    def test_ignores_extra_fields(self):
        s = Settings(_extra="ignored")
        assert not hasattr(s, "_extra")


class TestSettingsOverride:
    @patch.dict("os.environ", {"DATABASE_URL": "postgres://test", "DEBUG": "true"})
    def test_override_via_env(self):
        s = Settings()
        assert s.DATABASE_URL == "postgres://test"
        assert s.DEBUG is True

    @patch.dict("os.environ", {"DB_POOL_SIZ": "5", "DB_MAX_OVERFLOW": "10"})
    def test_override_pool_settings(self):
        s = Settings()
        assert s.DB_POOL_SIZ == 5
        assert s.DB_MAX_OVERFLOW == 10


class TestSettingsSingleton:
    def test_settings_importable(self):
        from app.shared.config import settings as singleton

        assert isinstance(singleton, Settings)
