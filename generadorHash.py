# Asegúrate de estar en tu venv y tener passlib instalado
from passlib.context import CryptContext

# Recrea el contexto que usas en auth.py (probablemente bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Genera un nuevo hash para '123456'
new_hash = pwd_context.hash("123456")

print(f"Nuevo Hash Generado: {new_hash}")
# El resultado será una cadena que comienza con algo como $2b$ o $2a$ (ej: $2b$12$ABCDEFGHIJ.K/LMNOPQRSTUVWXYZ012345678901)