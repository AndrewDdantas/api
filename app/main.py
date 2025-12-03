from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api_router import api_router
from app.core.config import settings
from app.database.database import engine, Base

# Criar tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
## 🏗️ API Sistema SST - Segurança e Saúde no Trabalho

Sistema completo para gerenciamento de obras, checklists de segurança, 
check-ins com geolocalização e controle de engenheiros.

### 🎯 Funcionalidades Principais

* **Autenticação JWT** - Login seguro para gestores e engenheiros
* **Gestão de Obras** - CRUD completo de obras e projetos
* **Check-ins com GPS** - Registro de presença com geolocalização obrigatória
* **Checklists Customizáveis** - Templates de checklist por obra
* **Upload de Fotos** - Evidências fotográficas dos checklists
* **Dashboard** - Estatísticas e indicadores de conformidade
* **Controle de Acesso** - Perfis gestor e engenheiro com permissões específicas

### 👥 Perfis de Usuário

* **Gestor**: Gerencia obras, cria checklists, adiciona engenheiros
* **Engenheiro**: Faz check-in, preenche checklists, tira fotos

### 🔐 Autenticação

A maioria dos endpoints requer autenticação via JWT Token.
Use o endpoint `/api/v1/auth/login` para obter o token.

### 📱 Rotas Mobile

Endpoints específicos para aplicativo mobile dos engenheiros: `/api/v1/mobile/*`

### 🌐 Documentação Completa

* **Swagger UI**: `/docs` (esta página)
* **ReDoc**: `/redoc` (documentação alternativa)
* **OpenAPI JSON**: `/openapi.json`
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "SST API Support",
        "email": "suporte@sst.com.br",
    },
    license_info={
        "name": "Proprietary",
    },
    openapi_tags=[
        {
            "name": "auth",
            "description": "Autenticação e gerenciamento de usuários"
        },
        {
            "name": "obras",
            "description": "Gestão de obras (Gestor)"
        },
        {
            "name": "mobile",
            "description": "Endpoints para aplicativo mobile (Engenheiro)"
        },
        {
            "name": "users",
            "description": "Gerenciamento de usuários (Gestor)"
        },
        {
            "name": "dashboard",
            "description": "Estatísticas e indicadores (Gestor)"
        }
    ]
)

# Configurar CORS - Permite todas as origens em desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight por 1 hora
)

# Incluir rotas
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "API SST - Sistema de Segurança e Saúde no Trabalho"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
