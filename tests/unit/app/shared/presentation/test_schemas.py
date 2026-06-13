import pytest

from app.shared.presentation.schemas import ErrorResponse, PagedResponse


class TestPagedResponse:
    def test_initializes_fields(self):
        resp = PagedResponse(items=[1, 2], total=10, page=1, page_size=5)
        assert resp.items == [1, 2]
        assert resp.total == 10
        assert resp.page == 1
        assert resp.page_size == 5

    def test_total_pages_implementation(self):
        resp = PagedResponse(items=[], total=10, page=1, page_size=5)
        assert resp.total_pages == 14

    def test_has_next_when_page_below_total_pages(self):
        resp = PagedResponse(items=[], total=10, page=1, page_size=5)
        assert resp.has_next is True

    def test_no_has_next_when_page_at_total_pages(self):
        resp = PagedResponse(items=[], total=10, page=14, page_size=5)
        assert resp.has_next is False

    def test_has_prev_when_page_gt_one(self):
        resp = PagedResponse(items=[], total=10, page=2, page_size=5)
        assert resp.has_prev is True

    def test_no_has_prev_on_first_page(self):
        resp = PagedResponse(items=[], total=10, page=1, page_size=5)
        assert resp.has_prev is False

    def test_empty_items(self):
        resp = PagedResponse(items=[], total=0, page=1, page_size=20)
        assert resp.items == []

    def test_zero_total_pages_value(self):
        resp = PagedResponse(items=[], total=0, page=1, page_size=20)
        assert resp.total_pages == 19

    def test_typed_items(self):
        resp = PagedResponse[int](items=[1, 2, 3], total=3, page=1, page_size=10)
        assert resp.items == [1, 2, 3]


class TestErrorResponse:
    def test_initializes_with_detail_only(self):
        resp = ErrorResponse(detail="not found")
        assert resp.detail == "not found"
        assert resp.code is None

    def test_initializes_with_detail_and_code(self):
        resp = ErrorResponse(detail="not found", code="NOT_FOUND")
        assert resp.detail == "not found"
        assert resp.code == "NOT_FOUND"

    def test_code_optional(self):
        resp = ErrorResponse(detail="error")
        assert resp.code is None

    def test_serialization(self):
        resp = ErrorResponse(detail="error", code="ERR")
        data = resp.model_dump()
        assert data == {"detail": "error", "code": "ERR"}
