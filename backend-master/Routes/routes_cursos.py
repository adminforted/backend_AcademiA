#   backend_AcademiA\backend-master\Routes\routes_cursos.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import Curso
import models, schemas

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


#   GET de todos los cursos, con info de Ciclo Lectivo y Plan de cada uno
@router.get("/completo/", response_model=list[schemas.CursoCicloLectivo])
# Definición de función
def obtener_cursos_ciclo_plan(db: Session = Depends(get_db)):
    # Inicio de la consulta
    cursos = db.query(models.Curso).options( 
        # Carga del Ciclo
        joinedload(models.Curso.ciclo)
        # Carga del Plan encadenada
        .joinedload(models.CicloLectivo.plan)
        # Cierre de la consulta
        ).all()
    # Retorno
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
