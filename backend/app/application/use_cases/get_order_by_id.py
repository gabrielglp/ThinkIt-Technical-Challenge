from app.domain.entities import OrderDetail
from app.domain.repositories import OrderRepository


class GetOrderByIdUseCase:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

    async def execute(self, order_id: str) -> OrderDetail | None:
        return await self._repository.get_by_id(order_id)
