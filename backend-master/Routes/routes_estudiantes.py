# Routes/routes_estudiantes.py

from fastapi import APIRouter, Depends, HTTPException, status 

from sqlalchemy.orm import Session,joinedload
from database import localSession
from typing import List

from models import ( 
    Entidad as EntidadORM, TipoEntidad, NombreMateria,  Inscripcion,
    CicloLectivo as CicloLectivoORM, Curso as CursoORM, Materia as MateriaORM, Nota as NotaORM,
    Inscripcion as InscripcionORM

)
from schemas import (
    EstudianteResponse, 
    EstudianteCreate, 
    EstudianteUpdate,
    UserAuthData, # Para obtener el rol
    CicloLectivoSimple,
    MateriaResponse
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
        EntidadORM.tipo_entidad.has(TipoEntidad.tipo_entidad =="ESTUDIANTE"),
        
        EntidadORM.apellido != "",
        EntidadORM.deleted_at.is_(None)
    ).all()
    
    # 3. Mapeo y entrega de datos
    return [
        EstudianteResponse(
            id_entidad=est.id_entidad,
            name=f"{est.apellido}, {est.nombre}".strip(),
            nombre=est.nombre,
            apellido=est.apellido,
            fec_nac=est.fec_nac,
            email=est.email,
            domicilio=est.domicilio,
            telefono=est.telefono
        ) for est in estudiantes_db
    ]


 
# # =====================================================
#  GET - Obtener Datos de un estudiante por ID
# =====================================================
@router.get("/{id}", response_model=EstudianteResponse)
async def get_estudiante(id: int, db: Session = Depends(get_db)):
     est = db.query(EntidadORM).filter(
         EntidadORM.id_entidad == id,
         EntidadORM.tipo_entidad.contains("ESTUDIANTE"),
         EntidadORM.deleted_at.is_(None)
     ).first()
     
     if not est:
         raise HTTPException(status_code=404, detail="Estudiante no encontrado")
     
     return EstudianteResponse(
         id_entidad=est.id_entidad,
         name=f"{est.apellido}, {est.nombre}".strip(),
         nombre=est.nombre,
         apellido=est.apellido,
         fec_nac=est.fec_nac,
         email=est.email,
         domicilio=est.domicilio,
         telefono=est.telefono
     )
     
# # =====================================================
#  GET - Obtener Datos de un estudiante por Curso
# =====================================================

@router.get("/curso/{id_curso}", response_model=List[EstudianteResponse])
async def get_estudiantes_por_curso(id_curso: int, db: Session = Depends(get_db)):
     estCurso = db.query(EntidadORM
         ).join(InscripcionORM, InscripcionORM.id_entidad == EntidadORM.id_entidad
         ).join(CicloLectivoORM, CicloLectivoORM.id_ciclo_lectivo == InscripcionORM.id_ciclo_lectivo
         ).join(CursoORM, CursoORM.id_ciclo_lectivo  ==  CicloLectivoORM.id_ciclo_lectivo
         ).filter( CursoORM.id_curso == id_curso,
         InscripcionORM.deleted_at.is_(None)
         ).all() 
                
     return [
        EstudianteResponse(
            id_entidad=est.id_entidad,
            # .strip() elimina espacios en blanco al inicio/final
            name=f"{est.apellido}, {est.nombre}".strip(), 
            nombre=est.nombre,
            apellido=est.apellido,
            fec_nac=est.fec_nac,
            email=est.email,
            domicilio=est.domicilio,
            telefono=est.telefono,
            )
        for est in estCurso
        ]
 
 
 
 
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
         id_tipo_entidad=1
     )
     
     db.add(new_estudiante)
     db.commit()
     db.refresh(new_estudiante)
     
     return EstudianteResponse(
         id_entidad=new_estudiante.id_entidad,
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
         id_entidad=db_estudiante.id_entidad,
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


# ========================================================================
#  GET - Obtener Materias de un estudiante por ID
#  Obtiene las Materias en las que ha tenido notas un estudiante.
# ========================================================================

@router.get("/{estudiante_id}/materias")    # El prefijo /api/estudiantes/ ya se añade en main.py
async def get_materias_por_estudiante(estudiante_id: int,
                                      db: Session = Depends(get_db),
                                      current_user: UserAuthData = Depends(get_current_user)): 


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
        .join(Inscripcion, Inscripcion.materia_id == MateriaORM.id_materia)
        .join(MateriaORM, MateriaORM.nombre_materia_id == NombreMateria.id_nombre_materia)
        .filter(
            Inscripcion.entidad_id == estudiante_id,
            Inscripcion.deleted_at.is_(None)
        )
        .order_by(NombreMateria.nombre_materia)
        .all()
    )

    # Devolver lista simple de diccionarios
    return [{"nombre_materia": m.nombre_materia} for m in materias]



# ========================================================================
#  GET - Obtener Materias de un estudiante por ID y Ciclo Lectivo
#  Obtiene las Materias de un ciclo lectivo en el que un estudiante se ha inscripto estudiante.
# ========================================================================

@router.get("/{id_ciclo}/{id_estudiante}/materias", response_model=List[MateriaResponse])    # El prefijo /api/estudiantes/ ya se añade en main.py
async def get_materias_ciclo_por_estudiante(id_ciclo: int, id_estudiante: int,
                                      db: Session = Depends(get_db),
                                      current_user: UserAuthData = Depends(get_current_user)): 

    # Lógica de Permisos (Solo el ADMIN o el PROPIO estudiante pueden ver sus materias)
    # rol_actual = current_user.tipo_rol.tipo_roles_usuarios
    rol_actual = current_user.rol_sistema
    if rol_actual not in ['ADMIN_SISTEMA', "DOCENTE_APP"] and current_user.id_entidad != id_estudiante:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para ver estas materias.")

    # Verificar que exista y sea estudiante
    estudiante = db.query(EntidadORM).filter(
        EntidadORM.id_entidad == id_estudiante,
        EntidadORM.id_tipo_entidad == 1,
        EntidadORM.deleted_at.is_(None)
    ).first()
    
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    # Consulta a la base de datos (usando SQL Alchemy)
    # Buscamos en inscripciones, pero devolvemos los objetos 'materia'
    inscripciones_db = (
        db.query(InscripcionORM
                 ).filter(
                    InscripcionORM.id_entidad == id_estudiante,
                    InscripcionORM.id_ciclo_lectivo == id_ciclo,
                    InscripcionORM.deleted_at.is_(None)
                ).options(
                     # Cargamos las relaciones anidadas que pide la MateriaResponse
                    joinedload(InscripcionORM.materia).joinedload(MateriaORM.nombre),
                    joinedload(InscripcionORM.materia).joinedload(MateriaORM.curso),
                    joinedload(InscripcionORM.materia).joinedload(MateriaORM.docente)
                ).all()
                )
    #   Extraer solo los objetos MateriaORM de las inscripciones encontradas
    materias_alu_ciclo = [ins.materia for ins in inscripciones_db if ins.materia]
    
    return materias_alu_ciclo



# ========================================================================
#  GET - Obtener Ciclos Lectivos de un estudiante por ID
#  Obtiene los ciclos lectivos donde un estudiante tiene notas registradas.
# ========================================================================

@router.get("/{id_entidad}/ciclos", response_model=List[CicloLectivoSimple])
def get_ciclos_por_estudiante(id_entidad: int, db: Session = Depends(get_db)):
    ciclos = (
        db.query(
            CicloLectivoORM.id_ciclo_lectivo,
            CicloLectivoORM.nombre_ciclo_lectivo
    )
     # Unión Ciclo con Curso (join t_curso tc on tc.id_ciclo_lectivo = tcl.id_ciclo_lectivo)
    .join(CursoORM, CursoORM.id_ciclo_lectivo == CicloLectivoORM.id_ciclo_lectivo) 
     # Unión Materia con Curso (join t_materia tm on tm.id_curso = tc.id_curso)
    .join(MateriaORM, MateriaORM.id_curso == CursoORM.id_curso) 
     # Unión Nota con Materia (join t_nota tn on tm.id_materia = tn.id_materia)
    .join(NotaORM, NotaORM.id_materia == MateriaORM.id_materia)
     # Filtro por Alumno (where te.id_entidad = 36543219)
    .filter(NotaORM.id_entidad_estudiante == id_entidad)
      # Agrupar repetidos (GROUP BY tcl.nombre_ciclo_lectivo)   
     .group_by(CicloLectivoORM.id_ciclo_lectivo, CicloLectivoORM.nombre_ciclo_lectivo)
      # Comando de ejecución
     .all() 
    )

    if not ciclos:
        # Si no hay notas, devuelveolvemos lista vacía
        return []

    return ciclos



routes_estudiantes = router