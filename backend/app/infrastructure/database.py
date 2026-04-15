"""
Gerenciamento da conexão assíncrona com o PostgreSQL.
O engine e a session factory são criados uma única vez (singleton via módulo Python).
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=False,           # True apenas em debug local — nunca em prod
    pool_size=5,          # conexões permanentes no pool
    max_overflow=10,      # conexões extras em pico
    pool_pre_ping=True,   # valida conexão antes de usar (evita broken pipe)
    pool_recycle=3600,    # recicla conexões a cada 1h
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # evita lazy load após commit (essencial com async)
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency do FastAPI — injeta uma sessão assíncrona por request.
    Faz rollback automático em caso de exceção e fecha a sessão sempre.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
