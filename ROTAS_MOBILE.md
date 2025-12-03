# 📱 Rotas Mobile - API SST

## 🔐 Autenticação
Todas as rotas mobile requerem autenticação JWT no header:
```
Authorization: Bearer {access_token}
```

**Base URL:** `/api/v1/mobile`

---

## 📋 Endpoints Disponíveis

### 1. **Listar Obras do Engenheiro**
```http
GET /mobile/obras
```

**Parâmetros Query (opcionais):**
- `skip`: int (default: 0) - Paginação
- `limit`: int (default: 100) - Limite de resultados

**Resposta (200 OK):**
```json
[
  {
    "id": 1,
    "nome": "Obra ABC",
    "descricao": "Construção de prédio residencial",
    "endereco": "Rua Exemplo, 123 - São Paulo",
    "latitude": -23.550520,
    "longitude": -46.633308,
    "is_active": true,
    "gestor_id": 1,
    "created_at": "2025-12-01T10:00:00"
  }
]
```

---

### 2. **Obter Detalhes de uma Obra**
```http
GET /mobile/obras/{obra_id}
```

**Parâmetros URL:**
- `obra_id`: int (obrigatório)

**Resposta (200 OK):**
```json
{
  "id": 1,
  "nome": "Obra ABC",
  "descricao": "Construção de prédio residencial",
  "endereco": "Rua Exemplo, 123 - São Paulo",
  "latitude": -23.550520,
  "longitude": -46.633308,
  "is_active": true,
  "gestor_id": 1,
  "created_at": "2025-12-01T10:00:00"
}
```

**Erros:**
- `403 Forbidden` - Engenheiro não tem acesso a essa obra
- `404 Not Found` - Obra não existe

---

### 3. **Fazer Check-in**
```http
POST /mobile/checkin
```

**Body (JSON):**
```json
{
  "obra_id": 1,
  "latitude": -23.550520,
  "longitude": -46.633308
}
```

**Campos obrigatórios:**
- `obra_id`: int - ID da obra
- `latitude`: float - Latitude GPS
- `longitude`: float - Longitude GPS

**Resposta (201 Created):**
```json
{
  "id": 1,
  "engineer_id": 2,
  "obra_id": 1,
  "latitude": -23.550520,
  "longitude": -46.633308,
  "checkin_time": "2025-12-03T08:30:00"
}
```

**Erros:**
- `403 Forbidden` - Engenheiro não tem acesso a essa obra
- `400 Bad Request` - Dados inválidos (lat/long fora do range)

---

### 4. **Listar Meus Check-ins**
```http
GET /mobile/checkins
```

**Parâmetros Query (opcionais):**
- `skip`: int (default: 0)
- `limit`: int (default: 100)

**Resposta (200 OK):**
```json
[
  {
    "id": 1,
    "engineer_id": 2,
    "obra_id": 1,
    "latitude": -23.550520,
    "longitude": -46.633308,
    "checkin_time": "2025-12-03T08:30:00"
  },
  {
    "id": 2,
    "engineer_id": 2,
    "obra_id": 1,
    "latitude": -23.550899,
    "longitude": -46.633401,
    "checkin_time": "2025-12-02T09:15:00"
  }
]
```

---

### 5. **Listar Checklists de uma Obra**
```http
GET /mobile/obras/{obra_id}/checklists
```

**Parâmetros URL:**
- `obra_id`: int (obrigatório)

**Parâmetros Query (opcionais):**
- `skip`: int (default: 0)
- `limit`: int (default: 100)

**Resposta (200 OK):**
```json
[
  {
    "id": 1,
    "nome": "Checklist de Segurança Diário",
    "descricao": "Verificação de EPIs e condições da obra",
    "obra_id": 1,
    "is_active": true,
    "created_at": "2025-12-01T10:00:00",
    "items": [
      {
        "id": 1,
        "template_id": 1,
        "titulo": "EPIs",
        "descricao": "Verificar se todos os trabalhadores estão usando EPIs",
        "ordem": 1,
        "created_at": "2025-12-01T10:00:00"
      },
      {
        "id": 2,
        "template_id": 1,
        "titulo": "Extintores",
        "descricao": "Verificar validade e localização dos extintores",
        "ordem": 2,
        "created_at": "2025-12-01T10:00:00"
      }
    ]
  }
]
```

**Erros:**
- `403 Forbidden` - Engenheiro não tem acesso a essa obra

---

### 6. **Submeter Checklist Preenchido**
```http
POST /mobile/checklists/submit
```

**Body (JSON):**
```json
{
  "template_id": 1,
  "responses": [
    {
      "template_item_id": 1,
      "status": "conforme",
      "observacao": "Todos os trabalhadores usando EPIs corretamente",
      "foto_url": "/uploads/checklist/photo_123.jpg"
    },
    {
      "template_item_id": 2,
      "status": "nao_conforme",
      "observacao": "Extintor vencido no 3º andar",
      "foto_url": "/uploads/checklist/photo_124.jpg"
    },
    {
      "template_item_id": 3,
      "status": "pendente",
      "observacao": "Aguardando entrega de novos equipamentos",
      "foto_url": null
    },
    {
      "template_item_id": 4,
      "status": "nao_aplicavel",
      "observacao": "Área não está em uso hoje",
      "foto_url": null
    }
  ]
}
```

**Campos obrigatórios:**
- `template_id`: int - ID do template de checklist
- `responses`: array - Lista de respostas
  - `template_item_id`: int - ID do item do checklist
  - `status`: string - "conforme" | "nao_conforme" | "pendente" | "nao_aplicavel"
  - `observacao`: string (opcional) - Observação sobre o item
  - `foto_url`: string (opcional) - URL da foto (obtida do upload)

**Resposta (201 Created):**
```json
{
  "id": 1,
  "template_id": 1,
  "engineer_id": 2,
  "submitted_at": "2025-12-03T14:30:00",
  "responses": [
    {
      "id": 1,
      "submission_id": 1,
      "template_item_id": 1,
      "status": "conforme",
      "observacao": "Todos os trabalhadores usando EPIs corretamente",
      "foto_url": "/uploads/checklist/photo_123.jpg",
      "created_at": "2025-12-03T14:30:00"
    },
    {
      "id": 2,
      "submission_id": 1,
      "template_item_id": 2,
      "status": "nao_conforme",
      "observacao": "Extintor vencido no 3º andar",
      "foto_url": "/uploads/checklist/photo_124.jpg",
      "created_at": "2025-12-03T14:30:00"
    }
  ]
}
```

**Erros:**
- `404 Not Found` - Template não existe
- `403 Forbidden` - Engenheiro não tem acesso à obra do checklist
- `400 Bad Request` - Dados inválidos (status inválido, template_item_id não existe)

---

### 7. **Listar Minhas Submissões de Checklist**
```http
GET /mobile/checklists/submissions
```

**Parâmetros Query (opcionais):**
- `skip`: int (default: 0)
- `limit`: int (default: 100)

**Resposta (200 OK):**
```json
[
  {
    "id": 1,
    "template_id": 1,
    "engineer_id": 2,
    "submitted_at": "2025-12-03T14:30:00",
    "responses": [
      {
        "id": 1,
        "submission_id": 1,
        "template_item_id": 1,
        "status": "conforme",
        "observacao": "OK",
        "foto_url": "/uploads/checklist/photo_123.jpg",
        "created_at": "2025-12-03T14:30:00"
      }
    ]
  }
]
```

---

### 8. **Upload de Foto**
```http
POST /mobile/upload-photo
```

**Content-Type:** `multipart/form-data`

**Body (Form Data):**
- `file`: File (obrigatório) - Imagem (JPEG, PNG, WebP)

**Exemplo cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/mobile/upload-photo" \
  -H "Authorization: Bearer {token}" \
  -F "file=@/caminho/para/foto.jpg"
```

**Resposta (200 OK):**
```json
{
  "filename": "checklist/20251203_143045_abc123.jpg",
  "url": "/uploads/checklist/20251203_143045_abc123.jpg"
}
```

**Erros:**
- `400 Bad Request` - Arquivo inválido (formato não suportado, tamanho muito grande)

**Formatos aceitos:** JPG, JPEG, PNG, WebP
**Tamanho máximo:** 10MB

---

## 📊 Status do Checklist

Os possíveis valores para o campo `status` são:

| Status | Descrição |
|--------|-----------|
| `conforme` | Item está conforme/OK |
| `nao_conforme` | Item não conforme/Problema encontrado |
| `pendente` | Item pendente/Aguardando resolução |
| `nao_aplicavel` | Item não aplicável no momento |

---

## 🔄 Fluxo Completo do Mobile

### 1. **Login**
```http
POST /api/v1/auth/login
Body: { "email": "engenheiro@sst.com", "password": "senha123" }
Resposta: { "access_token": "...", "token_type": "bearer" }
```

### 2. **Listar Obras**
```http
GET /api/v1/mobile/obras
```

### 3. **Fazer Check-in**
```http
POST /api/v1/mobile/checkin
Body: { "obra_id": 1, "latitude": -23.55, "longitude": -46.63 }
```

### 4. **Ver Checklists Disponíveis**
```http
GET /api/v1/mobile/obras/1/checklists
```

### 5. **Tirar Foto e Fazer Upload**
```http
POST /api/v1/mobile/upload-photo
Body: FormData com arquivo
Resposta: { "url": "/uploads/checklist/photo.jpg" }
```

### 6. **Submeter Checklist**
```http
POST /api/v1/mobile/checklists/submit
Body: { "template_id": 1, "responses": [...] }
```

### 7. **Ver Histórico**
```http
GET /api/v1/mobile/checkins
GET /api/v1/mobile/checklists/submissions
```

---

## ⚠️ Regras de Negócio

1. **Check-in obrigatório**: Engenheiro só pode submeter checklist após fazer check-in na obra
2. **GPS obrigatório**: Latitude e longitude são obrigatórios no check-in
3. **Acesso restrito**: Engenheiro só vê obras atribuídas a ele pelo gestor
4. **Fotos opcionais**: Não é obrigatório enviar foto em todos os itens do checklist
5. **Status obrigatório**: Todo item do checklist precisa ter um status definido
6. **Ordenação**: Check-ins e submissões retornam ordenados por data (mais recente primeiro)

---

## 🔒 Autenticação

Para obter o token JWT:

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "engenheiro@sst.com",
  "password": "senha123"
}
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Use o token em todas as requisições:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Token expira em:** 7 dias (10080 minutos)

---

## 📱 Exemplos de Uso (JavaScript/TypeScript)

### Configuração Axios
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor para adicionar token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

### Login
```typescript
const login = async (email: string, password: string) => {
  const { data } = await api.post('/auth/login', { email, password });
  localStorage.setItem('access_token', data.access_token);
  return data;
};
```

### Listar Obras
```typescript
const getObras = async () => {
  const { data } = await api.get('/mobile/obras');
  return data;
};
```

### Fazer Check-in
```typescript
const checkin = async (obraId: number, latitude: number, longitude: number) => {
  const { data } = await api.post('/mobile/checkin', {
    obra_id: obraId,
    latitude,
    longitude
  });
  return data;
};
```

### Upload de Foto
```typescript
const uploadPhoto = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const { data } = await api.post('/mobile/upload-photo', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  
  return data.url;
};
```

### Submeter Checklist
```typescript
const submitChecklist = async (templateId: number, responses: any[]) => {
  const { data } = await api.post('/mobile/checklists/submit', {
    template_id: templateId,
    responses
  });
  return data;
};
```

---

## 🐛 Códigos de Erro HTTP

| Código | Descrição |
|--------|-----------|
| 200 | OK - Sucesso |
| 201 | Created - Recurso criado |
| 400 | Bad Request - Dados inválidos |
| 401 | Unauthorized - Token inválido/expirado |
| 403 | Forbidden - Sem permissão para acessar |
| 404 | Not Found - Recurso não encontrado |
| 422 | Unprocessable Entity - Erro de validação |
| 500 | Internal Server Error - Erro no servidor |

---

**📝 Nota:** Esta documentação está atualizada em 03/12/2025. Para testar as rotas interativamente, acesse: http://localhost:8000/docs
