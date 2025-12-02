from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.models import ChecklistTemplate, ChecklistTemplateItem
from app.schemas.schemas import ChecklistTemplateCreate, ChecklistTemplateUpdate


class CRUDChecklistTemplate(CRUDBase[ChecklistTemplate, ChecklistTemplateCreate, ChecklistTemplateUpdate]):
    def create_with_items(
        self, db: Session, *, obj_in: ChecklistTemplateCreate, obra_id: int
    ) -> ChecklistTemplate:
        # Criar o template
        db_obj = ChecklistTemplate(
            nome=obj_in.nome,
            descricao=obj_in.descricao,
            obra_id=obra_id,
        )
        db.add(db_obj)
        db.flush()  # Para obter o ID antes do commit
        
        # Criar os items
        for item_data in obj_in.items:
            db_item = ChecklistTemplateItem(
                **item_data.dict(),
                template_id=db_obj.id
            )
            db.add(db_item)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_obra(
        self, db: Session, *, obra_id: int, skip: int = 0, limit: int = 100
    ) -> List[ChecklistTemplate]:
        return (
            db.query(ChecklistTemplate)
            .filter(ChecklistTemplate.obra_id == obra_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def add_item(
        self, db: Session, *, template_id: int, titulo: str, descricao: Optional[str] = None, ordem: int = 0
    ) -> ChecklistTemplateItem:
        db_obj = ChecklistTemplateItem(
            template_id=template_id,
            titulo=titulo,
            descricao=descricao,
            ordem=ordem
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove_item(self, db: Session, *, item_id: int) -> bool:
        obj = db.query(ChecklistTemplateItem).filter(ChecklistTemplateItem.id == item_id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False


crud_checklist_template = CRUDChecklistTemplate(ChecklistTemplate)
