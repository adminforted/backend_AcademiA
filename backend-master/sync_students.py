from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add backend directory to path to import models
sys.path.append(r'c:\Sistema\backend-master\backend-master')

from database import localSession
from models import Entidad, User, UsuarioTipos

def sync_students():
    db = localSession()
    try:
        print("Starting synchronization of Students (Users -> Entities)...")
        
        # 1. Get all users with type 'EST'
        # Explicit join condition
        est_users = db.query(User).join(UsuarioTipos, User.id == UsuarioTipos.usuario_id).filter(UsuarioTipos.cod_tipo_usuario == 'EST').all()
        print(f"Found {len(est_users)} users with type 'EST'.")
        
        count_created = 0
        count_skipped = 0
        
        for user in est_users:
            # 2. Check if entity already exists for this user (by usuario_id or email)
            # We check by usuario_id first as it's the most direct link, but also email to avoid duplicates if linked differently
            existing_entity = db.query(Entidad).filter(
                (Entidad.usuario_id == user.id) | (Entidad.email == user.email)
            ).first()
            
            if existing_entity:
                # Check if it has ALU type, if not add it? For now, just skip if exists
                # print(f"Skipping User {user.name} ({user.email}) - Entity already exists (ID: {existing_entity.id_entidad})")
                count_skipped += 1
                continue
            
            # 3. Create new Entity
            # Split name
            parts = user.name.split(' ', 1)
            nombre = parts[0]
            apellido = parts[1] if len(parts) > 1 else ""
            
            new_entity = Entidad(
                usuario_id=user.id,
                nombre=nombre,
                apellido=apellido,
                email=user.email,
                tipos_entidad="ALU", # Default to ALU for students
                # Optional fields left null for now
                domicilio=None,
                telefono=None,
                fec_nac=None
            )
            
            db.add(new_entity)
            count_created += 1
            print(f"Creating Entity for User {user.name} ({user.email})")
            
        db.commit()
        print(f"\nSync complete.")
        print(f"Created: {count_created}")
        print(f"Skipped: {count_skipped}")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    sync_students()
