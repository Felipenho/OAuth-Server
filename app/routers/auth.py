from datetime import datetime, timedelta, timezone
from typing import Annotated
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..models import User, RefreshToken, get_db
from ..schemas import UserCreate, UserResponse, UserLogin, Token, TokenData, RefreshTokenRequest
from ..utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    create_refresh_token,
    get_refresh_token_expire_time,
)
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth2 scheme para extrair o token do header Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_user_by_username(db: Session, username: str):
    """Busca usuário por username"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str):
    """Busca usuário por email"""
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, username: str, password: str):
    """Autentica usuário verificando username e senha"""
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
):
    """Dependência para obter o usuário atual a partir do token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    user_id: int = payload.get("user_id")
    
    if username is None or user_id is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Verifica se o usuário está ativo"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint para registro de novo usuário
    
    - **email**: Email do usuário (único)
    - **username**: Nome de usuário (único)
    - **password**: Senha (mínimo 6 caracteres)
    - **full_name**: Nome completo (opcional)
    """
    logger.info(f"Tentativa de registro: username={user_data.username}, email={user_data.email}")
    
    # Verificar se email já existe
    db_user = get_user_by_email(db, user_data.email)
    if db_user:
        logger.warning(f"Registro falhou: email {user_data.email} já existe")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Verificar se username já existe
    db_user = get_user_by_username(db, user_data.username)
    if db_user:
        logger.warning(f"Registro falhou: username {user_data.username} já existe")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    try:
        # Criar novo usuário
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"Usuário registrado com sucesso: {user_data.username} (ID: {db_user.id})")
        return db_user
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao registrar usuário {user_data.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )


@router.post("/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    """
    Endpoint OAuth2 compatível para login (token)
    
    - **username**: Nome de usuário
    - **password**: Senha
    
    Retorna um access_token JWT
    """
    logger.info(f"Tentativa de login: {form_data.username}")
    
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Login falhou: credenciais inválidas para {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Criar access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id},
            expires_delta=access_token_expires
        )
        
        # Criar e salvar refresh token
        refresh_token_str = create_refresh_token()
        refresh_token = RefreshToken(
            token=refresh_token_str,
            user_id=user.id,
            expires_at=get_refresh_token_expire_time()
        )
        db.add(refresh_token)
        db.commit()
        
        logger.info(f"Login bem-sucedido: {user.username} (ID: {user.id})")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token_str,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao gerar token para {user.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating token"
        )


@router.post("/login", response_model=Token)
async def login_json(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Endpoint alternativo para login com JSON
    
    - **username**: Nome de usuário
    - **password**: Senha
    
    Retorna um access_token JWT
    """
    logger.info(f"Tentativa de login (JSON): {user_data.username}")
    
    user = authenticate_user(db, user_data.username, user_data.password)
    if not user:
        logger.warning(f"Login falhou (JSON): credenciais inválidas para {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    try:
        # Criar access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id},
            expires_delta=access_token_expires
        )
        
        # Criar e salvar refresh token
        refresh_token_str = create_refresh_token()
        refresh_token = RefreshToken(
            token=refresh_token_str,
            user_id=user.id,
            expires_at=get_refresh_token_expire_time()
        )
        db.add(refresh_token)
        db.commit()
        
        logger.info(f"Login bem-sucedido (JSON): {user.username} (ID: {user.id})")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token_str,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao gerar token (JSON) para {user.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating token"
        )


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Endpoint para obter informações do usuário atual autenticado
    
    Requer token JWT válido no header Authorization
    """
    return current_user


@router.get("/verify")
async def verify_token(current_user: Annotated[User, Depends(get_current_active_user)]):
    """
    Endpoint para verificar se o token é válido
    
    Usado por outros backends para validar tokens
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
    }


@router.post("/refresh", response_model=Token)
async def refresh_access_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Endpoint para renovar access token usando refresh token
    
    - **refresh_token**: Refresh token válido
    
    Retorna novo access_token e refresh_token
    """
    logger.info("Tentativa de refresh de token")
    
    # Buscar refresh token no banco
    db_refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token == request.refresh_token,
        RefreshToken.is_revoked == False
    ).first()
    
    if not db_refresh_token:
        logger.warning("Refresh token inválido ou revogado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Verificar se o token expirou
    if db_refresh_token.expires_at < datetime.now(timezone.utc):
        logger.warning(f"Refresh token expirado para user_id={db_refresh_token.user_id}")
        db_refresh_token.is_revoked = True
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )
    
    # Buscar usuário
    user = db.query(User).filter(User.id == db_refresh_token.user_id).first()
    if not user or not user.is_active:
        logger.warning(f"Usuário inativo ou não encontrado: user_id={db_refresh_token.user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    try:
        # Revogar o refresh token antigo
        db_refresh_token.is_revoked = True
        
        # Criar novo access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id},
            expires_delta=access_token_expires
        )
        
        # Criar novo refresh token
        new_refresh_token_str = create_refresh_token()
        new_refresh_token = RefreshToken(
            token=new_refresh_token_str,
            user_id=user.id,
            expires_at=get_refresh_token_expire_time()
        )
        db.add(new_refresh_token)
        db.commit()
        
        logger.info(f"Token renovado com sucesso para user={user.username} (ID: {user.id})")
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token_str,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao renovar token para user_id={user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error refreshing token"
        )
