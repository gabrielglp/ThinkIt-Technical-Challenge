import pytest

from app.domain.value_objects import Pagination, PaginatedResult


class TestPagination:
    def test_offset_first_page(self):
        p = Pagination(page=1, page_size=20)
        assert p.offset == 0

    def test_offset_second_page(self):
        p = Pagination(page=2, page_size=20)
        assert p.offset == 20

    def test_offset_arbitrary_page(self):
        p = Pagination(page=5, page_size=10)
        assert p.offset == 40

    def test_invalid_page_raises(self):
        with pytest.raises(ValueError, match="page must be >= 1"):
            Pagination(page=0)

    def test_page_size_below_minimum_raises(self):
        with pytest.raises(ValueError, match="page_size must be between 1 and 100"):
            Pagination(page_size=0)

    def test_page_size_above_maximum_raises(self):
        with pytest.raises(ValueError, match="page_size must be between 1 and 100"):
            Pagination(page_size=101)

    def test_frozen(self):
        p = Pagination(page=1, page_size=10)
        with pytest.raises(Exception):
            p.page = 2  # type: ignore[misc]


class TestPaginatedResult:
    def _make(self, total: int, page: int = 1, page_size: int = 10) -> PaginatedResult:
        return PaginatedResult(items=[], total=total, page=page, page_size=page_size)

    def test_total_pages_exact_division(self):
        result = self._make(total=30, page_size=10)
        assert result.total_pages == 3

    def test_total_pages_with_remainder(self):
        result = self._make(total=31, page_size=10)
        assert result.total_pages == 4

    def test_total_pages_zero_items(self):
        result = self._make(total=0)
        assert result.total_pages == 0

    def test_has_next_true(self):
        result = self._make(total=30, page=1, page_size=10)
        assert result.has_next is True

    def test_has_next_false_on_last_page(self):
        result = self._make(total=30, page=3, page_size=10)
        assert result.has_next is False

    def test_has_previous_false_on_first_page(self):
        result = self._make(total=30, page=1)
        assert result.has_previous is False

    def test_has_previous_true(self):
        result = self._make(total=30, page=2)
        assert result.has_previous is True

    def test_single_page_no_navigation(self):
        result = self._make(total=5, page=1, page_size=10)
        assert result.total_pages == 1
        assert result.has_next is False
        assert result.has_previous is False
