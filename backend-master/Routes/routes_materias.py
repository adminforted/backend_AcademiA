#  backend-master\backend-master\Routes\routes_materias.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import localSession
from models import Materia, NombreMateria

router = APIRouter()

def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[dict])
async def get_materias(db: Session = Depends(get_db)):
    #   Devuelve todas las materias disponibles (únicas por nombre)

    # join para obtener el nombre real desde t_nombre_materia
    materias = (
        db.query(Materia.id_materia, NombreMateria.nombre_materia)
        .join(NombreMateria, Materia.id_nombre_materia == NombreMateria.id_nombre_materia)
        .order_by(NombreMateria.nombre_materia)
        .all()
    )
    
    return [
        {
            "id_materia": m.id_nombre_materia,  
            "nombre_materia": m.nombre_materia
        } for m in materias
    ]

materias_router = router 
