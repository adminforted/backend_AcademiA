# Importamos los tipos y funciones necesarias de SQLAlchemy para definir modelos ORM
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, DateTime  

# Para funciones como CURRENT_TIMESTAMP
from sqlalchemy.sql import func

from sqlalchemy.orm import relationship

# Para crear la base de modelos
from sqlalchemy.ext.declarative import declarative_base

# Definimos la base para todos los modelos ORM, que se usarán para mapear tablas
Base = declarative_base()



# Definici{on del mModelo de la tabla tbl_tipo_entidad, que almacena los tipos de entidad (EST, DOC, CLI, etc.)
class TipoEntidad(Base):
    __tablename__ = "t_tipo_entidad"  # Nombre de la tabla

    # Clave primaria, código del tipo de entidad. Es referenciada en Entidad.id_tipo_entidad
    id_tipo_entidad = Column(Integer, primary_key=True, nullable=False, index=True)
    # Campo que contiene la etiqueta de texto ('ALU', 'DOC', 'ADMIN')
    tipo_entidad = Column(String(50), nullable=True, unique=True) 
    # Fecha de creación
    created_at = Column(DateTime, default=func.current_timestamp())
    # Fecha de actualización
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    # Fecha de eliminación lógica
    deleted_at = Column(DateTime, nullable=True)


# Modelo para la tabla de roles de referencia
class TipoRol(Base):
    __tablename__ = 't_tipo_roles_usuarios'
    
    # El nombre de la PK en tu DB es 'id_tipo_roles_usuarios'
    id_tipo_roles_usuarios = Column(Integer, primary_key=True, index=True) 
    
    # El nombre de la columna que contiene el código del rol es 'tipo_roles_usuarios'
    tipo_roles_usuarios = Column('tipo_roles_usuarios', String(20), unique=True, nullable=False) 
    
    # La tabla t_tipo_roles_usuarios solo tiene dos columnas,
    # por lo que no tenemos una 'descripcion' para mapear.
    
    # Define la relación inversa con User
    usuarios = relationship("User", back_populates="tipo_rol")


# Modelo para la tabla t_usuarios, que almacena los datos de autenticación y el rol de la app
class User(Base):
    __tablename__ = "t_usuarios"  # Nombre de la tabla
    
    # Clave primaria, identificador único del usuario
    id_usuario = Column(Integer, primary_key=True, index=True)

    # Clave Foránea OPCIONAL a la Entidad
    id_entidad = Column(Integer, ForeignKey("t_entidad.id_entidad"), nullable=True)

    # Datos de Autenticación
    # Nombre de usuario, único y no nulo
    name = Column(String(100), unique=True, nullable=False)
    # Contraseña, no nula
    password = Column(String(255), nullable=False)
    
    # Campos de Gestión de Cuentas
    # Correo electrónico, único y no nulo
    email = Column(String(150), unique=True, nullable=False)
    # Indica si el email está verificado, por defecto False
    is_email_verified = Column(Boolean, default=False)
    # Token para restablecer contraseña, nullable
    reset_token = Column(String(255), nullable=True)

    # Clave Foránea que apunta a t_tipo_roles_usuarios
    id_tipo_rol_usuario_fk = Column(
        'id_tipo_roles_usuarios', # 🌟 Mapeo al nombre de la columna real que agregarás a t_usuarios
        Integer, 
        ForeignKey('t_tipo_roles_usuarios.id_tipo_roles_usuarios'), 
        nullable=False
    )
    
    # Definimos la relación con TipoRol
    tipo_rol = relationship("TipoEntidad", back_populates="usuarios")

    # Fecha de creación, se establece automáticamente
    created_at = Column(DateTime, default=func.current_timestamp())
    # Fecha de actualización, se actualiza automáticamente
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    # Fecha de eliminación lógica, nullable para soft deletes
    deleted_at = Column(DateTime, nullable=True)

# ----------------------------------------------------------------------------------
#  CLASE DE ENTIDADES DE NEGOCIO (Entidad)
# Modelo para la tabla t_entidad, que almacena datos de entidades (personas físicas)
# ----------------------------------------------------------------------------------
class Entidad(Base):
    __tablename__ = "t_entidad"  # Nombre de la tabla
    # Clave primaria, identificador único de la entidad
    id_entidad = Column(Integer, primary_key=True, index=True)
    # Nombre de la entidad, no nulo
    nombre = Column(String(100), nullable=False)
    # Apellido de la entidad, no nulo
    apellido = Column(String(100), nullable=False)
    # Fecha de Nacimiento
    fec_nac = Column(Date, nullable=True)

    # Relación ORM. Permite usar .join(TipoEntidad) y EntidadORM.tipo_entidad
    id_tipo_entidad = Column(Integer, ForeignKey('t_tipo_entidad.id_tipo_entidad'))
    # Tipos de entidad. Clave foránea. Columna que enlaza con t_tipo_entidad
    tipo_entidad = relationship("TipoEntidad")

    # Domicilio
    domicilio = Column(String(200), nullable=True)
    # Teléfono
    telefono = Column(String(50), nullable=True)
    # Fecha de creación
    created_at = Column(DateTime, default=func.current_timestamp())
    # Fecha de actualización
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    # Localidad
    localidad = Column(String(50), nullable=False)
    # Nacionalidad
    nacionalidad = Column(String(50), nullable=False)
    # Email de contacto
    email = Column(String(100), nullable=True)
    # DNI
    dni = Column(Integer, nullable=False)
    # Legajo, específico para Estudiantes
    legajo = Column(String(50), nullable=True)
    # Fecha de eliminación lógica
    deleted_at = Column(DateTime, nullable=True)
    # CUIT, específico para PROV, nullable
    cuit = Column(String(11), nullable=True)
   

"""
# Modelo para la tabla tbl_usuario_tipos, que relaciona usuarios con sus tipos (múltiples por usuario)
class UsuarioTipos(Base):
    __tablename__ = "tbl_usuario_tipos"  # Nombre de la tabla
    # Clave foránea y primaria, vincula al usuario
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), primary_key=True)
    # Clave foránea y primaria, vincula al tipo de usuario
    cod_tipo_usuario = Column(String(10), ForeignKey("tbl_tipo_usuario.cod_tipo_usuario"), primary_key=True)
"""

# Modelo para la tabla t_materia
class Materia(Base):
    __tablename__ = "t_materia"
    
    id_materia = Column(Integer, primary_key=True)
    id_nombre_materia = Column(Integer, ForeignKey("t_nombre_materia.id_nombre_materia"), nullable=False)
    id_nombre_curso = Column(Integer, ForeignKey("t_nombre_curso.id_nombre_curso"), nullable=False)
    id_entidad = Column(Integer, ForeignKey("t_entidad.id_entidad"), nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

# Modelo para la tabla tbl_nombre_materia
class NombreMateria(Base):
    __tablename__ = "t_nombre_materia"
    
    id_nombre_materia = Column(Integer, primary_key=True)
    nombre_materia = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())


# Modelo para la tabla t_inscripciones
class Inscripcion(Base):
    __tablename__ = "t_inscripciones"
    
    id_inscripcion = Column(Integer, primary_key=True)
    id_entidad = Column(Integer, ForeignKey("t_entidad.id_entidad"), nullable=False)
    id_materia = Column(Integer, ForeignKey("t_materia.id_materia"), nullable=False)
    id_tipo_insc = Column(Integer, ForeignKey("t_tipo_inscripcion.id_tipo_insc"), nullable=False)
    fecha_insc = Column(Date, nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    deleted_at = Column(DateTime, nullable=True)