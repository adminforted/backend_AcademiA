#   backend-master\backend-master\database.py

from sqlalchemy import create_engine  # Importamos create_engine para establecer la conexión con la base de datos

# Importamos declarative_base para definir modelos ORM 
# from sqlalchemy.ext.declarative import declarative_base   
# # Se comenta porque Base se define en models.py para evitar dependencias circulares.

from sqlalchemy.orm import sessionmaker  # Importamos sessionmaker para manejar sesiones de la base de datos
from dotenv import load_dotenv  # Para cargar datos del archivo .env
import os

load_dotenv()  # Carga los datos del archivo .env

DB_NAME=os.getenv('DB_NAME')
DB_USER=os.getenv('DB_USER')
DB_PASSWORD=os.getenv('DB_PASSWORD')
DB_HOST=os.getenv('DB_HOST')
DB_DIALECT=os.getenv('DB_DIALECT')
DB_PORT=os.getenv('DB_PORT')


# Definimos la URL de conexión para MySQL utilizando el driver pymysql
# Formato: 'mysql+pymysql://usuario:contraseña@host/nombre_base_de_datos'
# URL_CONNECTION = 'mysql+pymysql://root:Qazwsx123++@localhost:3383/test'

URL_CONNECTION = f'{DB_DIALECT}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
# Otra forma ok
# URL_CONNECTION = '{}://{}:{}@{}:{}/{}'.format(DB_DIALECT,DB_USER,DB_PASSWORD,DB_HOST,DB_PORT,DB_NAME)

# Creamos el motor de base de datos con la URL de conexión
# Este motor permite que SQLAlchemy interactúe con MySQL
# Creamos el motor de base de datos con la URL de conexión
engine = create_engine(
    URL_CONNECTION,
    pool_pre_ping=True,                    # Verifica conexiones muertas (¡importantísimo!)
    pool_recycle=3600,                     # Recicla conexiones cada hora
    pool_size=10,                          # Tamaño del pool
    max_overflow=20,                       # Conexiones extras permitidas
    pool_timeout=30,                       # Timeout para obtener conexión del pool
    echo=False,                            # Cambia a True solo para debug
    connect_args={"connect_timeout": 30}   # ¡Aquí va el timeout de conexión correcto!
)

# Creamos una fábrica de sesiones para interactuar con la base de datos
# - autoflush=False evita que los cambios se envíen automáticamente a la BD
# - autocommit=False significa que las transacciones deben confirmarse manualmente
# - bind=engine asocia la sesión con el motor de base de datos
localSession = sessionmaker(autoflush=False, autocommit=False, bind=engine)


# Dependency de FastAPI para inyectar una sesión de base de datos (SQLAlchemy) en los endpoints.
# Crea una sesión nueva (db = SessionLocal()).
# La entrega al endpoint con yield db (permite usarla dentro de la función).
# Al terminar (normal o por error), cierra la sesión automáticamente con db.close() en el finally.
# Garantiza que cada petición HTTP tenga su propia sesión limpia y que no queden conexiones abiertas.  
def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()


