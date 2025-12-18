from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
import aiosmtplib
from email.message import EmailMessage
import secrets

from models import User, UsuarioTipos
from schemas import UserInDB, LoginRequest, Token, EmailVerifyRequest, ForgotPasswordRequest, ResetPasswordRequest    #,UserRole
from database import localSession

from typing import List



load_dotenv()
print("EMAIL_USER:", os.getenv("EMAIL_USER"))
print("EMAIL_PASS:", os.getenv("EMAIL_PASS"))


# Configuración
JWT_SECRET = os.getenv('JWT_SECRET') or "your-secret-key"  # Clave segura para JWT
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT') or 587)
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')




# Hasheo de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 para JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

router = APIRouter()

# Dependencia para la base de datos
def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()
    
# Funciones de utilidad
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db))  -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        tipo_usuario: str = payload.get("tipo_usuario")
        if username is None or tipo_usuario is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.name == username).first()
    if user is None:
        raise credentials_exception
    tipos_usuario = [ut.cod_tipo_usuario for ut in db.query(UsuarioTipos).filter(UsuarioTipos.usuario_id == user.id).all()]
    if tipo_usuario not in tipos_usuario:
        raise HTTPException(status_code=403, detail="Tipo de usuario no válido")

    return UserInDB(
        id=user.id,
        name=user.name,
        email=user.email,
        is_email_verified=user.is_email_verified,
        reset_token=user.reset_token,
        tipos_usuario=tipos_usuario
    )


# Generar token de verificación o restablecimiento
def generate_token():
    return secrets.token_urlsafe(32)

# Enviar email
async def send_email(to_email: str, subject: str, body: str):
    message = EmailMessage()
    message["From"] = EMAIL_USER
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname=EMAIL_HOST,
        port=EMAIL_PORT,
        username=EMAIL_USER,
        password=EMAIL_PASS,
        start_tls=True,
    )

# Endpoint para login
@router.post("/api/login", response_model=Token)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.name == request.name).first()
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    if not user.is_email_verified:
        raise HTTPException(status_code=403, detail="El email no está verificado")
    tipos_usuario = [ut.cod_tipo_usuario for ut in db.query(UsuarioTipos).filter(UsuarioTipos.usuario_id == user.id).all()]
    if request.tipo_usuario not in tipos_usuario:
        raise HTTPException(status_code=403, detail="Tipo de usuario no válido")
    access_token = create_access_token(data={"sub": user.name, "tipo_usuario": request.tipo_usuario})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "tipos_usuario": tipos_usuario
    }

# Endpoint para verificar email
@router.post("/api/verify-email")
async def verify_email(request: EmailVerifyRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == request.token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Token inválido")
    user.is_email_verified = True
    user.reset_token = None
    db.commit()
    return {"detail": "Email verificado correctamente"}

# Endpoint para solicitar restablecimiento de contraseña
@router.post("/api/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    reset_token = generate_token()
    user.reset_token = reset_token
    db.commit()
    # Enviar email con el token
    reset_url = f"http://localhost:8000/reset-password?token={reset_token}"
    await send_email(
        to_email=user.email,
        subject="Restablecer contraseña",
        body=f"Haga clic en el siguiente enlace para restablecer su contraseña: {reset_url}"
    )
    return {"detail": "Se ha enviado un enlace para restablecer la contraseña"}

# Endpoint para restablecer contraseña
@router.post("/api/reset-password")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == request.token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Token inválido")
    user.password = get_password_hash(request.new_password)
    user.reset_token = None
    db.commit()
    return {"detail": "Contraseña restablecida correctamente"}

# Endpoint para testear el envío de mail.
# Se prueba mediante:  curl -X GET "http://localhost:8000/api/test-email"
@router.get("/api/test-email")
async def test_email():
    try:
        await send_email(
            to_email="sistema.academia.25@gmail.com",  # Cambia por un correo donde puedas verificar la recepción
            subject="Prueba de envío de correo",
            body="Este es un correo de prueba desde FastAPI."
        )
        return {"message": "Correo enviado correctamente"}
    except Exception as e:
        return {"error": str(e)}