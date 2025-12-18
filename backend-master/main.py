#   backend-master\backend-master\main.py

# Importamos FastAPI para crear la aplicación
from fastapi import FastAPI, Depends, HTTPException

# Importamos OAuth2PasswordBearer para autenticación con JWT
from fastapi.security import OAuth2PasswordBearer

# Importamos Session para manejar la base de datos
from sqlalchemy.orm import Session

# Importamos módulos locales para CRUD y autenticación
import crud
import auth

from Routes import  routes_docentes, attendance_estudiantes
from Routes import routes_notas

from Routes.routes_materias import router as materias_router
from Routes.routes_periodos import router as periodos_router
from Routes.routes_estudiantes import router as routes_estudiantes


from auth import send_email, get_password_hash, generate_token

# Importamos localSession para la base de datos
from database import localSession

# Importamos los esquemas necesarios para validar y serializar datos 
from schemas import (
    UserCreate, 
    UserAuthData, 
    Token, 
    EmailVerifyRequest, 
    ForgotPasswordRequest, 
    ResetPasswordRequest, 
    Entidad, 
    #   EstudianteResponse,
    #   EstudianteCreate,
    #   EstudianteUpdate,
    #   DocenteResponse,
    #   DocenteCreate,
    #   DocenteUpdate,
    #   Habilitarlas si se necesitan en otros endpoints que se quedan en main.py.
)


# Importamos CORSMiddleware para habilitar CORS
from fastapi.middleware.cors import CORSMiddleware

#from typing import List
from models import (
    Entidad as EntidadORM,
    #   NombreMateria,
    #   Materia,
    #   Inscripcion
)

   
# Creamos la instancia de FASTAPI
app = FastAPI(
    title="AcademIA API",
    description="API para el sistema académico",
    version="1.0.0"
)





# Create table database
# ase.metadata.create_all(bind=engine)

# Creamos la instancia de la aplicación FastAPI
app = FastAPI()
# Para que el acceso sea publico 
# origin = ['*']

# Rutas de autenticación definidas en auth.py
app.include_router(auth.router, prefix="/api", tags=["Autenticación"])

# Esquema OAuth2 para autenticación (definido en auth.py)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# INCLUIR ROUTERS CON EL OBJETO 'router' DE CADA ARCHIVO
#   Endpoint para listar alumnos: http://localhost:8000/api/estudiantes/
app.include_router(routes_estudiantes, prefix="/api/estudiantes", tags=["Estudiantes"])

app.include_router(routes_docentes.router, prefix="/api/docentes", tags=["Docentes"]) 

app.include_router(attendance_estudiantes.router, prefix="/api", tags=["Asistencias"])

app.include_router(routes_notas.router)

app.include_router(materias_router, prefix="/api/materias", tags=["Materias"])
app.include_router(periodos_router, prefix="/api/periodos", tags=["Períodos"])





# Configurar CORS
origins = [
    'http://localhost:3001',
    'http://localhost:1500',
    'http://localhost:3002',
]

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],    # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=['*'],    # Permitir todos los headers (Authorization, etc.)
)


# # Dependencia para la base de datos
def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()

# Ruta raiz
@app.get("/")
def root():
    return 'iniciando api...'

# Registro
@app.post("/api/register", response_model=UserAuthData)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Crea el usuario usando la función CRUD
    db_user, verification_token = crud.c_create_user(db, user)
    # Enviar email de verificación
    verification_url = f"http://localhost:3001/#/verify-email?token={verification_token}"
    await send_email(
        to_email=user.email,
        subject="Verifica tu email",
        body=f"Haz clic para verificar tu email: {verification_url}"
    )
    # Añade tipos_usuario a la respuesta
    db_user.tipos_usuario = [ut.cod_tipo_usuario for ut in db.query(auth.UsuarioTipos).filter(auth.UsuarioTipos.usuario_id == db_user.id).all()]
    return db_user


# Endpoint para listar todos los usuarios (solo para administradores)
@app.get("/api/users", response_model=list[UserAuthData])
async def get_users(current_user: UserAuthData = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    # Llama a la función CRUD para obtener todos los usuarios
    return crud.c_get_users(db, current_user)

# Endpoint para obtener un usuario por ID
@app.get("/api/users/{user_id}", response_model=UserAuthData)
async def get_user(user_id: int, current_user: UserAuthData = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    # Llama a la función CRUD para obtener el usuario, aplicando reglas de permisos
    return crud.c_get_user(db, user_id, current_user)

# Endpoint para crear un nuevo usuario
@app.post("/api/users", response_model=UserAuthData)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Llama a la función CRUD para crear el usuario
    db_user, _ = crud.c_create_user(db, user)
    db_user.tipos_usuario = [ut.cod_tipo_usuario for ut in db.query(auth.UsuarioTipos).filter(auth.UsuarioTipos.usuario_id == db_user.id).all()]
    return db_user


# Endpoint para actualizar un usuario existente
@app.put("/api/users/{user_id}", response_model=UserAuthData)
async def update_user(user_id: int, user: UserCreate, current_user: UserAuthData = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    # Llama a la función CRUD para actualizar el usuario
    db_user = crud.c_update_user(db, user_id, user, current_user)
    db_user.tipos_usuario = [ut.cod_tipo_usuario for ut in db.query(auth.UsuarioTipos).filter(auth.UsuarioTipos.usuario_id == db_user.id).all()]
    return db_user


# Endpoint para eliminar un usuario
@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int, current_user: UserAuthData = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    # Llama a la función CRUD para eliminar el usuario
    return crud.c_delete_user(db, user_id, current_user)


# Endpoint para obtener una entidad por ID (nuevo, para tbl_entidad)
@app.get("/api/entidades/{entidad_id}", response_model=Entidad)
async def get_entidad(entidad_id: int, current_user: UserAuthData = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    
    # Usamos la sintaxis correcta del rol para verificar permisos
    rol_actual = current_user.tipo_rol.tipo_roles_usuarios

    # Verifica que el usuario tenga permisos (ADM o DOC)
    if rol_actual not in ['ADMIN_SISTEMA', 'DOCENTE_APP', 'ALUMNO_APP']: # Usa los valores de la BD
        raise HTTPException(status_code=403, detail="No tienes permiso para ver entidades")
    
    # Consulta la entidad en la base de datos
    entidad = db.query(EntidadORM).filter(EntidadORM.id_entidad == entidad_id, EntidadORM.deleted_at.is_(None)).first()
    if not entidad:
        raise HTTPException(status_code=404, detail="Entidad no encontrada")
    # Convierte el campo tipos_entidad (texto separado por comas) en una lista
    entidad.tipos_entidad = entidad.tipos_entidad.split(',') if entidad.tipos_entidad else []
    return entidad


   
#   # ==================== ENDPOINTS ESTUDIANTES ====================
#   
#   @app.get("/api/estudiantes", response_model=list[EstudianteResponse])
#   async def get_estudiantes(db: Session = Depends(get_db)):
#       
#       print("\n" + "="*60)
#       print("ENDPOINT DE ESTUDIANTES EJECUTÁNDOSE CORRECTAMENTE")
#       print("="*60)
#       
#       # 1. Información de conexión y tabla
#       print(f"Base de datos conectada → {db.bind.url}")
#       print(f"Tabla usada → {EntidadORM.__tablename__}")
#       print("-"*60)
#   
#   
#       # Buscamos entidades que tengan 'ALU' en sus tipos_entidad
#       estudiantes_db = db.query(EntidadORM).filter(
#           EntidadORM.tipos_entidad.contains("ALU"),
#           EntidadORM.apellido != "",
#           EntidadORM.deleted_at.is_(None)
#           
#       ).all()
#       
#       # Mapeamos a EstudianteResponse
#       estudiantes = []
#       for est in estudiantes_db:
#           estudiantes.append(EstudianteResponse(
#               id=est.id_entidad,
#               name=f"{est.apellido}, {est.nombre}".strip(),
#               nombre=est.nombre,       # Asignamos nombre
#               apellido=est.apellido,   # Asignamos apellido
#               fec_nac=est.fec_nac,     # Asignamos fecha de nacimiento
#               email=est.email,
#               domicilio=est.domicilio,
#               telefono=est.telefono
#           ))
#       return estudiantes
#   
#   @app.get("/api/estudiantes/{id}", response_model=EstudianteResponse)
#   async def get_estudiante(id: int, db: Session = Depends(get_db)):
#       est = db.query(EntidadORM).filter(
#           EntidadORM.id_entidad == id,
#           EntidadORM.tipos_entidad.contains("ALU"),
#           EntidadORM.deleted_at.is_(None)
#       ).first()
#       
#       if not est:
#           raise HTTPException(status_code=404, detail="Estudiante no encontrado")
#       
#       return EstudianteResponse(
#           id=est.id_entidad,
#           name=f"{est.apellido}, {est.nombre}".strip(),
#           nombre=est.nombre,
#           apellido=est.apellido,
#           fec_nac=est.fec_nac,
#           email=est.email,
#           domicilio=est.domicilio,
#           telefono=est.telefono
#       )
#   
#   @app.post("/api/estudiantes/", response_model=EstudianteResponse)
#   async def create_estudiante(estudiante: EstudianteCreate, db: Session = Depends(get_db)):
#       # Verificar si el email ya existe (solo si se proporciona)
#       if estudiante.email and db.query(Entidad).filter(Entidad.email == estudiante.email).first():
#           raise HTTPException(status_code=400, detail="El email ya está registrado")
#       
#       # Separar nombre y apellido
#       # parts = estudiante.name.split(' ', 1)
#       # nombre = parts[0]
#       # apellido = parts[1] if len(parts) > 1 else ""
#       
#   
#       new_estudiante = Entidad(
#           nombre=estudiante.nombre.strip(),
#           apellido=estudiante.apellido.strip(),
#           email=estudiante.email,
#           fec_nac=estudiante.fec_nac,
#           domicilio=estudiante.domicilio,
#           telefono=estudiante.telefono,
#           tipos_entidad="ALU"
#       )
#       
#       db.add(new_estudiante)
#       db.commit()
#       db.refresh(new_estudiante)
#       
#       return EstudianteResponse(
#           id=new_estudiante.id_entidad,
#           name=f"{new_estudiante.apellido} {new_estudiante.nombre}".strip(),
#           nombre=new_estudiante.nombre,
#           apellido=new_estudiante.apellido,
#           fec_nac=new_estudiante.fec_nac,
#           email=new_estudiante.email,
#           domicilio=new_estudiante.domicilio,
#           telefono=new_estudiante.telefono
#       )
#   
#   @app.put("/api/estudiantes/{id}", response_model=EstudianteResponse)
#   async def update_estudiante(id: int, estudiante: EstudianteUpdate, db: Session = Depends(get_db)):
#       db_estudiante = db.query(Entidad).filter(Entidad.id_entidad == id).first()
#       
#       if not db_estudiante:
#           raise HTTPException(status_code=404, detail="Estudiante no encontrado")
#       
#       # Actualizar solo los campos que vengan
#       if estudiante.nombre is not None:
#           db_estudiante.nombre= estudiante.nombre.strip()
#       if estudiante.apellido is not None:
#           db_estudiante.apellido= estudiante.apellido.strip()
#       if estudiante.email is not None:
#           db_estudiante.email = estudiante.email
#       if estudiante.fec_nac is not None:
#           db_estudiante.fec_nac = estudiante.fec_nac
#       if estudiante.domicilio is not None:
#           db_estudiante.domicilio = estudiante.domicilio
#       if estudiante.telefono is not None:
#           db_estudiante.telefono = estudiante.telefono
#           
#       db.commit()
#       db.refresh(db_estudiante)
#       
#       return EstudianteResponse(
#           id=db_estudiante.id_entidad,
#           name=f"{db_estudiante.nombre} {db_estudiante.apellido}".strip(),
#           nombre=db_estudiante.nombre,
#           apellido=db_estudiante.apellido,
#           fec_nac=db_estudiante.fec_nac,
#           email=db_estudiante.email,
#           domicilio=db_estudiante.domicilio,
#           telefono=db_estudiante.telefono
#       )
#   
#   @app.delete("/api/estudiantes/{id}")
#   async def delete_estudiante(id: int, db: Session = Depends(get_db)):
#       db_estudiante = db.query(Entidad).filter(Entidad.id_entidad == id).first()
#       
#       if not db_estudiante:
#           raise HTTPException(status_code=404, detail="Estudiante no encontrado")
#       
#       db.delete(db_estudiante)
#       db.commit()
#       
#       return {"message": "Estudiante eliminado exitosamente"}
#   
#   # ==================== ENDPOINTS DOCENTES ====================
#   
#   @app.get("/api/docentes", response_model=list[DocenteResponse])
#   async def get_docentes(db: Session = Depends(get_db)):
#       
#       print("\n" + "="*60)
#       print("ENDPOINT DE DOCENTES EJECUTÁNDOSE CORRECTAMENTE")
#       print("="*60)
#       
#       # 1. Información de conexión y tabla
#       print(f"Base de datos conectada → {db.bind.url}")
#       print(f"Tabla usada → {EntidadORM.__tablename__}")
#       print("-"*60)
#   
#   
#       # Buscamos entidades que tengan 'DOC' en sus tipos_entidad
#       docentes_db = db.query(EntidadORM).filter(
#           EntidadORM.tipos_entidad.contains("DOC"),
#           EntidadORM.apellido != "",
#           EntidadORM.deleted_at.is_(None)
#           
#       ).all()
#       
#       # Mapeamos a DocentesResponse
#       docentes = []
#       for doc in docentes_db:
#           docentes.append(DocenteResponse(
#               id=doc.id_entidad,
#               name=f"{doc.apellido}, {doc.nombre}".strip(),
#               nombre=doc.nombre,       # Asignamos nombre
#               apellido=doc.apellido,   # Asignamos apellido
#               fec_nac=doc.fec_nac,     # Asignamos fecha de nacimiento
#               email=doc.email,
#               domicilio=doc.domicilio,
#               telefono=doc.telefono
#           ))
#       return docentes
#   
#   @app.get("/api/docentes/{id}", response_model=DocenteResponse)
#   async def get_docente(id: int, db: Session = Depends(get_db)):
#       doc = db.query(Entidad).filter(
#           Entidad.id_entidad == id,
#           Entidad.tipos_entidad.contains("DOC"),
#           Entidad.deleted_at.is_(None)
#       ).first()
#       
#       if not doc:
#           raise HTTPException(status_code=404, detail="Docente no encontrado")
#       
#       return DocenteResponse(
#           id=doc.id_entidad,
#           name=f"{doc.apellido}, {doc.nombre}".strip(),
#           nombre=doc.nombre,
#           apellido=doc.apellido,
#           fec_nac=doc.fec_nac,
#           email=doc.email,
#           domicilio=doc.domicilio,
#           telefono=doc.telefono
#       )
#   
#   @app.post("/api/docentes/", response_model=DocenteResponse)
#   async def create_docente(docente: DocenteCreate, db: Session = Depends(get_db)):
#   
#   
#       # Verificar si el email ya existe (solo si se proporciona)
#       if docente.email and db.query(Entidad).filter(Entidad.email == docente.email).first():
#           raise HTTPException(status_code=400, detail="El email ya está registrado")
#       
#       # Separar nombre y apellido
#       # parts = estudiante.name.split(' ', 1)
#       # nombre = parts[0]
#       # apellido = parts[1] if len(parts) > 1 else ""
#       
#   
#       new_docente = Entidad(
#           nombre=docente.nombre.strip(),
#           apellido=docente.apellido.strip(),
#           email=docente.email,
#           fec_nac=docente.fec_nac,
#           domicilio=docente.domicilio,
#           telefono=docente.telefono,
#           tipos_entidad="DOC"
#       )
#       
#       db.add(new_docente)
#       db.commit()
#       db.refresh(new_docente)
#       
#       return DocenteResponse(
#           id=new_docente.id_entidad,
#           name=f"{new_docente.apellido} {new_docente.nombre}".strip(),
#           nombre=new_docente.nombre,
#           apellido=new_docente.apellido,
#           fec_nac=new_docente.fec_nac,
#           email=new_docente.email,
#           domicilio=new_docente.domicilio,
#           telefono=new_docente.telefono
#       )
#   
#   @app.put("/api/docentes/{id}", response_model=DocenteResponse)
#   async def update_docente(id: int, docente: DocenteUpdate, db: Session = Depends(get_db)):
#       db_docente = db.query(Entidad).filter(Entidad.id_entidad == id).first()
#       
#       if not db_docente:
#           raise HTTPException(status_code=404, detail="Docente no encontrado")
#       
#       # Actualizar solo los campos que vengan
#       if docente.nombre is not None:
#           db_docente.nombre= docente.nombre.strip()
#       if docente.apellido is not None:
#           db_docente.apellido= docente.apellido.strip()
#       if docente.email is not None:
#           db_docente.email = docente.email
#       if docente.fec_nac is not None:
#           db_docente.fec_nac = docente.fec_nac
#       if docente.domicilio is not None:
#           db_docente.domicilio = docente.domicilio
#       if docente.telefono is not None:
#           db_docente.telefono = docente.telefono
#           
#       db.commit()
#       db.refresh(db_docente)
#       
#       return DocenteResponse(
#           id=db_docente.id_entidad,
#           name=f"{db_docente.nombre} {db_docente.apellido}".strip(),
#           nombre=db_docente.nombre,
#           apellido=db_docente.apellido,
#           fec_nac=db_docente.fec_nac,
#           email=db_docente.email,
#           domicilio=db_docente.domicilio,
#           telefono=db_docente.telefono
#       )
#   
#   @app.delete("/api/docentes/{id}")
#   async def delete_docente(id: int, db: Session = Depends(get_db)):
#       db_docente = db.query(Entidad).filter(Entidad.id_entidad == id).first()
#       
#       if not db_docente:
#           raise HTTPException(status_code=404, detail="Docente no encontrado")
#       
#       db.delete(db_docente)
#       db.commit()
#       
#       return {"message": "Docente eliminado exitosamente"}
#   
#   

# ==================== MIGRACIÓN DE BASE DE DATOS ====================
from sqlalchemy import text

@app.get("/api/migrate")
async def migrate_db(db: Session = Depends(get_db)):
    """
    Endpoint temporal para actualizar la estructura de la base de datos.
    Agrega las columnas email, domicilio y telefono a tbl_entidad.
    """
    try:
        # Intentar agregar columna email
        try:
            db.execute(text("ALTER TABLE tbl_entidad ADD COLUMN email VARCHAR(100)"))
        except Exception as e:
            print(f"Columna email ya existe o error: {e}")
            
        # Intentar agregar columna domicilio
        try:
            db.execute(text("ALTER TABLE tbl_entidad ADD COLUMN domicilio VARCHAR(200)"))
        except Exception as e:
            print(f"Columna domicilio ya existe o error: {e}")
            
        # Intentar agregar columna telefono
        try:
            db.execute(text("ALTER TABLE tbl_entidad ADD COLUMN telefono VARCHAR(50)"))
        except Exception as e:
            print(f"Columna telefono ya existe o error: {e}")

        # Intentar agregar columna fec_nac
        try:
            db.execute(text("ALTER TABLE tbl_entidad ADD COLUMN fec_nac DATE"))
        except Exception as e:
            print(f"Columna fec_nac ya existe o error: {e}")
            
        db.commit()
        return {"message": "Migración completada. Columnas agregadas si no existían."}
    except Exception as e:
        return {"error": str(e)}
    

  