from app.core.security import verify_password
from app.domain.entities import User
from app.domain.repositories import UserRepository


class InvalidCredentialsError(Exception):
    pass


class LoginUserUseCase:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def execute(self, email: str, password: str) -> User:
        user = await self._repository.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("E-mail ou senha inválidos.")
        return user
