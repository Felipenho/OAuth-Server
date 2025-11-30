from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Configurações da aplicação OAuth2"""
    
    # Configurações do JWT
    SECRET_KEY: str = "your-secret-key-here-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ISSUER: str = "auth"
    JWT_AUDIENCE: str = "mcp"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Configurações do banco de dados
    DATABASE_URL: str = "postgresql://oauth_user:oauth_password@localhost:5432/oauth_db"
    
    # Configurações da aplicação
    APP_NAME: str = "OAuth2 Server"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # CORS - Origens permitidas (use "*" para permitir todas em desenvolvimento)
    ALLOWED_ORIGINS: str = "*"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignora variáveis extras do .env (ex: POSTGRES_*, PGADMIN_*)
    )


# Instância global de configurações
settings = Settings()

# Validar configurações de segurança em produção
if not settings.DEBUG:
    if settings.SECRET_KEY == "your-secret-key-here-change-this-in-production":
        raise ValueError(
            "SECRET_KEY padrão não pode ser usada em produção! "
            "Configure uma SECRET_KEY forte no arquivo .env"
        )
    if len(settings.SECRET_KEY) < 32:
        raise ValueError(
            "SECRET_KEY deve ter no mínimo 32 caracteres em produção!"
        )
