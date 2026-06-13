from app.identity.infrastructure.models import AccessTokenModel, UserModel
from app.shared.infrastructure.database import Base


class TestUserModel:
    def test_table_name(self):
        assert UserModel.__tablename__ == "users"

    def test_extends_base(self):
        assert issubclass(UserModel, Base)

    def test_has_columns(self):
        assert hasattr(UserModel, "username")
        assert hasattr(UserModel, "email")
        assert hasattr(UserModel, "password_hash")
        assert hasattr(UserModel, "role")
        assert hasattr(UserModel, "last_login")

    def test_has_tokens_relationship(self):
        assert hasattr(UserModel, "tokens")

    def test_email_is_unique(self):
        for col in UserModel.__table__.columns:
            if col.name == "email":
                assert col.unique is True
                break


class TestAccessTokenModel:
    def test_table_name(self):
        assert AccessTokenModel.__tablename__ == "access_tokens"

    def test_extends_base(self):
        assert issubclass(AccessTokenModel, Base)

    def test_has_columns(self):
        assert hasattr(AccessTokenModel, "token")
        assert hasattr(AccessTokenModel, "user_id")
        assert hasattr(AccessTokenModel, "expired_at")
        assert hasattr(AccessTokenModel, "blacklisted")

    def test_has_user_relationship(self):
        assert hasattr(AccessTokenModel, "user")

    def test_token_is_unique(self):
        for col in AccessTokenModel.__table__.columns:
            if col.name == "token":
                assert col.unique is True
                break
