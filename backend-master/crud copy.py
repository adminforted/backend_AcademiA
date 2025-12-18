from sqlalchemy.orm import Session
from models import User, UsuarioTipos
#from schemas import UserData_schema

from schemas import UserCreate, UserUpdate, UserInDB
from auth import get_password_hash, generate_token
from fastapi import HTTPException


# Obtine todos los usuarios
def c_get_users(db: Session, current_user: UserInDB):
    if current_user.role != UserRole.superusuario:
        raise HTTPException(status_code=403, detail="Solo superusuarios pueden listar usuarios")
    return db.query(User).all()



# Obtiene todos los usuarios
def c_get_users(db: Session, current_user: UserInDB):
    if 'ADM' not in current_user.tipos_usuario:
        raise HTTPException(status_code=403, detail="Solo administradores pueden listar usuarios")
    return db.query(User).all()

# Obtiene el usuario por su id
def c_get_user(db: Session, user_id: int, current_user: UserInDB):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user_tipos = [ut.cod_tipo_usuario for ut in db.query(UsuarioTipos).filter(UsuarioTipos.usuario_id == user_id).all()]
    if 'ADM' in current_user.tipos_usuario:
        user.tipos_usuario = user_tipos
        return user
    if current_user.id == user_id:
        user.tipos_usuario = user_tipos
        return user
    if 'DOC' in current_user.tipos_usuario and 'EST' in user_tipos:
        user.tipos_usuario = user_tipos
        return user
    raise HTTPException(status_code=403, detail="No tienes permiso para ver este usuario")

# Obtiene el usuario por su nombre
def c_get_user_by_name(db: Session, name: str):
    return db.query(User).filter(User.name == name).first()

# Permite crear un usuario nuevo
def c_create_user(db: Session, user: UserCreate):
    db_user = db.query(User).filter(User.name == user.name).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El nombre ya está registrado")
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    hashed_password = get_password_hash(user.password)
    verification_token = generate_token()
    db_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        reset_token=verification_token
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # Asignar tipo de usuario (por ejemplo, EST por defecto)
    db.add(UsuarioTipos(usuario_id=db_user.id, cod_tipo_usuario=user.tipo_usuario or 'EST'))
    db.commit()
    return db_user, verification_token

# Permite actualizar un usuario existente
def c_update_user(db: Session, user_id: int, user: UserUpdate, current_user: UserInDB):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user_tipos = [ut.cod_tipo_usuario for ut in db.query(UsuarioTipos).filter(UsuarioTipos.usuario_id == user_id).all()]
    if 'ADM' not in current_user.tipos_usuario and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para editar este usuario")
    if 'DOC' in current_user.tipos_usuario and 'ADM' in user_tipos:
        raise HTTPException(status_code=403, detail="No tienes permiso para editar administradores")
    for key, value in user.dict(exclude_unset=True).items():
        if key == "password" and value:
            setattr(db_user, key, get_password_hash(value))
        elif key != "tipo_usuario":  # tipo_usuario se maneja por separado
            setattr(db_user, key, value)
    if user.tipo_usuario:
        # Actualizar tipo de usuario
        db.query(UsuarioTipos).filter(UsuarioTipos.usuario_id == user_id).delete()
        db.add(UsuarioTipos(usuario_id=user_id, cod_tipo_usuario=user.tipo_usuario))
    db.commit()
    db.refresh(db_user)
    return db_user

# Permite eliminar un usuario
def c_delete_user(db: Session, user_id: int, current_user: UserInDB):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if 'ADM' not in current_user.tipos_usuario:
        raise HTTPException(status_code=403, detail="Solo administradores pueden eliminar usuarios")
    db.delete(db_user)
    db.commit()
    return {"detail": "Usuario eliminado"}