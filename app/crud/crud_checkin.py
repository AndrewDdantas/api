from typing import List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.models import CheckIn
from app.schemas.schemas import CheckInCreate, CheckInResponse


class CRUDCheckIn(CRUDBase[CheckIn, CheckInCreate, CheckInResponse]):
    def create_checkin(
        self, db: Session, *, obj_in: CheckInCreate, engineer_id: int
    ) -> CheckIn:
        db_obj = CheckIn(
            **obj_in.dict(),
            engineer_id=engineer_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_engineer(
        self, db: Session, *, engineer_id: int, skip: int = 0, limit: int = 100
    ) -> List[CheckIn]:
        return (
            db.query(CheckIn)
            .filter(CheckIn.engineer_id == engineer_id)
            .order_by(CheckIn.checkin_time.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_obra(
        self, db: Session, *, obra_id: int, skip: int = 0, limit: int = 100
    ) -> List[CheckIn]:
        return (
            db.query(CheckIn)
            .filter(CheckIn.obra_id == obra_id)
            .order_by(CheckIn.checkin_time.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


crud_checkin = CRUDCheckIn(CheckIn)
