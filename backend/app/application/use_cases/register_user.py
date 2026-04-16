import uuid

from app.core.security import hash_password
from app.domain.entities import User
from app.domain.repositories import UserRepository


class EmailAlreadyExistsError(Exception):
    pass


class RegisterUserUseCase:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def execute(self, name: str, email: str, password: str) -> User:
        existing = await self._repository.get_by_email(email)
        if existing:
            raise EmailAlreadyExistsError(f"E-mail '{email}' já cadastrado.")

        user = User(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            hashed_password=hash_password(password),
        )
        return await self._repository.create(user)
