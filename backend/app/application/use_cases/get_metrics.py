from app.domain.entities import Metrics
from app.domain.repositories import MetricsRepository


class GetMetricsUseCase:
    def __init__(self, repository: MetricsRepository) -> None:
        self._repository = repository

    async def execute(self) -> Metrics:
        return await self._repository.get_metrics()
