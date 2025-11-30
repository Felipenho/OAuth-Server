from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """Schema de resposta com token de acesso e refresh token"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Dados extraídos do token JWT"""
    username: Optional[str] = None
    user_id: Optional[int] = None
