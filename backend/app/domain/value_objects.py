from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Generic, TypeVar

T = TypeVar("T")


class OrderStatus(str, Enum):
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class OrderFilters:
    """Value object que encapsula todos os critérios de busca de pedidos."""

    status: OrderStatus | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    min_value: Decimal | None = None
    max_value: Decimal | None = None
    customer_name: str | None = None


@dataclass(frozen=True)
class Pagination:
    """Value object de controle de paginação."""

    page: int = 1
    page_size: int = 20

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError("page must be >= 1")
        if not (1 <= self.page_size <= 100):
            raise ValueError("page_size must be between 1 and 100")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


@dataclass(frozen=True)
class PaginatedResult(Generic[T]):
    """Value object genérico de resultado paginado."""

    items: list[T]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        if self.page_size == 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        return self.page > 1
