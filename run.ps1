# Script para rodar o servidor em desenvolvimento
Write-Host "Iniciando servidor SST API..." -ForegroundColor Green

# Verificar se o ambiente virtual existe
if (-not (Test-Path "venv")) {
    Write-Host "Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv venv
}

# Ativar ambiente virtual
Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Instalar dependências
Write-Host "Instalando dependências..." -ForegroundColor Yellow
pip install -r requirements.txt

# Verificar se .env existe
if (-not (Test-Path ".env")) {
    Write-Host "Arquivo .env não encontrado. Criando a partir do .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "Por favor, configure o arquivo .env com suas credenciais!" -ForegroundColor Red
    exit
}

# Rodar servidor
Write-Host "Iniciando servidor na porta 8000..." -ForegroundColor Green
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
