#   backend-master\backend-master\Routes\attendance_estudiantes.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import extract  # Para filtrar por año
from typing import List

# --- Importaciones del proyecto ---
from database import localSession           # Importar la sesión de DB
from models import Entidad as EntidadORM, Inasistencia, User as Usuario, TipoInasistencia



    
# --- Modelos (Schemas) ---

class AsistenciaRecord(BaseModel):
    date: str
    type: str
    value: float
    justified: bool
    reason: str

class AsistenciaResponse(BaseModel):
    totalDaysLost: float
    justifiedDays: float
    detailedRecords: List[AsistenciaRecord]

def get_db():
    """Dependencia para obtener la sesión de base de datos"""
    db = localSession()
    try:
        yield db
    finally:
        db.close()

# Crea la instancia del router con un prefijo claro para organizar las rutas de la API.
router = APIRouter(prefix="/estudiantes")

# ---------------------------------------------------------------
# Endpoint Principal
# ---------------------------------------------------------------

# El parámetro de la ruta recibe el id_entidad, que es el identificador directo del estudiante.
# RUTA FINAL: /estudiantes/{id_entidad}/asistencias
@router.get("/{id_entidad}/asistencias", response_model=AsistenciaResponse)
def get_asistencias_entidad(
    id_entidad: int,  # Recibimos el ID DE USUARIO (ej: 102)
    year: int = 2025,
    db: Session = Depends(get_db)
):
    print(f"\n🔍 DEBUG: Buscando usuario ID: {id_entidad} en año {year}") # <--- DEBUG
        
    
    # Buscar las INASISTENCIAS usando el id_entidad del usuario
    print(f"🔍 DEBUG: Buscando inasistencias para Entidad ID: {id_entidad} en año {year}") # <--- DEBUG
    
    # Similar a la consulta SQL: select * from t_inasistencia ... where id_entidad = ...
    inasistencias = db.query(Inasistencia).filter(
        Inasistencia.id_entidad == id_entidad,
        extract('year', Inasistencia.fecha_inasistencia) == year
    ).all()
    
    # Calcular totales
    total_dias = sum((i.tipo_obj.valor if i.tipo_obj else 0) for i in inasistencias)
    dias_justif = sum((i.tipo_obj.valor if i.tipo_obj else 0) for i in inasistencias if i.justificada)
    
    return {
        "totalDaysLost": total_dias,
        "justifiedDays": dias_justif,
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



