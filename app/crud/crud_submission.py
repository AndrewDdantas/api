from typing import List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.models import ChecklistSubmission, ChecklistItemResponse
from app.schemas.schemas import ChecklistSubmissionCreate, ChecklistSubmissionResponse


class CRUDChecklistSubmission(CRUDBase[ChecklistSubmission, ChecklistSubmissionCreate, ChecklistSubmissionResponse]):
    def create_submission(
        self, db: Session, *, obj_in: ChecklistSubmissionCreate, engineer_id: int
    ) -> ChecklistSubmission:
        # Criar a submissão
        db_obj = ChecklistSubmission(
            template_id=obj_in.template_id,
            engineer_id=engineer_id,
        )
        db.add(db_obj)
        db.flush()  # Para obter o ID antes do commit
        
        # Criar as respostas dos items
        for response_data in obj_in.responses:
            db_response = ChecklistItemResponse(
                **response_data.dict(),
                submission_id=db_obj.id
            )
            db.add(db_response)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_engineer(
        self, db: Session, *, engineer_id: int, skip: int = 0, limit: int = 100
    ) -> List[ChecklistSubmission]:
        return (
            db.query(ChecklistSubmission)
            .filter(ChecklistSubmission.engineer_id == engineer_id)
            .order_by(ChecklistSubmission.submitted_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_template(
        self, db: Session, *, template_id: int, skip: int = 0, limit: int = 100
    ) -> List[ChecklistSubmission]:
        return (
            db.query(ChecklistSubmission)
            .filter(ChecklistSubmission.template_id == template_id)
            .order_by(ChecklistSubmission.submitted_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_obra(
        self, db: Session, *, obra_id: int, skip: int = 0, limit: int = 100
    ) -> List[ChecklistSubmission]:
        from app.models.models import ChecklistTemplate
        return (
            db.query(ChecklistSubmission)
            .join(ChecklistTemplate)
            .filter(ChecklistTemplate.obra_id == obra_id)
            .order_by(ChecklistSubmission.submitted_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


crud_checklist_submission = CRUDChecklistSubmission(ChecklistSubmission)
