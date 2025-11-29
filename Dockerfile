FROM python:3.13-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv
RUN pip install --no-cache-dir uv

# Copiar arquivos de dependências
COPY pyproject.toml .

# Instalar dependências Python
RUN uv pip install --system --no-cache-dir -e .

# Copiar o código da aplicação
COPY . .

# Expor a porta
EXPOSE 8000

# Comando para executar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
