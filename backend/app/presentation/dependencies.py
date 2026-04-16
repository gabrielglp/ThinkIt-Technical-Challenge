from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.create_order import CreateOrderUseCase
from app.application.use_cases.forgot_password import ForgotPasswordUseCase
from app.application.use_cases.import_orders_csv import ImportOrdersCsvUseCase
from app.application.use_cases.reset_password import ResetPasswordUseCase
from app.application.use_cases.get_metrics import GetMetricsUseCase
from app.application.use_cases.get_order_by_id import GetOrderByIdUseCase
from app.application.use_cases.list_orders import ListOrdersUseCase
from app.application.use_cases.login_user import LoginUserUseCase
from app.application.use_cases.register_user import RegisterUserUseCase
from app.application.use_cases.update_order import UpdateOrderUseCase
from app.core.security import decode_access_token
from app.domain.entities import User
from app.infrastructure.database import get_db_session
from app.infrastructure.repositories import SQLAlchemyMetricsRepository, SQLAlchemyOrderRepository, SQLAlchemyUserRepository

_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(_bearer),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    try:
        email = decode_access_token(credentials.credentials)
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado.")
    user = await SQLAlchemyUserRepository(session).get_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado.")
    return user


def get_list_orders_use_case(
    session: AsyncSession = Depends(get_db_session),
) -> ListOrdersUseCase:
    return ListOrdersUseCase(SQLAlchemyOrderRepository(session))


def get_order_by_id_use_case(
    session: AsyncSession = Depends(get_db_session),
) -> GetOrderByIdUseCase:
    return GetOrderByIdUseCase(SQLAlchemyOrderRepository(session))


def get_metrics_use_case(
    session: AsyncSession = Depends(get_db_session),
) -> GetMetricsUseCase:
    return GetMetricsUseCase(SQLAlchemyMetricsRepository(session))


def get_create_order_use_case(
    session: AsyncSession = Depends(get_db_session),
) -> CreateOrderUseCase:
    return CreateOrderUseCase(SQLAlchemyOrderRepository(session))


def get_update_order_use_case(
    session: AsyncSession = Depends(get_db_session),
) -> UpdateOrderUseCase:
    return UpdateOrderUseCase(SQLAlchemyOrderRepository(session))


def get_register_use_case(
    session: AsyncSession = Depends(get_db_session),
) -> RegisterUserUseCase:
    return RegisterUserUseCase(SQLAlchemyUserRepository(session))


def get_login_use_case(
    session: AsyncSession = Depends(get_db_session),
) -> LoginUserUseCase:
    return LoginUserUseCase(SQLAlchemyUserRepository(session))


def get_forgot_password_use_case(
    session: AsyncSession = Depends(get_db_session),
) -> ForgotPasswordUseCase:
    return ForgotPasswordUseCase(SQLAlchemyUserRepository(session))


def get_reset_password_use_case(
    session: AsyncSession = Depends(get_db_session),
) -> ResetPasswordUseCase:
    return ResetPasswordUseCase(SQLAlchemyUserRepository(session))


def get_import_orders_csv_use_case() -> ImportOrdersCsvUseCase:
    return ImportOrdersCsvUseCase()
