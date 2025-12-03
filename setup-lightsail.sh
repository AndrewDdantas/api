#!/bin/bash

# Script de setup completo para Lightsail
# Execute como root ou com sudo

echo "🚀 Setup SST API no Lightsail"
echo "=============================="

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Execute como root: sudo bash setup-lightsail.sh${NC}"
    exit 1
fi

# 1. Atualizar sistema
echo -e "${YELLOW}📦 Atualizando sistema...${NC}"
apt update && apt upgrade -y

# 2. Instalar dependências
echo -e "${YELLOW}📦 Instalando dependências...${NC}"
apt install -y python3-pip python3-venv nginx supervisor git curl

# 3. Criar usuário para aplicação (se não existir)
if ! id "ubuntu" &>/dev/null; then
    echo -e "${YELLOW}👤 Criando usuário ubuntu...${NC}"
    useradd -m -s /bin/bash ubuntu
fi

# 4. Configurar diretório da aplicação
echo -e "${YELLOW}📁 Configurando diretório...${NC}"
cd /home/ubuntu

# Se já existe, fazer backup
if [ -d "api" ]; then
    mv api api.backup.$(date +%Y%m%d_%H%M%S)
fi

# Clonar repositório
echo -e "${YELLOW}📥 Clonando repositório...${NC}"
git clone https://github.com/AndrewDdantas/api.git
cd api

# Ajustar permissões
chown -R ubuntu:ubuntu /home/ubuntu/api

# 5. Criar ambiente virtual
echo -e "${YELLOW}🐍 Criando ambiente virtual...${NC}"
sudo -u ubuntu python3 -m venv venv

# 6. Instalar dependências Python
echo -e "${YELLOW}📦 Instalando dependências Python...${NC}"
sudo -u ubuntu /home/ubuntu/api/venv/bin/pip install -r requirements.txt

# 7. Criar arquivo .env
echo -e "${YELLOW}⚙️  Configurando .env...${NC}"
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
PROJECT_NAME="SST API"
VERSION="1.0.0"
API_V1_STR="/api/v1"

# Database - Atualizar com suas credenciais Neon
DATABASE_URL="postgresql://user:pass@host/db?sslmode=require&connect_timeout=10"

# Security - MUDAR EM PRODUÇÃO
SECRET_KEY="MUDE-ESTA-CHAVE-SECRETA-EM-PRODUCAO"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Upload
UPLOAD_DIR="uploads"
MAX_UPLOAD_SIZE=10485760
EOF
    chown ubuntu:ubuntu .env
    echo -e "${RED}⚠️  ATENÇÃO: Edite o arquivo .env com suas credenciais!${NC}"
    echo -e "${RED}   sudo nano /home/ubuntu/api/.env${NC}"
fi

# 8. Criar diretório de uploads
mkdir -p uploads/checklist
chown -R ubuntu:ubuntu uploads

# 9. Configurar Nginx
echo -e "${YELLOW}🌐 Configurando Nginx...${NC}"
cp nginx.conf /etc/nginx/sites-available/sst-api
ln -sf /etc/nginx/sites-available/sst-api /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Testar configuração Nginx
nginx -t
if [ $? -eq 0 ]; then
    systemctl restart nginx
    echo -e "${GREEN}✅ Nginx configurado com sucesso${NC}"
else
    echo -e "${RED}❌ Erro na configuração do Nginx${NC}"
    exit 1
fi

# 10. Configurar Supervisor
echo -e "${YELLOW}⚙️  Configurando Supervisor...${NC}"
cat > /etc/supervisor/conf.d/sst-api.conf << 'EOF'
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
EOF

# Criar arquivos de log
touch /var/log/sst-api.out.log /var/log/sst-api.err.log
chown ubuntu:ubuntu /var/log/sst-api.*.log

# Atualizar Supervisor
supervisorctl reread
supervisorctl update

# 11. Iniciar aplicação
echo -e "${YELLOW}🚀 Iniciando aplicação...${NC}"
supervisorctl start sst-api

# Aguardar alguns segundos
sleep 3

# 12. Verificar status
STATUS=$(supervisorctl status sst-api | awk '{print $2}')

echo ""
echo "=============================="
if [ "$STATUS" == "RUNNING" ]; then
    PUBLIC_IP=$(curl -s ifconfig.me)
    echo -e "${GREEN}✅ Setup concluído com sucesso!${NC}"
    echo ""
    echo "📋 Próximos passos:"
    echo "1. Editar .env com credenciais do banco:"
    echo "   ${YELLOW}sudo nano /home/ubuntu/api/.env${NC}"
    echo ""
    echo "2. Criar tabelas do banco:"
    echo "   ${YELLOW}cd /home/ubuntu/api${NC}"
    echo "   ${YELLOW}source venv/bin/activate${NC}"
    echo "   ${YELLOW}python -c \"from app.database.database import engine; from app.models.models import Base; Base.metadata.create_all(bind=engine)\"${NC}"
    echo "   ${YELLOW}python create_admin.py${NC}"
    echo ""
    echo "3. Reiniciar aplicação:"
    echo "   ${YELLOW}sudo supervisorctl restart sst-api${NC}"
    echo ""
    echo "🌐 API disponível em:"
    echo "   ${GREEN}http://$PUBLIC_IP/docs${NC}"
    echo ""
    echo "📊 Monitoramento:"
    echo "   Status: ${YELLOW}sudo supervisorctl status sst-api${NC}"
    echo "   Logs:   ${YELLOW}sudo tail -f /var/log/sst-api.out.log${NC}"
else
    echo -e "${RED}❌ Erro ao iniciar aplicação${NC}"
    echo "Verificar logs:"
    echo "   ${YELLOW}sudo tail -50 /var/log/sst-api.err.log${NC}"
fi
