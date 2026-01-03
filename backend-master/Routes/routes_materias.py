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

#   ---- Traer todos los datos de todas las materias   ------
@router.get("/", response_model=list[schemas.MateriaResponse])
async def get_materias(db: Session = Depends(get_db)):
    #   Traemos el objeto completo con carga ansiosa (Eager Loading)
    materias = (
        db.query(models.Materia)
        .options(
            # Trae el nombre de la materia
            joinedload(models.Materia.nombre),

            # Trae el docente (Entidad)
            joinedload(models.Materia.docente),
            
            # 3. Trae el Curso -> Ciclo -> Plan (Triple Join)
            joinedload(models.Materia.curso)
                .joinedload(models.Curso.ciclo)
                .joinedload(models.CicloLectivo.plan)
            ) 
        .order_by(models.Materia.id_materia) # ordena por ID
        .all()
    )
    
    # Devolvemos la lista de objetos tal cual
    # Pydantic se encargará de mapear los IDs y el nombre_rel automáticamente
    return materias

#   ---- Traer las materias e info relacionada con curso, ciclo, etc, para tabla   ------
@router.get("/tabla/", response_model=list[schemas.MateriaResponse])
def obtener_materias_tabla(db: Session = Depends(get_db)):
    return db.query(models.Materia).options(
        joinedload(models.Materia.nombre),
        joinedload(models.Materia.docente),
        joinedload(models.Materia.curso)
            .joinedload(models.Curso.ciclo)
            .joinedload(models.CicloLectivo.plan)
    ).all()


#   ---- Traer las materias de un curso en particular   ------
@router.get("/curso/{id_curso}", response_model=list[schemas.MateriaResponse])
async def get_materias_curso(id_curso: int, db: Session = Depends(get_db)):
    materias = (
        db.query(models.Materia)
        .options(joinedload(models.Materia.nombre))
        .filter(models.Materia.id_curso == id_curso) # Filtramos por la columna del curso
        .all()
    )
    
    if materias is None:
        return []

    return materias

materias_router = router 