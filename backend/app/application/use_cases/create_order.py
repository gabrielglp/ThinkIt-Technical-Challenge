from app.domain.entities import OrderDetail
from app.domain.repositories import OrderRepository
from app.domain.value_objects import OrderWritePayload


class CreateOrderUseCase:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

    async def execute(self, payload: OrderWritePayload) -> OrderDetail:
        return await self._repository.create_order(payload)
