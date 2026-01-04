#   backend-master\backend-master\Routes\attendance_estudiantes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import extract  # Para filtrar por año
from typing import List

# --- Importaciones del proyecto ---
from models import Inasistencia
import schemas
from database import localSession          

# Creamos la instancia del router con un prefijo claro para organizar las rutas de la API.
router = APIRouter(prefix="/estudiantes/inasistencias")

# Dependencia para la base de datos
def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------------
# Endpoint Principal
# ---------------------------------------------------------------

# El parámetro de la ruta recibe id_entidad y year como parte de la URL.
@router.get("/{id_entidad}/{year}", response_model=schemas.InasistenciaResponse)
def get_asistencias_entidad(
    id_entidad: int,  # Parámetro de ruta
    year: int,   # Parámetro de ruta
    db: Session = Depends(get_db)
):
    # Debug
    print(f"\n🔍 DEBUG: Buscando usuario ID: {id_entidad} en año {year}") # <--- DEBUG
    print(f"🔍 DEBUG: Buscando inasistencias para Entidad ID: {id_entidad} en año {year}") # <--- DEBUG
    
    # # Consulta a la base de datos
    # Similar a SELECT * FROM t_inasistencia WHERE id_entidad = ... AND YEAR(fecha_inasistencia) = ...;
    inasistencias = db.query(Inasistencia).filter(
            Inasistencia.id_entidad == id_entidad,
            extract('year', Inasistencia.fecha_inasistencia) == year
        ).all()
    
    # Calculamos total inasistencias e inasistencias justificadas
    total_inasistencia = sum((i.tipo_obj.valor if i.tipo_obj else 0) for i in inasistencias)
    total_inasistencia_justif = sum((i.tipo_obj.valor if i.tipo_obj else 0) for i in inasistencias if i.justificada)
    
    # Retornamos el objeto siguiendo la estructura de schemas.InasistenciaResponse
    return {
        "totalInasistencia": total_inasistencia,
        "totalInasistenciaJustif": total_inasistencia_justif,
        "detailedRecords": [
            {
                "date": i.fecha_inasistencia.strftime("%d/%m/%Y"),
                # Accedemos a la descripción del tipo a través de la relación
                "type": i.tipo_obj.descripcion if i.tipo_obj else "Desconocido",
                "value": i.tipo_obj.valor if i.tipo_obj else 0.0,
                "justified": bool(i.justificada),
                "reason": i.motivo_inasistencia or ""
            }
            for i in inasistencias
        ]
    }



