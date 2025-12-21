# backend-master/Services/nota_service.py

from sqlalchemy.orm import Session
from datetime import date
# Ajusta estas importaciones si tus archivos de esquema y modelos están en la raíz
from schemas import NotaCreate 
from models import Nota 
from database import localSession



# Configuración de lógica de negocio (Valores que el backend inyecta)
ID_ENTIDAD_CARGA_DEFAULT = 2  
ID_TIPO_NOTA_DEFAULT = 1      

def crear_nota_individual(db: Session, nota_data: NotaCreate) -> Nota:
    """Función de servicio para ejecutar la inserción de una nota."""
    
    fecha_actual = date.today()
    
    # Mapear los datos de entrada al Modelo ORM
    db_nota = Nota(
        id_materia=nota_data.id_materia,
        id_entidad_estudiante=nota_data.id_entidad_estudiante,
        nota=nota_data.nota,
        id_periodo=nota_data.id_periodo, 
        
        # Datos definidos por el backend
        id_tipo_nota=ID_TIPO_NOTA_DEFAULT,
        id_entidad_carga=ID_ENTIDAD_CARGA_DEFAULT,
        fecha_carga=fecha_actual,
    )

    # Persistencia
    db.add(db_nota)
    db.commit()
    db.refresh(db_nota)
    
    return db_nota