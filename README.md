# [SECURITY] OAuth2 Authentication Server

Servidor de autenticação OAuth2 completo construído com FastAPI, PostgreSQL e JWT para gerenciamento seguro de usuários e tokens.

## Índice

- [Características](#-características)
- [Tecnologias](#-tecnologias)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Uso](#-uso)
- [Endpoints da API](#-endpoints-da-api)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Docker](#-docker)
- [Testes](#-testes)
- [Segurança](#-segurança)
- [Contribuindo](#-contribuindo)

## Características

- [OK] **Autenticação JWT** com tokens seguros
- [OK] **Registro e login** de usuários
- [OK] **Hash de senhas** com bcrypt
- [OK] **PostgreSQL** como banco de dados
- [OK] **CORS** configurável para integração com frontend
- [OK] **Docker** e Docker Compose para deploy fácil
- [OK] **Documentação interativa** com Swagger UI e ReDoc
- [OK] **Validação** de dados com Pydantic
- [OK] **SQLAlchemy ORM** para gerenciamento de banco de dados
- [OK] **Claims JWT customizados** (issuer, audience)
- [OK] **Verificação de tokens** para integração com outros backends

## Tecnologias

- **[FastAPI](https://fastapi.tiangolo.com/)** - Framework web moderno e rápido
- **[PostgreSQL](https://www.postgresql.org/)** - Banco de dados relacional
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - ORM Python
- **[Pydantic](https://docs.pydantic.dev/)** - Validação de dados
- **[python-jose](https://github.com/mpdavis/python-jose)** - JWT tokens
- **[bcrypt](https://github.com/pyca/bcrypt/)** - Hash de senhas
- **[Docker](https://www.docker.com/)** - Containerização
- **[Uvicorn](https://www.uvicorn.org/)** - Servidor ASGI

## Pré-requisitos

- Python 3.13+
- PostgreSQL 12+ (ou Docker)
- Docker e Docker Compose (opcional, recomendado)

## Instalação

### Opção 1: Com Docker (Recomendado)

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd oauth
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
```

3. Inicie os serviços:
```bash
docker-compose up -d
```

O servidor estará disponível em `http://localhost:8001`

### Opção 2: Instalação Local

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd oauth
```

2. Instale as dependências:
```bash
pip install -e .
```

3. Configure o PostgreSQL:
```sql
CREATE USER oauth_user WITH PASSWORD 'oauth_password';
CREATE DATABASE oauth_db OWNER oauth_user;
GRANT ALL PRIVILEGES ON DATABASE oauth_db TO oauth_user;
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o .env com suas configurações
```

5. Execute o servidor:
```bash
python main.py
```

## Configuração

Edite o arquivo `.env` com suas configurações:

```env
# Segurança JWT
SECRET_KEY=sua-chave-secreta-super-segura-min-32-caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_ISSUER=server-auth
JWT_AUDIENCE=server-mcp

# PostgreSQL
DATABASE_URL=postgresql://oauth_user:oauth_password@localhost:5432/oauth_db

# Aplicação
APP_NAME=OAuth2 Server
APP_VERSION=1.0.0
DEBUG=True

# CORS (opcional)
ALLOWED_ORIGINS=*
```

### Configurações Importantes:

- **SECRET_KEY**: Use uma chave aleatória forte (mínimo 32 caracteres)
- **ACCESS_TOKEN_EXPIRE_MINUTES**: Tempo de expiração do token em minutos
- **JWT_ISSUER**: Identificador de quem emitiu o token
- **JWT_AUDIENCE**: Identificador do público-alvo do token
- **ALLOWED_ORIGINS**: Use `*` para desenvolvimento, domínios específicos em produção

## Uso

### Documentação Interativa

Acesse a documentação Swagger UI:
```
http://localhost:8001/docs
```

Ou a documentação ReDoc:
```
http://localhost:8001/redoc
```

### Exemplo de Uso (Frontend)

#### 1. Registrar um usuário:
```javascript
const response = await fetch('http://localhost:8001/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'usuario@exemplo.com',
    username: 'usuario',
    password: 'senha123',
    full_name: 'Nome Completo'
  })
});

const user = await response.json();
console.log(user);
```

#### 2. Fazer login:
```javascript
const response = await fetch('http://localhost:8001/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'usuario',
    password: 'senha123'
  })
});

const { access_token } = await response.json();
localStorage.setItem('token', access_token);
```

#### 3. Acessar dados do usuário autenticado:
```javascript
const token = localStorage.getItem('token');

const response = await fetch('http://localhost:8001/auth/me', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const userData = await response.json();
console.log(userData);
```

### Exemplo de Uso (Outro Backend)

#### Verificar token:
```python
import requests

def verify_token(token: str):
    response = requests.get(
        'http://localhost:8001/auth/verify',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if response.status_code == 200:
        return response.json()  # {'valid': True, 'user_id': 1, 'username': '...'}
    return None
```

## Endpoints da API

### Autenticação

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/auth/register` | Registra novo usuário | Não |
| POST | `/auth/login` | Login com JSON | Não |
| POST | `/auth/token` | Login OAuth2 (form-data) | Não |
| GET | `/auth/me` | Dados do usuário atual | Sim |
| GET | `/auth/verify` | Verifica validade do token | Sim |

### Outros

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Informações do servidor |
| GET | `/health` | Health check |
| GET | `/docs` | Documentação Swagger |
| GET | `/redoc` | Documentação ReDoc |

### Detalhes dos Endpoints

#### POST /auth/register
Registra um novo usuário.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "full_name": "Full Name"
}
```

**Response (201):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "is_active": true,
  "created_at": "2025-11-23T10:30:00Z"
}
```

#### POST /auth/login
Faz login e retorna token JWT.

**Request Body:**
```json
{
  "username": "username",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### GET /auth/me
Retorna informações do usuário autenticado.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "is_active": true,
  "created_at": "2025-11-23T10:30:00Z"
}
```

#### GET /auth/verify
Verifica se o token é válido (usado por outros backends).

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "valid": true,
  "user_id": 1,
  "username": "username",
  "email": "user@example.com"
}
```

## Estrutura do Projeto

```
oauth/
├── app/
│   ├── __init__.py
│   ├── config.py              # Configurações da aplicação
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py        # Configuração do SQLAlchemy
│   │   └── user.py            # Modelo de usuário
│   ├── routers/
│   │   ├── __init__.py
│   │   └── auth.py            # Rotas de autenticação
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py            # Schemas de usuário
│   │   └── token.py           # Schemas de token
│   └── utils/
│       ├── __init__.py
│       └── security.py        # Funções de segurança (JWT, bcrypt)
├── .env                       # Variáveis de ambiente (não commitado)
├── .env.example               # Exemplo de variáveis de ambiente
├── .gitignore
├── docker-compose.yml         # Configuração Docker Compose
├── Dockerfile                 # Dockerfile da aplicação
├── main.py                    # Ponto de entrada da aplicação
├── pyproject.toml             # Dependências Python
└── README.md                  # Este arquivo
```

## Docker

### Serviços Disponíveis

O `docker-compose.yml` inclui três serviços:

1. **postgres** - Banco de dados PostgreSQL
2. **oauth-server** - Servidor OAuth2
3. **pgadmin** - Interface web para gerenciar PostgreSQL

### Comandos Úteis

```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f oauth-server

# Parar todos os serviços
docker-compose down

# Reconstruir após mudanças
docker-compose up -d --build oauth-server

# Acessar banco de dados
docker-compose exec postgres psql -U oauth_user -d oauth_db

# Ver usuários no banco
docker-compose exec postgres psql -U oauth_user -d oauth_db -c "SELECT * FROM users;"
```

### Portas

- **8001**: OAuth Server
- **80**: PgAdmin
- **5432**: PostgreSQL (não exposta por padrão)

## Testes

Execute os testes disponíveis:

```bash
# Teste rápido de autenticação
python test_oauth.py

# Teste de debug
python debug_auth.py
```

Ou use o Swagger UI em `http://localhost:8001/docs` para testar interativamente.

## Segurança

### Práticas Implementadas

- [OK] Senhas hasheadas com **bcrypt**
- [OK] Tokens JWT com **expiração configurável**
- [OK] Validação de dados com **Pydantic**
- [OK] CORS **configurável**
- [OK] Claims JWT customizados (**issuer**, **audience**)
- [OK] Verificação de tokens para **outros serviços**

### Recomendações para Produção

1. **Altere a SECRET_KEY**: Use uma chave forte e aleatória
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Configure DEBUG=False**

3. **Use HTTPS**: Configure certificados SSL/TLS

4. **Configure CORS específico**: Liste apenas domínios confiáveis
   ```env
   ALLOWED_ORIGINS=https://seusite.com,https://app.seusite.com
   ```

5. **Use banco de dados gerenciado**: PostgreSQL na nuvem (AWS RDS, Azure, etc.)

6. **Configure logs apropriados**

7. **Implemente rate limiting**

8. **Use variáveis de ambiente seguras**: AWS Secrets Manager, Azure Key Vault, etc.

9. **Monitore e faça backup do banco de dados**

10. **Mantenha dependências atualizadas**

## Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## Suporte

Para problemas, dúvidas ou sugestões:
- Abra uma issue no GitHub
- Entre em contato com a equipe de desenvolvimento

## Agradecimentos

- FastAPI pela excelente framework
- Comunidade Python pelo suporte e bibliotecas
- Todos os contribuidores do projeto
