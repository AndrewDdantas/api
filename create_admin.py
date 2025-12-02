"""
Script para criar um usuário gestor inicial
"""
import sys
from sqlalchemy.orm import Session
from app.database.database import SessionLocal, engine
from app.models.models import Base, User, UserRole
from app.core.security import get_password_hash

# Criar tabelas se não existirem
Base.metadata.create_all(bind=engine)

def create_admin():
    db: Session = SessionLocal()
    
    try:
        # Verificar se já existe um gestor
        existing_admin = db.query(User).filter(User.email == "admin@sst.com").first()
        if existing_admin:
            print("❌ Gestor admin@sst.com já existe!")
            return
        
        # Criar gestor
        admin = User(
            email="admin@sst.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Administrador SST",
            role=UserRole.GESTOR,
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("✅ Gestor criado com sucesso!")
        print(f"   Email: admin@sst.com")
        print(f"   Senha: admin123")
        print(f"   ID: {admin.id}")
        
        # Criar um engenheiro de exemplo
        engineer = User(
            email="engenheiro@sst.com",
            hashed_password=get_password_hash("eng123"),
            full_name="Engenheiro Teste",
            role=UserRole.ENGENHEIRO,
            is_active=True
        )
        
        db.add(engineer)
        db.commit()
        db.refresh(engineer)
        
        print("✅ Engenheiro criado com sucesso!")
        print(f"   Email: engenheiro@sst.com")
        print(f"   Senha: eng123")
        print(f"   ID: {engineer.id}")
        
    except Exception as e:
        print(f"❌ Erro ao criar usuários: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Criando usuários iniciais...")
    create_admin()
