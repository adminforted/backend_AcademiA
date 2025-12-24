# backend-master\schemas.py

# Importamos las clases y tipos necesarios de Pydantic para definir esquemas
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime


# -------------------------
# NUEVOS ESQUEMAS DE ROL
# -------------------------

class TipoRolResponse(BaseModel):
    tipo_entidad: str = Field(alias="cod_tipo_usuario")
    # La variable Python es tipo_entidad
    class Config:
        populate_by_name = True


# -------------------------------------------------------------
# ESQUEMAS CENTRALES DE AUTENTICACIÓN 
# -------------------------------------------------------------

# 1. Esquema de Entrada para Login (Lo que el cliente envía)
class UserLogin(BaseModel):
    name: str  # Nombre de usuario
    password: str # Contraseña

# 2. Esquema de Carga Útil del Token y Respuesta de Usuario
class UserAuthData(BaseModel):
    id_usuario: int
    name: str
    email: EmailStr
    is_email_verified: bool
    
    # Rol del Sistema (directamente del JWT)
    rol_sistema: Optional[str] = None # Contendrá "ADMIN_SISTEMA", "ALUMNO_APP", etc.
    
    # Relación TipoRol para la Entidad de Negocios
    tipo_rol: Optional[TipoRolResponse] = None
    
    # ID de la entidad (opcional, NULL para Admins Puros)
    id_entidad: Optional[int] = None 
    
    # Campos de gestión de cuentas
    email: Optional[EmailStr] = None 
    is_email_verified: bool
    
    class Config:
        # Permite a Pydantic mapear los campos desde el modelo ORM (SQLAlchemy)
        from_attributes = True # En Pydantic v2+ es from_attributes=True, si usas v1 es orm_mode=True

# 3. Esquema de Respuesta del Login
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    # Incluimos los datos de usuario para que el frontend sepa quién es y qué rol tiene
    user: UserAuthData 

# -------------------------------------------------------------
# ESQUEMAS DE GESTIÓN DE CUENTAS
# -------------------------------------------------------------

# Esquema para crear un nuevo usuario
class UserCreate(BaseModel):
    name: str 
    email: EmailStr 
    password: str 
    
    # Campo para la Clave Foránea (FK) del rol.
    # Usamos 'tipo_rol_code' para que sea más explícito al crear.
    tipo_rol_code: Optional[str] = 'ALUMNO_APP' 

    # Incluimos id_entidad si el endpoint de creación lo va a manejar
    # (Ej. un administrador crea un usuario asociado a una Entidad existente)
    id_entidad: Optional[int] = None
    
    class Config:
        # Se requiere esto si usas el esquema para recibir datos en un PUT/PATCH
        from_attributes = True

# Esquema para la solicitud de olvido de contraseña
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

# Esquema para la solicitud de restablecimiento de contraseña
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

# Esquema para la solicitud de verificación de email
class EmailVerifyRequest(BaseModel):
    token: str

# -------------------------------------------------------------
# ESQUEMAS DE NEGOCIO 
# -------------------------------------------------------------

# Esquema para la tabla t_tipo_entidad
class TipoEntidad(BaseModel):
    # Aquí puedes usar id_tipo_entidad si es la PK en lugar de cod_tipo_entidad
    id_tipo_entidad: int
    tipo_entidad: str        # El nombre de la columna en BD
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Esquema para la tabla t_entidad (Eliminamos usuario_id si la FK está en t_usuarios)
class Entidad(BaseModel):
    id_entidad: int             
    # ELIMINAR O COMENTAR: usuario_id: Optional[int]   
    nombre: str                 
    apellido: str               
    email: Optional[str] = None
    domicilio: Optional[str] = None
    # ... (el resto de campos de Entidad sin cambios)
    
    class Config:
        from_attributes = True

# =========================================================================
# === ESQUEMAS PARA ESTUDIANTES (EstudiantesRoutes) ===
# =========================================================================

class EstudianteBase(BaseModel):
    nombre: str
    apellido: str
    fec_nac: Optional[date] = None
    email: Optional[str] = None
    domicilio: Optional[str] = None
    telefono: Optional[str] = None
    
class EstudianteCreate(EstudianteBase):
    pass

class EstudianteUpdate(EstudianteBase):
    pass

class EstudianteResponse(EstudianteBase):
    id: int
    name: str # Campo calculado: "Apellido, Nombre"
    
    class Config:
        from_attributes = True


# =========================================================================
# === ESQUEMAS PARA DOCENTES (DocentesRoutes) ===
# =========================================================================

class DocenteBase(BaseModel):
    nombre: str
    apellido: str
    fec_nac: Optional[date] = None
    email: Optional[str] = None
    domicilio: Optional[str] = None
    telefono: Optional[str] = None

class DocenteCreate(DocenteBase):
    pass

class DocenteUpdate(DocenteBase):
    pass

class DocenteResponse(DocenteBase):
    id: int
    name: str
    
    class Config:
        from_attributes = True



        #  backend-master\schemas\nota_schema.py

# =========================================================================
#   === Esquema para NOTAS. Creación (Input desde el Front-end)
# =========================================================================

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
        from_attributes = True

# ----------------------------------------------------
#   === Esquema para NOTAS. Respuesta NOTAS (Output hacia el Front-end)
# ----------------------------------------------------
class NotaResponse(NotaCreate):
    """Define la estructura de la Nota una vez que ha sido guardada en la DB."""

    # Campos que la DB asigna automáticamente
    id_nota: int = Field(..., description="ID único autogenerado de la nota.")
    id_entidad_carga: int = Field(..., description="ID de la entidad docente/usuario que cargó la nota.")
    id_tipo_nota: int = Field(..., description="Tipo de nota (ej: Normal, Recuperatorio).")
    fecha_carga: date = Field(..., description="Fecha en que se cargó la nota.")

    class Config:
        from_attributes = True

# ----------------------------------------------------
#   === Esquema para Ciclos Lectivos === 
# ----------------------------------------------------

class CicloLectivoResponse(BaseModel):
    id_ciclo_lectivo: int
    nombre_ciclo_lectivo: Optional[str] = None  # Ej: "2024", "2025"
    fecha_inicio_cl: Optional[date] = None
    fecha_fin_cl: Optional[date] = None
    id_plan: Optional[int] = None
    
    class Config:
        from_attributes = True # Esto permite leer modelos de SQLAlchemy