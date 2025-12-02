from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.models import Obra, ObraEngineer, User
from app.schemas.schemas import ObraCreate, ObraUpdate


class CRUDObra(CRUDBase[Obra, ObraCreate, ObraUpdate]):
    def create_with_gestor(
        self, db: Session, *, obj_in: ObraCreate, gestor_id: int
    ) -> Obra:
        db_obj = Obra(
            **obj_in.dict(),
            gestor_id=gestor_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_gestor(
        self, db: Session, *, gestor_id: int, skip: int = 0, limit: int = 100
    ) -> List[Obra]:
        return (
            db.query(Obra)
            .filter(Obra.gestor_id == gestor_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_engineer(
        self, db: Session, *, engineer_id: int, skip: int = 0, limit: int = 100
    ) -> List[Obra]:
        return (
            db.query(Obra)
            .join(ObraEngineer)
            .filter(ObraEngineer.engineer_id == engineer_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def add_engineer(
        self, db: Session, *, obra_id: int, engineer_id: int
    ) -> ObraEngineer:
        # Verificar se já existe
        existing = (
            db.query(ObraEngineer)
            .filter(
                ObraEngineer.obra_id == obra_id,
                ObraEngineer.engineer_id == engineer_id
            )
            .first()
        )
        if existing:
            return existing
        
        db_obj = ObraEngineer(obra_id=obra_id, engineer_id=engineer_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove_engineer(
        self, db: Session, *, obra_id: int, engineer_id: int
    ) -> bool:
        obj = (
            db.query(ObraEngineer)
            .filter(
                ObraEngineer.obra_id == obra_id,
                ObraEngineer.engineer_id == engineer_id
            )
            .first()
        )
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False

    def get_engineers(self, db: Session, *, obra_id: int) -> List[User]:
        return (
            db.query(User)
            .join(ObraEngineer)
            .filter(ObraEngineer.obra_id == obra_id)
            .all()
        )


crud_obra = CRUDObra(Obra)
