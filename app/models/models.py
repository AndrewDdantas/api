from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum


class UserRole(enum.Enum):
    """Papéis de usuário"""
    GESTOR = "gestor"
    ENGENHEIRO = "engenheiro"


class ChecklistStatus(enum.Enum):
    """Status do checklist"""
    PENDENTE = "pendente"
    CONFORME = "conforme"
    NAO_CONFORME = "nao_conforme"
    NAO_APLICAVEL = "nao_aplicavel"


class User(Base):
    """Modelo de usuário (Gestor ou Engenheiro)"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    obras_criadas = relationship("Obra", back_populates="gestor", foreign_keys="Obra.gestor_id")
    obras_atribuidas = relationship("ObraEngineer", back_populates="engineer")
    checkins = relationship("CheckIn", back_populates="engineer")
    checklists_enviados = relationship("ChecklistSubmission", back_populates="engineer")


class Obra(Base):
    """Modelo de obra"""
    __tablename__ = "obras"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=True)
    endereco = Column(String(500), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    gestor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    gestor = relationship("User", back_populates="obras_criadas", foreign_keys=[gestor_id])
    engineers = relationship("ObraEngineer", back_populates="obra")
    checklist_templates = relationship("ChecklistTemplate", back_populates="obra")
    checkins = relationship("CheckIn", back_populates="obra")


class ObraEngineer(Base):
    """Tabela de associação entre obras e engenheiros"""
    __tablename__ = "obra_engineers"
    
    id = Column(Integer, primary_key=True, index=True)
    obra_id = Column(Integer, ForeignKey("obras.id"), nullable=False)
    engineer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    obra = relationship("Obra", back_populates="engineers")
    engineer = relationship("User", back_populates="obras_atribuidas")


class ChecklistTemplate(Base):
    """Template de checklist para uma obra"""
    __tablename__ = "checklist_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    obra_id = Column(Integer, ForeignKey("obras.id"), nullable=False)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    obra = relationship("Obra", back_populates="checklist_templates")
    items = relationship("ChecklistTemplateItem", back_populates="template", cascade="all, delete-orphan")
    submissions = relationship("ChecklistSubmission", back_populates="template")


class ChecklistTemplateItem(Base):
    """Item do template de checklist"""
    __tablename__ = "checklist_template_items"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("checklist_templates.id"), nullable=False)
    titulo = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=True)
    ordem = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    template = relationship("ChecklistTemplate", back_populates="items")
    responses = relationship("ChecklistItemResponse", back_populates="template_item")


class CheckIn(Base):
    """Check-in do engenheiro na obra"""
    __tablename__ = "checkins"
    
    id = Column(Integer, primary_key=True, index=True)
    engineer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    obra_id = Column(Integer, ForeignKey("obras.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    checkin_time = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    engineer = relationship("User", back_populates="checkins")
    obra = relationship("Obra", back_populates="checkins")


class ChecklistSubmission(Base):
    """Submissão de checklist pelo engenheiro"""
    __tablename__ = "checklist_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("checklist_templates.id"), nullable=False)
    engineer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    template = relationship("ChecklistTemplate", back_populates="submissions")
    engineer = relationship("User", back_populates="checklists_enviados")
    responses = relationship("ChecklistItemResponse", back_populates="submission", cascade="all, delete-orphan")


class ChecklistItemResponse(Base):
    """Resposta de cada item do checklist"""
    __tablename__ = "checklist_item_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("checklist_submissions.id"), nullable=False)
    template_item_id = Column(Integer, ForeignKey("checklist_template_items.id"), nullable=False)
    status = Column(SQLEnum(ChecklistStatus), nullable=False)
    observacao = Column(Text, nullable=True)
    foto_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    submission = relationship("ChecklistSubmission", back_populates="responses")
    template_item = relationship("ChecklistTemplateItem", back_populates="responses")
