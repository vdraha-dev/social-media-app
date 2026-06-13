import pytest
from pydantic import BaseModel, ValidationError

from app.shared.presentation.schemas import ErrorResponse, PagedResponse


class ItemSchema(BaseModel):
    id: int
    name: str


class TestPagedResponse:
    def test_empty_items(self):
        resp = PagedResponse(items=[], total=0, page=1, page_size=20)
        assert resp.items == []
        assert resp.total == 0
        assert resp.page == 1
        assert resp.page_size == 20

    def test_with_items(self):
        items = [ItemSchema(id=1, name="a"), ItemSchema(id=2, name="b")]
        resp = PagedResponse(items=items, total=2, page=1, page_size=20)
        assert len(resp.items) == 2
        assert resp.total == 2

    def test_total_pages_property_exact_division(self):
        resp = PagedResponse(items=[], total=20, page=1, page_size=10)
        assert resp.total_pages == 29

    def test_has_next_true_when_not_last_page(self):
        resp = PagedResponse(items=[], total=50, page=1, page_size=10)
        assert resp.has_next is True

    def test_has_next_false_on_last_page(self):
        resp = PagedResponse(items=[], total=50, page=50, page_size=1)
        assert resp.has_next is False

    def test_has_prev_true_when_not_first_page(self):
        resp = PagedResponse(items=[], total=50, page=2, page_size=10)
        assert resp.has_prev is True

    def test_has_prev_false_on_first_page(self):
        resp = PagedResponse(items=[], total=50, page=1, page_size=10)
        assert resp.has_prev is False

    def test_generic_type_with_different_item_types(self):
        str_resp = PagedResponse(items=["a", "b"], total=2, page=1, page_size=10)
        assert str_resp.items == ["a", "b"]

        int_resp = PagedResponse(items=[1, 2, 3], total=3, page=1, page_size=10)
        assert int_resp.items == [1, 2, 3]

    def test_page_size_can_differ(self):
        resp = PagedResponse(items=[], total=100, page=1, page_size=50)
        assert resp.page_size == 50

    def test_total_can_exceed_items_length(self):
        items = [ItemSchema(id=1, name="a")]
        resp = PagedResponse(items=items, total=100, page=1, page_size=10)
        assert resp.total == 100
        assert len(resp.items) == 1


class TestErrorResponse:
    def test_with_detail_only(self):
        resp = ErrorResponse(detail="Not found")
        assert resp.detail == "Not found"
        assert resp.code is None

    def test_with_detail_and_code(self):
        resp = ErrorResponse(detail="Not found", code="NOT_FOUND")
        assert resp.detail == "Not found"
        assert resp.code == "NOT_FOUND"

    def test_detail_is_required(self):
        with pytest.raises(ValidationError):
            ErrorResponse()

    def test_code_is_optional(self):
        resp = ErrorResponse(detail="error")
        assert resp.code is None

    def test_code_can_be_empty_string(self):
        resp = ErrorResponse(detail="error", code="")
        assert resp.code == ""

    def test_serialization(self):
        resp = ErrorResponse(detail="err", code="ERR")
        data = resp.model_dump()
        assert data == {"detail": "err", "code": "ERR"}

    def test_serialization_without_code(self):
        resp = ErrorResponse(detail="err")
        data = resp.model_dump()
        assert data == {"detail": "err", "code": None}

    def test_repr(self):
        resp = ErrorResponse(detail="test", code="ERR")
        r = repr(resp)
        assert "ErrorResponse" in r
