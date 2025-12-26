#  backend-master\backend-master\Routes\routes_materias.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from database import localSession
from models import Materia
import models, schemas 

router = APIRouter()

def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()

#   ---- Traer todas las materias   ------
@router.get("/", response_model=list[schemas.MateriaResponse])
async def get_materias(db: Session = Depends(get_db)):
    #   Traemos el objeto completo
    materias = (
        db.query(models.Materia)
        .options(joinedload(models.Materia.nombre_rel)) 
        .order_by(models.Materia.id_materia) # Opcional: ordenar por ID
        .all()
    )
    if materias is None:
        return []
    
    # Devolvemos la lista de objetos tal cual
    # Pydantic se encargará de mapear los IDs y el nombre_rel automáticamente
    return materias


#   ---- Traer las materias de un curso en particular   ------
@router.get("/curso/{id_curso}", response_model=list[schemas.MateriaResponse])
async def get_materias_curso(id_curso: int, db: Session = Depends(get_db)):
    materias = (
        db.query(models.Materia)
        .options(joinedload(models.Materia.nombre_rel))
        .filter(models.Materia.id_curso == id_curso) # Filtramos por la columna del curso
        .all()
    )
    
    if materias is None:
        return []

    return materias

materias_router = router 