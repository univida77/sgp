# database/local.py - MODIFICADO PARA FELIGRES
"""
CAMBIO ARQUITECTÓNICO: Persona → Feligres
Funciones CRUD actualizadas
"""

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
        print("✅ Base de datos SQLite inicializada con modelo Feligres")
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
    
    try:
        from sync_manager import SYNC_ORDER
        modelos = SYNC_ORDER
    except ImportError:
        from models import SYNC_ORDER_COMPLETE
        modelos = SYNC_ORDER_COMPLETE
    
    total = 0
    
    try:
        for modelo in modelos:
            if hasattr(modelo, 'sincronizado'):
                try:
                    with Session(engine) as session:
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
# 4. FUNCIONES ESPECÍFICAS PARA FELIGRES (antes Persona)
# ====================================================================

def crear_feligres(feligres: Feligres, engine, st_display_func, synchronize: bool = False) -> bool:
    """
    Crea un nuevo feligrés en la base de datos.
    CAMBIO: Antes era crear_persona
    """
    return crear_registro(feligres, engine, st_display_func, synchronize, "Feligrés")

def leer_feligreses(engine) -> List[Feligres]:
    """
    Lee todos los feligreses.
    CAMBIO: Antes era leer_personas
    """
    return leer_registros(Feligres, engine)

def actualizar_feligres(feligres_id: int, datos: Dict[str, Any], engine, st_display_func) -> bool:
    """
    Actualiza un feligrés existente.
    CAMBIO: Antes era actualizar_persona con persona_id
    """
    return actualizar_registro(Feligres, feligres_id, datos, engine, st_display_func, "Feligrés")

def eliminar_feligres(feligres_id: int, engine, st_display_func, synchronize: bool = False) -> bool:
    """
    Elimina un feligrés.
    CAMBIO: Antes era eliminar_persona con persona_id
    """
    return eliminar_registro(Feligres, feligres_id, engine, st_display_func, synchronize, "Feligrés")


# ====================================================================
# 5. COMPATIBILIDAD HACIA ATRÁS (DEPRECADO)
# ====================================================================

def crear_persona(persona: Feligres, engine, st_display_func, synchronize: bool = False) -> bool:
    """
    DEPRECADO: Usar crear_feligres
    Mantenido temporalmente para no romper código existente
    """
    import warnings
    warnings.warn(
        "crear_persona está deprecado. Usa crear_feligres",
        DeprecationWarning,
        stacklevel=2
    )
    return crear_feligres(persona, engine, st_display_func, synchronize)

def leer_personas(engine) -> List[Feligres]:
    """DEPRECADO: Usar leer_feligreses"""
    import warnings
    warnings.warn("leer_personas está deprecado. Usa leer_feligreses", DeprecationWarning)
    return leer_feligreses(engine)

def actualizar_persona(persona_id: int, datos: Dict[str, Any], engine, st_display_func) -> bool:
    """DEPRECADO: Usar actualizar_feligres"""
    import warnings
    warnings.warn("actualizar_persona está deprecado. Usa actualizar_feligres", DeprecationWarning)
    return actualizar_feligres(persona_id, datos, engine, st_display_func)

def eliminar_persona(persona_id: int, engine, st_display_func, synchronize: bool = False) -> bool:
    """DEPRECADO: Usar eliminar_feligres"""
    import warnings
    warnings.warn("eliminar_persona está deprecado. Usa eliminar_feligres", DeprecationWarning)
    return eliminar_feligres(persona_id, engine, st_display_func, synchronize)