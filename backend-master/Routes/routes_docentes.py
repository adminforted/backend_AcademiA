# Routes/routes_docentes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
# Importaciones corregidas usando notación relativa (..)
from database import localSession
from models import Entidad as EntidadORM
from schemas import (
    DocenteResponse, 
    DocenteCreate, 
    DocenteUpdate,
    UserAuthData
)
from auth import get_current_user

from datetime import datetime

# 1. Definición del router
router = APIRouter()

# Dependencia de la base de datos
def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()

# Aquí moverás todos los endpoints de docentes de main.py
#   # ==================== ENDPOINTS DOCENTES ====================
#   
@router.get("/", response_model=list[DocenteResponse])
async def get_docentes(db: Session = Depends(get_db)):
    
    print("\n" + "="*60)
    print("ENDPOINT DE DOCENTES EJECUTÁNDOSE CORRECTAMENTE")
    print("="*60)
    
    # 1. Información de conexión y tabla
    print(f"Base de datos conectada → {db.bind.url}")
    print(f"Tabla usada → {EntidadORM.__tablename__}")
    print("-"*60)


    # Buscamos entidades que tengan 'DOC' en sus tipos_entidad
    docentes_db = db.query(EntidadORM).filter(
        # Buscar entidades que tengan un tipo relacionado cuyo nombre sea ALUMNO".
        EntidadORM.tipo_entidad.has(tipo_entidad="DOCENTE"),
        EntidadORM.apellido != "",
        EntidadORM.deleted_at.is_(None)
        
    ).all()
    
    # Mapeamos a DocentesResponse
    docentes = []
    for doc in docentes_db:
        docentes.append(DocenteResponse(
            id=doc.id_entidad,
            name=f"{doc.apellido}, {doc.nombre}".strip(),
            nombre=doc.nombre,       # Asignamos nombre
            apellido=doc.apellido,   # Asignamos apellido
            dni=doc.dni or 0,          # El "or 0" salva el error si es NULL
            fec_nac=doc.fec_nac,     # Asignamos fecha de nacimiento
            email=doc.email,
            domicilio=doc.domicilio,
            localidad=doc.localidad or "-", 
            telefono=doc.telefono
        ))
    return docentes

@router.get("/{id}", response_model=DocenteResponse)
async def get_docente(id: int, db: Session = Depends(get_db)):
    doc = db.query(EntidadORM).filter(
        EntidadORM.id_entidad == id,
        EntidadORM.tipos_entidad.contains("DOC"),
        EntidadORM.deleted_at.is_(None)
    ).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Docente no encontrado")
    
    return DocenteResponse(
        id=doc.id_entidad,
        name=f"{doc.apellido}, {doc.nombre}".strip(),
        nombre=doc.nombre,
        apellido=doc.apellido,
        fec_nac=doc.fec_nac,
        email=doc.email,
        domicilio=doc.domicilio,
        telefono=doc.telefono
    )

@router.post("/", response_model=DocenteResponse)
async def create_docente(docente: DocenteCreate, db: Session = Depends(get_db)):


    # Verificar si el email ya existe (solo si se proporciona)
    if docente.email and db.query(EntidadORM).filter(EntidadORM.email == docente.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    # La fecha 'created_at' viene del formulario (editada o no por el usuario)
    # La fecha 'updated_at' la generamos nosotros ahora mismo
    ahora = datetime.now() # Fecha y Hora actual

    new_docente = EntidadORM(
        nombre=docente.nombre.strip(),
        apellido=docente.apellido.strip(),
        email=docente.email,
        dni=docente.dni or 0,  
        fec_nac=docente.fec_nac,
        domicilio=docente.domicilio,
        localidad=docente.localidad,
        nacionalidad=docente.nacionalidad,
        telefono=docente.telefono,
        cel=docente.cel  or 0,
        id_tipo_entidad=2,
        # Si el front manda solo fecha, SQLAlchemy lo convierte a datetime
        # pero updated_at siempre será "ahora"
        updated_at=ahora
    )
    
    db.add(new_docente)
    db.commit()
    db.refresh(new_docente)
    
    return DocenteResponse(
        id=new_docente.id_entidad,
        name=f"{new_docente.apellido} {new_docente.nombre}".strip(),
        nombre=new_docente.nombre,
        apellido=new_docente.apellido,
        fec_nac=new_docente.fec_nac,
        email=new_docente.email,
        domicilio=new_docente.domicilio,
        telefono=new_docente.telefono
    )

@router.put("/{id}", response_model=DocenteResponse)
async def update_docente(id: int, docente: DocenteUpdate, db: Session = Depends(get_db)):
    db_docente = db.query(EntidadORM).filter(EntidadORM.id_entidad == id).first()
    
    if not db_docente:
        raise HTTPException(status_code=404, detail="Docente no encontrado")
    
    # Actualizar solo los campos que vengan
    if docente.nombre is not None:
        db_docente.nombre= docente.nombre.strip()
    if docente.apellido is not None:
        db_docente.apellido= docente.apellido.strip()
    if docente.email is not None:
        db_docente.email = docente.email
    if docente.fec_nac is not None:
        db_docente.fec_nac = docente.fec_nac
    if docente.domicilio is not None:
        db_docente.domicilio = docente.domicilio
    if docente.telefono is not None:
        db_docente.telefono = docente.telefono
        
    db.commit()
    db.refresh(db_docente)
    
    return DocenteResponse(
        id=db_docente.id_entidad,
        name=f"{db_docente.nombre} {db_docente.apellido}".strip(),
        nombre=db_docente.nombre,
        apellido=db_docente.apellido,
        fec_nac=db_docente.fec_nac,
        email=db_docente.email,
        domicilio=db_docente.domicilio,
        telefono=db_docente.telefono
    )

@router.delete("/{id}")
async def delete_docente(id: int, db: Session = Depends(get_db)):
    db_docente = db.query(EntidadORM).filter(EntidadORM.id_entidad == id).first()
    
    if not db_docente:
        raise HTTPException(status_code=404, detail="Docente no encontrado")
    
    db.delete(db_docente)
    db.commit()
    
    return {"message": "Docente eliminado exitosamente"}

#   








@router.get("/", response_model=list[DocenteResponse])
async def get_docentes(db: Session = Depends(get_db), current_user: UserAuthData = Depends(get_current_user)):
    # Lógica de permisos
    if current_user.tipo_rol.tipo_roles_usuarios != 'ADMIN_SISTEMA':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos de administrador.")

    # ... (Resto de la lógica del endpoint de docentes que estaba en main.py)
    
    # Ejemplo de la consulta:
    docentes_db = db.query(EntidadORM).filter(
        EntidadORM.tipos_entidad.contains("DOC"),
        EntidadORM.apellido != "",
        EntidadORM.deleted_at.is_(None)
    ).all()
    
    # ... (Mapeo a DocenteResponse)
    
    return [
        DocenteResponse(
            # ... (código de mapeo) ...
            id=doc.id_entidad,
            name=f"{doc.apellido}, {doc.nombre}".strip(),
            nombre=doc.nombre,
            apellido=doc.apellido,
            fec_nac=doc.fec_nac,
            email=doc.email,
            domicilio=doc.domicilio,
            telefono=doc.telefono
        ) for doc in docentes_db
    ]

# Aquí van los endpoints:
# @router.get("/{id}", ...)
# @router.post("/", ...)
# @router.put("/{id}", ...)
# @router.delete("/{id}", ...)