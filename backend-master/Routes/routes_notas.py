# backend-master/Routes/routes_notas.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

# Importaciones CLAVE:
# Importar el servicio (ajusta la ruta de importación si es necesario, 
# asumiendo que está en la carpeta 'Services' al mismo nivel que 'Routes')
from Services import nota_service 
from schemas import NotaCreate, NotaResponse

# Uso la función de DB está de database.py en la raíz
from database  import get_db

# Importar modelos (ajustá la ruta si es necesario)
from models import Nota, Entidad, TipoNota, Periodo, Materia  # <-- Asegurate de tener estos importados

# Definición del Router
router = APIRouter(
    prefix="/notas",
    tags=["Notas"],
)

# =====================================
#  POST - Crear una nota individual
# =====================================
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
    
# =====================================
#  GET - Obtener planilla de calificaciones
# =====================================
@router.get("/planilla", response_model=List[dict])
def obtener_planilla_calificaciones(
    materia_id: int = Query(..., description="ID de la materia/asignatura"),
    periodo_id: int = Query(..., description="ID del período/ciclo lectivo"),
    db: Session = Depends(get_db)
):
    """
    Devuelve la planilla completa de calificaciones para una materia y período.
    Pivotea las notas por tipo (1ºT, 2ºT, 3ºT, Promedio, Dic, Feb, Definitiva).
    Ordena por apellido y nombre del alumno.
    """
    print("¡ESTO SE TIENE QUE VER EN CONSOLA!") # Si esto no sale, la ruta sigue mal registrada
    try:
        # 1. Obtener los nombres de los PERIODOS (1ºT, 2ºT, etc.)
        periodos = db.query(Periodo).all()
        periodos_dict = {p.id_periodo: p.nombre_periodo.strip() for p in periodos}
        
        # LOG DE DEPURACIÓN
        print(f"--- Buscando notas para Materia: {materia_id}, Periodo: {periodo_id} ---")

        # 1. Obtener todos los tipos de nota para mapear nombres
        # tipos_nota = db.query(TipoNota).all()
        # print(f"Tipos de nota encontrados: {len(tipos_nota)}")

        # tipos_dict = {tn.id_tipo_nota: tn.tipo_concepto.strip() for tn in tipos_nota}

        # 2. Traer todas las notas para esa materia y período
        notas = db.query(Nota).filter(
            Nota.id_materia == materia_id,
            Nota.id_periodo == periodo_id
        ).all()
        print(f"Notas crudas encontradas en DB: {len(notas)}")

        if not notas:
            return []  # Si no hay notas, devuelve lista vacía (frontend lo maneja bien)

        # 3. Agrupar por alumno
        planilla_por_alumno = {}

        for nota in notas:
            alumno_id = nota.id_entidad_estudiante

            if alumno_id not in planilla_por_alumno:
                # Traer datos del alumno una sola vez
                alumno = db.query(Entidad).filter(Entidad.id_entidad == alumno_id).first()
                if not alumno:
                    continue  # seguridad, aunque no debería pasar

                planilla_por_alumno[alumno_id] = {
                    "alumno": {
                        "id": alumno.id_entidad,
                        "nombre": alumno.nombre or "",
                        "apellido": alumno.apellido or "",
                    },
                    "notas": {}
                }

            # Buscamos el nombre del periodo (ej: "1er Trimestre") usando el id_periodo de la nota
            nombre_periodo = periodos_dict.get(nota.id_periodo, "Desconocido")
            
            # Guardamos la nota usando el nombre del periodo como clave
            planilla_por_alumno[alumno_id]["notas"][nombre_periodo] = float(nota.nota) if nota.nota is not None else None

        # Construir respuesta final con promedio calculado
        resultado = []
        for data in planilla_por_alumno.values():
            notas_dict = data["notas"]

            # Calcular promedio de trimestres
            trimestres = []
            for tipo in ["1º Trimestre", "2º Trimestre", "3º Trimestre"]:
                if tipo in notas_dict and notas_dict[tipo] is not None:
                    trimestres.append(notas_dict[tipo])

            prom = round(sum(trimestres) / len(trimestres), 2) if trimestres else None

            resultado.append({
                "alumno": data["alumno"],
                "nota_t1": notas_dict.get("1º Trimestre"),
                "nota_t2": notas_dict.get("2º Trimestre"),
                "nota_t3": notas_dict.get("3º Trimestre"),
                "prom": prom,
                "nota_dic": notas_dict.get("Diciembre"),
                "nota_feb": notas_dict.get("Febrero"),
                "nota_def": notas_dict.get("Definitiva") or prom,
                "observaciones": notas_dict.get("Observaciones", ""),
            })

        return resultado

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la planilla de calificaciones: {str(e)}"
        )