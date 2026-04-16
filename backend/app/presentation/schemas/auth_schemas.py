from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, examples=["João Silva"])
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", examples=["joao@email.com"])
    password: str = Field(..., min_length=8, examples=["Senha123"])

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("A senha deve conter pelo menos um número.")
        return v


class LoginRequest(BaseModel):
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", examples=["joao@email.com"])
    password: str = Field(..., min_length=1, examples=["Senha123"])


class UserResponse(BaseModel):
    id: str
    name: str
    email: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", examples=["joao@email.com"])


class ResetPasswordRequest(BaseModel):
    password: str = Field(..., min_length=8, examples=["NovaSenha123"])
    confirm_password: str = Field(..., min_length=8, examples=["NovaSenha123"])

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("A senha deve conter pelo menos um número.")
        return v
