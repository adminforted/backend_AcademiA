from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add backend directory to path to import models if needed
sys.path.append(r'c:\Sistema\backend-master\backend-master')

from database import localSession
from models import Entidad, User, UsuarioTipos

def check_students():
    db = localSession()
    try:
        # Query all entities
        print("--- All Entities (tbl_entidad) ---")
        all_entities = db.query(Entidad).all()
        for e in all_entities:
            print(f"ID: {e.id_entidad}, Name: {e.nombre} {e.apellido}, Type: {e.tipos_entidad}, Deleted: {e.deleted_at}")

        # Query students specifically as the API does
        print("\n--- Students (API Query on Entidad) ---")
        students = db.query(Entidad).filter(
            Entidad.tipos_entidad.like("%ALU%"),
            Entidad.deleted_at.is_(None)
        ).all()
        
        print(f"Found {len(students)} students in Entidad.")
        for s in students:
            print(f"ID: {s.id_entidad}, Name: {s.nombre} {s.apellido}, Type: {s.tipos_entidad}")

        # Query Users
        print("\n--- All Users (tbl_usuarios) ---")
        users = db.query(User).all()
        for u in users:
            print(f"ID: {u.id}, Name: {u.name}, Email: {u.email}")
            
        # Query User Types
        print("\n--- User Types (tbl_usuario_tipos) ---")
        user_types = db.query(UsuarioTipos).all()
        for ut in user_types:
            print(f"User ID: {ut.usuario_id}, Type: {ut.cod_tipo_usuario}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_students()
