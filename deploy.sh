#!/bin/bash

# Script de deploy para Lightsail
# Uso: bash deploy.sh

echo "🚀 Iniciando deploy da API SST..."

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Parar aplicação
echo -e "${YELLOW}⏸️  Parando aplicação...${NC}"
sudo supervisorctl stop sst-api

# Atualizar código
echo -e "${YELLOW}📥 Atualizando código...${NC}"
git pull origin main

# Ativar ambiente virtual
source venv/bin/activate

# Instalar/atualizar dependências
echo -e "${YELLOW}📦 Instalando dependências...${NC}"
pip install -r requirements.txt

# Criar/atualizar tabelas do banco
echo -e "${YELLOW}🗄️  Atualizando banco de dados...${NC}"
python -c "from app.database.database import engine; from app.models.models import Base; Base.metadata.create_all(bind=engine)"

# Reiniciar aplicação
echo -e "${YELLOW}🔄 Reiniciando aplicação...${NC}"
sudo supervisorctl start sst-api

# Aguardar alguns segundos
sleep 3

# Verificar status
STATUS=$(sudo supervisorctl status sst-api | awk '{print $2}')

if [ "$STATUS" == "RUNNING" ]; then
    echo -e "${GREEN}✅ Deploy concluído com sucesso!${NC}"
    echo -e "${GREEN}API rodando em: http://$(curl -s ifconfig.me):8000${NC}"
else
    echo -e "${RED}❌ Erro no deploy. Verificar logs:${NC}"
    echo -e "${RED}sudo tail -f /var/log/sst-api.err.log${NC}"
fi
