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

from Routes.routes_materias import router as materias_router
from Routes.routes_periodos import router as periodos_router
from Routes.routes_estudiantes import router as routes_estudiantes
from Routes.routes_notas import router as notas_router

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


# Rutas de autenticación definidas en auth.py
app.include_router(auth.router, prefix="/api", tags=["Autenticación"])

# Esquema OAuth2 para autenticación (definido en auth.py)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# INCLUIR ROUTERS CON EL OBJETO 'router' DE CADA ARCHIVO
#   Endpoint para listar alumnos: http://localhost:8000/api/estudiantes/
app.include_router(
    routes_estudiantes, 
    prefix="/api/estudiantes", 
    tags=["Estudiantes"]
    )

app.include_router(notas_router, prefix="/api", tags=["Notas"])

app.include_router(routes_docentes.router, prefix="/api/docentes", tags=["Docentes"]) 

app.include_router(attendance_estudiantes.router, prefix="/api", tags=["Asistencias"])

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
    return 'iniciando api... - ESTOY EN LA CARPETA CORRECTA - V2'

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
    # rol_actual = current_user.tipo_rol.tipo_roles_usuarios
    rol_actual = current_user.tipo_rol.tipo_entidad

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
    

print("🔍 --- REVISIÓN DE RUTAS REGISTRADAS ---")
for route in app.routes:
    if hasattr(route, "path"):
        print(f"Ruta: {route.path} | Nombre: {route.name}")
print("🔍 ------------------------------------")

# Al final de todo en main.py
print("\n" + "="*50)
print("SISTEMA DE RUTAS ACTIVAS")
for route in app.routes:
    print(f"URL: {route.path} --> Name: {route.name}")
print("="*50 + "\n")

