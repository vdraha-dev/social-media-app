from dataclasses import FrozenInstanceError

import pytest

from app.shared.domain.value_objects import Email, Pagination, Url


class TestEmail:
    def test_valid_email(self):
        email = Email("user@example.com")
        assert email.value == "user@example.com"

    def test_valid_email_with_plus(self):
        email = Email("user+tag@example.com")
        assert email.value == "user+tag@example.com"

    def test_valid_email_with_subdomain(self):
        email = Email("user@sub.example.com")
        assert email.value == "user@sub.example.com"

    def test_invalid_email_no_at(self):
        with pytest.raises(ValueError, match="Unvalid email"):
            Email("userexample.com")

    def test_invalid_email_no_domain(self):
        with pytest.raises(ValueError):
            Email("user@.com")

    def test_invalid_email_empty(self):
        with pytest.raises(ValueError):
            Email("")

    def test_invalid_email_spaces(self):
        with pytest.raises(ValueError):
            Email("user @example.com")

    def test_str_representation(self):
        email = Email("test@example.com")
        assert str(email) == "test@example.com"

    def test_repr_representation(self):
        email = Email("test@example.com")
        assert repr(email) == "Email(value='test@example.com')"

    def test_domain_property(self):
        email = Email("user@example.com")
        assert email.domain == "example.com"

    def test_domain_with_subdomain(self):
        email = Email("user@mail.example.co.uk")
        assert email.domain == "mail.example.co.uk"

    def test_equality_same_value(self):
        e1 = Email("a@b.com")
        e2 = Email("a@b.com")
        assert e1 == e2
        assert hash(e1) == hash(e2)

    def test_inequality_different_value(self):
        e1 = Email("a@b.com")
        e2 = Email("c@d.com")
        assert e1 != e2

    def test_frozen_dataclass(self):
        email = Email("a@b.com")
        with pytest.raises(FrozenInstanceError):
            email.value = "other@b.com"

    def test_email_strips_whitespace(self):
        with pytest.raises(ValueError):
            Email("  a@b.com  ")


class TestUrl:
    def test_valid_http_url(self):
        url = Url("http://example.com")
        assert url.value == "http://example.com"

    def test_valid_https_url(self):
        url = Url("https://example.com")
        assert url.value == "https://example.com"

    def test_invalid_url_no_scheme(self):
        with pytest.raises(ValueError, match="Invalid URL"):
            Url("example.com")

    def test_invalid_url_ftp_scheme(self):
        with pytest.raises(ValueError):
            Url("ftp://example.com")

    def test_str_representation(self):
        url = Url("https://example.com")
        assert str(url) == "https://example.com"

    def test_repr_representation(self):
        url = Url("https://example.com")
        assert repr(url) == "Url(value='https://example.com')"

    def test_url_with_path(self):
        url = Url("https://example.com/path/to/resource?q=1")
        assert url.value == "https://example.com/path/to/resource?q=1"

    def test_url_frozen(self):
        url = Url("https://example.com")
        with pytest.raises(FrozenInstanceError):
            url.value = "changed"

    def test_equality(self):
        u1 = Url("https://example.com")
        u2 = Url("https://example.com")
        assert u1 == u2
        assert hash(u1) == hash(u2)


class TestPagination:
    def test_default_values(self):
        p = Pagination()
        assert p.page_number == 1
        assert p.page_size == 20

    def test_custom_values(self):
        p = Pagination(page_number=3, page_size=50)
        assert p.page_number == 3
        assert p.page_size == 50

    def test_invalid_page_number_zero(self):
        with pytest.raises(ValueError, match="Invalid page number"):
            Pagination(page_number=0)

    def test_invalid_page_number_negative(self):
        with pytest.raises(ValueError):
            Pagination(page_number=-1)

    def test_invalid_page_size_zero(self):
        with pytest.raises(ValueError):
            Pagination(page_size=0)

    def test_invalid_page_size_too_large(self):
        with pytest.raises(ValueError, match="Invalid page size"):
            Pagination(page_size=101)

    def test_offset_property_first_page(self):
        p = Pagination(page_number=1, page_size=20)
        assert p.offset == 0

    def test_offset_property_second_page(self):
        p = Pagination(page_number=2, page_size=20)
        assert p.offset == 20

    def test_offset_property_custom(self):
        p = Pagination(page_number=5, page_size=10)
        assert p.offset == 40

    def test_limit_property(self):
        p = Pagination(page_size=50)
        assert p.limit == 50

    def test_frozen_dataclass(self):
        p = Pagination(page_number=1, page_size=20)
        with pytest.raises(FrozenInstanceError):
            p.page_number = 2

    def test_boundary_page_size_min(self):
        p = Pagination(page_size=1)
        assert p.page_size == 1

    def test_boundary_page_size_max(self):
        p = Pagination(page_size=100)
        assert p.page_size == 100

    def test_equality(self):
        p1 = Pagination(1, 20)
        p2 = Pagination(1, 20)
        assert p1 == p2
