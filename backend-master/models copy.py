# Importamos los tipos y funciones necesarias de SQLAlchemy para definir modelos ORM
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, DateTime  

# Para funciones como CURRENT_TIMESTAMP
from sqlalchemy.sql import func

# Para crear la base de modelos
from sqlalchemy.ext.declarative import declarative_base

# Definimos la base para todos los modelos ORM, que se usarán para mapear tablas
Base = declarative_base()

# Modelo para la tabla tbl_tipo_usuario, que almacena los tipos de usuario (EST, DOC, ADM)


class TipoUsuario(Base):
    __tablename__ = "tbl_tipo_usuario"  # Nombre de la tabla en la base de datos
    
    # Clave primaria, código del tipo de usuario (por ejemplo, 'EST')
    cod_tipo_usuario = Column(String(10), primary_key=True)
    # Descripción del tipo de usuario (por ejemplo, 'Estudiante'), no nulo
    descripcion = Column(String(100), nullable=False)
    # Fecha de creación, se establece automáticamente
    created_at = Column(DateTime, default=func.current_timestamp())
    # Fecha de actualización, se actualiza automáticamente
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    # Fecha de eliminación lógica, nullable para soft deletes
    deleted_at = Column(DateTime, nullable=True)

# Modelo para la tabla tbl_tipo_entidad, que almacena los tipos de entidad (EST, DOC, CLI, etc.)
class TipoEntidad(Base):
    __tablename__ = "tbl_tipo_entidad"  # Nombre de la tabla
    # Clave primaria, código del tipo de entidad (por ejemplo, 'EST')
    cod_tipo_entidad = Column(String(10), primary_key=True)
    # Descripción del tipo de entidad (por ejemplo, 'Alumno'), no nulo
    descripcion = Column(String(100), nullable=False)
    # Fecha de creación
    created_at = Column(DateTime, default=func.current_timestamp())
    # Fecha de actualización
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    # Fecha de eliminación lógica
    deleted_at = Column(DateTime, nullable=True)

# Modelo para la tabla usuarios, que almacena los datos de autenticación
class User(Base):
    __tablename__ = "tbl_usuarios"  # Nombre de la tabla
    # Clave primaria, identificador único del usuario
    id = Column(Integer, primary_key=True, index=True)
    # Nombre de usuario, único y no nulo
    name = Column(String(100), unique=True, nullable=False)
    # Correo electrónico, único y no nulo
    email = Column(String(100), unique=True, nullable=False)
    # Contraseña hasheada, no nula
    password = Column(String(100), nullable=False)
    # Indica si el email está verificado, por defecto False
    is_email_verified = Column(Boolean, default=False)
    # Token para restablecer contraseña, nullable
    reset_token = Column(String(255), nullable=True)

# Modelo para la tabla tbl_entidad, que almacena datos de entidades (personas físicas)
class Entidad(Base):
    __tablename__ = "tbl_entidad"  # Nombre de la tabla
    # Clave primaria, identificador único de la entidad
    id_entidad = Column(Integer, primary_key=True, index=True)
    # Clave foránea que vincula a la tabla usuarios, nullable (entidades como CLI pueden no tener usuario)
    usuario_id = Column(Integer, ForeignKey("tbl_usuarios.id"), nullable=True)
    # Nombre de la entidad, no nulo
    nombre = Column(String(100), nullable=False)
    # Apellido de la entidad, no nulo
    apellido = Column(String(100), nullable=False)
    # Email de contacto
    email = Column(String(100), nullable=True)
    # Domicilio
    domicilio = Column(String(200), nullable=True)
    # Teléfono
    telefono = Column(String(50), nullable=True)
    # Tipos de entidad (por ejemplo, 'EST,DOC'), almacenados como texto separado por comas
    tipos_entidad = Column(String(100), nullable=True)
    # Fecha de nacimiento, nullable
    fec_nac = Column(Date, nullable=True)
    # Legajo, específico para EST, nullable
    legajo = Column(String(50), nullable=True)
    # Especialidad, específico para DOC, nullable
    especialidad = Column(String(100), nullable=True)
    # CUIT, específico para PROV, nullable
    cuit = Column(String(20), nullable=True)
    # Cuenta bancaria, específico para PROV, nullable
    cuenta_bancaria = Column(String(100), nullable=True)
    # ID de cliente, específico para CLI, nullable
    id_cliente = Column(String(50), nullable=True)
    # Fecha de creación
    created_at = Column(DateTime, default=func.current_timestamp())
    # Fecha de actualización
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    # Fecha de eliminación lógica
    deleted_at = Column(DateTime, nullable=True)

# Modelo para la tabla tbl_usuario_tipos, que relaciona usuarios con sus tipos (múltiples por usuario)
class UsuarioTipos(Base):
    __tablename__ = "tbl_usuario_tipos"  # Nombre de la tabla
    # Clave foránea y primaria, vincula al usuario
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), primary_key=True)
    # Clave foránea y primaria, vincula al tipo de usuario
    cod_tipo_usuario = Column(String(10), ForeignKey("tbl_tipo_usuario.cod_tipo_usuario"), primary_key=True)

# Modelo para la tabla tbl_materia
class Materia(Base):
    __tablename__ = "tbl_materia"
    
    id_materia = Column(Integer, primary_key=True)
    nombre_materia_id = Column(Integer, ForeignKey("tbl_nombre_materia.id_nombre_materia"), nullable=False)
    curso_id = Column(Integer, ForeignKey("tbl_curso.id_curso"), nullable=False)
    docente_id = Column(Integer, ForeignKey("tbl_entidad.id_entidad"), nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    deleted_at = Column(DateTime, nullable=True)

# Modelo para la tabla tbl_nombre_materia
class NombreMateria(Base):
    __tablename__ = "tbl_nombre_materia"
    
    id_nombre_materia = Column(Integer, primary_key=True)
    nombre_materia = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    deleted_at = Column(DateTime, nullable=True)


# Modelo para la tabla tbl_curso (opcional pero útil para extender después)
class Curso(Base):
    __tablename__ = "tbl_curso"
    
    id_curso = Column(Integer, primary_key=True)
    curso = Column(String(50), nullable=False)
    division = Column(String(10), nullable=False)
    ciclo_lectivo = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    deleted_at = Column(DateTime, nullable=True)

# Modelo para la tabla tbl_inscripcion
class Inscripcion(Base):
    __tablename__ = "tbl_inscripcion"
    
    id_inscripcion = Column(Integer, primary_key=True)
    entidad_id = Column(Integer, ForeignKey("tbl_entidad.id_entidad"), nullable=False)
    materia_id = Column(Integer, ForeignKey("tbl_materia.id_materia"), nullable=False)
    tipo_inscripcion_id = Column(Integer, ForeignKey("tbl_tipo_inscripcion.id_tipo_inscripcion"), nullable=False)
    fecha_inscripcion = Column(Date, nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    deleted_at = Column(DateTime, nullable=True)