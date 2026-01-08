#   backend_AcademiA\backend-master\Routes\routes_estudiantes_notas.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
import models, schemas
from database import localSession


def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()



router = APIRouter(prefix="/estudiantes/notas")


@router.get("/informe-individual/{id_estudiante}", response_model=schemas.InformeAcademicoEstudianteResponse)
def obtener_informe_notas_estudiante(
    id_estudiante: int,
    ciclo_id: int = Query(..., description="ID del ciclo lectivo"),
    curso_id: int = Query(..., description="ID del curso"),
    db: Session = Depends(get_db)
):
    try:
        # 1. Obtener Columnas (Headers de tipos de nota)
        columnas_query = (
            db.query(models.TipoNota.id_tipo_nota, models.TipoNota.tipo_nota)
            .order_by(models.TipoNota.id_tipo_nota)
            .all()
        )
        headers = [schemas.ColumnaHeader(id_tipo_nota=c.id_tipo_nota, label=c.tipo_nota) 
                   for c in columnas_query]

        # 2. Obtener todas las notas del estudiante para este ciclo/curso
        # Filtramos por id_entidad_estudiante
        notas_existentes = (
            db.query(models.Nota)
            .join(models.Materia)
            .filter(
                models.Nota.id_entidad_estudiante == id_estudiante,
                models.Materia.id_curso == curso_id # Filtramos por el curso indicado
            )
            .all()
        )

        # 3. Identificar las materias involucradas
        # Mapeamos materias por ID para evitar duplicados
        materias_query = (
            db.query(models.Materia)
            # Acceder una sola vez a la BD para cargar el nombre de la materia
            .options(joinedload(models.Materia.nombre)) 
            .filter(models.Materia.id_curso == curso_id)
            .all()
        )
        
        filas = []
        for mat in materias_query:
            # Filtramos las notas que pertenecen a esta materia específica
            notas_de_materia = {n.id_tipo_nota: float(n.nota) for n in notas_existentes 
                                if n.id_materia == mat.id_materia}
            
            # Mapeamos las calificaciones según los headers (id_tipo_nota)
            calificaciones = {col.id_tipo_nota: notas_de_materia.get(col.id_tipo_nota) 
                             for col in headers}

            # Cálculo de promedio de la materia
            notas_val = [v for v in calificaciones.values() if v is not None]
            promedio = round(sum(notas_val) / len(notas_val), 2) if notas_val else None

            filas.append(schemas.MateriaNotaRow(
                id_materia=mat.id_materia,
                
                # Accedo al nombre de la materia, de forma indirecta: mat (Materia) -> nombre (Relación) -> nombre_materia (String)
                nombre_materia=mat.nombre.nombre_materia if mat.nombre else "Materia sin nombre",
                calificaciones=calificaciones,
                promedio=promedio,
                definitiva=calificaciones.get(7) # ID 7 según la lógica de "Definitiva" ??????????
            ))

        return schemas.InformeAcademicoEstudianteResponse(
            columnas=headers,
            filas=sorted(filas, key=lambda x: x.nombre_materia)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar informe: {str(e)}")