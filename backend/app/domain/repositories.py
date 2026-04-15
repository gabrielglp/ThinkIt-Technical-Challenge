from typing import Protocol, runtime_checkable

from app.domain.entities import Metrics, Order, OrderDetail
from app.domain.value_objects import OrderFilters, Pagination, PaginatedResult


@runtime_checkable
class OrderRepository(Protocol):
    async def list_orders(
        self,
        filters: OrderFilters,
        pagination: Pagination,
    ) -> PaginatedResult[Order]: ...

    async def get_by_id(self, order_id: str) -> OrderDetail | None: ...


@runtime_checkable
class MetricsRepository(Protocol):
    async def get_metrics(self) -> Metrics: ...
