# sync_manager.py - ACTUALIZADO: Persona → Feligres
"""
Sistema de sincronización optimizado para evitar errores de threading.
Compatible con Python 3.13 en Windows.

CAMBIO ARQUITECTÓNICO: Todos los modelos actualizados para usar Feligres
"""

from typing import List, Dict, Any, Optional, Type, Tuple
from sqlmodel import Session, select, SQLModel
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import traceback
import time

from models import (
    # Geografía
    Pais, Provincia, Arquidiocesis, Decanato, Parroquia, Comunidad, Capilla,
    
    # ⚠️ CAMBIO CRÍTICO: Persona → Feligres
    Feligres, Telefono, Direccion,
    
    # Catequesis
    CentroCatecismo, Catecumeno, GrupoCatequesis, RolCatequista, RolCatequistaIntegrante,
    
    # Clero
    Presbitero,
    
    # Sacramentos
    SacramentoBautizo, SacramentoConfirmacion, SacramentoEucaristia, 
    SacramentoMatrimonio, RenovacionBautismal,
    
    # Grupos y educación
    GrupoParroquial, Rol, MembresiaGrupo, Curso, TemaCurso, Actividad, 
    Horario, Salon, ReservacionSalon, Sesion, Inscripcion, RegistroAsistencia, 
    ReunionGrupal, AsistenciaReunion,
    
    # Sistema
    Usuario,
    
    # Finanzas e inventario
    PerfilUsuario, UsuarioPerfil,
    PresupuestoAnual, CategoriaFinanciera, Donador, TransaccionFinanciera,
    Bodega, AreaParroquial, CategoriaInventario, BienInventario, MovimientoBien,
    
    # Actas
    TipoReunion, ActaReunion, AsistenteActa, HistorialActa,
    
    # Constancias
    ConfiguracionConstancia, SolicitudConstancia, ConstanciaEmitida,
    HistorialTransaccionConstancia, VerificacionConstancia,
    PlantillaCorreoConstancia, ConfiguracionCampoPlantilla
)

# ====================================================================
# CONFIGURACIÓN
# ====================================================================

# Campos únicos por modelo
UNIQUE_FIELDS = {
    'feligres': ['curp'],  # ⚠️ CAMBIO: 'persona' → 'feligres'
    'usuario': ['username'],
    'arquidiocesis': ['nombre_arquidiocesis'],
    'decanato': ['nombre_decanato'],
    'parroquia': ['nombre_parroquia'],
    'comunidad': ['clave_comunidad'],
    'capilla': ['nombre_capilla'],
    'centro_catecismo': ['nombre_centro'],
    'rol_catequista': ['nombre_rol'],
    'rol': ['nombre_rol'],
    'perfil_usuario': ['nombre_perfil'],
    'grupo_parroquial': ['nombre_grupo'],
    'bodega': ['codigo_bodega'],
    'bien_inventario': ['codigo_bien'],
    'area_parroquial': ['nombre_area'],
    'tipo_reunion': ['nombre_tipo'],
    'solicitud_constancia': ['payu_reference_code'],
    'constancia_emitida': ['folio'],
    'plantilla_correo_constancia': ['nombre_plantilla'],
}

# ✅ ORDEN DE SINCRONIZACIÓN COMPLETO Y CORRECTO
SYNC_ORDER = [
    # ========================================
    # GEOGRAFÍA (sin cambios)
    # ========================================
    Pais,
    Provincia,
    Arquidiocesis,
    Decanato,
    Parroquia,
    Comunidad,
    Capilla,
    
    # ========================================
    # ⚠️ FELIGRESES (ANTES: PERSONAS)
    # ========================================
    Feligres,      # ⚠️ CAMBIO CRÍTICO
    Telefono,      # Depende de Feligres
    Direccion,     # Depende de Feligres
    
    # ========================================
    # CATEQUESIS
    # ========================================
    CentroCatecismo,
    GrupoCatequesis,
    RolCatequista,
    RolCatequistaIntegrante,
    Catecumeno,    # Depende de Feligres
    
    # ========================================
    # CLERO
    # ========================================
    Presbitero,    # Depende de Feligres
    
    # ========================================
    # SACRAMENTOS
    # ========================================
    SacramentoBautizo,       # Depende de Feligres
    SacramentoConfirmacion,  # Depende de Feligres
    SacramentoEucaristia,    # Depende de Feligres
    SacramentoMatrimonio,    # Depende de Feligres
    RenovacionBautismal,     # Depende de Feligres
    
    # ========================================
    # GRUPOS Y EDUCACIÓN
    # ========================================
    GrupoParroquial,
    Rol,
    MembresiaGrupo,  # Depende de Feligres
    Curso,
    TemaCurso,
    Actividad,
    Salon,
    Horario,
    ReservacionSalon,  # Depende de Feligres
    Sesion,
    Inscripcion,       # Depende de Feligres
    RegistroAsistencia,  # Depende de Feligres
    ReunionGrupal,
    AsistenciaReunion,   # Depende de Feligres
    
    # ========================================
    # SISTEMA
    # ========================================
    PerfilUsuario,
    Usuario,         # Depende de Feligres
    UsuarioPerfil,   # Depende de Usuario
    
    # ========================================
    # FINANZAS
    # ========================================
    PresupuestoAnual,
    CategoriaFinanciera,
    Donador,         # Puede depender de Feligres
    TransaccionFinanciera,
    
    # ========================================
    # INVENTARIO
    # ========================================
    Bodega,
    AreaParroquial,
    CategoriaInventario,
    BienInventario,
    MovimientoBien,  # Depende de Usuario (que depende de Feligres)
    
    # ========================================
    # ACTAS
    # ========================================
    TipoReunion,
    ActaReunion,     # Depende de Feligres (responsable)
    AsistenteActa,   # Depende de Feligres
    HistorialActa,   # Depende de Usuario
    
    # ========================================
    # CONSTANCIAS
    # ========================================
    ConfiguracionConstancia,
    PlantillaCorreoConstancia,
    ConfiguracionCampoPlantilla,
    SolicitudConstancia,
    ConstanciaEmitida,
    HistorialTransaccionConstancia,
    VerificacionConstancia,
]

# ====================================================================
# CACHÉ SIMPLE
# ====================================================================

class SyncCache:
    """Caché simplificado sin threading complejo."""
    
    def __init__(self):
        self.mapeo: Dict[str, Dict[int, int]] = {}
        self.duplicados: Dict[str, Dict[str, int]] = {}
        
    def agregar_mapeo(self, tabla: str, id_local: int, id_remoto: int):
        if tabla not in self.mapeo:
            self.mapeo[tabla] = {}
        self.mapeo[tabla][id_local] = id_remoto
    
    def obtener_id_remoto(self, tabla: str, id_local: int) -> Optional[int]:
        return self.mapeo.get(tabla, {}).get(id_local)
    
    def agregar_duplicado(self, tabla: str, valor: str, id_reg: int):
        if tabla not in self.duplicados:
            self.duplicados[tabla] = {}
        self.duplicados[tabla][valor] = id_reg
    
    def buscar_por_unico(self, tabla: str, valor: str) -> Optional[int]:
        return self.duplicados.get(tabla, {}).get(valor)

# ====================================================================
# FUNCIONES AUXILIARES
# ====================================================================

def obtener_pk_field(modelo: Type[SQLModel]) -> str:
    """Obtiene campo de clave primaria."""
    return list(modelo.__table__.primary_key.columns)[0].name

def buscar_registro_existente(
    modelo: Type[SQLModel],
    registro_origen,
    session: Session,
    cache: SyncCache
) -> Optional[SQLModel]:
    """Busca registro existente por id_remoto o campos únicos."""
    tabla = modelo.__tablename__
    
    # 1. Por id_remoto
    if hasattr(registro_origen, 'id_remoto') and registro_origen.id_remoto:
        try:
            registro = session.get(modelo, registro_origen.id_remoto)
            if registro:
                return registro
        except:
            pass
    
    # 2. Por campos únicos
    campos = UNIQUE_FIELDS.get(tabla, [])
    for campo in campos:
        if hasattr(registro_origen, campo):
            valor = getattr(registro_origen, campo)
            if valor:
                if isinstance(valor, str):
                    valor = valor.strip().upper()
                
                try:
                    statement = select(modelo).where(getattr(modelo, campo) == valor)
                    registro = session.exec(statement).first()
                    if registro:
                        return registro
                except:
                    pass
    
    return None

def copiar_campos(registro_origen, modelo_destino: Type[SQLModel]) -> Dict[str, Any]:
    """Copia campos básicos sin procesamiento complejo."""
    datos = {}
    pk_field = obtener_pk_field(modelo_destino)
    
    for campo in modelo_destino.__fields__.keys():
        if campo in ['id_local', 'id_remoto', 'sincronizado', 'fecha_sync', pk_field]:
            continue
        
        if hasattr(registro_origen, campo):
            datos[campo] = getattr(registro_origen, campo)
    
    return datos

# ====================================================================
# SINCRONIZACIÓN SIMPLE
# ====================================================================

def sincronizar_tabla_simple(
    modelo: Type[SQLModel],
    engine_local,
    engine_remoto,
    cache: SyncCache,
    st_display_func,
    batch_size: int = 50
) -> Tuple[int, int, int]:
    """Sincroniza una tabla de forma simple y segura."""
    
    tabla = modelo.__tablename__
    pk_field = obtener_pk_field(modelo)
    creados = actualizados = errores = 0
    
    try:
        # Leer todos los remotos
        with Session(engine_remoto) as session:
            remotos = session.exec(select(modelo)).all()
        
        if not remotos:
            return 0, 0, 0
        
        # Procesar en lotes pequeños
        for i in range(0, len(remotos), batch_size):
            batch = remotos[i:i+batch_size]
            
            # Procesar batch
            with Session(engine_local) as session_local:
                for remoto in batch:
                    try:
                        id_remoto = getattr(remoto, pk_field)
                        
                        # Buscar existente
                        local = buscar_registro_existente(modelo, remoto, session_local, cache)
                        
                        if local:
                            # Actualizar
                            for campo, valor in copiar_campos(remoto, modelo).items():
                                if hasattr(local, campo):
                                    setattr(local, campo, valor)
                            
                            if hasattr(local, 'id_remoto'):
                                local.id_remoto = id_remoto
                            if hasattr(local, 'sincronizado'):
                                local.sincronizado = True
                            if hasattr(local, 'fecha_sync'):
                                local.fecha_sync = datetime.now()
                            
                            session_local.add(local)
                            actualizados += 1
                        else:
                            # Crear
                            datos = copiar_campos(remoto, modelo)
                            nuevo = modelo(**datos)
                            
                            if hasattr(nuevo, 'id_remoto'):
                                nuevo.id_remoto = id_remoto
                            if hasattr(nuevo, 'sincronizado'):
                                nuevo.sincronizado = True
                            if hasattr(nuevo, 'fecha_sync'):
                                nuevo.fecha_sync = datetime.now()
                            
                            session_local.add(nuevo)
                            session_local.flush()
                            
                            id_local = getattr(nuevo, pk_field)
                            cache.agregar_mapeo(tabla, id_local, id_remoto)
                            creados += 1
                    
                    except IntegrityError:
                        errores += 1
                        session_local.rollback()
                        continue
                    except Exception as e:
                        errores += 1
                        print(f"Error en {tabla}: {e}")
                        continue
                
                # Commit del batch
                try:
                    session_local.commit()
                except Exception as e:
                    session_local.rollback()
                    st_display_func(f"⚠️ Error commit {tabla}: {e}", is_warning=True)
            
            # Pequeña pausa entre batches
            time.sleep(0.1)
        
        return creados, actualizados, errores
    
    except Exception as e:
        st_display_func(f"❌ Error en {tabla}: {e}", is_error=True)
        return creados, actualizados, errores + 1

# ====================================================================
# FUNCIÓN PRINCIPAL: REMOTO → LOCAL
# ====================================================================

def sincronizar_bases_de_datos(engine_local, engine_remoto, st_display_func) -> bool:
    """
    Sincroniza Remoto → Local de forma segura.
    ACTUALIZADO para usar modelo Feligres
    """
    
    if not engine_local or not engine_remoto:
        st_display_func("❌ Se requieren ambas conexiones", is_error=True)
        return False
    
    st_display_func("🔄 Iniciando sincronización (Remoto → Local)...")
    st_display_func("📋 Modelo actualizado: Feligres (antes Persona)")
    cache = SyncCache()
    
    total_creados = total_actualizados = total_errores = 0
    
    try:
        for i, modelo in enumerate(SYNC_ORDER, 1):
            tabla = modelo.__tablename__
            
            # Mensaje especial para Feligres
            if tabla == "feligres":
                st_display_func(f"📋 [{i}/{len(SYNC_ORDER)}] ⚠️ {tabla} (Modelo Base - antes 'persona')...")
            else:
                st_display_func(f"📋 [{i}/{len(SYNC_ORDER)}] {tabla}...")
            
            creados, actualizados, errores = sincronizar_tabla_simple(
                modelo, engine_local, engine_remoto, cache, st_display_func, batch_size=50
            )
            
            total_creados += creados
            total_actualizados += actualizados
            total_errores += errores
            
            if creados > 0 or actualizados > 0:
                st_display_func(f"  ✅ {creados} creados, {actualizados} actualizados")
            
            if errores > 0:
                st_display_func(f"  ⚠️ {errores} errores", is_warning=True)
            
            # Pausa pequeña entre tablas
            time.sleep(0.1)
        
        # Resumen
        st_display_func("─" * 60)
        st_display_func(f"✅ Creados: {total_creados}")
        st_display_func(f"🔄 Actualizados: {total_actualizados}")
        
        if total_errores > 0:
            st_display_func(f"⚠️ Errores: {total_errores}", is_warning=True)
        
        st_display_func("✅ Sincronización completada - Modelo Feligres activo")
        
        return total_errores == 0
    
    except Exception as e:
        st_display_func(f"❌ Error crítico: {e}", is_error=True)
        traceback.print_exc()
        return False

# ====================================================================
# FUNCIÓN AUXILIAR: LOCAL → REMOTO
# ====================================================================

def sincronizar_local_a_remoto(engine_local, engine_remoto, st_display_func) -> bool:
    """
    Sincroniza Local → Remoto de forma segura.
    ACTUALIZADO para usar modelo Feligres
    """
    
    if not engine_local or not engine_remoto:
        st_display_func("❌ Se requieren ambas conexiones", is_error=True)
        return False
    
    st_display_func("🔄 Sincronizando Local → Remoto...")
    st_display_func("📋 Modelo actualizado: Feligres (antes Persona)")
    cache = SyncCache()
    
    total_enviados = total_actualizados = 0
    
    try:
        for modelo in SYNC_ORDER:
            tabla = modelo.__tablename__
            pk_field = obtener_pk_field(modelo)
            
            # Buscar no sincronizados
            with Session(engine_local) as session:
                if not hasattr(modelo, 'sincronizado'):
                    continue
                
                pendientes = session.exec(
                    select(modelo).where(
                        (getattr(modelo, 'sincronizado') == False) |
                        (getattr(modelo, 'id_remoto').is_(None))
                    )
                ).all()
            
            if not pendientes:
                continue
            
            # Mensaje especial para Feligres
            if tabla == "feligres":
                st_display_func(f"📤 feligres (Modelo Base): {len(pendientes)} pendientes...")
            else:
                st_display_func(f"📤 {tabla}: {len(pendientes)} pendientes...")
            
            for local in pendientes:
                try:
                    id_local = getattr(local, pk_field)
                    
                    with Session(engine_remoto) as session_remoto:
                        remoto = buscar_registro_existente(modelo, local, session_remoto, cache)
                        
                        if remoto:
                            # Actualizar
                            for campo, valor in copiar_campos(local, modelo).items():
                                if hasattr(remoto, campo) and campo != pk_field:
                                    setattr(remoto, campo, valor)
                            
                            if hasattr(remoto, 'id_local'):
                                remoto.id_local = id_local
                            
                            session_remoto.add(remoto)
                            session_remoto.commit()
                            
                            id_remoto = getattr(remoto, pk_field)
                            total_actualizados += 1
                        else:
                            # Crear
                            datos = copiar_campos(local, modelo)
                            nuevo = modelo(**datos)
                            
                            if hasattr(nuevo, 'id_local'):
                                nuevo.id_local = id_local
                            
                            session_remoto.add(nuevo)
                            session_remoto.commit()
                            session_remoto.refresh(nuevo)
                            
                            id_remoto = getattr(nuevo, pk_field)
                            total_enviados += 1
                        
                        # Actualizar local
                        with Session(engine_local) as session_local:
                            registro = session_local.get(modelo, id_local)
                            if registro:
                                if hasattr(registro, 'id_remoto'):
                                    registro.id_remoto = id_remoto
                                if hasattr(registro, 'sincronizado'):
                                    registro.sincronizado = True
                                if hasattr(registro, 'fecha_sync'):
                                    registro.fecha_sync = datetime.now()
                                session_local.add(registro)
                                session_local.commit()
                
                except IntegrityError:
                    continue
                except Exception as e:
                    print(f"Error en {tabla}: {e}")
                    continue
                
                # Pausa pequeña
                time.sleep(0.05)
        
        st_display_func(f"✅ Enviados: {total_enviados}, Actualizados: {total_actualizados}")
        st_display_func("✅ Sincronización Local → Remoto completada")
        return True
    
    except Exception as e:
        st_display_func(f"❌ Error: {e}", is_error=True)
        return False

# ====================================================================
# VERIFICACIÓN DE INTEGRIDAD
# ====================================================================

def verificar_integridad_feligres(engine_local, engine_remoto, st_display_func) -> bool:
    """
    Verifica la integridad de los datos de Feligres entre ambas bases.
    NUEVA FUNCIÓN: Específica para el modelo Feligres
    """
    st_display_func("🔍 Verificando integridad de Feligres...")
    
    try:
        with Session(engine_local) as session_local:
            feligreses_local = session_local.exec(select(Feligres)).all()
        
        with Session(engine_remoto) as session_remoto:
            feligreses_remoto = session_remoto.exec(select(Feligres)).all()
        
        st_display_func(f"📊 Local: {len(feligreses_local)} feligreses")
        st_display_func(f"📊 Remoto: {len(feligreses_remoto)} feligreses")
        
        # Verificar CURPs únicos
        curps_local = {f.curp for f in feligreses_local if f.curp}
        curps_remoto = {f.curp for f in feligreses_remoto if f.curp}
        
        solo_local = curps_local - curps_remoto
        solo_remoto = curps_remoto - curps_local
        
        if solo_local:
            st_display_func(f"⚠️ {len(solo_local)} feligreses solo en Local", is_warning=True)
        
        if solo_remoto:
            st_display_func(f"⚠️ {len(solo_remoto)} feligreses solo en Remoto", is_warning=True)
        
        if not solo_local and not solo_remoto:
            st_display_func("✅ Bases sincronizadas correctamente")
            return True
        
        return False
        
    except Exception as e:
        st_display_func(f"❌ Error verificando integridad: {e}", is_error=True)
        return False

# ====================================================================
# EXPORTACIÓN
# ====================================================================

__all__ = [
    'SYNC_ORDER',
    'SyncCache',
    'sincronizar_bases_de_datos',
    'sincronizar_local_a_remoto',
    'verificar_integridad_feligres',
]