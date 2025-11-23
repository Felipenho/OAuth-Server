# Checklist de Segurança - Servidor OAuth

## Boas Práticas Implementadas

### Autenticação e Autorização
- [OK] **Tokens JWT** com expiração configurável
- [OK] **Claims customizados** (issuer, audience) para validação adicional
- [OK] **Senhas hasheadas** com bcrypt (algoritmo forte)
- [OK] **Validação de credenciais** em todos os endpoints protegidos
- [OK] **OAuth2 Password Flow** implementado corretamente

### Banco de Dados
- [OK] **SQLAlchemy ORM** para prevenção de SQL injection
- [OK] **PostgreSQL** como banco de dados robusto
- [OK] **Pool de conexões** configurado (pool_size=10, max_overflow=20)
- [OK] **Health checks** do banco de dados
- [OK] **Transações com rollback** em caso de erro

### Validação de Dados
- [OK] **Pydantic schemas** para validação automática
- [OK] **Validação de email** com formato correto
- [OK] **Senhas mínimas** de 6 caracteres
- [OK] **Username único** e email único

### Logging e Monitoramento
- [OK] **Sistema de logging** estruturado
- [OK] **Logs de requisições** (método, path, IP, tempo de resposta)
- [OK] **Logs de autenticação** (tentativas de login, registros)
- [OK] **Logs de erros** detalhados
- [OK] **Arquivos de log** persistentes

### Segurança de Rede
- [OK] **CORS configurável** por ambiente
- [OK] **Rate limiting** (60 req/min por IP em produção)
- [OK] **HTTPS ready** (configure certificados no proxy reverso)
- [OK] **Headers de segurança** (X-Process-Time)

### Configuração e Ambiente
- [OK] **Variáveis de ambiente** para configurações sensíveis
- [OK] **.env não commitado** ao git (.gitignore configurado)
- [OK] **Validação de SECRET_KEY** em produção
- [OK] **Modo DEBUG** desabilitável
- [OK] **Configurações específicas** por ambiente

### Docker e Deploy
- [OK] **Dockerfile otimizado** com multi-stage build potencial
- [OK] **Docker Compose** para orquestração
- [OK] **Health checks** do PostgreSQL
- [OK] **Networks isoladas** para comunicação entre containers
- [OK] **Volumes persistentes** para dados

### Documentação
- [OK] **Swagger UI** interativo
- [OK] **ReDoc** alternativo
- [OK] **README completo** com exemplos
- [OK] **Comentários** em código crítico
- [OK] **Guias de setup** e testes

## Checklist para Produção

### Crítico (Deve Fazer)
- [ ] **Alterar SECRET_KEY** para valor aleatório forte (32+ caracteres)
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- [ ] **Configurar DEBUG=False** no .env de produção
- [ ] **Configurar CORS específico** (remover "*", listar domínios permitidos)
- [ ] **Usar HTTPS** (configure no nginx/traefik/cloudflare)
- [ ] **Backup automático** do banco de dados PostgreSQL
- [ ] **Monitoramento** (Sentry, Datadog, ou similar)

### Importante (Recomendado)
- [ ] **Aumentar ACCESS_TOKEN_EXPIRE_MINUTES** conforme necessidade (atualmente 15min)
- [ ] **Configurar rate limiting** adequado (60 req/min pode ser pouco/muito)
- [ ] **Implementar refresh tokens** para sessões longas
- [ ] **Adicionar 2FA** (autenticação de dois fatores) opcional
- [ ] **Implementar logout/revogação** de tokens
- [ ] **Configurar alertas** para falhas de autenticação
- [ ] **Log rotation** para evitar disco cheio
- [ ] **Adicionar métricas** (Prometheus)

### Bom Ter (Opcional)
- [ ] **Redis** para cache de tokens/sessões
- [ ] **Email verification** no registro
- [ ] **Password reset** via email
- [ ] **Account lockout** após N tentativas falhas
- [ ] **Auditoria** de acessos e mudanças
- [ ] **CAPTCHA** em login/registro
- [ ] **IP whitelisting** para endpoints administrativos
- [ ] **WAF** (Web Application Firewall)

## Configuração de Produção Recomendada

### Arquivo .env de Produção
```env
# NUNCA commitar este arquivo!
SECRET_KEY=<CHAVE_FORTE_GERADA_ALEATORIAMENTE>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_ISSUER=auth
JWT_AUDIENCE=mcp

DATABASE_URL=postgresql://user:password@db.production.com:5432/oauth_db

APP_NAME=OAuth2 Server
APP_VERSION=1.0.0
DEBUG=False

ALLOWED_ORIGINS=https://seusite.com,https://app.seusite.com
RATE_LIMIT_PER_MINUTE=100
```

### Nginx como Proxy Reverso
```nginx
server {
    listen 443 ssl http2;
    server_name auth.seusite.com;

    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;

    # Headers de segurança
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Docker Compose para Produção
```yaml
services:
  oauth-server:
    image: seu-registry/oauth-server:latest
    restart: always
    environment:
      DATABASE_URL: ${DATABASE_URL}
    env_file:
      - .env.production
    depends_on:
      - postgres
    networks:
      - internal
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
```

## Testes de Segurança

### Testes Recomendados
1. **Penetration Testing** com OWASP ZAP
2. **Dependency Scanning** com `safety` ou `snyk`
3. **Static Analysis** com `bandit`
4. **Container Scanning** com Trivy
5. **Load Testing** com Locust ou k6

### Comandos Úteis
```bash
# Verificar vulnerabilidades em dependências
pip install safety
safety check

# Análise estática de segurança
pip install bandit
bandit -r app/

# Scan de container
trivy image oauth-server:latest
```

## Monitoramento Recomendado

### Métricas a Monitorar
- Taxa de requisições por endpoint
- Tempo de resposta médio
- Taxa de erros 4xx e 5xx
- Tentativas de login falhas
- Uso de CPU e memória
- Conexões do banco de dados
- Espaço em disco (logs)

### Alertas Recomendados
- > 10 login failures em 1 minuto
- Tempo de resposta > 5 segundos
- Taxa de erro > 5%
- Disco > 80% cheio
- CPU > 90% por 5 minutos
- Banco de dados inacessível

## Manutenção Contínua

### Semanalmente
- Verificar logs de erro
- Revisar tentativas de login falhas
- Verificar uso de recursos

### Mensalmente
- Atualizar dependências Python
- Revisar configurações de segurança
- Backup e teste de restauração
- Análise de performance

### Trimestralmente
- Audit de segurança completo
- Revisão de logs de acesso
- Atualização do PostgreSQL
- Testes de penetração

---

**Última atualização**: 23 de novembro de 2025
