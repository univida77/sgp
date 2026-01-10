# database/local.py - CORREGIDO CON MARCADO DE SINCRONIZACIÓN
from typing import List, Optional, Dict, Any
from sqlmodel import create_engine, Session, select, SQLModel
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import os

from models import *

# ====================================================================
# 1. CONFIGURACIÓN LOCAL
# ====================================================================

current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, "parroquia.db")

SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

# ====================================================================
# 2. MOTOR DE BASE DE DATOS
# ====================================================================

def get_engine():
    """Crea y retorna el motor de base de datos SQLite."""
    try:
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            echo=False,
            connect_args={"check_same_thread": False}
        )
        
        SQLModel.metadata.create_all(engine)
        print("✅ Base de datos SQLite inicializada")
        return engine
        
    except Exception as e:
        print(f"❌ Error conectando a SQLite: {e}")
        return None

# ====================================================================
# 3. FUNCIONES CRUD CON MARCADO DE SINCRONIZACIÓN
# ====================================================================

def crear_registro(registro: SQLModel, engine, st_display_func,
                  synchronize: bool = False, nombre_tabla: str = "Registro") -> bool:
    """Crea un nuevo registro en SQLite y lo marca como NO SINCRONIZADO."""
    try:
        with Session(engine) as session:
            # ✅ MARCAR COMO NO SINCRONIZADO
            if hasattr(registro, 'sincronizado'):
                registro.sincronizado = False
            if hasattr(registro, 'id_remoto'):
                registro.id_remoto = None
            if hasattr(registro, 'fecha_sync'):
                registro.fecha_sync = None
            
            session.add(registro)
            session.commit()
            session.refresh(registro)
            
            if not synchronize:
                st_display_func(f"✅ {nombre_tabla} creado en SQLite (pendiente de sincronizar)")
            return True
    except IntegrityError as e:
        if not synchronize:
            st_display_func(f"❌ Error de integridad: {e}", is_error=True)
        return False
    except Exception as e:
        if not synchronize:
            st_display_func(f"❌ Error creando {nombre_tabla}: {e}", is_error=True)
        return False

def actualizar_registro(modelo_clase, registro_id: int, datos: Dict[str, Any],
                       engine, st_display_func, nombre_tabla: str = "Registro") -> bool:
    """Actualiza un registro en SQLite y lo marca como NO SINCRONIZADO."""
    try:
        with Session(engine) as session:
            registro = session.get(modelo_clase, registro_id)
            if registro:
                for key, value in datos.items():
                    if hasattr(registro, key):
                        setattr(registro, key, value)
                
                # ✅ MARCAR COMO NO SINCRONIZADO
                if hasattr(registro, 'sincronizado'):
                    registro.sincronizado = False
                if hasattr(registro, 'fecha_sync'):
                    registro.fecha_sync = None
                
                session.add(registro)
                session.commit()
                st_display_func(f"✅ {nombre_tabla} actualizado en SQLite (pendiente de sincronizar)")
                return True
            st_display_func(f"❌ {nombre_tabla} no encontrado", is_error=True)
            return False
    except Exception as e:
        st_display_func(f"❌ Error actualizando {nombre_tabla}: {e}", is_error=True)
        return False

def eliminar_registro(modelo_clase, registro_id: int, engine, st_display_func,
                     synchronize: bool = False, nombre_tabla: str = "Registro") -> bool:
    """Elimina un registro de SQLite."""
    try:
        with Session(engine) as session:
            registro = session.get(modelo_clase, registro_id)
            if registro:
                session.delete(registro)
                session.commit()
                if not synchronize:
                    st_display_func(f"⚠️ {nombre_tabla} eliminado de SQLite", is_warning=True)
                return True
            st_display_func(f"❌ {nombre_tabla} no encontrado", is_error=True)
            return False
    except Exception as e:
        if not synchronize:
            st_display_func(f"❌ Error eliminando {nombre_tabla}: {e}", is_error=True)
        return False

def leer_registros(modelo_clase, engine, limit: Optional[int] = None) -> List:
    """Lee registros de SQLite."""
    if not engine:
        return []
    try:
        with Session(engine) as session:
            statement = select(modelo_clase)
            if limit:
                statement = statement.limit(limit)
            return session.exec(statement).all()
    except Exception as e:
        print(f"Error leyendo {modelo_clase.__name__}: {e}")
        return []

def contar_pendientes_sincronizacion(engine) -> int:
    """Cuenta cuántos registros están pendientes de sincronizar."""
    if not engine:
        return 0
    
    # ✅ CORRECCIÓN: Importar desde sync_manager o usar SYNC_ORDER_COMPLETE
    try:
        from sync_manager import SYNC_ORDER
        modelos = SYNC_ORDER
    except ImportError:
        # Si no existe SYNC_ORDER en sync_manager, usar SYNC_ORDER_COMPLETE de models
        from models import SYNC_ORDER_COMPLETE
        modelos = SYNC_ORDER_COMPLETE
    
    total = 0
    
    try:
        for modelo in modelos:
            if hasattr(modelo, 'sincronizado'):
                try:
                    with Session(engine) as session:
                        # Contar registros no sincronizados
                        count = len([
                            r for r in session.exec(select(modelo)).all()
                            if not r.sincronizado
                        ])
                        total += count
                except:
                    continue
        return total
    except Exception as e:
        print(f"Error contando pendientes: {e}")
        return 0

# ====================================================================
# 4. FUNCIONES ESPECÍFICAS PARA PERSONA
# ====================================================================

def crear_persona(persona: Persona, engine, st_display_func, synchronize: bool = False) -> bool:
    return crear_registro(persona, engine, st_display_func, synchronize, "Persona")

def leer_personas(engine) -> List[Persona]:
    return leer_registros(Persona, engine)

def actualizar_persona(persona_id: int, datos: Dict[str, Any], engine, st_display_func) -> bool:
    return actualizar_registro(Persona, persona_id, datos, engine, st_display_func, "Persona")

def eliminar_persona(persona_id: int, engine, st_display_func, synchronize: bool = False) -> bool:
    return eliminar_registro(Persona, persona_id, engine, st_display_func, synchronize, "Persona")