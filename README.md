# Sistema SST - API

Sistema de Segurança e Saúde no Trabalho (SST) com API REST desenvolvida em FastAPI.

## Funcionalidades

### Para Gestores (Web):
- ✅ Criar e gerenciar obras
- ✅ Criar templates de checklist para cada obra
- ✅ Adicionar/remover engenheiros nas obras
- ✅ Visualizar check-ins e checklists enviados
- ✅ Autenticação com JWT

### Para Engenheiros (Mobile):
- ✅ Login com email e senha
- ✅ Visualizar obras atribuídas
- ✅ Fazer check-in com geolocalização
- ✅ Preencher checklists com:
  - Status (Conforme, Não Conforme, Não Aplicável, Pendente)
  - Observação
  - Upload de foto
- ✅ Histórico de check-ins e checklists

## Estrutura do Projeto

```
api/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── routes/          # Rotas da API
│   │       │   ├── auth.py      # Autenticação
│   │       │   ├── obras.py     # Gestão de obras (web)
│   │       │   ├── mobile.py    # Rotas mobile (engenheiros)
│   │       │   └── users.py     # Gerenciamento de usuários
│   │       ├── api_router.py    # Router principal
│   │       └── deps.py          # Dependências (auth, db)
│   ├── core/
│   │   ├── config.py            # Configurações
│   │   └── security.py          # Segurança (JWT, hash)
│   ├── crud/                    # Operações de banco
│   ├── database/                # Configuração do banco
│   ├── models/                  # Models SQLAlchemy
│   ├── schemas/                 # Schemas Pydantic
│   ├── services/                # Serviços (upload, auth)
│   └── main.py                  # Aplicação principal
├── requirements.txt
└── .env.example
```

## Instalação

### 1. Criar ambiente virtual

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar banco de dados

Crie um arquivo `.env` baseado no `.env.example`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/sst_db
SECRET_KEY=sua-chave-secreta-aqui
```

### 4. Criar banco de dados

```sql
CREATE DATABASE sst_db;
```

## Executar

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Acesse a documentação interativa em: http://localhost:8000/docs

## Endpoints Principais

### Autenticação
- `POST /api/v1/auth/register` - Registrar usuário
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Dados do usuário atual

### Gestores (Web)
- `POST /api/v1/obras` - Criar obra
- `GET /api/v1/obras` - Listar minhas obras
- `POST /api/v1/obras/{id}/engineers` - Adicionar engenheiro
- `POST /api/v1/obras/{id}/checklists` - Criar checklist template

### Engenheiros (Mobile)
- `GET /api/v1/mobile/obras` - Listar obras atribuídas
- `POST /api/v1/mobile/checkin` - Fazer check-in
- `GET /api/v1/mobile/obras/{id}/checklists` - Listar checklists da obra
- `POST /api/v1/mobile/checklists/submit` - Enviar checklist preenchido
- `POST /api/v1/mobile/upload-photo` - Upload de foto

## Modelos de Dados

### User
- Email, senha (hash), nome completo
- Role: GESTOR ou ENGENHEIRO

### Obra
- Nome, descrição, endereço, coordenadas
- Relacionada a um gestor
- Pode ter múltiplos engenheiros

### ChecklistTemplate
- Template de checklist para uma obra
- Contém múltiplos items

### CheckIn
- Registro de presença do engenheiro
- Horário e geolocalização

### ChecklistSubmission
- Checklist preenchido pelo engenheiro
- Contém respostas para cada item

## Tecnologias

- **FastAPI** - Framework web
- **SQLAlchemy** - ORM
- **PostgreSQL** - Banco de dados
- **JWT** - Autenticação
- **Pydantic** - Validação de dados
- **Pillow** - Processamento de imagens

## Próximos Passos

- [ ] Implementar Alembic para migrations
- [ ] Adicionar testes unitários
- [ ] Implementar paginação
- [ ] Adicionar filtros e busca
- [ ] Dashboard com estatísticas
- [ ] Notificações
- [ ] Export de relatórios (PDF/Excel)
- [ ] WebSocket para atualizações em tempo real
