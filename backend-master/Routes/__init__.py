# Routes/__init__.py

#   Esto  no hace falta, pero se pone para una mejor organización
from .routes_estudiantes import router as estudiantes_router
from .routes_materias import router as materias_router
from .routes_periodos import router as periodos_router

__all__ = ["estudiantes_router", "materias_router", "periodos_router"]