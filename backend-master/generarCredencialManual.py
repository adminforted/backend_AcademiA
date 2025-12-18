#    Script para generar un hash bcrypt para una contraseña 

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
password = "123456"  # Cambia por la contraseña deseada
hashed_password = pwd_context.hash(password)
print(hashed_password)