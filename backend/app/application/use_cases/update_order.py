from app.domain.entities import OrderDetail
from app.domain.repositories import OrderRepository
from app.domain.value_objects import OrderWritePayload


class UpdateOrderUseCase:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

    async def execute(self, order_id: str, payload: OrderWritePayload) -> OrderDetail | None:
        return await self._repository.update_order(order_id, payload)
