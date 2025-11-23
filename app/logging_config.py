"""
Configuração de logging para a aplicação OAuth2
"""
import logging
import sys
from pathlib import Path

# Criar diretório de logs se não existir
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)


def setup_logging(debug: bool = False):
    """
    Configura o sistema de logging da aplicação
    
    Args:
        debug: Se True, configura nível DEBUG, senão INFO
    """
    log_level = logging.DEBUG if debug else logging.INFO
    
    # Formato do log
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configurar logging
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            # File handler
            logging.FileHandler(log_dir / "oauth_server.log"),
        ]
    )
    
    # Reduzir verbosidade de bibliotecas externas
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Obtém um logger configurado
    
    Args:
        name: Nome do módulo/componente
    
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)
