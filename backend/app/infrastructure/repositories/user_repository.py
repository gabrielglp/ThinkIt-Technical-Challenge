from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import User


class SQLAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_email(self, email: str) -> User | None:
        row = (
            await self._session.execute(
                text("SELECT id, name, email, hashed_password FROM users WHERE email = :email"),
                {"email": email},
            )
        ).mappings().first()

        if not row:
            return None

        return User(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            hashed_password=row["hashed_password"],
        )

    async def create(self, user: User) -> User:
        await self._session.execute(
            text("""
                INSERT INTO users (id, name, email, hashed_password)
                VALUES (:id, :name, :email, :hashed_password)
            """),
            {"id": user.id, "name": user.name, "email": user.email, "hashed_password": user.hashed_password},
        )
        return user

    async def update_password(self, user_id: str, hashed_password: str) -> None:
        await self._session.execute(
            text("UPDATE users SET hashed_password = :hashed_password WHERE id = :id"),
            {"id": user_id, "hashed_password": hashed_password},
        )
