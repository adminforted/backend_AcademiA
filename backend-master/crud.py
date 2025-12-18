
from sqlalchemy.orm import Session, joinedload
from models import User, TipoEntidad, TipoRolSistema 
from schemas import UserCreate, UserAuthData # <-- Usamos UserAuthData para current_user

# Importaciones que faltaban/eran incorrectas:
from auth import get_password_hash, generate_token
from fastapi import HTTPException, status
from typing import List, Optional


# ---------------------------------------------------------------------------------
# FUNCIONES DE LECTURA (GET)
# ----------------------------------------------------------------------------------


# Obtiene todos los usuarios
def c_get_users(db: Session, current_user: UserAuthData) -> List[UserAuthData]:

    # Definimos los roles de sistema que pueden listar usuarios
    # Solo ADMIN_SISTEMA (ID 1)
    ROLES_SISTEMA_PERMITIDOS = ['ADMIN_SISTEMA']

    try:
        # Acceder al Rol del Sistema
        rol_usuario = current_user.rol_sistema  
    
    except AttributeError:
            # Fallback si tipo_rol no existe o es None
            rol_usuario = None

    # Verificación si el rol logueado está dentro de los permitidos para listar usuarios
    if rol_usuario not in ROLES_SISTEMA_PERMITIDOS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=f"Permiso denegado. Sólo los roles {ROLES_SISTEMA_PERMITIDOS} pueden listar usuarios. Rol actual: {rol_usuario}"
        )
    
    #   if current_user.tipo_rol.tipo_entidad != 'ADMIN_SISTEMA':
    #       raise HTTPException(status_code=403, detail="Solo administradores pueden listar usuarios")
    
    # Si la verificación pasa, se listan los usuarios
    users = db.query(User).options(joinedload(User.rol_sistema_obj)).all()
    
    
    # Devolvemos la lista usando el esquema UserAuthData
    # Pydantic mapeará automáticamente user.tipo_rol a tipo_rol en UserAuthData
    return users

# Obtiene el usuario por su id
def c_get_user(db: Session, user_id: int, current_user: UserAuthData) -> UserAuthData:

    # Cargamos la relación TipoRol en la consulta
    user = db.query(User).options(joinedload(User.rol_sistema_obj)).filter(User.id_usuario == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user_rol_code = user.rol_sistema_obj.tipo_roles_usuarios # Rol del usuario solicitado
    current_rol_code = current_user.rol_sistema # Rol del usuario logueado (viene del token)
    
    # Lógica de permisos refactorizada para Rol Único
    
    # 1. El administrador puede ver a cualquiera
    if current_rol_code == 'ADMIN_SISTEMA':
        return user # Devuelve el objeto User que Pydantic mapeará
        
    # 2. El usuario solo puede verse a sí mismo
    if current_user.id_usuario == user.id_usuario:
        return user
        
    # 3. Permiso especial para Docentes (asumiendo que Docente puede ver Alumno)
    if current_rol_code == 'DOCENTE_APP' and user_rol_code == 'ALUMNO_APP':
        return user
        
    # Si ninguna regla aplica
    raise HTTPException(status_code=403, detail="No tienes permiso para ver este usuario")


# Obtiene el usuario por su nombre
def c_get_user_by_name(db: Session, name: str) -> Optional[User]:
    return db.query(User).filter(User.name == name).first()


# ----------------------------------------------------------------------------------
# FUNCIONES DE ESCRITURA (CREATE/UPDATE)
# ----------------------------------------------------------------------------------

# Permite crear un usuario nuevo
def c_create_user(db: Session, user: UserCreate):
    # La creación de usuario debe incluir el ID de TIPO DE ROL
    
    # Validación de existencia de usuario y email (sin cambios)
    if c_get_user_by_name(db, user.name):
        raise HTTPException(status_code=400, detail="El nombre ya está registrado")
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
        
    # Buscamos el ID del rol a asignar (necesario para la FK)
    # Asumimos que user.tipo_rol_code contiene el código de rol (ej. 'ALUMNO_APP')
    # tipo_rol_obj = db.query(TipoEntidad).filter(TipoEntidad.tipo_entidad == user.tipo_rol_code).first()
    tipo_rol_obj = db.query(TipoRolSistema).filter(TipoRolSistema.tipo_roles_usuarios == user.tipo_rol_code).first()
    tipo_rol_obj = db.query(TipoRolSistema).filter(TipoRolSistema.tipo_roles_usuarios == value).first()

    
    if not tipo_rol_obj:
        raise HTTPException(status_code=400, detail=f"Código de rol '{user.tipo_rol_code}' inválido.")
        
    hashed_password = get_password_hash(user.password)
    verification_token = generate_token()
    
    db_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        reset_token=verification_token,
        # 🚨 CAMBIO 3: Asignamos el ID de la FK
        id_tipo_roles_usuarios=tipo_rol_obj.id_tipo_roles_usuarios, 
        # Si tienes id_entidad aquí, agrégalo también
        id_entidad=user.id_entidad if hasattr(user, 'id_entidad') else None
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # 🚨 NOTA: DEBES ACTUALIZAR EL ESQUEMA UserCreate en schemas.py 
    # para que acepte el campo 'tipo_rol_code' o 'id_tipo_roles_usuarios'.
    
    return db_user, verification_token


# Permite actualizar un usuario existente
def c_update_user(db: Session, user_id: int, user_data: UserCreate, current_user: UserAuthData):
    # Usamos UserCreate como esquema de entrada, ajustando el nombre del argumento a 'user_data'
    db_user = db.query(User).options(joinedload(User.rol_sistema_obj)).filter(User.id_usuario == user_id).first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    current_rol_code = current_user.rol_sistema # Rol del usuario logueado
    db_user_rol_code = db_user.rol_sistema_obj.tipo_roles_usuarios # Rol del usuario a editar
    
    # Lógica de permisos de edición refactorizada
    # 1. Solo ADM puede editar a otros, excepto a sí mismo.
    if current_rol_code != 'ADMIN_SISTEMA' and current_user.id_usuario != user_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para editar este usuario")
        
    # 2. DOC no puede editar a ADM
    if current_rol_code == 'DOCENTE_APP' and db_user_rol_code == 'ADMIN_SISTEMA':
        raise HTTPException(status_code=403, detail="No tienes permiso para editar administradores")
        
    # Actualización de campos
    for key, value in user_data.dict(exclude_unset=True).items():
        if key == "password" and value:
            setattr(db_user, key, get_password_hash(value))
        
        # Actualizar el rol (si el código de rol es enviado)
        elif key == "tipo_rol_code" and value:
            tipo_rol_obj = db.query(TipoRolSistema).filter(TipoRolSistema.tipo_roles_usuarios == value).first()
            if tipo_rol_obj:
                # Usar el atributo correcto de la FK en el modelo User
                db_user.id_rol_sistema_fk = tipo_rol_obj.id_tipo_roles_usuarios # O rol_sistema_fk, según models.py
            else:
                raise HTTPException(status_code=400, detail=f"Código de rol '{value}' inválido para actualización.")
        
        # Actualizar cualquier otro campo (name, email, id_entidad, etc.)
        elif key not in ["id", "tipo_rol"]: 
             setattr(db_user, key, value)
             
    db.commit()
    db.refresh(db_user)
    return db_user


# Permite eliminar un usuario
def c_delete_user(db: Session, user_id: int, current_user: UserAuthData):
    db_user = db.query(User).filter(User.id_usuario == user_id).first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    # Verificación de rol simplificada
    if current_user.rol_sistema != 'ADMIN_SISTEMA':
        raise HTTPException(status_code=403, detail="Solo administradores pueden eliminar usuarios")
        
    # Solo borramos el usuario principal.
    
    db.delete(db_user)
    db.commit()
    return {"detail": "Usuario eliminado"}