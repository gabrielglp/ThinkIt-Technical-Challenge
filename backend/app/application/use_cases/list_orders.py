from app.domain.entities import Order
from app.domain.repositories import OrderRepository
from app.domain.value_objects import OrderFilters, Pagination, PaginatedResult


class ListOrdersUseCase:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

    async def execute(self, filters: OrderFilters, pagination: Pagination) -> PaginatedResult[Order]:
        return await self._repository.list_orders(filters, pagination)
