from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.api.v1.deps import get_current_engineer
from app.schemas.schemas import (
    ObraResponse,
    CheckInCreate,
    CheckInResponse,
    ChecklistTemplateResponse,
    ChecklistSubmissionCreate,
    ChecklistSubmissionResponse
)
from app.crud import crud_obra, crud_checkin, crud_checklist_template, crud_checklist_submission
from app.models.models import User
from app.services.file_service import file_service

router = APIRouter()


@router.get("/obras", response_model=List[ObraResponse])
def list_my_obras(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_engineer)
):
    """Listar obras atribuídas ao engenheiro"""
    obras = crud_obra.get_by_engineer(db, engineer_id=current_user.id, skip=skip, limit=limit)
    return obras


@router.get("/obras/{obra_id}", response_model=ObraResponse)
def get_obra(
    obra_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_engineer)
):
    """Obter detalhes de uma obra"""
    # Verificar se o engenheiro tem acesso a essa obra
    obras = crud_obra.get_by_engineer(db, engineer_id=current_user.id)
    obra_ids = [obra.id for obra in obras]
    
    if obra_id not in obra_ids:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    obra = crud_obra.get(db, id=obra_id)
    if not obra:
        raise HTTPException(status_code=404, detail="Obra not found")
    
    return obra


@router.post("/checkin", response_model=CheckInResponse, status_code=status.HTTP_201_CREATED)
def create_checkin(
    checkin_in: CheckInCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_engineer)
):
    """Fazer check-in na obra"""
    # Verificar se o engenheiro tem acesso a essa obra
    obras = crud_obra.get_by_engineer(db, engineer_id=current_user.id)
    obra_ids = [obra.id for obra in obras]
    
    if checkin_in.obra_id not in obra_ids:
        raise HTTPException(status_code=403, detail="Not authorized for this obra")
    
    checkin = crud_checkin.create_checkin(db, obj_in=checkin_in, engineer_id=current_user.id)
    return checkin


@router.get("/checkins", response_model=List[CheckInResponse])
def list_my_checkins(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_engineer)
):
    """Listar meus check-ins"""
    checkins = crud_checkin.get_by_engineer(db, engineer_id=current_user.id, skip=skip, limit=limit)
    return checkins


@router.get("/obras/{obra_id}/checklists", response_model=List[ChecklistTemplateResponse])
def list_obra_checklists(
    obra_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_engineer)
):
    """Listar checklists disponíveis para a obra"""
    # Verificar se o engenheiro tem acesso a essa obra
    obras = crud_obra.get_by_engineer(db, engineer_id=current_user.id)
    obra_ids = [obra.id for obra in obras]
    
    if obra_id not in obra_ids:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    templates = crud_checklist_template.get_by_obra(db, obra_id=obra_id, skip=skip, limit=limit)
    return templates


@router.post("/checklists/submit", response_model=ChecklistSubmissionResponse, status_code=status.HTTP_201_CREATED)
def submit_checklist(
    submission_in: ChecklistSubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_engineer)
):
    """Submeter um checklist preenchido"""
    # Verificar se o template existe
    template = crud_checklist_template.get(db, id=submission_in.template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Checklist template not found")
    
    # Verificar se o engenheiro tem acesso à obra desse template
    obras = crud_obra.get_by_engineer(db, engineer_id=current_user.id)
    obra_ids = [obra.id for obra in obras]
    
    if template.obra_id not in obra_ids:
        raise HTTPException(status_code=403, detail="Not authorized for this checklist")
    
    submission = crud_checklist_submission.create_submission(
        db, obj_in=submission_in, engineer_id=current_user.id
    )
    return submission


@router.get("/checklists/submissions", response_model=List[ChecklistSubmissionResponse])
def list_my_submissions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_engineer)
):
    """Listar minhas submissões de checklist"""
    submissions = crud_checklist_submission.get_by_engineer(
        db, engineer_id=current_user.id, skip=skip, limit=limit
    )
    return submissions


@router.post("/upload-photo")
async def upload_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_engineer)
):
    """Upload de foto para o checklist"""
    try:
        filepath = await file_service.save_checklist_photo(file)
        file_url = file_service.get_file_url(filepath)
        return {"filename": filepath, "url": file_url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
