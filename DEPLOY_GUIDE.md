# 🚀 Deploy Completo - AWS Lightsail

## ✅ Checklist de Deploy

- [ ] Servidor Lightsail criado
- [ ] Python 3.12+ instalado
- [ ] Código da API clonado
- [ ] Banco de dados Neon configurado
- [ ] Nginx instalado e configurado
- [ ] Supervisor instalado e configurado ⚠️ **IMPORTANTE**
- [ ] Usuários criados (admin + engenheiro)
- [ ] Domínio configurado (opcional)
- [ ] HTTPS configurado (opcional)

---

## 📋 Passo a Passo Completo

### 1. Conectar no Lightsail

```bash
ssh ubuntu@200.225.235.218
```

### 2. Instalar Dependências do Sistema

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nginx supervisor git curl
```

### 3. Configurar a Aplicação

```bash
# Ir para home
cd /home/ubuntu

# Clonar repositório (se ainda não clonou)
git clone https://github.com/AndrewDdantas/api.git
cd api

# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Criar arquivo .env
nano .env
```

**Conteúdo do .env:**
```bash
PROJECT_NAME="SST API"
VERSION="1.0.0"
API_V1_STR="/api/v1"

# Database - Neon PostgreSQL
DATABASE_URL="postgresql://neondb_owner:npg_rgntNO1b5FYv@ep-ancient-pine-acje25in-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&connect_timeout=10"

# Security
SECRET_KEY="sua-chave-super-secreta-mude-em-producao-12345"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Upload
UPLOAD_DIR="uploads"
MAX_UPLOAD_SIZE=10485760
```

Salvar: `Ctrl+O`, `Enter`, `Ctrl+X`

```bash
# Criar diretório de uploads
mkdir -p uploads/checklist

# Criar tabelas no banco
python -c "from app.database.database import engine; from app.models.models import Base; Base.metadata.create_all(bind=engine)"

# Criar usuários iniciais
python create_admin.py

# Desativar ambiente virtual
deactivate
```

---

### 4. Configurar Nginx

```bash
# Copiar configuração
sudo cp nginx.conf /etc/nginx/sites-available/sst-api

# Criar link simbólico
sudo ln -sf /etc/nginx/sites-available/sst-api /etc/nginx/sites-enabled/

# Remover site padrão
sudo rm -f /etc/nginx/sites-enabled/default

# Testar configuração
sudo nginx -t

# Se OK, reiniciar Nginx
sudo systemctl restart nginx

# Verificar status
sudo systemctl status nginx
```

---

### 5. ⚠️ Configurar Supervisor (CRÍTICO)

**Este é o passo que faltou!** O Supervisor mantém a aplicação rodando mesmo depois de fechar o terminal.

```bash
# Criar arquivo de configuração do Supervisor
sudo nano /etc/supervisor/conf.d/sst-api.conf
```

**Conteúdo do arquivo (copie SEM a palavra 'ini'):**
```
[program:sst-api]
directory=/home/ubuntu/api
command=/home/ubuntu/api/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
user=ubuntu
autostart=true
autorestart=true
startsecs=5
startretries=3
stopwaitsecs=10
redirect_stderr=true
stdout_logfile=/var/log/sst-api.out.log
stderr_logfile=/var/log/sst-api.err.log
environment=PATH="/home/ubuntu/api/venv/bin"
```

**⚠️ ATENÇÃO: Copie apenas o conteúdo entre os [colchetes], NÃO copie a palavra "ini"!**

Salvar: `Ctrl+O`, `Enter`, `Ctrl+X`

```bash
# Criar arquivos de log
sudo touch /var/log/sst-api.out.log
sudo touch /var/log/sst-api.err.log
sudo chown ubuntu:ubuntu /var/log/sst-api.out.log
sudo chown ubuntu:ubuntu /var/log/sst-api.err.log

# Recarregar configuração do Supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Iniciar aplicação
sudo supervisorctl start sst-api

# Verificar status
sudo supervisorctl status sst-api
```

**Saída esperada:**
```
sst-api                          RUNNING   pid 12345, uptime 0:00:05
```

---

### 6. Testar API

```bash
# Testar localmente no servidor
curl http://localhost:8000/health

# Testar do seu computador
curl http://200.225.235.218/health

# Testar documentação
curl http://200.225.235.218/docs
```

---

## 🔧 Comandos do Supervisor

### Ver status
```bash
sudo supervisorctl status sst-api
```

### Iniciar aplicação
```bash
sudo supervisorctl start sst-api
```

### Parar aplicação
```bash
sudo supervisorctl stop sst-api
```

### Reiniciar aplicação
```bash
sudo supervisorctl restart sst-api
```

### Ver todos os processos
```bash
sudo supervisorctl status
```

### Ver logs em tempo real
```bash
# Logs de output
sudo tail -f /var/log/sst-api.out.log

# Logs de erro
sudo tail -f /var/log/sst-api.err.log

# Ambos
sudo tail -f /var/log/sst-api.out.log -f /var/log/sst-api.err.log
```

### Recarregar após mudanças na configuração
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart sst-api
```

---

## 🔄 Deploy de Atualizações

Quando você fizer mudanças no código:

```bash
# SSH no servidor
ssh ubuntu@200.225.235.218

# Ir para pasta da API
cd /home/ubuntu/api

# Fazer pull das mudanças
git pull origin main

# Ativar ambiente virtual (se necessário instalar novos pacotes)
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Reiniciar aplicação
sudo supervisorctl restart sst-api

# Ver logs
sudo tail -f /var/log/sst-api.out.log
```

---

## 🐛 Troubleshooting

### Aplicação não inicia

```bash
# Ver status detalhado
sudo supervisorctl status sst-api

# Ver logs de erro
sudo tail -50 /var/log/sst-api.err.log

# Reiniciar
sudo supervisorctl restart sst-api
```

### Aplicação para sozinha

```bash
# Ver se o Supervisor está rodando
sudo systemctl status supervisor

# Se não estiver, iniciar
sudo systemctl start supervisor
sudo systemctl enable supervisor

# Reiniciar aplicação
sudo supervisorctl restart sst-api
```

### Erro de permissão

```bash
# Ajustar permissões
sudo chown -R ubuntu:ubuntu /home/ubuntu/api
sudo chown ubuntu:ubuntu /var/log/sst-api.*.log
sudo supervisorctl restart sst-api
```

### Erro de conexão com banco

```bash
# Verificar .env
cat /home/ubuntu/api/.env

# Testar conexão
cd /home/ubuntu/api
source venv/bin/activate
python << EOF
from app.database.database import engine
conn = engine.connect()
print("✅ Conexão OK!")
conn.close()
EOF
```

### Porta 8000 já em uso

```bash
# Ver o que está usando a porta
sudo lsof -i :8000

# Parar aplicação antiga
sudo supervisorctl stop sst-api

# Matar processo manualmente (se necessário)
sudo kill -9 <PID>

# Reiniciar
sudo supervisorctl start sst-api
```

---

## 🔒 Configurar Firewall (Opcional mas Recomendado)

```bash
# Permitir SSH, HTTP e HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Bloquear porta 8000 (só Nginx deve acessar)
# Não precisa fazer nada, ela só é acessível localmente

# Ativar firewall
sudo ufw --force enable

# Ver status
sudo ufw status
```

---

## 🌐 Configurar HTTPS (Opcional)

Se você tiver um domínio:

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obter certificado SSL
sudo certbot --nginx -d seu-dominio.com.br

# Renovação é automática, mas pode testar
sudo certbot renew --dry-run
```

---

## 📊 Monitoramento

### Ver uso de recursos
```bash
# CPU e Memória
htop

# Espaço em disco
df -h

# Processos Python
ps aux | grep python
```

### Ver logs do Nginx
```bash
# Access logs
sudo tail -f /var/log/nginx/sst-api-access.log

# Error logs
sudo tail -f /var/log/nginx/sst-api-error.log
```

### Ver logs do sistema
```bash
# Logs do Supervisor
sudo tail -f /var/log/supervisor/supervisord.log

# Logs do sistema
sudo journalctl -u supervisor -f
```

---

## ✅ Verificar se está tudo OK

Execute este checklist:

```bash
# 1. Nginx rodando?
sudo systemctl status nginx | grep "active (running)"

# 2. Supervisor rodando?
sudo systemctl status supervisor | grep "active (running)"

# 3. API rodando?
sudo supervisorctl status sst-api | grep "RUNNING"

# 4. API responde?
curl http://localhost:8000/health

# 5. Nginx responde?
curl http://200.225.235.218/health

# 6. Logs sem erros recentes?
sudo tail -20 /var/log/sst-api.err.log
```

Se todos retornarem OK, **deploy completo!** ✅

---

## 📝 Arquivo de Configuração Rápida

Salve isso como `quick-check.sh`:

```bash
#!/bin/bash
echo "=== Status SST API ==="
echo ""
echo "1. Nginx:"
sudo systemctl is-active nginx
echo ""
echo "2. Supervisor:"
sudo systemctl is-active supervisor
echo ""
echo "3. API:"
sudo supervisorctl status sst-api
echo ""
echo "4. Últimas 5 linhas de log:"
sudo tail -5 /var/log/sst-api.out.log
```

Executar:
```bash
bash quick-check.sh
```

---

**🎉 Agora sua API roda em background permanentemente!**

Pode fechar o terminal que ela continuará funcionando. 🚀
