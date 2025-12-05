# 🔒 Guia de Autenticação e Permissões

## 📋 Roles do Sistema

O sistema possui 2 tipos de usuários:

| Role | Valor | Descrição |
|------|-------|-----------|
| **Gestor** | `gestor` | Gerencia obras, cria checklists, adiciona engenheiros |
| **Engenheiro** | `engenheiro` | Faz check-in, preenche checklists, tira fotos |

---

## ❌ Erro 403 Forbidden

### Sintoma
```
INFO: "GET /api/v1/mobile/obras HTTP/1.0" 403 Forbidden
```

### Causa
O usuário logado não tem a role necessária para acessar o endpoint.

### Diagnóstico

#### 1. Verificar role do usuário logado
```bash
GET /api/v1/auth/me
Authorization: Bearer {seu_token}

# Resposta:
{
  "id": 1,
  "email": "admin@sst.com",
  "full_name": "Administrador SST",
  "role": "gestor",  # <-- Verificar este campo
  "is_active": true,
  "created_at": "2025-12-03T10:00:00"
}
```

#### 2. Verificar permissões necessárias

**Rotas Mobile** (`/api/v1/mobile/*`) → Requerem role `engenheiro`
**Rotas Obras** (`/api/v1/obras/*`) → Requerem role `gestor`
**Rotas Users** (`/api/v1/users/*`) → Requerem role `gestor`
**Rotas Dashboard** (`/api/v1/dashboard/*`) → Requerem role `gestor`

---

## ✅ Solução

### Caso 1: Usuário Gestor tentando acessar rotas Mobile

Se você é gestor e está tentando acessar `/mobile/obras`, você receberá 403.

**Solução:** Use as rotas de gestor:
```bash
# ❌ Errado (403 Forbidden)
GET /api/v1/mobile/obras

# ✅ Correto
GET /api/v1/obras
```

### Caso 2: Usuário Engenheiro tentando acessar rotas de Gestor

Se você é engenheiro e está tentando criar uma obra, você receberá 403.

**Solução:** Faça login com um usuário gestor.

### Caso 3: Criar usuário com role errada

Se você criou um usuário e esqueceu de definir a role correta:

```python
# ❌ Errado
{
  "email": "joao@empresa.com",
  "password": "senha123",
  "full_name": "João Silva",
  "role": "gestor"  # Mas deveria ser "engenheiro"
}

# ✅ Correto
{
  "email": "joao@empresa.com",
  "password": "senha123",
  "full_name": "João Silva",
  "role": "engenheiro"  # Role correta
}
```

---

## 👥 Criar Usuários

### Criar Gestor
```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "gestor@empresa.com",
  "password": "senha123",
  "full_name": "Maria Santos",
  "role": "gestor"
}
```

### Criar Engenheiro
```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "engenheiro@empresa.com",
  "password": "senha123",
  "full_name": "João Silva",
  "role": "engenheiro"
}
```

---

## 🔍 Verificar Permissões no Código

### Python (FastAPI)
```python
from app.api.v1.deps import get_current_engineer, get_current_gestor

# Rota que requer engenheiro
@router.get("/mobile/obras")
def list_obras(current_user: User = Depends(get_current_engineer)):
    # current_user.role == "engenheiro"
    pass

# Rota que requer gestor
@router.get("/obras")
def list_obras(current_user: User = Depends(get_current_gestor)):
    # current_user.role == "gestor"
    pass
```

---

## 🧪 Testar Permissões

### Teste 1: Login como Gestor
```bash
# 1. Login
POST /api/v1/auth/login
{
  "email": "admin@sst.com",
  "password": "admin123"
}

# 2. Verificar role
GET /api/v1/auth/me
# Resposta: "role": "gestor"

# 3. Tentar acessar rota de gestor (✅ Deve funcionar)
GET /api/v1/obras

# 4. Tentar acessar rota mobile (❌ Deve dar 403)
GET /api/v1/mobile/obras
```

### Teste 2: Login como Engenheiro
```bash
# 1. Login
POST /api/v1/auth/login
{
  "email": "engenheiro@sst.com",
  "password": "eng123"
}

# 2. Verificar role
GET /api/v1/auth/me
# Resposta: "role": "engenheiro"

# 3. Tentar acessar rota mobile (✅ Deve funcionar)
GET /api/v1/mobile/obras

# 4. Tentar acessar rota de gestor (❌ Deve dar 403)
GET /api/v1/obras
```

---

## 🔧 Comandos Úteis

### Verificar usuários no banco (Lightsail)
```bash
# SSH no servidor
ssh ubuntu@seu-ip

# Conectar ao banco Neon
psql "postgresql://user:pass@host/db?sslmode=require"

# Listar todos os usuários
SELECT id, email, full_name, role, is_active FROM users;

# Ver usuários por role
SELECT * FROM users WHERE role = 'engenheiro';
SELECT * FROM users WHERE role = 'gestor';

# Atualizar role de um usuário
UPDATE users SET role = 'engenheiro' WHERE email = 'joao@empresa.com';
```

### Criar usuários via script
```bash
# No servidor
cd /home/ubuntu/api
source venv/bin/activate
python create_admin.py
```

---

## 📊 Mapeamento Completo de Rotas

### Rotas Públicas (sem autenticação)
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/register` - Registro
- `GET /health` - Health check
- `GET /docs` - Documentação Swagger

### Rotas de Autenticação (qualquer usuário autenticado)
- `GET /api/v1/auth/me` - Ver meus dados
- `PUT /api/v1/auth/me` - Atualizar meu perfil

### Rotas Mobile (role: `engenheiro`)
- `GET /api/v1/mobile/obras` - Listar minhas obras
- `GET /api/v1/mobile/obras/{id}` - Ver detalhes da obra
- `POST /api/v1/mobile/checkin` - Fazer check-in
- `GET /api/v1/mobile/checkins` - Meus check-ins
- `GET /api/v1/mobile/obras/{id}/checklists` - Checklists da obra
- `POST /api/v1/mobile/checklists/submit` - Submeter checklist
- `GET /api/v1/mobile/checklists/submissions` - Minhas submissões
- `POST /api/v1/mobile/upload-photo` - Upload de foto

### Rotas Obras (role: `gestor`)
- `POST /api/v1/obras` - Criar obra
- `GET /api/v1/obras` - Listar minhas obras
- `GET /api/v1/obras/{id}` - Ver detalhes da obra
- `PUT /api/v1/obras/{id}` - Atualizar obra
- `DELETE /api/v1/obras/{id}` - Deletar obra
- `POST /api/v1/obras/{id}/engineers` - Adicionar engenheiro
- `DELETE /api/v1/obras/{id}/engineers/{eng_id}` - Remover engenheiro
- `GET /api/v1/obras/{id}/engineers` - Listar engenheiros
- `POST /api/v1/obras/{id}/checklists` - Criar checklist
- `GET /api/v1/obras/{id}/checklists` - Listar checklists
- `GET /api/v1/obras/{id}/checkins` - Ver check-ins da obra
- `GET /api/v1/obras/{id}/checklist-submissions` - Ver submissões da obra

### Rotas Users (role: `gestor`)
- `GET /api/v1/users/engineers` - Listar engenheiros
- `GET /api/v1/users/engineers/{id}` - Ver engenheiro

### Rotas Dashboard (role: `gestor`)
- `GET /api/v1/dashboard/stats` - Estatísticas gerais
- `GET /api/v1/dashboard/atividades-recentes` - Atividades recentes
- `GET /api/v1/dashboard/conformidade` - Estatísticas de conformidade
- `GET /api/v1/dashboard/obras/{id}/stats` - Stats de uma obra

---

## 💡 Dicas

1. **Sempre verifique a role antes de testar**
   ```bash
   GET /api/v1/auth/me
   ```

2. **Use o Swagger** para ver quais rotas estão disponíveis
   - http://localhost:8000/docs
   - http://200.225.235.218/docs

3. **Mensagem de erro melhorada**
   - Agora mostra a role atual: `Current role: gestor`

4. **Tokens expiram em 7 dias**
   - Faça novo login se receber 401 Unauthorized

---

**Última atualização:** 03/12/2025
