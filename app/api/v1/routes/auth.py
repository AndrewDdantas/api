from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.api.v1.deps import get_current_active_user
from app.schemas.schemas import UserCreate, UserResponse, UserUpdate, LoginRequest, Token
from app.crud import crud_user
from app.services.auth_service import auth_service
from app.models.models import User

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login de usuário (gestor ou engenheiro)"""
    return auth_service.login(db, credentials)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    """Registrar novo usuário"""
    user = crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    user = crud_user.create(db, obj_in=user_in)
    return user


@router.get("/me", response_model=UserResponse)
def read_users_me(
    current_user: User = Depends(get_current_active_user)
):
    """Obter informações do usuário atual"""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_user_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Atualizar informações do usuário atual"""
    user = crud_user.update(db, db_obj=current_user, obj_in=user_in)
    return user
