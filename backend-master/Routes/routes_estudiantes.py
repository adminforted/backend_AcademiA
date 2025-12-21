# Routes/routes_estudiantes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
# Importaciones corregidas usando notación relativa (..)
from database import localSession
from models import ( 
    Entidad as EntidadORM, 
    TipoEntidad,
    NombreMateria, 
    Materia, 
    Inscripcion
)
from schemas import (
    EstudianteResponse, 
    EstudianteCreate, 
    EstudianteUpdate,
    UserAuthData # Para obtener el rol
)

from auth import get_current_user # Para obtener el usuario actual

def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()

# 1. Definición del router
router = APIRouter()

# Dependencia de la base de datos
def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()



 
 # ==================== ENDPOINTS ESTUDIANTES ====================
 
@router.get("/", response_model=list[EstudianteResponse])
async def get_estudiantes(
    db: Session = Depends(get_db), 
    current_user: UserAuthData = Depends(get_current_user) # Seguridad activa
):
    # 1. Validación de permisos (Solo Admins)
    if current_user.tipo_rol.tipo_entidad != 'ADMIN_SISTEMA':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permisos de administrador."
        )

    # 2. Consulta a la base de datos
    estudiantes_db = db.query(EntidadORM).filter(
        # Buscar entidades que tengan un tipo relacionado cuyo nombre sea ALUMNO".
        EntidadORM.tipo_entidad.has(tipo_entidad="ALUMNO"),
        
        EntidadORM.apellido != "",
        EntidadORM.deleted_at.is_(None)
    ).all()
    
    # 3. Mapeo y entrega de datos
    return [
        EstudianteResponse(
            id=est.id_entidad,
            name=f"{est.apellido}, {est.nombre}".strip(),
            nombre=est.nombre,
            apellido=est.apellido,
            fec_nac=est.fec_nac,
            email=est.email,
            domicilio=est.domicilio,
            telefono=est.telefono
        ) for est in estudiantes_db
    ]


 
 
@router.get("/{id}", response_model=EstudianteResponse)
async def get_estudiante(id: int, db: Session = Depends(get_db)):
     est = db.query(EntidadORM).filter(
         EntidadORM.id_entidad == id,
         EntidadORM.tipos_entidad.contains("ALU"),
         EntidadORM.deleted_at.is_(None)
     ).first()
     
     if not est:
         raise HTTPException(status_code=404, detail="Estudiante no encontrado")
     
     return EstudianteResponse(
         id=est.id_entidad,
         name=f"{est.apellido}, {est.nombre}".strip(),
         nombre=est.nombre,
         apellido=est.apellido,
         fec_nac=est.fec_nac,
         email=est.email,
         domicilio=est.domicilio,
         telefono=est.telefono
     )
 
@router.post("/", response_model=EstudianteResponse)
async def create_estudiante(estudiante: EstudianteCreate, db: Session = Depends(get_db)):
     # Verificar si el email ya existe (solo si se proporciona)
     if estudiante.email and db.query(EntidadORM).filter(EntidadORM.email == estudiante.email).first():
         raise HTTPException(status_code=400, detail="El email ya está registrado")
     
     # Separar nombre y apellido
     # parts = estudiante.name.split(' ', 1)
     # nombre = parts[0]
     # apellido = parts[1] if len(parts) > 1 else ""
     
 
     new_estudiante = EntidadORM(
         nombre=estudiante.nombre.strip(),
         apellido=estudiante.apellido.strip(),
         email=estudiante.email,
         fec_nac=estudiante.fec_nac,
         domicilio=estudiante.domicilio,
         telefono=estudiante.telefono,
         tipos_entidad="ALU"
     )
     
     db.add(new_estudiante)
     db.commit()
     db.refresh(new_estudiante)
     
     return EstudianteResponse(
         id=new_estudiante.id_entidad,
         name=f"{new_estudiante.apellido} {new_estudiante.nombre}".strip(),
         nombre=new_estudiante.nombre,
         apellido=new_estudiante.apellido,
         fec_nac=new_estudiante.fec_nac,
         email=new_estudiante.email,
         domicilio=new_estudiante.domicilio,
         telefono=new_estudiante.telefono
     )
 
@router.put("/{id}", response_model=EstudianteResponse)
async def update_estudiante(id: int, estudiante: EstudianteUpdate, db: Session = Depends(get_db)):
     db_estudiante = db.query(EntidadORM).filter(EntidadORM.id_entidad == id).first()
     
     if not db_estudiante:
         raise HTTPException(status_code=404, detail="Estudiante no encontrado")
     
     # Actualizar solo los campos que vengan
     if estudiante.nombre is not None:
         db_estudiante.nombre= estudiante.nombre.strip()
     if estudiante.apellido is not None:
         db_estudiante.apellido= estudiante.apellido.strip()
     if estudiante.email is not None:
         db_estudiante.email = estudiante.email
     if estudiante.fec_nac is not None:
         db_estudiante.fec_nac = estudiante.fec_nac
     if estudiante.domicilio is not None:
         db_estudiante.domicilio = estudiante.domicilio
     if estudiante.telefono is not None:
         db_estudiante.telefono = estudiante.telefono
         
     db.commit()
     db.refresh(db_estudiante)
     
     return EstudianteResponse(
         id=db_estudiante.id_entidad,
         name=f"{db_estudiante.nombre} {db_estudiante.apellido}".strip(),
         nombre=db_estudiante.nombre,
         apellido=db_estudiante.apellido,
         fec_nac=db_estudiante.fec_nac,
         email=db_estudiante.email,
         domicilio=db_estudiante.domicilio,
         telefono=db_estudiante.telefono
     )
 
@router.delete("/{id}")
async def delete_estudiante(id: int, db: Session = Depends(get_db)):
     db_estudiante = db.query(EntidadORM).filter(EntidadORM.id_entidad == id).first()
     
     if not db_estudiante:
         raise HTTPException(status_code=404, detail="Estudiante no encontrado")
     
     db.delete(db_estudiante)
     db.commit()
     
     return {"message": "Estudiante eliminado exitosamente"}


      # ==================== MATERIAS DE UN ESTUDIANTE ====================

@router.get("/api/estudiantes/{estudiante_id}/materias")    # Nota: El prefijo /api/estudiantes/ ya se añade en main.py
async def get_materias_por_estudiante(estudiante_id: int, 
                                      db: Session = Depends(get_db),
                                      current_user: UserAuthData = Depends(get_current_user)): # 🚨 Añadir contro


# Lógica de Permisos (Ejemplo: Solo el ADMIN o el PROPIO estudiante pueden ver sus materias)
    rol_actual = current_user.tipo_rol.tipo_roles_usuarios
    if rol_actual not in ['ADMIN_SISTEMA'] and current_user.entidad_id != estudiante_id:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para ver estas materias.")
    

    # Verificar que exista y sea estudiante (tipo ALU)
    estudiante = db.query(EntidadORM).filter(
        EntidadORM.id_entidad == estudiante_id,
        EntidadORM.tipos_entidad.contains("ALU"),
        EntidadORM.deleted_at.is_(None)
    ).first()
    
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    # Consulta con joins naturales
    materias = (
        db.query(NombreMateria.nombre_materia)
        .join(Inscripcion, Inscripcion.materia_id == Materia.id_materia)
        .join(Materia, Materia.nombre_materia_id == NombreMateria.id_nombre_materia)
        .filter(
            Inscripcion.entidad_id == estudiante_id,
            Inscripcion.deleted_at.is_(None)
        )
        .order_by(NombreMateria.nombre_materia)
        .all()
    )

    # Devolver lista simple de diccionarios
    return [{"nombre_materia": m.nombre_materia} for m in materias]


# Aquí van los endpoints:
# @router.get("/{id}", ...)
# @router.post("/", ...)
# @router.put("/{id}", ...)
# @router.delete("/{id}", ...)
# @router.get("/{estudiante_id}/materias", ...)

routes_estudiantes = router