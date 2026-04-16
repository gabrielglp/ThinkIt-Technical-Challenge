from app.core.security import hash_password, verify_password
from app.domain.entities import User
from app.domain.repositories import UserRepository

# Pre-computed dummy hash used when the e-mail is not found.
# Running verify_password against it ensures the response time is
# identical whether the user exists or not, preventing timing-based
# user enumeration attacks.
_DUMMY_HASH: str = hash_password("dummy-timing-guard")


class InvalidCredentialsError(Exception):
    pass


class LoginUserUseCase:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def execute(self, email: str, password: str) -> User:
        user = await self._repository.get_by_email(email)
        candidate_hash = user.hashed_password if user else _DUMMY_HASH
        if not user or not verify_password(password, candidate_hash):
            raise InvalidCredentialsError("E-mail ou senha inválidos.")
        return user
