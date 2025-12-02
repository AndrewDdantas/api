from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.api.v1.deps import get_current_gestor
from app.schemas.schemas import (
    ObraCreate, 
    ObraResponse, 
    ObraUpdate, 
    ObraDetailResponse,
    ObraEngineerCreate,
    ChecklistTemplateCreate,
    ChecklistTemplateResponse,
    ChecklistSubmissionResponse,
    UserResponse,
    CheckInResponse
)
from app.crud import crud_obra, crud_checklist_template, crud_user, crud_checkin, crud_checklist_submission
from app.models.models import User

router = APIRouter()


@router.post("/", response_model=ObraResponse, status_code=status.HTTP_201_CREATED)
def create_obra(
    obra_in: ObraCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_gestor)
):
    """Criar nova obra (apenas gestores)"""
    obra = crud_obra.create_with_gestor(db, obj_in=obra_in, gestor_id=current_user.id)
    return obra


@router.get("/", response_model=List[ObraResponse])
def list_obras(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_gestor)
):
    """Listar obras do gestor"""
    obras = crud_obra.get_by_gestor(db, gestor_id=current_user.id, skip=skip, limit=limit)
    return obras


@router.get("/{obra_id}", response_model=ObraDetailResponse)
def get_obra(
    obra_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_gestor)
):
    """Obter detalhes de uma obra"""
    obra = crud_obra.get(db, id=obra_id)
    if not obra:
        raise HTTPException(status_code=404, detail="Obra not found")
    if obra.gestor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return obra


@router.put("/{obra_id}", response_model=ObraResponse)
def update_obra(
    obra_id: int,
    obra_in: ObraUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_gestor)
):
    """Atualizar obra"""
    obra = crud_obra.get(db, id=obra_id)
    if not obra:
        raise HTTPException(status_code=404, detail="Obra not found")
    if obra.gestor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    obra = crud_obra.update(db, db_obj=obra, obj_in=obra_in)
    return obra


@router.delete("/{obra_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_obra(
    obra_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_gestor)
):
    """Deletar obra"""
    obra = crud_obra.get(db, id=obra_id)
    if not obra:
        raise HTTPException(status_code=404, detail="Obra not found")
    if obra.gestor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    crud_obra.remove(db, id=obra_id)
    return None


# Gerenciar engenheiros na obra
@router.post("/{obra_id}/engineers", status_code=status.HTTP_201_CREATED)
def add_engineer_to_obra(
    obra_id: int,
    engineer_data: ObraEngineerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_gestor)
):
    """Adicionar engenheiro à obra"""
    obra = crud_obra.get(db, id=obra_id)
    if not obra:
        raise HTTPException(status_code=404, detail="Obra not found")
    if obra.gestor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Verificar se o engenheiro existe
    engineer = crud_user.get(db, id=engineer_data.engineer_id)
    if not engineer:
        raise HTTPException(status_code=404, detail="Engineer not found")
    
    result = crud_obra.add_engineer(db, obra_id=obra_id, engineer_id=engineer_data.engineer_id)
    return {"message": "Engineer added successfully", "id": result.id}


@router.delete("/{obra_id}/engineers/{engineer_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_engineer_from_obra(
    obra_id: int,
    engineer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_gestor)
):
    """Remover engenheiro da obra"""
    obra = crud_obra.get(db, id=obra_id)
    if not obra:
        raise HTTPException(status_code=404, detail="Obra not found")
    if obra.gestor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    success = crud_obra.remove_engineer(db, obra_id=obra_id, engineer_id=engineer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Engineer not assigned to this obra")
    return None


@router.get("/{obra_id}/engineers", response_model=List[UserResponse])
def list_obra_engineers(
    obra_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_gestor)
):
    """Listar engenheiros da obra"""
    obra = crud_obra.get(db, id=obra_id)
    if not obra:
        raise HTTPException(status_code=404, detail="Obra not found")
    if obra.gestor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    engineers = crud_obra.get_engineers(db, obra_id=obra_id)
    return engineers


# Gerenciar checklists da obra
@router.post("/{obra_id}/checklists", response_model=ChecklistTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_checklist_template(
    obra_id: int,
    checklist_in: ChecklistTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_gestor)
):
    """Criar template de checklist para a obra"""
    obra = crud_obra.get(db, id=obra_id)
    if not obra:
        raise HTTPException(status_code=404, detail="Obra not found")
    if obra.gestor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    template = crud_checklist_template.create_with_items(db, obj_in=checklist_in, obra_id=obra_id)
    return template


@router.get("/{obra_id}/checklists", response_model=List[ChecklistTemplateResponse])
def list_checklist_templates(
    obra_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_gestor)
):
    """Listar templates de checklist da obra"""
    obra = crud_obra.get(db, id=obra_id)
    if not obra:
        raise HTTPException(status_code=404, detail="Obra not found")
    if obra.gestor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    templates = crud_checklist_template.get_by_obra(db, obra_id=obra_id, skip=skip, limit=limit)
    return templates


@router.get("/{obra_id}/checkins", response_model=List[CheckInResponse])
def list_obra_checkins(
    obra_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_gestor)
):
    """Listar todos os check-ins de uma obra (para o gestor)"""
    obra = crud_obra.get(db, id=obra_id)
    if not obra:
        raise HTTPException(status_code=404, detail="Obra not found")
    if obra.gestor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    checkins = crud_checkin.get_by_obra(db, obra_id=obra_id, skip=skip, limit=limit)
    return checkins


@router.get("/{obra_id}/checklist-submissions", response_model=List[ChecklistSubmissionResponse])
def list_obra_submissions(
    obra_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_gestor)
):
    """Listar todas as submissões de checklist de uma obra (para o gestor)"""
    obra = crud_obra.get(db, id=obra_id)
    if not obra:
        raise HTTPException(status_code=404, detail="Obra not found")
    if obra.gestor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    submissions = crud_checklist_submission.get_by_obra(db, obra_id=obra_id, skip=skip, limit=limit)
    return submissions
