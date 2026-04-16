from app.core.email import build_reset_password_email, send_mail
from app.core.security import create_reset_token
from app.domain.repositories import UserRepository


class UserNotFoundError(Exception):
    pass


class ForgotPasswordUseCase:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def execute(self, email: str) -> None:
        user = await self._repository.get_by_email(email.lower().strip())
        if not user:
            raise UserNotFoundError("E-mail não cadastrado.")

        token = create_reset_token(user.email)
        html = build_reset_password_email(name=user.name, token=token)
        await send_mail(to=user.email, subject="Redefinição de senha — Função extra", html=html)
