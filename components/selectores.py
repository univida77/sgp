# components/selectores.py - Componentes Reutilizables
"""
Selectores y componentes reutilizables para evitar duplicación de código
"""

import streamlit as st
from typing import Optional, Dict, Tuple
from sqlmodel import Session, select
from models import (
    Persona, GrupoParroquial, Comunidad, Presbitero, 
    CentroCatecismo, Salon, Actividad, Parroquia
)

# ====================================================================
# SELECTOR DE PERSONAS
# ====================================================================

def selector_persona_completo(
    db_engine,
    label: str = "Persona",
    key_prefix: str = "persona",
    requerido: bool = True,
    con_busqueda_curp: bool = True
) -> Optional[int]:
    """
    Selector completo de persona con búsqueda por CURP y lista desplegable
    
    Returns:
        int: id_persona seleccionado o None
    """
    persona_encontrada = None
    
    if con_busqueda_curp:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            curp_busqueda = st.text_input(
                f"Buscar {label} por CURP",
                max_chars=18,
                key=f"{key_prefix}_curp",
                help="Ingresa el CURP para búsqueda rápida"
            )
            
            if curp_busqueda:
                from utils import buscar_persona_por_curp
                persona_encontrada = buscar_persona_por_curp(curp_busqueda, db_engine)
                if persona_encontrada:
                    st.success(f"✅ {persona_encontrada.nombre_completo()}")
                else:
                    st.warning("⚠️ CURP no encontrado")
        
        with col2:
            opciones = _obtener_opciones_personas(db_engine, requerido)
            id_sel = st.selectbox(
                f"{label}:",
                options=opciones.keys(),
                format_func=lambda x: opciones[x],
                key=f"{key_prefix}_select"
            )
    else:
        opciones = _obtener_opciones_personas(db_engine, requerido)
        id_sel = st.selectbox(
            f"{label}:",
            options=opciones.keys(),
            format_func=lambda x: opciones[x],
            key=f"{key_prefix}_select"
        )
    
    # Determinar ID final
    if persona_encontrada:
        return persona_encontrada.id_persona
    elif id_sel != 0:
        return id_sel
    else:
        return None


def selector_persona_simple(
    db_engine,
    label: str = "Persona",
    key: str = "persona_simple",
    requerido: bool = True
) -> Optional[int]:
    """
    Selector simple de persona (solo desplegable)
    
    Returns:
        int: id_persona seleccionado o None
    """
    opciones = _obtener_opciones_personas(db_engine, requerido)
    
    id_sel = st.selectbox(
        label,
        options=opciones.keys(),
        format_func=lambda x: opciones[x],
        key=key
    )
    
    return id_sel if id_sel != 0 else None


def _obtener_opciones_personas(db_engine, requerido: bool) -> Dict[int, str]:
    """Obtiene opciones de personas para selectbox"""
    with Session(db_engine) as session:
        personas = session.exec(select(Persona)).all()
    
    if not personas:
        st.error("❌ No hay personas registradas")
        return {0: "-- No hay personas --"}
    
    texto_vacio = "-- Selecciona --" if requerido else "-- Opcional --"
    opciones = {0: texto_vacio}
    opciones.update({
        p.id_persona: f"{p.nombre_completo()} - {p.curp or 'Sin CURP'}"
        for p in personas
    })
    
    return opciones


# ====================================================================
# SELECTOR DE GRUPOS
# ====================================================================

def selector_grupo_parroquial(
    db_engine,
    label: str = "Grupo Parroquial",
    key: str = "grupo",
    solo_activos: bool = True,
    requerido: bool = True
) -> Optional[int]:
    """
    Selector de grupo parroquial
    
    Returns:
        int: id_grupo seleccionado o None
    """
    with Session(db_engine) as session:
        statement = select(GrupoParroquial)
        if solo_activos:
            statement = statement.where(GrupoParroquial.activo == True)
        grupos = session.exec(statement).all()
    
    if not grupos:
        st.error("❌ No hay grupos parroquiales disponibles")
        return None
    
    texto_vacio = "-- Selecciona --" if requerido else "-- Sin grupo --"
    opciones = {0: texto_vacio}
    opciones.update({g.id_grupo: g.nombre_grupo for g in grupos})
    
    id_sel = st.selectbox(
        label,
        options=opciones.keys(),
        format_func=lambda x: opciones[x],
        key=key
    )
    
    return id_sel if id_sel != 0 else None


# ====================================================================
# SELECTOR DE COMUNIDADES
# ====================================================================

def selector_comunidad(
    db_engine,
    label: str = "Comunidad",
    key: str = "comunidad",
    requerido: bool = True,
    mostrar_parroquia: bool = True
) -> Optional[int]:
    """
    Selector de comunidad con información de parroquia
    
    Returns:
        int: id_comunidad seleccionado o None
    """
    with Session(db_engine) as session:
        comunidades = session.exec(select(Comunidad)).all()
    
    if not comunidades:
        st.error("❌ No hay comunidades registradas")
        return None
    
    texto_vacio = "-- Selecciona --" if requerido else "-- Sin comunidad --"
    opciones = {0: texto_vacio}
    
    if mostrar_parroquia:
        with Session(db_engine) as session:
            for c in comunidades:
                parroquia = session.get(Parroquia, c.id_parroquia)
                nombre_completo = f"{c.nombre_comunidad} ({c.clave_comunidad})"
                if parroquia:
                    nombre_completo += f" - {parroquia.nombre_parroquia}"
                opciones[c.id_comunidad] = nombre_completo
    else:
        opciones.update({
            c.id_comunidad: f"{c.nombre_comunidad} ({c.clave_comunidad})"
            for c in comunidades
        })
    
    id_sel = st.selectbox(
        label,
        options=opciones.keys(),
        format_func=lambda x: opciones[x],
        key=key
    )
    
    return id_sel if id_sel != 0 else None


# ====================================================================
# SELECTOR DE PRESBÍTEROS
# ====================================================================

def selector_presbitero(
    db_engine,
    label: str = "Ministro Celebrante",
    key: str = "presbitero",
    requerido: bool = False
) -> Optional[int]:
    """
    Selector de presbítero (sacerdote)
    
    Returns:
        int: id_presbitero seleccionado o None
    """
    with Session(db_engine) as session:
        presbiteros = session.exec(select(Presbitero)).all()
    
    if not presbiteros:
        if requerido:
            st.error("❌ No hay presbíteros registrados")
        else:
            st.info("ℹ️ No hay presbíteros registrados")
        return None
    
    texto_vacio = "-- Selecciona --" if requerido else "-- Sin ministro --"
    opciones = {0: texto_vacio}
    
    with Session(db_engine) as session:
        for pres in presbiteros:
            persona = session.get(Persona, pres.id_persona)
            if persona:
                opciones[pres.id_presbitero] = f"{persona.nombre_completo()} - {pres.cargo}"
    
    id_sel = st.selectbox(
        label,
        options=opciones.keys(),
        format_func=lambda x: opciones[x],
        key=key
    )
    
    return id_sel if id_sel != 0 else None


# ====================================================================
# SELECTOR DE SALONES
# ====================================================================

def selector_salon(
    db_engine,
    label: str = "Salón",
    key: str = "salon",
    id_centro: Optional[int] = None,
    solo_activos: bool = True,
    requerido: bool = False
) -> Optional[int]:
    """
    Selector de salón, opcionalmente filtrado por centro
    
    Returns:
        int: id_salon seleccionado o None
    """
    with Session(db_engine) as session:
        statement = select(Salon)
        
        if id_centro:
            statement = statement.where(Salon.id_centro == id_centro)
        
        if solo_activos:
            statement = statement.where(Salon.activo == True)
        
        salones = session.exec(statement).all()
    
    if not salones:
        if id_centro:
            st.warning("⚠️ No hay salones disponibles en este centro")
        else:
            st.warning("⚠️ No hay salones disponibles")
        return None
    
    texto_vacio = "-- Selecciona --" if requerido else "-- Sin salón --"
    opciones = {0: texto_vacio}
    
    with Session(db_engine) as session:
        for salon in salones:
            centro = session.get(CentroCatecismo, salon.id_centro)
            nombre = salon.nombre_salon
            if centro:
                nombre += f" - {centro.nombre_centro}"
            opciones[salon.id_salon] = nombre
    
    id_sel = st.selectbox(
        label,
        options=opciones.keys(),
        format_func=lambda x: opciones[x],
        key=key
    )
    
    return id_sel if id_sel != 0 else None


# ====================================================================
# SELECTOR DE ACTIVIDADES
# ====================================================================

def selector_actividad(
    db_engine,
    label: str = "Actividad",
    key: str = "actividad",
    id_grupo: Optional[int] = None,
    solo_activas: bool = True,
    requerido: bool = False
) -> Optional[int]:
    """
    Selector de actividad, opcionalmente filtrada por grupo
    
    Returns:
        int: id_actividad seleccionado o None
    """
    with Session(db_engine) as session:
        statement = select(Actividad)
        
        if id_grupo:
            statement = statement.where(Actividad.id_grupo_parroquial == id_grupo)
        
        if solo_activas:
            statement = statement.where(Actividad.activo == True)
        
        actividades = session.exec(statement).all()
    
    if not actividades:
        if not requerido:
            return None
        
        if id_grupo:
            st.warning("⚠️ No hay actividades para este grupo")
        else:
            st.warning("⚠️ No hay actividades disponibles")
        return None
    
    texto_vacio = "-- Selecciona --" if requerido else "-- Sin actividad --"
    opciones = {0: texto_vacio}
    opciones.update({
        a.id_actividad: f"{a.nombre_actividad} ({a.ciclo or 'N/A'})"
        for a in actividades
    })
    
    id_sel = st.selectbox(
        label,
        options=opciones.keys(),
        format_func=lambda x: opciones[x],
        key=key
    )
    
    return id_sel if id_sel != 0 else None


# ====================================================================
# SELECTOR DE FECHAS CON VALIDACIÓN
# ====================================================================

def selector_fecha(
    label: str,
    key: str,
    valor_defecto = None,
    fecha_minima = None,
    fecha_maxima = None,
    requerido: bool = True
):
    """
    Selector de fecha con validaciones comunes
    
    Returns:
        date o None
    """
    if valor_defecto is None:
        from datetime import date
        valor_defecto = date.today()
    
    fecha = st.date_input(
        label,
        value=valor_defecto,
        min_value=fecha_minima,
        max_value=fecha_maxima,
        key=key
    )
    
    if requerido and not fecha:
        st.error(f"❌ {label} es obligatoria")
        return None
    
    return fecha


# ====================================================================
# SELECTOR DE MONEDA
# ====================================================================

def selector_moneda(
    label: str = "Moneda",
    key: str = "moneda",
    valor_defecto: str = "MXN"
) -> str:
    """
    Selector estándar de moneda MXN/USD
    
    Returns:
        str: "MXN" o "USD"
    """
    opciones = ["MXN", "USD"]
    index = opciones.index(valor_defecto) if valor_defecto in opciones else 0
    
    return st.selectbox(
        label,
        options=opciones,
        index=index,
        key=key
    )


# ====================================================================
# SELECTOR DE ESTADO
# ====================================================================

def selector_estado_general(
    label: str = "Estado",
    key: str = "estado",
    estados_personalizados: list = None,
    valor_defecto: str = None
) -> str:
    """
    Selector genérico de estados
    
    Returns:
        str: estado seleccionado
    """
    if estados_personalizados is None:
        estados = ["Activo", "Inactivo"]
    else:
        estados = estados_personalizados
    
    index = 0
    if valor_defecto and valor_defecto in estados:
        index = estados.index(valor_defecto)
    
    return st.selectbox(
        label,
        options=estados,
        index=index,
        key=key
    )


# ====================================================================
# FILTROS COMUNES
# ====================================================================

def filtros_fecha_rango(
    key_prefix: str = "filtro",
    mostrar_mes: bool = True,
    mostrar_anio: bool = True
) -> Tuple[Optional[int], Optional[int]]:
    """
    Filtros estándar de mes y año
    
    Returns:
        Tuple[mes, año]: mes puede ser 0 para "Todos"
    """
    from datetime import date
    
    col1, col2 = st.columns(2)
    
    mes = None
    anio = None
    
    with col1:
        if mostrar_mes:
            mes = st.selectbox(
                "Mes:",
                options=list(range(13)),
                format_func=lambda x: "Todos" if x == 0 else [
                    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
                ][x-1],
                index=date.today().month,
                key=f"{key_prefix}_mes"
            )
    
    with col2:
        if mostrar_anio:
            anio = st.number_input(
                "Año:",
                min_value=2020,
                max_value=2030,
                value=date.today().year,
                key=f"{key_prefix}_anio"
            )
    
    return mes, anio


# ====================================================================
# CONFIRMACIÓN DE ELIMINACIÓN
# ====================================================================

def confirmar_eliminacion(
    mensaje: str,
    key: str,
    callback_si,
    callback_no = None
):
    """
    Diálogo de confirmación para eliminación con patrón de dos pasos
    
    Args:
        mensaje: Mensaje de confirmación
        key: Key única para session_state
        callback_si: Función a ejecutar si confirma
        callback_no: Función opcional si cancela
    """
    CONFIRM_KEY = f"confirm_{key}"
    
    if not st.session_state.get(CONFIRM_KEY, False):
        if st.button("🗑️ Eliminar", type="secondary", key=f"init_{key}"):
            st.session_state[CONFIRM_KEY] = True
            st.rerun()
    else:
        st.error(mensaje)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ SÍ, ELIMINAR", type="primary", use_container_width=True, key=f"yes_{key}"):
                st.session_state.pop(CONFIRM_KEY, None)
                callback_si()
        
        with col2:
            if st.button("❌ Cancelar", use_container_width=True, key=f"no_{key}"):
                st.session_state[CONFIRM_KEY] = False
                if callback_no:
                    callback_no()
                st.rerun()
