from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta

from app.database.database import get_db
from app.api.v1.deps import get_current_gestor
from app.schemas.schemas import DashboardStats, RecentActivity, ConformidadeStats
from app.models.models import User, Obra, CheckIn, ChecklistSubmission, ChecklistItemResponse, ChecklistStatus

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_gestor)
):
    """Obter estatísticas gerais do dashboard"""
    
    # Total de obras ativas do gestor
    total_obras = db.query(Obra).filter(
        Obra.gestor_id == current_user.id,
        Obra.is_active == True
    ).count()
    
    # Total de engenheiros
    from app.models.models import UserRole
    total_engenheiros = db.query(User).filter(
        User.role == UserRole.ENGENHEIRO,
        User.is_active == True
    ).count()
    
    # Check-ins hoje
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    checkins_hoje = db.query(CheckIn).join(Obra).filter(
        Obra.gestor_id == current_user.id,
        CheckIn.checkin_time >= today_start
    ).count()
    
    # Checklists submetidos hoje
    checklists_hoje = db.query(ChecklistSubmission).join(
        ChecklistSubmission.template
    ).join(Obra).filter(
        Obra.gestor_id == current_user.id,
        ChecklistSubmission.submitted_at >= today_start
    ).count()
    
    return {
        "total_obras_ativas": total_obras,
        "total_engenheiros": total_engenheiros,
        "checkins_hoje": checkins_hoje,
        "checklists_hoje": checklists_hoje
    }


@router.get("/atividades-recentes", response_model=List[RecentActivity])
def get_recent_activities(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_gestor)
):
    """Obter atividades recentes (check-ins e checklists)"""
    
    activities = []
    
    # Buscar últimos check-ins
    recent_checkins = db.query(CheckIn).join(Obra).join(User).filter(
        Obra.gestor_id == current_user.id
    ).order_by(CheckIn.checkin_time.desc()).limit(limit).all()
    
    for checkin in recent_checkins:
        activities.append({
            "tipo": "checkin",
            "titulo": "Check-in Realizado",
            "descricao": f"{checkin.obra.nome} - {checkin.engineer.full_name}",
            "timestamp": checkin.checkin_time,
            "obra_nome": checkin.obra.nome,
            "usuario_nome": checkin.engineer.full_name
        })
    
    # Buscar últimas submissões de checklist
    recent_submissions = db.query(ChecklistSubmission).join(
        ChecklistSubmission.template
    ).join(Obra).join(User).filter(
        Obra.gestor_id == current_user.id
    ).order_by(ChecklistSubmission.submitted_at.desc()).limit(limit).all()
    
    for submission in recent_submissions:
        activities.append({
            "tipo": "checklist",
            "titulo": "Checklist Completo",
            "descricao": f"{submission.template.obra.nome} - {submission.engineer.full_name}",
            "timestamp": submission.submitted_at,
            "obra_nome": submission.template.obra.nome,
            "usuario_nome": submission.engineer.full_name
        })
    
    # Ordenar por timestamp e limitar
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    return activities[:limit]


@router.get("/conformidade", response_model=ConformidadeStats)
def get_conformidade_stats(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_gestor)
):
    """Obter estatísticas de conformidade dos checklists"""
    
    # Data limite (últimos X dias)
    date_limit = datetime.now() - timedelta(days=days)
    
    # Buscar todas as respostas dos checklists do gestor
    responses = db.query(
        ChecklistItemResponse.status,
        func.count(ChecklistItemResponse.id).label('count')
    ).join(ChecklistSubmission).join(
        ChecklistSubmission.template
    ).join(Obra).filter(
        Obra.gestor_id == current_user.id,
        ChecklistSubmission.submitted_at >= date_limit
    ).group_by(ChecklistItemResponse.status).all()
    
    # Processar contagens
    stats = {
        "conforme": 0,
        "nao_conforme": 0,
        "pendente": 0,
        "nao_aplicavel": 0,
        "total": 0
    }
    
    for response in responses:
        status_key = response.status.value if hasattr(response.status, 'value') else str(response.status)
        if status_key == "conforme":
            stats["conforme"] = response.count
        elif status_key == "nao_conforme":
            stats["nao_conforme"] = response.count
        elif status_key == "pendente":
            stats["pendente"] = response.count
        elif status_key == "nao_aplicavel":
            stats["nao_aplicavel"] = response.count
        stats["total"] += response.count
    
    # Calcular percentuais
    if stats["total"] > 0:
        stats["percentual_conforme"] = round((stats["conforme"] / stats["total"]) * 100, 1)
        stats["percentual_nao_conforme"] = round((stats["nao_conforme"] / stats["total"]) * 100, 1)
        stats["percentual_pendente"] = round((stats["pendente"] / stats["total"]) * 100, 1)
    else:
        stats["percentual_conforme"] = 0.0
        stats["percentual_nao_conforme"] = 0.0
        stats["percentual_pendente"] = 0.0
    
    return stats


@router.get("/obras/{obra_id}/stats")
def get_obra_stats(
    obra_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_gestor)
):
    """Obter estatísticas de uma obra específica"""
    
    from app.crud import crud_obra
    
    obra = crud_obra.get(db, id=obra_id)
    if not obra or obra.gestor_id != current_user.id:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Obra not found")
    
    # Total de check-ins
    total_checkins = db.query(CheckIn).filter(CheckIn.obra_id == obra_id).count()
    
    # Total de checklists submetidos
    total_checklists = db.query(ChecklistSubmission).join(
        ChecklistSubmission.template
    ).filter(ChecklistSubmission.template.has(obra_id=obra_id)).count()
    
    # Último check-in
    last_checkin = db.query(CheckIn).filter(
        CheckIn.obra_id == obra_id
    ).order_by(CheckIn.checkin_time.desc()).first()
    
    # Taxa de conformidade da obra
    responses = db.query(
        ChecklistItemResponse.status,
        func.count(ChecklistItemResponse.id).label('count')
    ).join(ChecklistSubmission).join(
        ChecklistSubmission.template
    ).filter(
        ChecklistSubmission.template.has(obra_id=obra_id)
    ).group_by(ChecklistItemResponse.status).all()
    
    total_responses = sum(r.count for r in responses)
    conforme_count = next((r.count for r in responses if str(r.status) == "conforme"), 0)
    conformidade_rate = round((conforme_count / total_responses * 100), 1) if total_responses > 0 else 0
    
    return {
        "obra_id": obra_id,
        "obra_nome": obra.nome,
        "total_checkins": total_checkins,
        "total_checklists": total_checklists,
        "conformidade_rate": conformidade_rate,
        "ultimo_checkin": last_checkin.checkin_time if last_checkin else None,
        "ultimo_checkin_engenheiro": last_checkin.engineer.full_name if last_checkin else None
    }
