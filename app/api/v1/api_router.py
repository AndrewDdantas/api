from fastapi import APIRouter
from app.api.v1.routes import auth, obras, mobile, users, dashboard

api_router = APIRouter()

# Rotas de autenticação (públicas)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Rotas para gestores (web)
api_router.include_router(obras.router, prefix="/obras", tags=["obras"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

# Rotas para engenheiros (mobile)
api_router.include_router(mobile.router, prefix="/mobile", tags=["mobile"])
