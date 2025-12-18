# backend-master/Routes/routes_notas.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Importaciones CLAVE:
# Importar el servicio (ajusta la ruta de importación si es necesario, 
# asumiendo que está en la carpeta 'Services' al mismo nivel que 'Routes')
from Services import nota_service 
from schemas import NotaCreate, NotaResponse

# Uso la función de DB está de database.py en la raíz
from database  import get_db


# Definición del Router
router = APIRouter(
    prefix="/notas",
    tags=["Notas"],
)

@router.post("/", response_model=NotaResponse, status_code=status.HTTP_201_CREATED)
def crear_nota(nota: NotaCreate, db: Session = Depends(get_db)):
    """
    Endpoint para registrar una nueva nota individual llamando al servicio.
    """
    try:
        # LLAMADA AL SERVICIO: El endpoint solo delega la tarea
        db_nota = nota_service.crear_nota_individual(db=db, nota_data=nota)
        return db_nota
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar la nota: {str(e)}",
        )