from app.identity.infrastructure.models import AccessTokenModel, UserModel
from app.shared.infrastructure.database import Base


class TestUserModel:
    def test_table_name(self):
        assert UserModel.__tablename__ == "users"

    def test_inherits_base(self):
        assert issubclass(UserModel, Base)

    def test_has_all_columns(self):
        cols = ["username", "email", "password_hash", "role", "last_login"]
        for c in cols:
            assert hasattr(UserModel, c)

    def test_has_tokens_relationship(self):
        assert hasattr(UserModel, "tokens")

    def test_email_is_unique(self):
        col = UserModel.__table__.columns["email"]
        assert col.unique


class TestAccessTokenModel:
    def test_table_name(self):
        assert AccessTokenModel.__tablename__ == "access_tokens"

    def test_inherits_base(self):
        assert issubclass(AccessTokenModel, Base)

    def test_has_all_columns(self):
        cols = ["token", "user_id", "expired_at", "blacklisted"]
        for c in cols:
            assert hasattr(AccessTokenModel, c)

    def test_has_user_relationship(self):
        assert hasattr(AccessTokenModel, "user")

    def test_token_is_unique(self):
        col = AccessTokenModel.__table__.columns["token"]
        assert col.unique

    def test_user_id_is_foreign_key(self):
        fks = list(AccessTokenModel.__table__.foreign_keys)
        assert len(fks) == 1
        assert list(fks)[0].column.table.name == "users"
