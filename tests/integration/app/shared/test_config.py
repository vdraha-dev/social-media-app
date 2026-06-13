from app.shared.config import Settings, settings


class TestSettingsFromEnv:
    def test_loads_from_env_file(self):
        assert isinstance(settings.DATABASE_URL, str)

    def test_defaults_are_reasonable(self):
        s = Settings()
        assert s.DB_POOL_SIZ == 10
        assert s.DB_MAX_OVERFLOW == 20
        assert s.ACCESS_TOKEN_TTL_HOURS == 24
        assert s.ALGORITHM == "HS256"
        assert s.HASH_ALGORITHMS == ["argon2"]
        assert s.DEBUG is False

    def test_overrides_from_env(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
        monkeypatch.setenv("DEBUG", "true")
        monkeypatch.setenv("SECRET_KEY", "super-secret")

        s = Settings()
        assert s.DATABASE_URL == "sqlite:///test.db"
        assert s.DEBUG is True
        assert s.SECRET_KEY == "super-secret"

    def test_pool_size_from_env(self, monkeypatch):
        monkeypatch.setenv("DB_POOL_SIZ", "25")
        s = Settings()
        assert s.DB_POOL_SIZ == 25

    def test_extra_env_vars_are_ignored(self, monkeypatch):
        monkeypatch.setenv("UNRELATED_VAR", "whatever")
        s = Settings()
        assert not hasattr(s, "UNRELATED_VAR")

    def test_algorithm_from_env(self, monkeypatch):
        monkeypatch.setenv("ALGORITHM", "RS256")
        s = Settings()
        assert s.ALGORITHM == "RS256"

    def test_hash_algorithms_from_env_json(self, monkeypatch):
        monkeypatch.setenv("HASH_ALGORITHMS", '["bcrypt","argon2"]')
        s = Settings()
        assert s.HASH_ALGORITHMS == ["bcrypt", "argon2"]

    def test_access_token_ttl_from_env(self, monkeypatch):
        monkeypatch.setenv("ACCESS_TOKEN_TTL_HOURS", "48")
        s = Settings()
        assert s.ACCESS_TOKEN_TTL_HOURS == 48

    def test_global_settings_is_singleton(self):
        from app.shared.config import settings as s2

        assert settings is s2


class TestSettingsIntegration:
    def test_config_round_trip(self, monkeypatch):
        env_vals = {
            "DATABASE_URL": "postgresql://u:p@localhost/db",
            "SYNC_DATABASE_URL": "postgresql://u:p@localhost/db",
            "SECRET_KEY": "test-key-12345",
            "DEBUG": "false",
        }
        for k, v in env_vals.items():
            monkeypatch.setenv(k, v)

        s = Settings()
        assert str(s.SYNC_DATABASE_URL) == "postgresql://u:p@localhost/db"
        assert str(s.DATABASE_URL) == "postgresql://u:p@localhost/db"
        assert s.SECRET_KEY == "test-key-12345"
        assert s.DEBUG is False
