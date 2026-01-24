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

# ========================================================================
#  Obtener todaslas materias
# ========================================================================

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


# ========================================================================
#  Obtener todaslas materias e info. Para tablas
# ========================================================================

@router.get("/tabla/", response_model=list[schemas.MateriaResponse])
def obtener_materias_tabla(db: Session = Depends(get_db)):
    return db.query(models.Materia).options(
        joinedload(models.Materia.nombre),
        joinedload(models.Materia.docente),
        joinedload(models.Materia.curso)
            .joinedload(models.Curso.ciclo)
            .joinedload(models.CicloLectivo.plan)
    ).all()


# ========================================================================
#  Obtener las materias de un curso en particular
#   Tiene un problema: sólo hace joinedload(models.Materia.nombre), con lo cual ejecuta
#   una consulta a la base por cada materia.
# ========================================================================

@router.get("/curso/{id_curso}", response_model=list[schemas.MateriaResponse])
async def get_materias_curso(id_curso: int, db: Session = Depends(get_db)):
    materias = (
        db.query(models.Materia)
        .options(joinedload(models.Materia.nombre))
        .filter(models.Materia.id_curso == id_curso) # Filtramos por la columna del curso
        .all()
    )
    
    # Este if en realidad no hace falta, porque SQL Alchemy solo devuelve [] si no encuentra registros
    if materias is None:    
        return []
    
    return materias
materias_router = router 

# ========================================================================
#  Obtener sólo id y nombre de las materias de un curso en particular
# ========================================================================

@router.get("/curso/{id_curso}/simple", response_model=list[schemas.MateriaSimpleResponse])
async def get_materias_curso_simple(id_curso: int, db: Session = Depends(get_db)):
    # Seleccionamos COLUMNAS ESPECÍFICAS. Devuelve una lista de tuplas con nombre.
    materias = (
        db.query(
            models.Materia.id_materia,                  # ID de la tabla Materia
            models.NombreMateria.nombre_materia         # Nombre, de la tabla t_npmbre_materia
        )
        .join(models.Materia.nombre)                    # Join entre las dos tablas
        .filter(models.Materia.id_curso == id_curso)    # Filtramos por la columna del curso
        .all()
    )
    
    return materias
materias_router = router 

