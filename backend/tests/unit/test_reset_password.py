import pytest
from unittest.mock import AsyncMock, MagicMock

from app.application.use_cases.reset_password import (
    InvalidTokenError,
    PasswordMismatchError,
    ResetPasswordUseCase,
)
from app.core.security import create_reset_token
from app.domain.entities import User


def _make_user() -> User:
    return User(
        id="user-id-123",
        name="Test User",
        email="user@example.com",
        hashed_password="hashed",
    )


def _make_repo(user: User | None = None) -> AsyncMock:
    repo = AsyncMock()
    repo.get_by_email.return_value = user
    repo.update_password.return_value = None
    return repo


class TestResetPasswordUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        user = _make_user()
        repo = _make_repo(user)
        token = create_reset_token(user.email)

        use_case = ResetPasswordUseCase(repo)
        await use_case.execute(token, "nova_senha", "nova_senha")

        repo.update_password.assert_called_once()
        call_args = repo.update_password.call_args
        assert call_args[0][0] == user.id

    @pytest.mark.asyncio
    async def test_password_mismatch_raises(self):
        user = _make_user()
        repo = _make_repo(user)
        token = create_reset_token(user.email)

        use_case = ResetPasswordUseCase(repo)
        with pytest.raises(PasswordMismatchError):
            await use_case.execute(token, "senha1", "senha2")

        repo.update_password.assert_not_called()

    @pytest.mark.asyncio
    async def test_invalid_token_raises(self):
        repo = _make_repo()
        use_case = ResetPasswordUseCase(repo)

        with pytest.raises(InvalidTokenError):
            await use_case.execute("token-invalido", "senha123", "senha123")

    @pytest.mark.asyncio
    async def test_expired_or_wrong_type_token_raises(self):
        from app.core.security import create_access_token

        access_token = create_access_token("user@example.com")
        repo = _make_repo()
        use_case = ResetPasswordUseCase(repo)

        with pytest.raises(InvalidTokenError):
            await use_case.execute(access_token, "senha123", "senha123")

    @pytest.mark.asyncio
    async def test_user_not_found_raises(self):
        repo = _make_repo(user=None)
        token = create_reset_token("ghost@example.com")

        use_case = ResetPasswordUseCase(repo)
        with pytest.raises(InvalidTokenError):
            await use_case.execute(token, "senha123", "senha123")
