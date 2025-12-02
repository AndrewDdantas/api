from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.api.v1.deps import get_current_gestor
from app.schemas.schemas import UserResponse
from app.crud import crud_user
from app.models.models import User

router = APIRouter()


@router.get("/engineers", response_model=List[UserResponse])
def list_engineers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_gestor)
):
    """Listar todos os engenheiros disponíveis"""
    engineers = crud_user.get_engineers(db, skip=skip, limit=limit)
    return engineers


@router.get("/engineers/{engineer_id}", response_model=UserResponse)
def get_engineer(
    engineer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_gestor)
):
    """Obter informações de um engenheiro"""
    engineer = crud_user.get(db, id=engineer_id)
    if not engineer:
        raise HTTPException(status_code=404, detail="Engineer not found")
    return engineer
