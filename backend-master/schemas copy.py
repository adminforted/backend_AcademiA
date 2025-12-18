# Importamos las clases y tipos necesarios de Pydantic para definir esquemas
from pydantic import BaseModel, EmailStr  

# Importamos tipos de Python para manejar datos opcionales y listas
from typing import Optional, List

# Importamos tipos para fechas y horas
from datetime import date, datetime

# Esquema para la tabla tbl_tipo_usuario, usado para representar tipos de usuario (EST, DOC, ADM)
class TipoUsuario(BaseModel):
    cod_tipo_usuario: str   # Código del tipo de usuario (por ejemplo, 'EST'), obligatorio
    descripcion: str        # Descripción del tipo (por ejemplo, 'Estudiante'), obligatorio
    created_at: Optional[datetime] = None   # Fecha de creación, opcional (se llena desde la BD)
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    # Configuración para permitir la conversión desde objetos ORM (SQLAlchemy)
    class Config:
        from_attributes = True

# Esquema para la tabla tbl_tipo_entidad, usado para representar tipos de entidad (EST, DOC, CLI, etc.)
class TipoEntidad(BaseModel):
    cod_tipo_entidad: str   # Código del tipo de entidad (por ejemplo, 'EST'), obligatorio
    descripcion: str        # Descripción del tipo (por ejemplo, 'Alumno'), obligatorio
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    # Configuración para soportar objetos ORM
    class Config:
        from_attributes = True

# Esquema para representar un usuario en la base de datos, incluyendo sus tipos
class UserInDB(BaseModel):
    id: int             # ID del usuario, obligatorio
    name: str           # Nombre de usuario, obligatorio
    email: EmailStr     # Correo electrónico, validado como email, obligatorio
    is_email_verified: bool     # Indica si el email está verificado, obligatorio
    reset_token: Optional[str] = None       # Token para restablecer contraseña, opcional
    tipos_usuario: List[str]        # Lista de tipos de usuario (por ejemplo, ['EST', 'DOC']), obligatorio

    class Config:
        from_attributes = True

# Esquema para crear un nuevo usuario
class UserCreate(BaseModel):
    name: str           # Nombre de usuario, obligatorio
    email: EmailStr     # Correo electrónico, validado como email, obligatorio
    password: str       # Contraseña, obligatorio
    tipo_usuario: Optional[str] = 'EST'  # Tipo de usuario. Opcional. Por defecto 'EST'

# Esquema para actualizar un usuario existente
class UserUpdate(BaseModel):
    name: Optional[str] = None          # Nombre de usuario, opcional
    email: Optional[EmailStr] = None    # Correo electrónico, opcional
    password: Optional[str] = None      # Contraseña, opcional
    tipo_usuario: Optional[str] = None  # Tipo de usuario, opcional

# Esquema para la tabla tbl_entidad, usado para representar entidades (personas físicas)
class Entidad(BaseModel):
    id_entidad: int             # ID de la entidad, obligatorio
    usuario_id: Optional[int]   # ID del usuario asociado, opcional (entidades como CLI pueden no tener usuario)
    nombre: str                 # Nombre de la entidad, obligatorio
    apellido: str               # Apellido de la entidad, obligatorio
    email: Optional[str] = None
    domicilio: Optional[str] = None
    telefono: Optional[str] = None
    tipos_entidad: Optional[str] = None    # Lista de tipos de entidad (por ejemplo, ['EST', 'DOC']), obligatorio
    fec_nac: Optional[date] = None
    legajo: Optional[str] = None            # Legajo, específico para EST, opcional
    especialidad: Optional[str] = None      # Especialidad, específico para DOC, opcional
    cuit: Optional[str] = None              # CUIT, opcional
    cuenta_bancaria: Optional[str] = None   # Cuenta bancaria, opcional
    id_cliente: Optional[str] = None        # ID de cliente, específico para CLI, opcional
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None   # Fecha de actualización, opcional
    deleted_at: Optional[datetime] = None   # Fecha de eliminación lógica, opcional

    # Configuración para soportar objetos ORM
    class Config:
        from_attributes = True

# Esquemas para Estudiantes
class EstudianteCreate(BaseModel):

    # name: str  # Se usará para nombre y apellido - Se quita por ser redundante, ya que es nombre + apellido
    nombre: Optional[str] = None # Nuevo: Nombre separado
    apellido: Optional[str] = None # Nuevo: Apellido separado

    email: Optional[EmailStr] = None  # Email opcional
    fec_nac: Optional[date] = None  # Fecha de nacimiento
    domicilio: Optional[str] = None
    telefono: Optional[str] = None
    password: Optional[str] = None # Opcional, si se crea usuario asociado

class EstudianteUpdate(BaseModel):
    
    # name: Optional[str] = None #  Se quita por ser redundante, ya que es nombre + apellido
    nombre: Optional[str] = None # Nuevo: Nombre separado
    apellido: Optional[str] = None # Nuevo: Apellido separado

    email: Optional[EmailStr] = None
    fec_nac: Optional[date] = None
    domicilio: Optional[str] = None
    telefono: Optional[str] = None
    password: Optional[str] = None

class EstudianteResponse(BaseModel):
    id: int

    # name: Optional[str] = None   # Mantenemos name por compatibilidad #  Se quita por ser redundante, ya que es nombre + apellido
    nombre: Optional[str] = None # Nuevo: Nombre separado
    apellido: Optional[str] = None # Nuevo: Apellido separado

    fec_nac: Optional[date] = None # Nuevo: Fecha de nacimiento
    email: Optional[str] = None
    domicilio: Optional[str] = None
    telefono: Optional[str] = None
    
    class Config:
        from_attributes = True

# Esquemas para Docentes
class DocenteCreate(BaseModel):

    # name: str  # Se usará para nombre y apellido - Se quita por ser redundante, ya que es nombre + apellido
    nombre: Optional[str] = None # Nuevo: Nombre separado
    apellido: Optional[str] = None # Nuevo: Apellido separado

    email: Optional[EmailStr] = None  # Email opcional
    fec_nac: Optional[date] = None  # Fecha de nacimiento
    domicilio: Optional[str] = None
    telefono: Optional[str] = None
    password: Optional[str] = None # Opcional, si se crea usuario asociado

class DocenteUpdate(BaseModel):
    
    # name: Optional[str] = None #  Se quita por ser redundante, ya que es nombre + apellido
    nombre: Optional[str] = None # Nuevo: Nombre separado
    apellido: Optional[str] = None # Nuevo: Apellido separado

    email: Optional[EmailStr] = None
    fec_nac: Optional[date] = None
    domicilio: Optional[str] = None
    telefono: Optional[str] = None
    password: Optional[str] = None

class DocenteResponse(BaseModel):
    id: int

    # name: Optional[str] = None   # Mantenemos name por compatibilidad #  Se quita por ser redundante, ya que es nombre + apellido
    nombre: Optional[str] = None # Nuevo: Nombre separado
    apellido: Optional[str] = None # Nuevo: Apellido separado

    fec_nac: Optional[date] = None # Nuevo: Fecha de nacimiento
    email: Optional[str] = None
    domicilio: Optional[str] = None
    telefono: Optional[str] = None
    
    class Config:
        from_attributes = True

# Esquema para la solicitud de login
class LoginRequest(BaseModel):
    name: str           # Nombre de usuario, obligatorio
    password: str       # Contraseña, obligatorio
    tipo_usuario: str   # Tipo de usuario seleccionado para el login (por ejemplo, 'EST'), obligatorio

# Esquema para el token de autenticación
class Token(BaseModel):
    access_token: str
    token_type: str
    tipos_usuario: List[str]

# Esquema para la solicitud de verificación de email
class EmailVerifyRequest(BaseModel):
    token: str

# Esquema para la solicitud de olvido de contraseña
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

# Esquema para la solicitud de restablecimiento de contraseña
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str