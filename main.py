from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

from app.config import settings
from app.models import Base, engine
from app.routers import auth_router
from app.logging_config import setup_logging
from app.middleware import RequestLoggingMiddleware, RateLimitMiddleware

# Configurar logging
setup_logging(debug=settings.DEBUG)
logger = logging.getLogger(__name__)

logger.info("Iniciando servidor OAuth2...")
logger.info(f"Modo DEBUG: {settings.DEBUG}")

# Criar as tabelas do banco de dados
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Tabelas do banco de dados criadas/verificadas com sucesso")
except Exception as e:
    logger.error(f"Erro ao criar tabelas do banco de dados: {e}")
    raise

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Servidor OAuth2 para autenticação e autorização",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar CORS
# Em desenvolvimento, permite todas as origens
# Em produção, configure ALLOWED_ORIGINS com domínios específicos
allowed_origins = ["*"] if settings.ALLOWED_ORIGINS == "*" else settings.ALLOWED_ORIGINS.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Adicionar middleware de logging de requisições
app.add_middleware(RequestLoggingMiddleware)

# Adicionar rate limiting (apenas em produção)
if not settings.DEBUG:
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=settings.RATE_LIMIT_PER_MINUTE
    )
    logger.info(f"Rate limiting habilitado: {settings.RATE_LIMIT_PER_MINUTE} req/min")

# Incluir rotas
app.include_router(auth_router)
logger.info("Rotas de autenticação registradas")


@app.get("/")
async def root():
    """Endpoint raiz com informações do servidor"""
    return {
        "message": "OAuth2 Server",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "debug_mode": settings.DEBUG,
        "endpoints": {
            "register": "/auth/register",
            "login": "/auth/login",
            "token": "/auth/token",
            "me": "/auth/me",
            "verify": "/auth/verify"
        }
    }


@app.get("/health")
async def health_check():
    """Endpoint para health check"""
    try:
        # Verificar conexão com o banco
        from app.models import get_db
        db = next(get_db())
        db.execute("SELECT 1")
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check falhou: {e}")
        return {"status": "unhealthy", "error": str(e)}


@app.on_event("startup")
async def startup_event():
    """Evento executado ao iniciar o servidor"""
    logger.info("========================================")
    logger.info(f"Servidor {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Documentação disponível em /docs")
    logger.info("========================================")


@app.on_event("shutdown")
async def shutdown_event():
    """Evento executado ao desligar o servidor"""
    logger.info("Servidor OAuth2 sendo desligado...")


def main():
    """Função principal para iniciar o servidor"""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )


if __name__ == "__main__":
    main()
