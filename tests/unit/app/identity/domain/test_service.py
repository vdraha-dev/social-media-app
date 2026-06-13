from abc import ABC

from app.identity.domain.service import (
    IAccessTokenRepository,
    IPasswordHasher,
    ITokenService,
    IUserRepository,
)


class TestIUserRepository:
    def test_is_abstract(self):
        assert issubclass(IUserRepository, ABC)

    def test_has_abstract_methods(self):
        methods = [
            "get_user_by_id",
            "get_by_email",
            "save",
            "exists_by_email",
        ]
        for m in methods:
            assert hasattr(IUserRepository, m)


class TestIAccessTokenRepository:
    def test_is_abstract(self):
        assert issubclass(IAccessTokenRepository, ABC)

    def test_has_abstract_methods(self):
        methods = ["get_by_token", "save", "blacklist_all_for_user"]
        for m in methods:
            assert hasattr(IAccessTokenRepository, m)


class TestIPasswordHasher:
    def test_is_abstract(self):
        assert issubclass(IPasswordHasher, ABC)

    def test_has_abstract_methods(self):
        methods = ["hash", "verify"]
        for m in methods:
            assert hasattr(IPasswordHasher, m)


class TestITokenService:
    def test_is_abstract(self):
        assert issubclass(ITokenService, ABC)

    def test_has_abstract_methods(self):
        methods = ["generate", "decode"]
        for m in methods:
            assert hasattr(ITokenService, m)
