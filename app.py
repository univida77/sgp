# app.py - SISTEMA PARROQUIAL V4.0 CON SUPABASE
"""
Sistema de Gestión Parroquial v4.0
Base de datos: SQLite (local) + Supabase/PostgreSQL (remoto)

⚠️ CAMBIO ARQUITECTÓNICO: Persona → Feligres

Parroquia de Santa María de la Asunción
Tlacolula de Matamoros, Oaxaca
"""

import streamlit as st
from datetime import date, datetime
from sqlmodel import Session, select, SQLModel, func

# Cargar variables de entorno desde .env si existe
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv no instalado, usar variables de sistema directamente

# ====================================================================
# CONFIGURACIÓN INICIAL
# ====================================================================

st.set_page_config(
    page_title="Sistema Parroquial v4.0",
    page_icon="⛪",
    layout="wide",
    initial_sidebar_state="expanded"
)

SQLModel.metadata.clear()

# ====================================================================
# IMPORTS DE MÓDULOS
# ====================================================================

# Core
from models import *
from sync_manager import sincronizar_bases_de_datos, sincronizar_local_a_remoto

# Database
from database import local as database_local
from database import remote as database_remote

# Módulos: Feligreses (⚠️ CAMBIO: antes Personas)
from modules.feligreses import crud_feligreses, crud_contacto, crud_catecumenos

# Módulos: Pastoral
from modules.geografia import crud_geografia
from modules.sacramentos import crud_sacramentos
from modules.clero import crud_presbiteros
from modules.grupos import crud_cursos_catequesis, crud_grupo_parroquial

# Módulos: Educación
from modules.educacion import crud_cursos, crud_actividades, crud_sesiones
from modules.espacios import crud_salones
from modules.asistencia import crud_asistencia

# Módulos: Administración
from modules.finanzas import crud_finanzas
from modules.inventario import crud_inventario
from modules.actas import crud_actas
from modules.constancias import crud_constancias

# Módulos: Sistema
from modules.sistema import crud_usuarios

# ====================================================================
# FUNCIONES AUXILIARES
# ====================================================================

def st_display_func(message, is_error=False, is_warning=False):
    """Función para mostrar mensajes estandarizados"""
    if is_error:
        st.error(message)
    elif is_warning:
        st.warning(message)
    else:
        st.success(message)


@st.cache_resource(ttl=300)
def get_database_engines():
    """Obtiene engines con caché para mejor rendimiento"""
    local_engine = database_local.get_engine()
    remote_engine = database_remote.get_engine()
    return local_engine, remote_engine


def sincronizar_todas_las_tablas(db_local_engine, db_remote_engine, st_display_func):
    """Sincronización completa bidireccional"""
    if not db_local_engine or not db_remote_engine:
        st.error("❌ Se requieren ambas conexiones.")
        return

    forzar_recreacion = st.checkbox(
        "⚠️ Forzar recreación completa de BD remota",
        help="Elimina y recrea todas las tablas en Supabase",
        key="forzar_recreacion_bd"
    )

    if forzar_recreacion:
        st.warning("⚠️ Esta opción eliminará y recreará la base de datos remota...")
        if st.button("🔴 CONFIRMAR RECREACIÓN", type="primary"):
            if database_remote.eliminar_y_recrear_base_de_datos(db_remote_engine, st_display_func):
                st.success("✅ Base de datos remota recreada")
            else:
                st.error("❌ No se pudo recrear la base de datos")
                return
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 SUPABASE → LOCAL", use_container_width=True, key="sync_remote_to_local"):
            with st.spinner("Sincronizando desde Supabase..."):
                if sincronizar_bases_de_datos(db_local_engine, db_remote_engine, st_display_func):
                    st.success("✅ Sincronización completada")
                    st.balloons()
                else:
                    st.error("❌ Hubo errores en la sincronización")
    
    with col2:
        if st.button("📤 LOCAL → SUPABASE", use_container_width=True, key="sync_local_to_remote"):
            with st.spinner("Enviando cambios a Supabase..."):
                if sincronizar_local_a_remoto(db_local_engine, db_remote_engine, st_display_func):
                    st.success("✅ Cambios enviados a Supabase")
                else:
                    st.error("❌ Hubo errores al enviar")


def obtener_estadisticas_rapidas(db_engine, db_module):
    """
    Obtiene estadísticas rápidas del sistema.
    ⚠️ ACTUALIZADO para usar Feligres
    """
    try:
        with Session(db_engine) as session:
            stats = {
                'feligreses': session.exec(select(func.count(Feligres.id_feligres))).first() or 0,  # ⚠️ CAMBIO
                'telefonos': session.exec(select(func.count(Telefono.id_telefono))).first() or 0,
                'direcciones': session.exec(select(func.count(Direccion.id_direccion))).first() or 0,
                'catecumenos': session.exec(select(func.count(Catecumeno.id_catecumeno))).first() or 0,
                'actividades': session.exec(select(func.count(Actividad.id_actividad))).first() or 0,
                'sesiones': session.exec(select(func.count(Sesion.id_sesion))).first() or 0,
                'grupos': session.exec(select(func.count(GrupoParroquial.id_grupo))).first() or 0,
                'transacciones': session.exec(select(func.count(TransaccionFinanciera.id_transaccion))).first() or 0,
                'bienes': session.exec(select(func.count(BienInventario.id_bien))).first() or 0,
                'actas': session.exec(select(func.count(ActaReunion.id_acta))).first() or 0,
                'constancias': session.exec(select(func.count(ConstanciaEmitida.id_constancia))).first() or 0
            }
        return stats
    except Exception as e:
        print(f"Error obteniendo estadísticas: {e}")
        return None


# ====================================================================
# PÁGINA DE INICIO
# ====================================================================

def mostrar_pagina_inicio():
    """Página principal del sistema"""
    st.header("🏠 Sistema de Gestión Parroquial v4.0")
    
    st.markdown("""
    ### ⛪ Parroquia de Santa María de la Asunción
    **Tlacolula de Matamoros, Oaxaca**  
    *Arquidiócesis de Antequera-Oaxaca A.R.*
    
    ---
    
    ### 🎯 Sistema Completo de Gestión Pastoral y Administrativa
    
    **Versión 4.0** - Arquitectura modular con Supabase  
    ⚠️ **Modelo actualizado: Feligres** (antes Personas)
    """)
    
    # Mostrar estadísticas si hay conexión
    if db_engine and db_module:
        stats = obtener_estadisticas_rapidas(db_engine, db_module)
        
        if stats:
            st.markdown("### 📊 Estadísticas del Sistema")
            
            # Fila 1: Feligreses (⚠️ CAMBIO)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("👥 Feligreses", f"{stats['feligreses']:,}")  # ⚠️ CAMBIO
            with col2:
                st.metric("📱 Teléfonos", f"{stats['telefonos']:,}")
            with col3:
                st.metric("🏠 Direcciones", f"{stats['direcciones']:,}")
            with col4:
                st.metric("📚 Catecúmenos", f"{stats['catecumenos']:,}")
            
            # Fila 2: Educación
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("👥 Grupos", f"{stats['grupos']:,}")
            with col2:
                st.metric("🎯 Actividades", f"{stats['actividades']:,}")
            with col3:
                st.metric("📅 Sesiones", f"{stats['sesiones']:,}")
            with col4:
                completitud = (stats['telefonos'] / stats['feligreses'] * 100) if stats['feligreses'] > 0 else 0
                st.metric("✅ Contactos", f"{completitud:.0f}%")
            
            # Fila 3: Administración
            if stats['transacciones'] > 0 or stats['bienes'] > 0:
                st.markdown("---")
                st.markdown("### 💼 Administración")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("💰 Transacciones", f"{stats['transacciones']:,}")
                with col2:
                    st.metric("📦 Bienes", f"{stats['bienes']:,}")
                with col3:
                    st.metric("📄 Actas", f"{stats['actas']:,}")
                with col4:
                    st.metric("📜 Constancias", f"{stats['constancias']:,}")
    
    st.markdown("---")
    
    # Módulos disponibles
    with st.expander("📋 Módulos Disponibles", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **👥 Gestión de Feligreses**
            - Registro de feligreses
            - Contacto (teléfonos/direcciones)
            - Catecúmenos
            
            **⛪ Gestión Pastoral**
            - Geografía eclesiástica
            - Sacramentos
            - Presbíteros
            - Grupos de catequesis
            - Grupos parroquiales
            """)
        
        with col2:
            st.markdown("""
            **📚 Gestión Educativa**
            - Cursos y contenidos
            - Actividades pastorales
            - Sesiones y horarios
            - Salones y espacios
            - Control de asistencia
            """)
        
        with col3:
            st.markdown("""
            **💼 Gestión Administrativa**
            - 💰 Finanzas (ingresos/egresos)
            - 📦 Inventario de bienes
            - 📄 Archivo de actas
            - 📜 Constancias oficiales
            
            **⚙️ Sistema**
            - Usuarios y permisos
            - Sincronización con Supabase
            """)


# ====================================================================
# CONFIGURACIÓN DE BASE DE DATOS (SIDEBAR)
# ====================================================================

with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    
    db_mode = st.radio(
        "Modo de BD:",
        ["Local (SQLite)", "Remoto (Supabase)"],
        key="db_mode"
    )
    
    # Variables globales
    db_engine = None
    db_module = None
    db_remote_engine = None
    db_local_engine = None
    remote_connected = False
    usuario_actual = None
    
    # Obtener engines
    cached_local, cached_remote = get_database_engines()
    
    if db_mode == "Local (SQLite)":
        db_local_engine = cached_local
        db_engine = db_local_engine
        db_module = database_local
        st.success("✅ SQLite Conectado")
        
        if db_engine:
            pendientes = database_local.contar_pendientes_sincronizacion(db_engine)
            if pendientes > 0:
                st.warning(f"⚠️ {pendientes} cambios sin sincronizar")
            else:
                st.info("✅ Todo sincronizado")
    else:
        db_remote_engine = cached_remote
        if db_remote_engine:
            db_engine = db_remote_engine
            db_module = database_remote
            remote_connected = True
            st.success("✅ Supabase Conectado")
        else:
            st.error("❌ No conectado a Supabase")
            st.info("💡 Configura tus credenciales")
            with st.expander("📖 Ver instrucciones"):
                st.markdown("""
                **1. Crea proyecto en Supabase:**
                - https://supabase.com
                
                **2. Obtén credenciales:**
                - Settings → Database → Connection string
                
                **3. Configura variables:**
                ```powershell
                $env:SUPABASE_HOST="db.xxx.supabase.co"
                $env:SUPABASE_PASSWORD="tu_password"
                ```
                
                **4. Reinicia la app**
                """)


# ====================================================================
# BOTÓN DE SINCRONIZACIÓN
# ====================================================================

with st.sidebar:
    st.markdown("### 🔄 Sincronización")
    
    if remote_connected:
        if not db_local_engine:
            db_local_engine = cached_local
        
        pendientes = 0
        if db_local_engine:
            pendientes = database_local.contar_pendientes_sincronizacion(db_local_engine)
        
        if pendientes > 0:
            st.warning(f"⚠️ {pendientes} cambios pendientes")
        
        if st.button("🔄 SINCRONIZAR", type="primary", use_container_width=True):
            sincronizar_todas_las_tablas(db_local_engine, db_remote_engine, st_display_func)
    else:
        st.info("💡 Conéctate a Supabase para sincronizar")
    
    st.markdown("---")


# ====================================================================
# MENÚ PRINCIPAL
# ====================================================================

with st.sidebar:
    st.markdown("## 📋 Menú Principal")
    
    menu_option = st.radio(
        "Navega:",
        [
            "🏠 Inicio",
            
            "--- 👥 FELIGRESES ---",  # ⚠️ CAMBIO
            "👥 Feligreses",          # ⚠️ CAMBIO
            "📱 Contacto",
            "📚 Catecúmenos",
            
            "--- ⛪ PASTORAL ---",
            "🌎 Geografía",
            "✝️ Sacramentos",
            "🙏 Presbíteros",
            "👥 Grupos Catequesis",
            "⛪ Grupos Parroquiales",
            
            "--- 📚 EDUCACIÓN ---",
            "📖 Cursos",
            "🎯 Actividades",
            "📅 Sesiones",
            "🏫 Salones",
            "✅ Asistencia",
            
            "--- 💼 ADMINISTRACIÓN ---",
            "💰 Finanzas",
            "📦 Inventario",
            "📄 Actas",
            "📜 Constancias",
            
            "--- ⚙️ SISTEMA ---",
            "👤 Usuarios",
            "📊 Dashboard",
        ],
        key="menu_principal",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.caption(f"**Modo:** {db_mode}")
    st.caption("**Versión:** 4.0 + Supabase")
    st.caption("⚠️ Modelo: **Feligres**")  # ⚠️ NUEVO
    st.caption("🕐 " + datetime.now().strftime("%H:%M:%S"))


# ====================================================================
# PROCESAMIENTO DE OPCIONES DEL MENÚ
# ====================================================================

# Separadores (no hacen nada)
if menu_option.startswith("---"):
    mostrar_pagina_inicio()

# Página de inicio
elif menu_option == "🏠 Inicio":
    mostrar_pagina_inicio()

# ========== MÓDULO: FELIGRESES (⚠️ CAMBIO: antes Personas) ==========
elif menu_option == "👥 Feligreses":  # ⚠️ CAMBIO
    if db_engine and db_module:
        crud_feligreses.mostrar_crud_feligreses(db_engine, db_module, db_mode, st_display_func)
    else:
        st.error("❌ Sin conexión a la base de datos")

elif menu_option == "📱 Contacto":
    if db_engine and db_module:
        crud_contacto.mostrar_crud_contacto(db_engine, db_module, db_mode, st_display_func)
    else:
        st.error("❌ Sin conexión")

elif menu_option == "📚 Catecúmenos":
    if db_engine and db_module:
        crud_catecumenos.mostrar_crud_catecumenos(db_engine, db_module, db_mode, st_display_func)
    else:
        st.error("❌ Sin conexión")

# ========== MÓDULO: PASTORAL ==========
elif menu_option == "🌎 Geografía":
    if db_engine and db_module:
        crud_geografia.mostrar_crud_geografia(db_engine, db_module, db_mode, st_display_func)
    else:
        st.error("❌ Sin conexión")

elif menu_option == "✝️ Sacramentos":
    if db_engine and db_module:
        crud_sacramentos.mostrar_crud_sacramentos(db_engine, db_module, db_mode, st_display_func)
    else:
        st.error("❌ Sin conexión")

elif menu_option == "🙏 Presbíteros":
    if db_engine and db_module:
        crud_presbiteros.mostrar_crud_presbiteros(db_engine, db_module, db_mode, st_display_func)
    else:
        st.error("❌ Sin conexión")

elif menu_option == "👥 Grupos Catequesis":
    if db_engine and db_module:
        crud_cursos_catequesis.mostrar_crud_cursos_catequesis(db_engine, db_module, db_mode, st_display_func)
    else:
        st.error("❌ Sin conexión")

elif menu_option == "⛪ Grupos Parroquiales":
    if db_engine and db_module:
        crud_grupo_parroquial.mostrar_crud_grupos_parroquiales(db_engine, db_module, db_mode, st_display_func)
    else:
        st.error("❌ Sin conexión")

# ========== MÓDULO: EDUCACIÓN ==========
elif menu_option == "📖 Cursos":
    if db_engine and db_module:
        crud_cursos.mostrar_crud_cursos(db_engine, db_module, db_mode, st_display_func)
    else:
        st.error("❌ Sin conexión")

elif menu_option == "🎯 Actividades":
    if db_engine and db_module:
        crud_actividades.mostrar_crud_actividades(db_engine, db_module, db_mode, st_display_func)
    else:
        st.error("❌ Sin conexión")

elif menu_option == "📅 Sesiones":
    if db_engine and db_module:
        crud_sesiones.mostrar_crud_sesiones(db_engine, db_module, db_mode, st_display_func)
    else:
        st.error("❌ Sin conexión")

elif menu_option == "🏫 Salones":
    if db_engine and db_module:
        crud_salones.mostrar_crud_salones(db_engine, db_module, db_mode, st_display_func)
    else:
        st.error("❌ Sin conexión")

elif menu_option == "✅ Asistencia":
    if db_engine and db_module:
        crud_asistencia.mostrar_crud_asistencia(db_engine, db_module, db_mode, st_display_func)
    else:
        st.error("❌ Sin conexión")

# ========== MÓDULO: ADMINISTRACIÓN ==========
elif menu_option == "💰 Finanzas":
    if db_engine and db_module:
        crud_finanzas.mostrar_crud_finanzas(db_engine, db_module, db_mode, st_display_func, usuario_actual)
    else:
        st.error("❌ Sin conexión")

elif menu_option == "📦 Inventario":
    if db_engine and db_module:
        crud_inventario.mostrar_crud_inventario(db_engine, db_module, db_mode, st_display_func, usuario_actual)
    else:
        st.error("❌ Sin conexión")

elif menu_option == "📄 Actas":
    if db_engine and db_module:
        crud_actas.mostrar_crud_actas(db_engine, db_module, db_mode, st_display_func, usuario_actual)
    else:
        st.error("❌ Sin conexión")

elif menu_option == "📜 Constancias":
    if db_engine and db_module:
        crud_constancias.mostrar_crud_constancias(db_engine, db_module, db_mode, st_display_func, usuario_actual)
    else:
        st.error("❌ Sin conexión")

# ========== MÓDULO: SISTEMA ==========
elif menu_option == "👤 Usuarios":
    if db_engine and db_module:
        crud_usuarios.mostrar_crud_usuarios(db_engine, db_module, db_mode, st_display_func)
    else:
        st.error("❌ Sin conexión")

elif menu_option == "📊 Dashboard":
    if db_engine and db_module:
        st.header("📊 Dashboard Completo")
        mostrar_pagina_inicio()
    else:
        st.error("❌ Sin conexión")


# ====================================================================
# FOOTER
# ====================================================================

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888;'>"
    "Sistema Parroquial v4.0 - Supabase Edition<br>"
    "⚠️ Modelo actualizado: <strong>Feligres</strong> (antes Personas)<br>"
    "Parroquia de Santa María de la Asunción • Tlacolula de Matamoros, Oaxaca<br>"
    "✨ Desarrollado con ❤️ para la gestión pastoral y administrativa"
    "</div>",
    unsafe_allow_html=True
)