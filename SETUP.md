# Guia de Setup Rápido - SST API

## Pré-requisitos
- Python 3.8+
- PostgreSQL 12+
- Git (opcional)

## Setup Rápido (5 minutos)

### 1. Instalar PostgreSQL
Se ainda não tiver, baixe em: https://www.postgresql.org/download/

### 2. Criar banco de dados
```sql
-- Abra o pgAdmin ou psql e execute:
CREATE DATABASE sst_db;
CREATE USER sst_user WITH PASSWORD 'sst_password';
GRANT ALL PRIVILEGES ON DATABASE sst_db TO sst_user;
```

### 3. Configurar o projeto

```powershell
# Clone ou navegue até o diretório do projeto
cd api

# Crie o ambiente virtual
python -m venv venv

# Ative o ambiente virtual
.\venv\Scripts\Activate.ps1

# Instale as dependências
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Copie o arquivo `.env.example` para `.env`:
```powershell
Copy-Item .env.example .env
```

Edite o arquivo `.env` com suas credenciais:
```env
DATABASE_URL=postgresql://sst_user:sst_password@localhost:5432/sst_db
SECRET_KEY=sua-chave-secreta-muito-segura-aqui
```

### 5. Criar usuários iniciais

```powershell
python create_admin.py
```

Isso criará:
- **Gestor**: admin@sst.com / admin123
- **Engenheiro**: engenheiro@sst.com / eng123

### 6. Iniciar o servidor

```powershell
uvicorn app.main:app --reload
```

Ou use o script:
```powershell
.\run.ps1
```

### 7. Acessar a aplicação

- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc

## Testando a API

### 1. Login (via Swagger UI)
1. Abra http://localhost:8000/docs
2. Vá para `/api/v1/auth/login`
3. Clique em "Try it out"
4. Use as credenciais:
   ```json
   {
     "email": "admin@sst.com",
     "password": "admin123"
   }
   ```
5. Copie o `access_token` da resposta

### 2. Autorizar na Swagger UI
1. Clique no botão "Authorize" 🔒 no topo
2. Cole o token no formato: `Bearer {seu_token}`
3. Clique em "Authorize"

### 3. Criar uma obra
1. Vá para `/api/v1/obras` POST
2. Use o exemplo:
   ```json
   {
     "nome": "Obra Teste SST",
     "descricao": "Primeira obra de teste",
     "endereco": "Rua Teste, 100"
   }
   ```

### 4. Criar checklist
1. Vá para `/api/v1/obras/{obra_id}/checklists` POST
2. Use o obra_id da obra criada
3. Exemplo de checklist:
   ```json
   {
     "nome": "Checklist de Segurança",
     "descricao": "Verificação diária",
     "items": [
       {
         "titulo": "EPIs",
         "descricao": "Verificar uso de EPIs",
         "ordem": 1
       },
       {
         "titulo": "Sinalização",
         "descricao": "Verificar sinalização",
         "ordem": 2
       }
     ]
   }
   ```

### 5. Testar Dashboard (Novo!)
1. Vá para `/api/v1/dashboard/stats` GET
2. Veja as estatísticas gerais:
   - Total de obras ativas
   - Total de engenheiros
   - Check-ins hoje
   - Checklists hoje

3. Teste `/api/v1/dashboard/atividades-recentes` GET
   - Veja as últimas atividades (check-ins e checklists)

4. Teste `/api/v1/dashboard/conformidade` GET
   - Veja as estatísticas de conformidade dos checklists
   - Percentuais de conforme, não conforme, pendente

## Estrutura de Pastas Criadas

```
api/
├── app/                    # Código da aplicação
├── venv/                   # Ambiente virtual (criado)
├── uploads/                # Fotos (criado ao fazer upload)
├── .env                    # Configurações (você cria)
├── requirements.txt        # Dependências
├── README.md              # Documentação
└── create_admin.py        # Script de setup
```

## Solução de Problemas

### Erro: "could not connect to server"
- Verifique se o PostgreSQL está rodando
- Confirme as credenciais no arquivo `.env`

### Erro: "relation does not exist"
- O SQLAlchemy cria as tabelas automaticamente na primeira execução
- Se houver problemas, verifique as permissões do usuário no banco

### Erro: "Module not found"
- Certifique-se de que o ambiente virtual está ativo
- Reinstale as dependências: `pip install -r requirements.txt`

### Erro: psycopg2-binary ou pydantic-core não compilam (Windows)
- Atualize o pip: `python -m pip install --upgrade pip`
- Use versões mais recentes com wheels pré-compilados:
  ```powershell
  pip install --upgrade fastapi uvicorn sqlalchemy pydantic pydantic-settings
  ```
- As versões no `requirements.txt` já foram atualizadas para Python 3.13+

### Erro ao fazer upload de foto
- A pasta `uploads/` será criada automaticamente
- Verifique as permissões de escrita no diretório

## Próximos Passos

1. ✅ Sistema básico funcionando
2. ✅ **Rotas de Dashboard** - IMPLEMENTADO!
3. 📱 Desenvolver app mobile (Flutter - veja PROMPT_MOBILE.md)
4. 💻 Desenvolver interface web para gestores (React/Next.js - veja PROMPT_FRONTEND.md)
5. 📊 Integrar gráficos no frontend (já tem as rotas!)
6. 📧 Implementar notificações por email
7. 🔔 Adicionar notificações push no mobile
8. 📄 Gerar relatórios em PDF

## Suporte

Para dúvidas ou problemas:
1. Verifique a documentação em `/docs`
2. Consulte os exemplos em `EXAMPLES.md`
3. Revise o arquivo `README.md`

## Comandos Úteis

```powershell
# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Desativar ambiente virtual
deactivate

# Rodar servidor
uvicorn app.main:app --reload

# Rodar em outra porta
uvicorn app.main:app --reload --port 8080

# Ver logs detalhados
uvicorn app.main:app --reload --log-level debug

# Instalar nova dependência
pip install nome-pacote
pip freeze > requirements.txt
```

## Pronto para Produção

Antes de colocar em produção:
1. ✅ Altere a `SECRET_KEY` no `.env`
2. ✅ Use um banco de dados dedicado
3. ✅ Configure HTTPS
4. ✅ Ajuste `ALLOWED_ORIGINS` no CORS
5. ✅ Configure backup do banco
6. ✅ Use um servidor WSGI (Gunicorn)
7. ✅ Configure logs adequados
8. ✅ Implemente rate limiting

---

**Pronto! Sua API SST está funcionando! 🚀**
