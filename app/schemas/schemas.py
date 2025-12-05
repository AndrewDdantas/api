from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# Enums
class UserRole(str, Enum):
    GESTOR = "gestor"
    ENGENHEIRO = "engenheiro"


class ChecklistStatus(str, Enum):
    PENDENTE = "pendente"
    CONFORME = "conforme"
    NAO_CONFORME = "nao_conforme"
    NAO_APLICAVEL = "nao_aplicavel"


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Obra Schemas
class ObraBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    endereco: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ObraCreate(ObraBase):
    pass


class ObraUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    endereco: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_active: Optional[bool] = None


class ObraResponse(ObraBase):
    id: int
    is_active: bool
    gestor_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Engineer Assignment
class ObraEngineerCreate(BaseModel):
    engineer_id: int


class ObraEngineerResponse(BaseModel):
    id: int
    obra_id: int
    engineer_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Checklist Template Schemas
class ChecklistTemplateItemBase(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    ordem: int = 0


class ChecklistTemplateItemCreate(ChecklistTemplateItemBase):
    pass


class ChecklistTemplateItemResponse(ChecklistTemplateItemBase):
    id: int
    template_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChecklistTemplateBase(BaseModel):
    nome: str
    descricao: Optional[str] = None


class ChecklistTemplateCreate(ChecklistTemplateBase):
    items: List[ChecklistTemplateItemCreate] = []


class ChecklistTemplateUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    is_active: Optional[bool] = None


class ChecklistTemplateResponse(ChecklistTemplateBase):
    id: int
    obra_id: int
    is_active: bool
    created_at: datetime
    items: List[ChecklistTemplateItemResponse] = []
    
    class Config:
        from_attributes = True


# CheckIn Schemas
class CheckInCreate(BaseModel):
    obra_id: int
    latitude: float
    longitude: float


class CheckInResponse(BaseModel):
    id: int
    engineer_id: int
    obra_id: int
    latitude: float
    longitude: float
    checkin_time: datetime
    
    class Config:
        from_attributes = True


# Checklist Submission Schemas
class ChecklistItemResponseCreate(BaseModel):
    template_item_id: int
    status: ChecklistStatus
    observacao: Optional[str] = None
    foto_url: Optional[str] = None


class ChecklistItemResponseResponse(ChecklistItemResponseCreate):
    id: int
    submission_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChecklistSubmissionCreate(BaseModel):
    template_id: int
    responses: List[ChecklistItemResponseCreate]


class ChecklistSubmissionResponse(BaseModel):
    id: int
    template_id: int
    engineer_id: int
    submitted_at: datetime
    responses: List[ChecklistItemResponseResponse] = []
    
    class Config:
        from_attributes = True


# Dashboard/Report Schemas
class ObraDetailResponse(ObraResponse):
    engineers: List[UserResponse] = []
    checklist_templates: List[ChecklistTemplateResponse] = []
    
    @staticmethod
    def model_validate(obj):
        """Customiza a validação para lidar com relacionamentos ORM"""
        # Extrair usuários dos ObraEngineer
        engineers_list = []
        if hasattr(obj, 'engineers'):
            for oe in obj.engineers:
                if hasattr(oe, 'engineer'):
                    engineers_list.append(oe.engineer)
        
        # Criar dict com dados corretos
        data = {
            'id': obj.id,
            'nome': obj.nome,
            'descricao': obj.descricao,
            'endereco': obj.endereco,
            'latitude': obj.latitude,
            'longitude': obj.longitude,
            'is_active': obj.is_active,
            'gestor_id': obj.gestor_id,
            'created_at': obj.created_at,
            'engineers': engineers_list,
            'checklist_templates': obj.checklist_templates if hasattr(obj, 'checklist_templates') else []
        }
        return super(ObraDetailResponse, ObraDetailResponse).model_validate(data)
    
    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    """Estatísticas gerais do dashboard"""
    total_obras_ativas: int
    total_engenheiros: int
    checkins_hoje: int
    checklists_hoje: int


class RecentActivity(BaseModel):
    """Atividade recente (check-in ou checklist)"""
    tipo: str  # "checkin" ou "checklist"
    titulo: str
    descricao: str
    timestamp: datetime
    obra_nome: str
    usuario_nome: str


class ConformidadeStats(BaseModel):
    """Estatísticas de conformidade dos checklists"""
    conforme: int
    nao_conforme: int
    pendente: int
    nao_aplicavel: int
    total: int
    percentual_conforme: float
    percentual_nao_conforme: float
    percentual_pendente: float
