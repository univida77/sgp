# database/remote.py - CONEXIÓN A SUPABASE (PostgreSQL)
from typing import List, Optional, Dict, Any
from sqlmodel import create_engine, Session, select, SQLModel, text
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import os
import urllib.parse

# Importación de modelos y orden de sincronización
try:
    from models import SQLModel, SYNC_ORDER_COMPLETE
except ImportError:
    print("⚠️ No se pudieron importar los modelos. Asegúrate de que models.py esté en la misma carpeta.")

# ====================================================================
# CONFIGURACIÓN SUPABASE - VALORES CORREGIDOS
# ====================================================================

# 1. Host: Se usa el Pooler (aws...) sin el prefijo 'db.' para compatibilidad IPv4
SUPABASE_HOST = os.getenv("SUPABASE_HOST", "aws-0-us-west-2.pooler.supabase.com")
SUPABASE_DB = os.getenv("SUPABASE_DB", "postgres")
SUPABASE_USER = os.getenv("SUPABASE_USER", "postgres.emaktovavsuxvofltkbq")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD", "Tlacolula70400")

# 2. Puerto: El pooler de Supabase requiere obligatoriamente el puerto 6543
SUPABASE_PORT = os.getenv("SUPABASE_PORT", "6543")

def get_engine():
    """Crea conexión a PostgreSQL de Supabase."""
    try:
        # Codificamos la contraseña para manejar caracteres especiales
        password_encoded = urllib.parse.quote_plus(SUPABASE_PASSWORD)
        
        # Construcción de la URL de conexión (psycopg2)
        connection_string = (
            f"postgresql+psycopg2://{SUPABASE_USER}:{password_encoded}"
            f"@{SUPABASE_HOST}:{SUPABASE_PORT}/{SUPABASE_DB}"
        )
        
        print(f"🔗 Intentando conectar a: {SUPABASE_HOST} por puerto {SUPABASE_PORT}...")
        
        engine = create_engine(
            connection_string,
            pool_size=5,
            max_overflow=10,
            pool_recycle=1800,
            pool_pre_ping=True, # Verifica la conexión antes de cada uso
            connect_args={
                'connect_timeout': 30,
                'application_name': 'Sistema_Parroquial'
            },
            echo=False
        )
        
        # Prueba de conexión real
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✅ ¡Conexión exitosa a Supabase!")
        
        # Intentar creación automática de tablas al conectar
        # Nota: Solo crea las tablas que no existan
        SQLModel.metadata.create_all(engine)
        
        return engine
        
    except Exception as e:
        print(f"❌ Error crítico de conexión: {str(e)}")
        return None

def forzar_creacion_tablas(db_engine, st_display_func):
    """
    Fuerza la creación de todas las tablas definidas en models.py.
    CORRECCIÓN: Se eliminó .clear() para no borrar los modelos de la memoria.
    """
    if not db_engine:
        return False
    
    try:
        st_display_func("🔄 Verificando y creando tablas en Supabase...")
        
        # No usamos metadata.clear() porque borraría las definiciones cargadas
        SQLModel.metadata.create_all(db_engine)
        
        # Verificación de tablas existentes en el esquema público
        with Session(db_engine) as session:
            result = session.execute(text(
                "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'"
            ))
            count = result.fetchone()[0]
        
        st_display_func(f"✅ {count} tablas detectadas/creadas en Supabase.")
        return True
    except Exception as e:
        st_display_func(f"❌ Error en creación de tablas: {e}")
        return False

def obtener_estadisticas_sincronizacion(engine) -> Dict[str, Any]:
    """Obtiene estadísticas de sincronización de Supabase."""
    if not engine:
        return {}
    
    estadisticas = {
        'total_registros': 0,
        'con_id_local': 0,
        'ultima_sincronizacion': None
    }
    
    try:
        # Usamos el orden de sincronización definido en models.py
        from models import SYNC_ORDER_COMPLETE
        modelos = SYNC_ORDER_COMPLETE
        
        with Session(engine) as session:
            for modelo in modelos:
                try:
                    # Contamos registros de cada tabla
                    statement = select(modelo)
                    resultados = session.exec(statement).all()
                    estadisticas['total_registros'] += len(resultados)
                    
                    if hasattr(modelo, 'id_local'):
                        con_local = [r for r in resultados if getattr(r, 'id_local', None) is not None]
                        estadisticas['con_id_local'] += len(con_local)
                    
                    if hasattr(modelo, 'fecha_sync'):
                        fechas = [r.fecha_sync for r in resultados if getattr(r, 'fecha_sync', None)]
                        if fechas:
                            ultima = max(fechas)
                            if not estadisticas['ultima_sincronizacion'] or ultima > estadisticas['ultima_sincronizacion']:
                                estadisticas['ultima_sincronizacion'] = ultima
                except Exception:
                    # Si una tabla no existe aún, saltamos a la siguiente
                    continue
        
        return estadisticas
    except Exception as e:
        print(f"Error obteniendo estadísticas: {e}")
        return estadisticas