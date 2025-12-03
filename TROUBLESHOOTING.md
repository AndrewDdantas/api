# 🔧 Troubleshooting - Problemas de Conexão com Neon PostgreSQL

## ❌ Erro: SSL connection has been closed unexpectedly

### Causa
Conexão SSL com o banco Neon foi fechada inesperadamente, comum em bancos serverless que hibernam após inatividade.

### ✅ Solução Implementada

#### 1. Atualizado `app/database/database.py`:
```python
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=NullPool,  # Desabilita pool para evitar conexões antigas
    connect_args={
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    },
    pool_pre_ping=True,  # Testa conexão antes de usar
)
```

#### 2. URL de conexão otimizada:
```bash
DATABASE_URL="postgresql://user:pass@host/db?sslmode=require&connect_timeout=10"
```

### 🔄 Como aplicar no servidor:

```bash
# SSH no Lightsail
ssh ubuntu@seu-ip

# Ir para pasta da API
cd /home/ubuntu/api

# Fazer pull das atualizações
git pull origin main

# Ativar ambiente virtual
source venv/bin/activate

# Reinstalar dependências (se necessário)
pip install -r requirements.txt

# Reiniciar aplicação
sudo supervisorctl restart sst-api

# Verificar logs
sudo tail -f /var/log/sst-api.out.log
```

---

## 🐛 Outros Problemas Comuns

### 1. **Connection timeout**

**Sintomas:**
```
psycopg2.OperationalError: timeout expired
```

**Solução:**
- Aumentar `connect_timeout` na URL
- Verificar se o banco Neon não está hibernando (free tier hiberna após 5min)
- Considerar upgrade para Neon Pro (sem hibernação)

**Teste rápido:**
```bash
# Testar conexão direta
psql "postgresql://user:pass@host/db?sslmode=require"
```

---

### 2. **Too many connections**

**Sintomas:**
```
FATAL: remaining connection slots are reserved
```

**Solução:**
- Usar `poolclass=NullPool` (já implementado)
- Limitar workers do uvicorn: `--workers 2`
- Upgrade do plano Neon para mais conexões

**Configuração Supervisor:**
```ini
[program:sst-api]
command=/home/ubuntu/api/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

---

### 3. **SSL SYSCALL error**

**Sintomas:**
```
SSL SYSCALL error: EOF detected
```

**Solução:**
- Adicionar `pool_pre_ping=True` (já implementado)
- Usar Neon Pooler connection string:

```bash
# Use o endpoint -pooler
DATABASE_URL="postgresql://user:pass@ep-xxx-pooler.aws.neon.tech/db?sslmode=require"
```

---

### 4. **Connection refused**

**Sintomas:**
```
could not connect to server: Connection refused
```

**Solução:**
- Verificar se o banco Neon está ativo
- Conferir firewall do Lightsail (porta 5432 bloqueada?)
- Testar conectividade:

```bash
telnet ep-xxx.aws.neon.tech 5432
```

---

### 5. **Authentication failed**

**Sintomas:**
```
FATAL: password authentication failed
```

**Solução:**
- Verificar credenciais no `.env`
- Gerar nova senha no dashboard Neon
- Usar senha sem caracteres especiais que precisam encoding

---

## 🚀 Otimizações para Produção

### 1. **Usar Neon Pooler** (Recomendado)

Trocar de connection direto para pooler:

**Antes:**
```
ep-ancient-pine-acje25in.sa-east-1.aws.neon.tech
```

**Depois (Pooler):**
```
ep-ancient-pine-acje25in-pooler.sa-east-1.aws.neon.tech
```

### 2. **Configurar Health Check**

Adicionar endpoint que testa conexão:

```python
@app.get("/health/db")
def health_check_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}
```

### 3. **Monitoramento com Logs**

```bash
# Ver logs em tempo real
sudo tail -f /var/log/sst-api.out.log

# Filtrar erros de conexão
sudo grep -i "OperationalError" /var/log/sst-api.err.log

# Ver últimas 50 linhas de erro
sudo tail -50 /var/log/sst-api.err.log
```

### 4. **Auto-restart em caso de erro**

No Supervisor (`/etc/supervisor/conf.d/sst-api.conf`):

```ini
[program:sst-api]
directory=/home/ubuntu/api
command=/home/ubuntu/api/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
user=ubuntu
autostart=true
autorestart=true
startsecs=5
startretries=3
redirect_stderr=true
stdout_logfile=/var/log/sst-api.out.log
stderr_logfile=/var/log/sst-api.err.log
```

---

## 📊 Verificar Status do Neon

Dashboard Neon: https://console.neon.tech

**Verificar:**
- ✅ Project está ativo
- ✅ Compute não está suspenso
- ✅ Connection limit não foi atingido
- ✅ Storage disponível

---

## 🆘 Comandos de Emergência

```bash
# Reiniciar aplicação
sudo supervisorctl restart sst-api

# Ver status
sudo supervisorctl status sst-api

# Parar e iniciar
sudo supervisorctl stop sst-api
sudo supervisorctl start sst-api

# Recarregar configuração
sudo supervisorctl reread
sudo supervisorctl update

# Ver logs ao vivo
sudo tail -f /var/log/sst-api.out.log /var/log/sst-api.err.log

# Testar conexão Python
python3 << EOF
from sqlalchemy import create_engine
engine = create_engine("postgresql://user:pass@host/db?sslmode=require")
conn = engine.connect()
print("✅ Conexão OK!")
conn.close()
EOF
```

---

## 📞 Suporte

- **Neon Status**: https://neonstatus.com
- **Neon Discord**: https://discord.gg/neon
- **Neon Docs**: https://neon.tech/docs

---

**Última atualização:** 03/12/2025
