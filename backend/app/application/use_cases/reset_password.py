from jose import JWTError

from app.core.security import decode_reset_token, hash_password
from app.domain.repositories import UserRepository


class InvalidTokenError(Exception):
    pass


class PasswordMismatchError(Exception):
    pass


class ResetPasswordUseCase:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def execute(self, token: str, password: str, confirm_password: str) -> None:
        if password != confirm_password:
            raise PasswordMismatchError("As senhas não coincidem.")

        try:
            email = decode_reset_token(token)
        except JWTError:
            raise InvalidTokenError("Link de redefinição inválido ou expirado.")

        user = await self._repository.get_by_email(email)
        if not user:
            raise InvalidTokenError("Link de redefinição inválido ou expirado.")

        hashed = hash_password(password)
        await self._repository.update_password(user.id, hashed)
