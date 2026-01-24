# backend-master/Routes/routes_notas.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List

# Importaciones CLAVE:
# Importar el servicio (ajusta la ruta de importación si es necesario, 
# asumiendo que está en la carpeta 'Services' al mismo nivel que 'Routes')
from Services import nota_service 

# Importamos todos los modelos y esquemas, por practicidad y limpieza
import models, schemas, database

# Uso la función de DB está de database.py en la raíz
from database  import get_db


# Definición del Router
router = APIRouter(
    prefix="/notas",
    tags=["Notas"],
)

# =====================================
#  POST - Crear una nota individual
# =====================================
@router.post("/", response_model=schemas.NotaResponse, status_code=status.HTTP_201_CREATED)
def crear_nota(nota: schemas.NotaCreate, db: Session = Depends(get_db)):
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



# =====================================================
#  GET - Obtener planilla de calificaciones
# =====================================================

@router.get("/planilla-acta", response_model=schemas.PlanillaActaResponse)
def obtener_acta_calificaciones(
    ciclo_id: int = Query(..., description="ID del ciclo lectivo"),
    curso_id: int = Query(..., description="ID del curso"),
    materia_id: int = Query(..., description="ID de la materia"),
    db: Session = Depends(get_db)
):
    try:
        # Obtener Columnas (Encabezados)
        columnas_query = db.query(
            models.TipoNota
            ).filter(
                models.Nota.id_materia == materia_id,
                models.TipoNota.es_final == 1
            ).order_by(
                models.TipoNota.id_tipo_nota
            ).all()

        headers = [schemas.ColumnaHeader(id_tipo_nota=c.id_tipo_nota, label=c.tipo_nota) 
                   for c in columnas_query]

        # Obtener TODAS las notas de la materia
        # Usamos join con Entidad para traer los nombres de los ESTUDIANTES (id_entidad_estudiante)
        notas_existentes = (
         db.query(models.Nota)
         .options(joinedload(models.Nota.estudiante)) # Carga al alumno de un solo golpe
         .filter(models.Nota.id_materia == materia_id)
         .all()
)
        # Identificar Estudiantes únicos a partir de las notas
        # Creamos un diccionario para no repetir alumnos
        estudiantes_map = {}
        for n in notas_existentes:
            if n.id_entidad_estudiante not in estudiantes_map:
                # n.estudiante es la relación en tu modelo Nota que apunta al alumno
                est = n.estudiante 
                estudiantes_map[n.id_entidad_estudiante] = {
                    "id": est.id_entidad,
                    "nombre_completo": f"{est.apellido}, {est.nombre}"
                }

        # Construir las filas procesando las notas de cada estudiante
        filas = []
        for alu_id, alu_info in estudiantes_map.items():
            # Filtramos las notas que pertenecen a este alumno específico
            notas_del_alumno = {n.id_tipo_nota: float(n.nota) for n in notas_existentes 
                                if n.id_entidad_estudiante == alu_id}
            
            # Mapeamos las calificaciones según los headers
            calificaciones = {col.id_tipo_nota: notas_del_alumno.get(col.id_tipo_nota) 
                              for col in headers}

            # Cálculo de promedio
            notas_val = [v for v in calificaciones.values() if v is not None]
            promedio = round(sum(notas_val) / len(notas_val), 2) if notas_val else None

            filas.append(schemas.AlumnoNotaRow(
                id_alumno=alu_id,
                nombre_completo=alu_info["nombre_completo"],
                calificaciones=calificaciones,
                promedio=promedio,
                definitiva=calificaciones.get(7) # ID 7 según tu JSON
            ))

        return schemas.PlanillaActaResponse(
            columnas=headers,
            filas=sorted(filas, key=lambda x: x.nombre_completo)
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    

# =====================================================
#  POST - UPSERT de nota (VERSIÓN SIMPLIFICADA)
# =====================================================
@router.post("/upsert")
def upsert_nota(
    payload: schemas.NotaUpsert, 
    db: Session = Depends(database.get_db)
):
    try:
        print("="*60)
        print("📥 PAYLOAD RECIBIDO:", payload.dict())
        print("="*60)
        
        # 1. Buscar si la nota ya existe
        nota_db = db.query(models.Nota).filter(
            models.Nota.id_entidad_estudiante == payload.id_alumno,
            models.Nota.id_materia == payload.id_materia,
            models.Nota.id_tipo_nota == payload.id_tipo_nota
        ).first()
        
        if nota_db:
            # ===== ACTUALIZAR nota existente =====
            print(f"📝 Actualizando nota existente ID: {nota_db.id_nota}")
            nota_db.nota = payload.valor
            
            # Actualizar campos opcionales si vienen
            if payload.id_periodo:
                nota_db.id_periodo = payload.id_periodo
            if payload.id_entidad_carga:
                nota_db.id_entidad_carga = payload.id_entidad_carga
                
            db.commit()
            db.refresh(nota_db)
            
            print(f"✅ Nota actualizada: {nota_db.nota}")
            return {
                "status": "success", 
                "message": "Nota actualizada correctamente",
                "data": {
                    "id_nota": nota_db.id_nota,
                    "nota": nota_db.nota
                }
            }
        else:
            # ===== CREAR nueva nota =====
            print(f"✨ Creando nueva nota para alumno {payload.id_alumno}")
            
            nueva_nota = models.Nota(
                id_entidad_estudiante=payload.id_alumno,
                id_materia=payload.id_materia,
                id_tipo_nota=payload.id_tipo_nota,
                nota=payload.valor,
                id_periodo=payload.id_periodo,  # Puede ser None
                id_entidad_carga=payload.id_entidad_carga or 1  # Default a 1 si es None
            )
            
            db.add(nueva_nota)
            db.commit()
            db.refresh(nueva_nota)
            
            print(f"✅ Nota creada con ID: {nueva_nota.id_nota}")
            return {
                "status": "success", 
                "message": "Nota creada correctamente",
                "data": {
                    "id_nota": nueva_nota.id_nota,
                    "nota": nueva_nota.nota
                }
            }
            
    except Exception as e:
        db.rollback()
        print(f"❌ ERROR DE BASE DE DATOS:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Detalle: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error de base de datos: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        print(f"❌ ERROR GENERAL:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Detalle: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error al guardar nota: {str(e)}"
        )
    
# =====================================================
#  GET - Obtener Notas de materias de un estudiante
# =====================================================

# Recibe el estudiante_id y el ciclo_id, y trae todas las materias con sus notas
@router.get("/informe-individual/{id_estudiante}", response_model=schemas.InformeAcademicoEstudianteResponse)
def obtener_informe_notas_estudiante(
    id_estudiante: int,
    ciclo_id: int = Query(..., description="ID del ciclo lectivo"),
    curso_id: int = Query(..., description="ID del curso"),
    db: Session = Depends(get_db)
):
    try:
        # 1. Obtener Columnas (Headers de tipos de nota)
        tipos_nota = (
            db.query(models.TipoNota)
            .order_by(models.TipoNota.id_tipo_nota)
            .all()
)
        headers = [
            schemas.ColumnaHeader(id_tipo_nota=t.id_tipo_nota, label=t.tipo_nota)
            for t in tipos_nota
        ]

        # 2. Obtener todas las notas del estudiante para este ciclo/curso
        # Filtramos por id_entidad_estudiante
        notas_existentes = (
            db.query(models.Nota)
            .join(models.Materia)
            .filter(
                models.Nota.id_entidad_estudiante == id_estudiante,
                models.Materia.id_curso == curso_id # Filtramos por el curso indicado
            )
            .all()
        )

        # 3. Identificar las materias involucradas
        # Mapeamos materias por ID para evitar duplicados
        materias_query = (
            db.query(models.Materia)
            .options(joinedload(models.Materia.nombre)) # Trae el nombre junto con la materia
            .filter(models.Materia.id_curso == curso_id)
            .all()
        )
        
        filas = []
        for mat in materias_query:
            # Filtramos las notas que pertenecen a esta materia específica
            notas_de_materia = {n.id_tipo_nota: float(n.nota) for n in notas_existentes 
                                if n.id_materia == mat.id_materia}
            
            # Mapeamos las calificaciones según los headers (id_tipo_nota)
            calificaciones = {col.id_tipo_nota: notas_de_materia.get(col.id_tipo_nota) 
                             for col in headers}

            # Cálculo de promedio de la materia
            notas_val = [v for v in calificaciones.values() if v is not None]
            promedio = round(sum(notas_val) / len(notas_val), 2) if notas_val else None

            filas.append(schemas.MateriaNotaRow(
                id_materia=mat.id_materia,
                # mat.nombre es la relación, mat.nombre.nombre_materia es el texto "Matemática"
                nombre_materia=mat.nombre.nombre_materia,
                calificaciones=calificaciones,
                promedio=promedio,
                definitiva=calificaciones.get(7) # ID 7 según tu lógica de "Definitiva"
            ))

        return schemas.InformeAcademicoEstudianteResponse(
            columnas=headers,
            filas=sorted(filas, key=lambda x: x.nombre_materia)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar informe: {str(e)}")

# =============================================================
#  GET - Obtener NOTAS FINALES de una materia de estudiantes
# =============================================================
@router.get("/curso/{id_curso}/materia/{id_materia}/notas-final", response_model=list[schemas.NotaEstudianteResponse])
async def get_notas_finales_estudiantes(
    id_curso: int, 
    id_materia: int, 
    db: Session = Depends(get_db)
):
    notas = (
        db.query(
            models.Nota.id_entidad_estudiante,
            # Concatenamos Nombre y Apellido para el campo 'nombre_entidad'
            # Para mostrar solo el campo nombre: models.Entidad.nombre.label('nombre_entidad')
            func.concat(
                (models.Entidad.apellido), ", ", (models.Entidad.nombre))
                .label('alumno'), 
            models.Nota.nota
        )
        # Join con Entidad para obtener el nombre del alumno
        .join(models.Nota.estudiante)
        # Join con Materia para validar que sea del curso correcto (por seguridad)
        .join(models.Nota.materia)
        # Definimos condiciones y validaciones
        .filter(
            models.Materia.id_curso == id_curso,       # Validamos el curso
            models.Nota.id_materia == id_materia,      # Filtramos la materia
            models.Nota.id_tipo_nota == 7              # Filtro para Nota Final
        )
        .all()
    )
    
    return notas


# ====================================================================================
#  GET - Obtener Notas de Cuatrimestres y Rec de un estudiante, materia y curso
# ====================================================================================
@router.get("/estudiante-materia-curso/{estudiante_id}/{materia_id}/{curso_id}", 
            response_model=list[schemas.NotaDetalle])   # Se pone list, porque se espera una lista (array)
def get_notas_estudiante_materia(
    estudiante_id: int, 
    materia_id: int, 
    curso_id: int,
    db: Session = Depends(get_db)
):
    return db.query(
        # 1. Traigo del models sólo los campos que voy a mandar en el JSON
        models.TipoNota.tipo_nota,
        models.Nota.nota,
        models.Nota.id_periodo,
    # 2. Defino las relaciones entre los MODELOS y 3. Establezco filtros y condiciones
    ).join(models.TipoNota,
           models.Nota.id_tipo_nota == models.TipoNota.id_tipo_nota)\
     .join(models.Materia, 
           models.Materia.id_materia == models.Nota.id_materia)\
    .join(models.TipoConcepto, 
           models.TipoConcepto.id_tipo_concepto == models.TipoNota.id_tipo_concepto)\
    .filter(        
        models.Nota.id_entidad_estudiante == estudiante_id,
        models.Nota.id_materia == materia_id,
        models.Materia.id_curso == curso_id,
        models.TipoNota.id_tipo_concepto.in_([2, 3, 4])
    ).all()

# ==============================================================================================
#  GET - Obtener Notas de Exámen y T. Práctico de un Trimestre, estudiante, materia y curso.
# Datos para subjectEvaluationHistoryDetail
# ==============================================================================================
@router.get("/estudiante-materia-curso-tnota/{estudiante_id}/{materia_id}/{curso_id}/{periodo_id}", 
            response_model=list[schemas.NotaTipoDetalle])   # Se pone list, porque se espera una lista (array)
def get_notas_estudiante_materia_Tipo(
    estudiante_id: int, 
    materia_id: int, 
    curso_id: int,
    periodo_id:int,

    db: Session = Depends(get_db)
):
    return db.query(
        # 1. Traigo del models sólo los campos que voy a mandar en el JSON
        models.Nota.fecha_carga,
        models.TipoNota.tipo_nota,
        models.Nota.nota,
    # 2. Defino las relaciones entre los MODELOS y 3. Establezco filtros y condiciones
   ).join(models.Materia, 
           models.Materia.id_materia == models.Nota.id_materia
    ).join(models.TipoNota,
           models.Nota.id_tipo_nota == models.TipoNota.id_tipo_nota
    ).filter(        
        models.Nota.id_entidad_estudiante == estudiante_id,
        models.Nota.id_materia == materia_id,
        models.Materia.id_curso == curso_id,
        models.Nota.id_periodo == periodo_id,
        models.Nota.id_tipo_nota.in_([1, 8]),
    ).all()