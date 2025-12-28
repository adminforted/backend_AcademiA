# backend_AcademiA\backend-master\Routes\routes_personal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import localSession
from models import Entidad as EntidadORM, TipoEntidad as TipoEntidadORM    # Uso EntidadORM para entender que es del ORM

from models_schemas.personal_schemas import PersonalResponse

# Definición del router
router = APIRouter()

# Dependencia de la base de datos
def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()


#   # ==================== ENDPOINTS PERSONAL ====================
#   Obtener todos
@router.get("/personal", response_model=list[PersonalResponse])
def get_personal(db: Session = Depends(get_db)):
    
    # Información de conexión y tabla
    print(f"Base de datos conectada → {db.bind.url}")
    print(f"Tabla usada → {EntidadORM.__tablename__}")
    print("-"*60)

    # Hacemos la consulta con el JOIN
    resultados = db.query(EntidadORM).join(TipoEntidadORM).filter(
        TipoEntidadORM.id_tipo_entidad.in_([3, 4, 5, 6, 8, 9]),
        EntidadORM.deleted_at.is_(None) # Filtramos los no eliminados
    ).all()
    
    print(f"Datos leidos: {resultados}")
    print(f"\n🔍 Total registros: {len(resultados)}")

    # Mapeamos los datos al esquema
    return [
        PersonalResponse(
            apellido=p.apellido,   # Asignamos apellido
            nombre=p.nombre,       # Asignamos nombre
            dni=p.dni,
            domicilio=p.domicilio,
            localidad=p.localidad,
            telefono=p.telefono,
            cel=p.cel,
            email=p.email,
            # Accedemos al nombre del tipo a través de la relación
            tipo_entidad=p.tipo_entidad.tipo_entidad
        ) for p in resultados
    ]