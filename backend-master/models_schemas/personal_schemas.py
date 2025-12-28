#   backend_AcademiA\backend-master\schemas\personal_schemas.py
from pydantic import BaseModel, computed_field
from typing import Optional

class PersonalResponse(BaseModel):
    apellido: str
    nombre: str
    dni: int
    email: Optional[str] = None
    domicilio: Optional[str] = None
    localidad: str
    telefono: Optional[str] = None 
    cel: Optional[str] = None 
    tipo_entidad: str # Aquí guardaremos el texto 'ALU', 'DOC', etc.
    
    # Uso un campo calculado, para unir telefono y/o celular
    @computed_field
    @property
    def tel_cel(self) -> Optional[str]:
        """Combina teléfono y celular en un solo campo"""
        if self.telefono and self.cel:
            return f"{self.telefono} / {self.cel}"
        return self.telefono or self.cel or "-"

class Config:
    from_attributes = True