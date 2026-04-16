import logging

from fastapi import APIRouter, Depends, HTTPException

log = logging.getLogger(__name__)

from app.application.use_cases.forgot_password import ForgotPasswordUseCase, UserNotFoundError
from app.application.use_cases.login_user import InvalidCredentialsError, LoginUserUseCase
from app.application.use_cases.register_user import EmailAlreadyExistsError, RegisterUserUseCase
from app.core.security import create_access_token
from app.presentation.dependencies import get_forgot_password_use_case, get_login_use_case, get_register_use_case
from app.presentation.schemas.auth_schemas import AuthResponse, ForgotPasswordRequest, LoginRequest, RegisterRequest, UserResponse

router = APIRouter()


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=201,
    summary="Registrar novo usuário",
    description="Cria uma nova conta de usuário e retorna um token JWT junto com os dados do usuário.",
    responses={
        201: {"description": "Conta criada com sucesso."},
        409: {"description": "E-mail já cadastrado."},
        422: {"description": "Dados de entrada inválidos."},
    },
)
async def register(
    body: RegisterRequest,
    use_case: RegisterUserUseCase = Depends(get_register_use_case),
) -> AuthResponse:
    try:
        user = await use_case.execute(body.name, body.email, body.password)
    except EmailAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    token = create_access_token(subject=user.email)
    return AuthResponse(access_token=token, user=UserResponse(id=user.id, name=user.name, email=user.email))


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Autenticar usuário",
    description="Autentica com e-mail e senha e retorna um token JWT junto com os dados do usuário.",
    responses={
        200: {"description": "Autenticação bem-sucedida."},
        401: {"description": "Credenciais inválidas."},
        422: {"description": "Dados de entrada inválidos."},
    },
)
async def login(
    body: LoginRequest,
    use_case: LoginUserUseCase = Depends(get_login_use_case),
) -> AuthResponse:
    try:
        user = await use_case.execute(body.email, body.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    token = create_access_token(subject=user.email)
    return AuthResponse(access_token=token, user=UserResponse(id=user.id, name=user.name, email=user.email))


@router.post(
    "/forgot-password",
    status_code=200,
    summary="Esqueceu a senha",
    description=(
        "Gera uma nova senha aleatória, atualiza no banco e envia por e-mail para o usuário. "
        "Por segurança, retorna 200 mesmo quando o e-mail não está cadastrado."
    ),
    responses={
        200: {"description": "E-mail de recuperação enviado (se o endereço existir)."},
        500: {"description": "Falha ao enviar e-mail. Tente novamente."},
    },
)
async def forgot_password(
    body: ForgotPasswordRequest,
    use_case: ForgotPasswordUseCase = Depends(get_forgot_password_use_case),
) -> dict[str, str]:
    try:
        await use_case.execute(body.email)
    except UserNotFoundError:
        pass
    except Exception as exc:
        log.exception("Erro ao processar forgot-password para %s: %s", body.email, exc)
        raise HTTPException(status_code=500, detail="Falha ao enviar e-mail de recuperação. Tente novamente.")
    return {"message": "Se o e-mail estiver cadastrado, uma nova senha foi enviada."}
