from typing import Protocol, runtime_checkable

from app.domain.entities import Metrics, Order, OrderDetail, User
from app.domain.value_objects import OrderFilters, Pagination, PaginatedResult


@runtime_checkable
class OrderRepository(Protocol):
    async def list_orders(
        self,
        filters: OrderFilters,
        pagination: Pagination,
    ) -> PaginatedResult[Order]: ...

    async def get_by_id(self, order_id: str) -> OrderDetail | None: ...

    async def create_order(self, payload: "OrderWritePayload") -> OrderDetail: ...

    async def update_order(self, order_id: str, payload: "OrderWritePayload") -> OrderDetail | None: ...


@runtime_checkable
class UserRepository(Protocol):
    async def get_by_email(self, email: str) -> User | None: ...
    async def create(self, user: User) -> User: ...
    async def update_password(self, user_id: str, hashed_password: str) -> None: ...


@runtime_checkable
class MetricsRepository(Protocol):
    async def get_metrics(self) -> Metrics: ...
