from datetime import timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.crud import crud_user
from app.core.security import create_access_token, verify_password
from app.schemas.schemas import Token, LoginRequest


class AuthService:
    def authenticate_user(
        self, 
        db: Session, 
        email: str, 
        password: str
    ) -> Optional[dict]:
        """Autentica um usuário e retorna o token"""
        user = crud_user.authenticate(db, email=email, password=password)
        if not user:
            return None
        if not crud_user.is_active(user):
            return None
        
        access_token = create_access_token(data={"sub": str(user.id)})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }

    def login(self, db: Session, credentials: LoginRequest) -> Token:
        """Realiza login e retorna token JWT"""
        result = self.authenticate_user(
            db, 
            email=credentials.email, 
            password=credentials.password
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return Token(
            access_token=result["access_token"],
            token_type=result["token_type"]
        )


auth_service = AuthService()
