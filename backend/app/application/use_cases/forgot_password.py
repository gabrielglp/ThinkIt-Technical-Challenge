import random
import string

from app.core.email import build_forgot_password_email, send_mail
from app.core.security import hash_password
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

        new_password = _generate_password()
        await self._repository.update_password(user.id, hash_password(new_password))

        html = build_forgot_password_email(name=user.name, new_password=new_password)
        await send_mail(to=user.email, subject="Nova senha — Função extra", html=html)


def _generate_password(length: int = 12) -> str:
    chars = string.ascii_letters + string.digits + "!@#$%&*"
    mandatory = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice("!@#$%&*"),
    ]
    rest = [random.choice(chars) for _ in range(length - len(mandatory))]
    pool = mandatory + rest
    random.shuffle(pool)
    return "".join(pool)
