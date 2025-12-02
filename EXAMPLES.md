# Exemplos de Uso da API SST

Este documento contém exemplos de como usar a API do sistema SST.

## Base URL
```
http://localhost:8000/api/v1
```

## 1. Autenticação

### Registrar um novo usuário (Gestor)
```bash
POST /auth/register
Content-Type: application/json

{
  "email": "gestor@empresa.com",
  "password": "senha123",
  "full_name": "João Silva",
  "role": "gestor"
}
```

### Registrar um novo usuário (Engenheiro)
```bash
POST /auth/register
Content-Type: application/json

{
  "email": "engenheiro@empresa.com",
  "password": "senha123",
  "full_name": "Maria Santos",
  "role": "engenheiro"
}
```

### Login
```bash
POST /auth/login
Content-Type: application/json

{
  "email": "gestor@empresa.com",
  "password": "senha123"
}

# Resposta:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Obter dados do usuário logado
```bash
GET /auth/me
Authorization: Bearer {token}
```

## 2. Gestão de Obras (Gestor)

### Criar uma obra
```bash
POST /obras
Authorization: Bearer {token}
Content-Type: application/json

{
  "nome": "Construção Edifício Central",
  "descricao": "Construção de edifício comercial de 15 andares",
  "endereco": "Rua Principal, 1000 - Centro",
  "latitude": -23.5505,
  "longitude": -46.6333
}
```

### Listar minhas obras
```bash
GET /obras?skip=0&limit=10
Authorization: Bearer {token}
```

### Obter detalhes de uma obra
```bash
GET /obras/{obra_id}
Authorization: Bearer {token}
```

### Atualizar obra
```bash
PUT /obras/{obra_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "nome": "Construção Edifício Central - Atualizado",
  "is_active": true
}
```

## 3. Gerenciar Engenheiros na Obra

### Adicionar engenheiro à obra
```bash
POST /obras/{obra_id}/engineers
Authorization: Bearer {token}
Content-Type: application/json

{
  "engineer_id": 2
}
```

### Listar engenheiros da obra
```bash
GET /obras/{obra_id}/engineers
Authorization: Bearer {token}
```

### Remover engenheiro da obra
```bash
DELETE /obras/{obra_id}/engineers/{engineer_id}
Authorization: Bearer {token}
```

## 4. Gerenciar Checklists (Gestor)

### Criar template de checklist para uma obra
```bash
POST /obras/{obra_id}/checklists
Authorization: Bearer {token}
Content-Type: application/json

{
  "nome": "Checklist Diário de Segurança",
  "descricao": "Checklist de verificação diária de itens de segurança",
  "items": [
    {
      "titulo": "EPIs em uso",
      "descricao": "Verificar se todos os trabalhadores estão usando EPIs adequados",
      "ordem": 1
    },
    {
      "titulo": "Sinalização de segurança",
      "descricao": "Verificar se toda sinalização está visível e em bom estado",
      "ordem": 2
    },
    {
      "titulo": "Equipamentos de proteção coletiva",
      "descricao": "Verificar guarda-corpos, redes de proteção, etc.",
      "ordem": 3
    },
    {
      "titulo": "Ordem e limpeza",
      "descricao": "Verificar condições de ordem e limpeza no canteiro",
      "ordem": 4
    }
  ]
}
```

### Listar checklists de uma obra
```bash
GET /obras/{obra_id}/checklists
Authorization: Bearer {token}
```

## 5. Mobile - Engenheiro

### Listar obras atribuídas ao engenheiro
```bash
GET /mobile/obras
Authorization: Bearer {token}
```

### Obter detalhes de uma obra
```bash
GET /mobile/obras/{obra_id}
Authorization: Bearer {token}
```

### Fazer check-in
```bash
POST /mobile/checkin
Authorization: Bearer {token}
Content-Type: application/json

{
  "obra_id": 1,
  "latitude": -23.5505,
  "longitude": -46.6333
}
```

### Listar meus check-ins
```bash
GET /mobile/checkins
Authorization: Bearer {token}
```

### Listar checklists disponíveis de uma obra
```bash
GET /mobile/obras/{obra_id}/checklists
Authorization: Bearer {token}
```

### Upload de foto
```bash
POST /mobile/upload-photo
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [arquivo de imagem]

# Resposta:
{
  "filename": "checklist/a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg",
  "url": "/uploads/checklist/a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg"
}
```

### Submeter checklist preenchido
```bash
POST /mobile/checklists/submit
Authorization: Bearer {token}
Content-Type: application/json

{
  "template_id": 1,
  "responses": [
    {
      "template_item_id": 1,
      "status": "conforme",
      "observacao": "Todos os trabalhadores usando capacete, luvas e botas",
      "foto_url": "checklist/abc123.jpg"
    },
    {
      "template_item_id": 2,
      "status": "nao_conforme",
      "observacao": "Sinalização de área restrita danificada",
      "foto_url": "checklist/def456.jpg"
    },
    {
      "template_item_id": 3,
      "status": "conforme",
      "observacao": "Guarda-corpos instalados corretamente",
      "foto_url": null
    },
    {
      "template_item_id": 4,
      "status": "nao_conforme",
      "observacao": "Materiais desorganizados na área de circulação",
      "foto_url": "checklist/ghi789.jpg"
    }
  ]
}
```

### Listar minhas submissões de checklist
```bash
GET /mobile/checklists/submissions
Authorization: Bearer {token}
```

## 6. Gerenciar Usuários (Gestor)

### Listar todos os engenheiros
```bash
GET /users/engineers
Authorization: Bearer {token}
```

### Obter dados de um engenheiro específico
```bash
GET /users/engineers/{engineer_id}
Authorization: Bearer {token}
```

## Status do Checklist

Os possíveis status para cada item do checklist são:
- `conforme` - Item está em conformidade
- `nao_conforme` - Item não está em conformidade
- `nao_aplicavel` - Item não se aplica à situação
- `pendente` - Item aguardando verificação

## Fluxo Completo de Uso

### Para Gestor:
1. Fazer login → `/auth/login`
2. Criar uma obra → `/obras`
3. Criar template de checklist → `/obras/{id}/checklists`
4. Adicionar engenheiros à obra → `/obras/{id}/engineers`

### Para Engenheiro:
1. Fazer login → `/auth/login`
2. Ver obras atribuídas → `/mobile/obras`
3. Fazer check-in → `/mobile/checkin`
4. Ver checklists disponíveis → `/mobile/obras/{id}/checklists`
5. Upload de fotos → `/mobile/upload-photo`
6. Submeter checklist → `/mobile/checklists/submit`
7. Ver histórico → `/mobile/checklists/submissions`

## Testando com cURL

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sst.com","password":"admin123"}'
```

### Criar obra
```bash
curl -X POST "http://localhost:8000/api/v1/obras" \
  -H "Authorization: Bearer {seu_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Obra Teste",
    "descricao": "Descrição da obra",
    "endereco": "Rua Teste, 123"
  }'
```

## 8. Dashboard (Gestor)

### Obter estatísticas gerais
```bash
GET /dashboard/stats
Authorization: Bearer {token_gestor}

# Resposta:
{
  "total_obras_ativas": 12,
  "total_engenheiros": 24,
  "checkins_hoje": 8,
  "checklists_hoje": 18
}
```

### Obter atividades recentes
```bash
GET /dashboard/atividades-recentes?limit=10
Authorization: Bearer {token_gestor}

# Resposta:
[
  {
    "tipo": "checklist",
    "titulo": "Checklist Completo",
    "descricao": "Obra Central - João Silva",
    "timestamp": "2025-11-30T14:30:00Z",
    "obra_nome": "Obra Central",
    "usuario_nome": "João Silva"
  },
  {
    "tipo": "checkin",
    "titulo": "Check-in Realizado",
    "descricao": "Obra Norte - Maria Santos",
    "timestamp": "2025-11-30T13:15:00Z",
    "obra_nome": "Obra Norte",
    "usuario_nome": "Maria Santos"
  }
]
```

### Obter estatísticas de conformidade
```bash
GET /dashboard/conformidade?days=30
Authorization: Bearer {token_gestor}

# Resposta:
{
  "conforme": 150,
  "nao_conforme": 15,
  "pendente": 25,
  "nao_aplicavel": 10,
  "total": 200,
  "percentual_conforme": 75.0,
  "percentual_nao_conforme": 7.5,
  "percentual_pendente": 12.5
}
```

### Obter estatísticas de uma obra
```bash
GET /dashboard/obras/1/stats
Authorization: Bearer {token_gestor}

# Resposta:
{
  "obra_id": 1,
  "obra_nome": "Construção Edifício Central",
  "total_checkins": 45,
  "total_checklists": 30,
  "conformidade_rate": 92.5,
  "ultimo_checkin": "2025-11-30T14:30:00Z",
  "ultimo_checkin_engenheiro": "João Silva"
}
```

### Exemplo de uso no Frontend (React/Next.js)
```typescript
// hooks/useDashboard.ts
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

export const useDashboard = () => {
  const token = localStorage.getItem('access_token');
  
  const api = axios.create({
    baseURL: API_URL,
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

  const fetchStats = async () => {
    const response = await api.get('/dashboard/stats');
    return response.data;
  };

  const fetchRecentActivities = async (limit = 10) => {
    const response = await api.get(`/dashboard/atividades-recentes?limit=${limit}`);
    return response.data;
  };

  const fetchConformidade = async (days = 30) => {
    const response = await api.get(`/dashboard/conformidade?days=${days}`);
    return response.data;
  };

  return { fetchStats, fetchRecentActivities, fetchConformidade };
};
```

### Exemplo de componente Dashboard
```typescript
// components/Dashboard.tsx
import { useEffect, useState } from 'react';
import { useDashboard } from '@/hooks/useDashboard';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [activities, setActivities] = useState([]);
  const [conformidade, setConformidade] = useState(null);
  const { fetchStats, fetchRecentActivities, fetchConformidade } = useDashboard();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [statsData, activitiesData, conformidadeData] = await Promise.all([
        fetchStats(),
        fetchRecentActivities(10),
        fetchConformidade(30)
      ]);
      
      setStats(statsData);
      setActivities(activitiesData);
      setConformidade(conformidadeData);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    }
  };

  return (
    <div className="dashboard">
      {/* Cards de estatísticas */}
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Obras Ativas</h3>
          <p>{stats?.total_obras_ativas}</p>
        </div>
        <div className="stat-card">
          <h3>Engenheiros</h3>
          <p>{stats?.total_engenheiros}</p>
        </div>
        <div className="stat-card">
          <h3>Checklists Hoje</h3>
          <p>{stats?.checklists_hoje}</p>
        </div>
        <div className="stat-card">
          <h3>Check-ins Hoje</h3>
          <p>{stats?.checkins_hoje}</p>
        </div>
      </div>

      {/* Atividades recentes */}
      <div className="activities">
        <h2>Atividades Recentes</h2>
        {activities.map((activity) => (
          <div key={activity.timestamp} className="activity-item">
            <span>{activity.titulo}</span>
            <span>{activity.descricao}</span>
          </div>
        ))}
      </div>

      {/* Status de conformidade */}
      <div className="conformidade">
        <h2>Status de Conformidade</h2>
        <div>Conforme: {conformidade?.percentual_conforme}%</div>
        <div>Não Conforme: {conformidade?.percentual_nao_conforme}%</div>
        <div>Pendente: {conformidade?.percentual_pendente}%</div>
      </div>
    </div>
  );
}
```

## Documentação Interativa

Acesse http://localhost:8000/docs para testar todos os endpoints através da interface Swagger UI.
