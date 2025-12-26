#   backend_AcademiA\backend-master\Routes\routes_ciclos.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import CicloLectivo
import schemas

router = APIRouter(
    prefix="/ciclos",
    tags=["Ciclos Lectivos"],
)

@router.get("/", response_model=list[schemas.CicloLectivoResponse])
def obtener_ciclos(db: Session = Depends(get_db)):
    # Esta línea busca todos los registros en la tabla
    ciclos = db.query(CicloLectivo).order_by(CicloLectivo.nombre_ciclo_lectivo.desc()).all()
    return ciclos
