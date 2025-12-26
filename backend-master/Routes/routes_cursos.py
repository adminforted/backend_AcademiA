#   backend_AcademiA\backend-master\Routes\routes_cursos.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Curso
import schemas

router = APIRouter(
    prefix="/cursos",
    tags=["Cursos"],
)

#   GET de todos los cursos
@router.get("/", response_model=list[schemas.CursoResponse])
def obtener_cursos(db: Session = Depends(get_db)):
    # Esta línea busca todos los registros en la tabla
    cursos = (
        db.query(Curso)
        .all()
    )
    return cursos


# GET de los cursos de un cierto Ciclo Lectivo
@router.get("/por_ciclo/{id_ciclo}", response_model=list[schemas.CursoResponse])
def obtener_cursos_por_ciclo(id_ciclo: int, db: Session = Depends(get_db)):
    # Buscamos en la tabla de cursos donde el id_ciclo_lectivo coincida
    cursos = (
        db.query(Curso)
        .filter(Curso.id_ciclo_lectivo == id_ciclo)
        .all()
    )
    return cursos
