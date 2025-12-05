from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Optional
import secrets
import os


class Settings(BaseSettings):
    """Configurações da aplicação OAuth2"""
    
    # Configurações do JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
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
    
    # CORS - Origens permitidas
    # Em desenvolvimento: "*"
    # Em produção: "https://app.exemplo.com,https://api.exemplo.com"
    ALLOWED_ORIGINS: str = "*"
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Valida SECRET_KEY e gera uma segura se não configurada."""
        if not v:
            # Em desenvolvimento, gera uma chave aleatória
            if os.getenv("DEBUG", "True").lower() == "true":
                generated_key = secrets.token_urlsafe(32)
                print(f"⚠️  WARNING: SECRET_KEY não configurada. Usando chave gerada: {generated_key[:16]}...")
                print(f"⚠️  Para produção, defina SECRET_KEY nas variáveis de ambiente!")
                return generated_key
            else:
                # Em produção, falha se não configurada
                raise ValueError(
                    "❌ ERRO CRÍTICO: SECRET_KEY não configurada!\n"
                    "   Defina a variável de ambiente SECRET_KEY com uma chave segura.\n"
                    "   Exemplo: SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
                )
        
        # Validar comprimento mínimo
        if len(v) < 32:
            raise ValueError(
                "❌ SECRET_KEY muito curta! Deve ter pelo menos 32 caracteres.\n"
                "   Gere uma segura com: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        
        return v
    
    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def validate_cors(cls, v: str) -> str:
        """Valida configuração de CORS."""
        if v == "*" and not os.getenv("DEBUG", "True").lower() == "true":
            print(
                "⚠️  WARNING: CORS configurado como '*' em modo produção!\n"
                "   Isso permite qualquer origem acessar sua API.\n"
                "   Configure ALLOWED_ORIGINS com domínios específicos."
            )
        return v
    
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
