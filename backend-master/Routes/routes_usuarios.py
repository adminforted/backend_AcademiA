#   backend_AcademiA\backend-master\Routes\routes_usuarios.py


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from database import localSession
from models import ( 
    Entidad as EntidadORM, 
)
from schemas import (
    EntidadTipoEntidad,
    UserAuthData # Para obtener el rol
)

from auth import get_current_user # Para obtener el usuario actual

def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()

# Definición del router
router = APIRouter()

# # =====================================================
#  GET - Obtener el NOMBRE de un usuario y TIPO, por ID
# =====================================================
@router.get("/{id}", response_model=EntidadTipoEntidad)
async def get_entidad_nombre(id: int, db: Session = Depends(get_db)):
    ent = db.query(EntidadORM).options(
        joinedload(EntidadORM.tipo_entidad) #  El nombre de la relación en el modelo
    ).filter(
        EntidadORM.id_entidad == id,
        EntidadORM.deleted_at.is_(None)
    ).first()
     
    if not ent:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    # Construcción manual respetando los tipos de datos 
    return EntidadTipoEntidad(
         id_entidad=ent.id_entidad,
         nombre=ent.nombre,
         apellido=ent.apellido,
         id_tipo_entidad=ent.id_tipo_entidad,   # El número, no está relacionada, proque está en t_entidad
         tipo_entidad_rel=ent.tipo_entidad  # El objeto cargado por joinedload
     )