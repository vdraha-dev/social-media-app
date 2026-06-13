import pytest

from app.shared.domain.value_objects import Email, Pagination, Url


class TestEmail:
    @pytest.mark.parametrize(
        "address",
        [
            "user@example.com",
            "a.b@example.co.uk",
            "user+tag@example.org",
            "123@example.io",
            "a@b.cd",
        ],
    )
    def test_valid_email(self, address):
        email = Email(address)
        assert email.value == address

    @pytest.mark.parametrize(
        "address",
        [
            "",
            "not-an-email",
            "@example.com",
            "user@",
            "user@.com",
            "user@example.",
            "user @example.com",
        ],
    )
    def test_invalid_email_raises(self, address):
        with pytest.raises(ValueError, match="Unvalid email"):
            Email(address)

    def test_domain_property(self):
        email = Email("user@example.com")
        assert email.domain == "example.com"

    def test_domain_with_multiple_parts(self):
        email = Email("user@sub.example.co.uk")
        assert email.domain == "sub.example.co.uk"

    def test_str(self):
        email = Email("a@b.com")
        assert str(email) == "a@b.com"

    def test_repr(self):
        email = Email("a@b.com")
        assert repr(email) == "Email(value='a@b.com')"

    def test_immutable(self):
        email = Email("a@b.com")
        with pytest.raises(AttributeError):
            email.value = "other@b.com"

    def test_equality_based_on_value(self):
        e1 = Email("a@b.com")
        e2 = Email("a@b.com")
        assert e1 == e2
        assert hash(e1) == hash(e2)

    def test_inequality(self):
        e1 = Email("a@b.com")
        e2 = Email("c@d.com")
        assert e1 != e2


class TestUrl:
    @pytest.mark.parametrize(
        "url",
        [
            "http://example.com",
            "https://example.com",
            "http://example.com/path?q=1",
            "https://example.com:8080/path",
        ],
    )
    def test_valid_url(self, url):
        u = Url(url)
        assert u.value == url

    @pytest.mark.parametrize(
        "url",
        [
            "",
            "ftp://example.com",
            "://example.com",
            "example.com",
            "www.example.com",
            "HTTP://example.com",
        ],
    )
    def test_invalid_url_raises(self, url):
        with pytest.raises(ValueError, match="Invalid URL"):
            Url(url)

    def test_str(self):
        u = Url("http://example.com")
        assert str(u) == "http://example.com"

    def test_repr(self):
        u = Url("http://example.com")
        assert repr(u) == "Url(value='http://example.com')"

    def test_immutable(self):
        u = Url("http://example.com")
        with pytest.raises(AttributeError):
            u.value = "https://other.com"

    def test_equality_based_on_value(self):
        u1 = Url("http://a.com")
        u2 = Url("http://a.com")
        assert u1 == u2
        assert hash(u1) == hash(u2)


class TestPagination:
    def test_default_values(self):
        p = Pagination()
        assert p.page_number == 1
        assert p.page_size == 20

    def test_valid_custom_values(self):
        p = Pagination(page_number=2, page_size=50)
        assert p.page_number == 2
        assert p.page_size == 50

    @pytest.mark.parametrize("page_number", [0, -1, -100])
    def test_invalid_page_number_raises(self, page_number):
        with pytest.raises(ValueError, match="Invalid page number"):
            Pagination(page_number=page_number)

    @pytest.mark.parametrize("page_size", [0, -1, 101, 200])
    def test_invalid_page_size_raises(self, page_size):
        with pytest.raises(ValueError, match="Invalid page size"):
            Pagination(page_size=page_size)

    def test_min_page_size(self):
        p = Pagination(page_size=1)
        assert p.page_size == 1

    def test_max_page_size(self):
        p = Pagination(page_size=100)
        assert p.page_size == 100

    def test_limit_property(self):
        p = Pagination(page_size=50)
        assert p.limit == 50

    def test_offset_property_raises_attribute_error(self):
        p = Pagination(page_number=3, page_size=10)
        with pytest.raises(AttributeError):
            p.offset

    def test_immutable(self):
        p = Pagination()
        with pytest.raises(AttributeError):
            p.page_number = 5

    def test_frozen(self):
        p = Pagination()
        with pytest.raises(AttributeError):
            p.page_size = 10
