# backend-master/schemas/__init__.py

# --- Expone los modelos de autenticación (UserCreate, UserAuthData, etc.) ---
# Reemplaza 'user_schema' con el nombre real de tu archivo si es diferente (ej: 'auth_schema')
from .user_schema import (
    UserCreate, 
    UserAuthData, 
    UserLogin,
    Token,
    # Puedes añadir más si otros archivos los importan directamente
)

# --- Expone los modelos de notas (que te causaron el error anterior) ---
from .nota_schema import NotaCreate, NotaResponse

# --- Exponer los modelos de negocio (Estudiantes, Docentes, etc.) ---
from .user_schema import ( # O el nombre del archivo que los contiene
    EstudianteResponse,
    DocenteResponse,
    TipoEntidad
)