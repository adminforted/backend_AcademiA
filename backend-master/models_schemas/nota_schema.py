#  backend-master\schemas\nota_schema.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

# ----------------------------------------------------
# 1. Esquema de Creación (Input desde el Front-end)
# ----------------------------------------------------
class NotaCreate(BaseModel):
    """Define los campos necesarios que el Front-end debe enviar para crear una Nota."""
    
    # Campos requeridos que vienen del formulario (CargarNotaIndividual.jsx)
    id_materia: int = Field(..., description="ID de la materia calificada.")
    id_entidad_estudiante: int = Field(..., description="ID del estudiante calificado.")
    nota: float = Field(..., ge=1.0, le=10.0, description="Calificación obtenida (entre 1.0 y 10.0).")
    id_periodo: int = Field(..., description="ID del período (trimestre, semestre, etc.)")
    
    # Campo opcional que puede ser ignorado por el servicio si se define en el backend
    # id_entidad_carga: Optional[int] = None 
    # id_tipo_nota: Optional[int] = None

    class Config:
        # Esto permite que los objetos puedan ser usados en un ORM.
        # Es una práctica recomendada en Pydantic v1 (que usa FastAPI clásico)
        orm_mode = True

# ----------------------------------------------------
# 2. Esquema de Respuesta (Output hacia el Front-end)
# ----------------------------------------------------
class NotaResponse(NotaCreate):
    """Define la estructura de la Nota una vez que ha sido guardada en la DB."""

    # Campos que la DB asigna automáticamente
    id_nota: int = Field(..., description="ID único autogenerado de la nota.")
    id_entidad_carga: int = Field(..., description="ID de la entidad docente/usuario que cargó la nota.")
    id_tipo_nota: int = Field(..., description="Tipo de nota (ej: Normal, Recuperatorio).")
    fecha_carga: date = Field(..., description="Fecha en que se cargó la nota.")

    # No es estrictamente necesario repetir Config, pero ayuda a la claridad.
    class Config:
        orm_mode = True