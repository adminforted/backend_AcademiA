
# backend-master\models.py

# Importamos los tipos y funciones necesarias de SQLAlchemy para definir modelos ORM
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, DateTime, Float 

# Para funciones como CURRENT_TIMESTAMP
from sqlalchemy.sql import func

from sqlalchemy.orm import relationship

# Para crear la base de modelos
from sqlalchemy.ext.declarative import declarative_base

# Definimos la base para todos los modelos ORM, que se usarán para mapear tablas
Base = declarative_base()


# Definición del Modelo de la tabla tbl_tipo_entidad, que almacena los tipos de entidad (EST, DOC, CLI, etc.)
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

    @property
    def rol_sistema(self):
        # Esta propiedad traduce el objeto complejo al texto simple 'ADMIN_SISTEMA'
        return self.rol_sistema_obj.tipo_roles_usuarios if self.rol_sistema_obj else None
    
    # Renombramos la columna FK para evitar ambigüedades
    # Usamos 'id_tipo_entidad_fk' como el nombre de la columna en BD
    # Y la llamaremos id_rol_sistema_fk en Python para evitar confusión con el rol de Entidad.
    id_rol_sistema_fk = Column(
        'id_tipo_entidad_fk', # <--- Nombre de la columna en BD
        Integer, 
        ForeignKey('t_tipo_roles_usuarios.id_tipo_roles_usuarios'), 
        nullable=False
    )
    
    # 🚨 RELACIÓN 1: ROL DEL SISTEMA (la que buscamos para el 403)
    rol_sistema_obj = relationship(
        "TipoRolSistema", 
        back_populates="usuarios_con_rol_sistema",
        # Usamos el nombre de la FK en Python para la relación
        foreign_keys=[id_rol_sistema_fk] 
    )

    

    # Fecha de creación, se establece automáticamente
    created_at = Column(DateTime, default=func.current_timestamp())
    # Fecha de actualización, se actualiza automáticamente
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    # Fecha de eliminación lógica, nullable para soft deletes
    deleted_at = Column(DateTime, nullable=True)

# ----------------------------------------------------------------------------------
# CLASE DE ROLES DEL SISTEMA (t_tipo_roles_usuarios)
# ----------------------------------------------------------------------------------
class TipoRolSistema(Base): # <--- Nuevo nombre de clase
    __tablename__ = "t_tipo_roles_usuarios"

    id_tipo_roles_usuarios = Column(Integer, primary_key=True, nullable=False, index=True)
    # ESTE ES EL CAMPO QUE BUSCAMOS: 'ADMIN_SISTEMA', 'ALUMNO_APP', etc.
    tipo_roles_usuarios = Column(String(20), nullable=False, unique=True) 
    
    # Relación inversa a User
    usuarios_con_rol_sistema = relationship("User", back_populates="rol_sistema_obj")


# ----------------------------------------------------------------------------------
#  CLASE DE ENTIDADES DE NEGOCIO (Entidad)
# Modelo para la tabla t_entidad, que almacena datos de entidades (personas físicas)
# ----------------------------------------------------------------------------------
class Entidad(Base):
    __tablename__ = "t_entidad"  # Nombre de la tabla
    # Clave primaria, identificador único de la entidad
    id_entidad = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
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
    # Celular
    cel = Column(String(50), nullable=True)
    # DNI
    dni = Column(Integer, nullable=False)
    # Legajo, específico para Estudiantes
    legajo = Column(String(50), nullable=True)
    # Fecha de eliminación lógica
    deleted_at = Column(DateTime, nullable=True)
    # CUIT, específico para PROV, nullable
    cuit = Column(String(11), nullable=True)
    


# ----------------------------------------------------------------------------------
# MODELOS PARA MATERIAS
# ----------------------------------------------------------------------------------

# Modelo para la tabla t_materia
class Materia(Base):
    __tablename__ = "t_materia"
    
    id_materia = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    id_nombre_materia = Column(Integer, ForeignKey("t_nombre_materia.id_nombre_materia"), nullable=False)
    id_curso = Column(Integer, ForeignKey("t_curso.id_curso"), nullable=False)
    id_entidad = Column(Integer, ForeignKey("t_entidad.id_entidad"), nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

    # --- RELACIONES ---
    # Con el nombre (Matemática, Lengua, etc.)
    nombre = relationship("NombreMateria", back_populates="materias_vinculadas")
    
    # Con el Curso (para llegar a Ciclo y Plan)
    curso = relationship("Curso") 
    
    # Con el Docente (Entidad)
    docente = relationship("Entidad")


# Modelo para la tabla tbl_nombre_materia
class NombreMateria(Base):
    __tablename__ = "t_nombre_materia"
    
    id_nombre_materia = Column(Integer, primary_key=True)
    nombre_materia = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relaciones
    # Para crear relacion bidireccional con Materia
    materias_vinculadas = relationship("Materia", back_populates="nombre") 


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

# ----------------------------------------------------------------------------------
# MODELOS PARA ASISTENCIAS
# ----------------------------------------------------------------------------------

  # Definir la tabla de Tipos
class TipoInasistencia(Base):
    __tablename__ = "t_tipo_inasistencia"  # <--- Nombre de la tabla de tipos
    
    id_tipo_inasistencia = Column(Integer, primary_key=True)
    descripcion = Column(String(50)) # Ej: "Completa", "Media"
    valor = Column(Float)      

# Modelo para la tabla t_inasistencia
class Inasistencia(Base):
    __tablename__ = "t_inasistencia"
    id_inasistencia = Column(Integer, primary_key=True)
    id_entidad = Column(Integer, ForeignKey("t_entidad.id_entidad")) # Relación con estudiante
    id_curso = Column(Integer, ForeignKey("t_curso.id_curso")) # Relación con Curso
    id_materia = Column(Integer, ForeignKey("t_materia.id_materia")) # Relación con Materia
    fecha_inasistencia = Column(Date)
    id_tipo_inasistencia = Column(Integer, ForeignKey("t_tipo_inasistencia.id_tipo_inasistencia")) # Relación con Tipo de asistencia
    
    # Relación (Magia de SQLAlchemy para acceder a .tipo_obj.valor)
    tipo_obj = relationship("TipoInasistencia") 
    justificada = Column(Boolean, default=False)
    motivo_inasistencia = Column(String(255))

        # Ej: 1.0, 0.5


# ----------------------------------------------------------------------------------
# MODELOS PARA TIPOS Y PERIODOS (Necesarios para la FK de TNota)
# ----------------------------------------------------------------------------------

# Modelo para la tabla t_periodo
class Periodo(Base):
    __tablename__ = "t_periodo"
    
    id_periodo = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nombre_periodo = Column(String(100), nullable=False)    # Ej: "1er Trimestre", "Final"
    fecha_inicio_periodo = Column(Date, nullable=False)
    fecha_fin_periodo = Column(Date, nullable=False)
    # created_at = Column(DateTime, default=func.current_timestamp())
    # updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

# Modelo para la tabla t_tipo_nota
class TipoNota(Base):
    __tablename__ = "t_tipo_nota"
    
    id_tipo_nota = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tipo_nota = Column(String(20), nullable=False) # Ej: "Calificación Normal", "Recuperatorio"

# ----------------------------------------------------------------------------------
# MODELO ORM PRINCIPAL DE NOTAS
# ----------------------------------------------------------------------------------

# Modelo para la tabla t_nota
class Nota(Base):
    __tablename__ = "t_nota"
    
    # Clave primaria (Auto-generada)
    id_nota = Column(Integer, primary_key=True, index=True)
    
    # ------------------
    # CAMPOS DEL FRONTEND
    # ------------------
    # FK a Materia
    id_materia = Column(Integer, ForeignKey("t_materia.id_materia"), nullable=False)
    # FK a Estudiante (es una Entidad)
    id_entidad_estudiante = Column(Integer, ForeignKey("t_entidad.id_entidad"), nullable=False)
    # Valor de la nota
    nota = Column(Float, nullable=False)
    # FK a Período (catalogo)
    id_periodo = Column(Integer, ForeignKey("t_periodo.id_periodo"), nullable=False)
    
    # ------------------
    # CAMPOS DE AUDITORÍA Y BACKEND
    # ------------------
    # FK a Tipo de Nota (catalogo)
    id_tipo_nota = Column(Integer, ForeignKey("t_tipo_nota.id_tipo_nota"), nullable=False)
    # Fecha de carga (se genera automáticamente al insertar)
    fecha_carga = Column(Date, default=func.now(), nullable=False)
    # FK a la Entidad que carga la nota (ej. el Docente o Admin logueado)
    id_entidad_carga = Column(Integer, ForeignKey("t_entidad.id_entidad"), nullable=False)
    
    # ------------------
    # RELACIONES ORM (Opcional, pero recomendada)
    # ------------------
    materia = relationship("Materia")
    estudiante = relationship("Entidad", foreign_keys=[id_entidad_estudiante])
    cargador = relationship("Entidad", foreign_keys=[id_entidad_carga])
    periodo_obj = relationship("Periodo")
    tipo_nota_obj = relationship("TipoNota")
    
    # ------------------
    # CAMPOS DE CONTROL (Auditoría)
    # ------------------
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

# ----------------------------------------------------------------------------------
# MODELO CICLOS LECTIVOS
# ----------------------------------------------------------------------------------
class CicloLectivo(Base):
    __tablename__ = "t_ciclo_lectivo"
    id_ciclo_lectivo = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    nombre_ciclo_lectivo = Column(String(100), nullable=True)
    fecha_inicio_cl = Column(Date, nullable=True)
    fecha_fin_cl = Column(Date, nullable=True)
    id_plan = Column(Integer, ForeignKey("t_plan.id_plan"), nullable=True)

    # RELACIONES 
    plan = relationship("Plan")     # Un ciclo pertenece a un plan
    cursos = relationship("Curso", back_populates="ciclo")      

# ----------------------------------------------------------------------------------
# MODELO PLAN
# ----------------------------------------------------------------------------------
class Plan(Base):
    __tablename__ = "t_plan"
    id_plan = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    nombre_plan = Column(String(50), nullable=False)
    vigencia_desde= Column(Date, nullable=False)
    vigencia_hasta= Column(Date, nullable=True)
    resolucion_nro = Column(String(30), nullable=False)
    
    # Relación inversa 
    ciclos = relationship("CicloLectivo", back_populates="plan")

# ----------------------------------------------------------------------------------
# MODELO CURSOS
# ----------------------------------------------------------------------------------
class Curso(Base):
    __tablename__ = "t_curso"
    id_curso = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    curso = Column(String(50), nullable=False)
    id_ciclo_lectivo = Column(Integer, ForeignKey("t_ciclo_lectivo.id_ciclo_lectivo"))
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=True)

    # Relación: Un curso pertenece a un ciclo
    ciclo = relationship("CicloLectivo", back_populates="cursos")   # Busca "cursos" en CicloLectivo