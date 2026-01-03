# routes/routes_periodos.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import localSession
from models import Periodo  

router = APIRouter()

def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[dict])
async def get_periodos(db: Session = Depends(get_db)):
    periodos = db.query(Periodo).order_by(Periodo.id_periodo).all()
    return [
        {
            "id_periodo": p.id_periodo,
            "nombre_periodo": p.nombre_periodo
        } for p in periodos
    ]

periodos_routes = router