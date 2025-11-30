from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import bcrypt
import secrets
from ..config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha plain text corresponde ao hash"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def get_password_hash(password: str) -> str:
    """Gera hash da senha"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um token JWT de acesso com claims padrão
    
    Args:
        data: Dados a serem codificados no token (deve conter 'sub' e 'user_id')
        expires_delta: Tempo de expiração customizado
    
    Returns:
        Token JWT como string
    """
    now = datetime.now(timezone.utc)
    
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Montar payload com todos os claims necessários
    payload = {
        "sub": data.get("sub"),           # Subject (username)
        "user_id": data.get("user_id"),   # ID do usuário
        "iat": now,                        # Issued At
        "exp": expire,                     # Expiration
        "iss": settings.JWT_ISSUER,       # Issuer - quem emitiu o token
        "aud": settings.JWT_AUDIENCE      # Audience - para quem o token foi criado
    }
    
    encoded_jwt = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica e valida um token JWT com verificação de issuer e audience
    
    Args:
        token: Token JWT a ser decodificado
    
    Returns:
        Payload do token ou None se inválido
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={
                "verify_aud": True,
                "verify_iss": True
            },
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER
        )
        return payload
    except JWTError:
        return None


def create_refresh_token() -> str:
    """
    Cria um refresh token seguro e aleatório
    
    Returns:
        Token aleatório de 64 caracteres hexadecimais
    """
    return secrets.token_hex(32)


def get_refresh_token_expire_time() -> datetime:
    """
    Calcula o tempo de expiração para um refresh token
    
    Returns:
        Datetime de expiração
    """
    return datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
