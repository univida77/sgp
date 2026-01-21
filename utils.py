# utils.py - Funciones auxiliares optimizadas
"""
MODIFICADO: Persona → Feligres
Todas las funciones actualizadas para trabajar con el modelo Feligres
"""

import streamlit as st
from typing import Optional, Dict, List, Tuple
from sqlmodel import Session, select
from models import Feligres, Presbitero, Parroquia, Comunidad  # ⚠️ CAMBIO
from datetime import date

# ====================================================================
# BÚSQUEDA Y VALIDACIÓN
# ====================================================================

def buscar_feligres_por_curp(curp: str, engine) -> Optional[Feligres]:
    """
    Busca un feligrés por su CURP.
    CAMBIO: Antes era buscar_persona_por_curp
    """
    if not engine or not curp:
        return None
    
    try:
        with Session(engine) as session:
            statement = select(Feligres).where(Feligres.curp == curp.strip().upper())
            return session.exec(statement).first()
    except Exception as e:
        print(f"Error al buscar CURP: {e}")
        return None


def validar_curp(curp: str) -> bool:
    """Valida que el CURP tenga 18 caracteres alfanuméricos."""
    if not curp:
        return False
    curp = curp.strip()
    return len(curp) == 18 and curp.isalnum()


def validar_no_auto_referencia(feligres_id: int, id_padre: Optional[int], 
                               id_madre: Optional[int]) -> bool:
    """
    Valida que un feligrés no sea su propio padre o madre.
    CAMBIO: Antes era persona_id
    """
    if id_padre and id_padre == feligres_id:
        return False
    if id_madre and id_madre == feligres_id:
        return False
    return True


def validar_matrimonio(id_varon: int, id_mujer: int) -> bool:
    """Valida que los contrayentes no sean la misma persona."""
    return id_varon != id_mujer


def validar_email(email: str) -> bool:
    """Validación básica de formato de email."""
    if not email:
        return False
    return '@' in email and '.' in email.split('@')[1]


# ====================================================================
# OBTENCIÓN DE LISTAS
# ====================================================================

def obtener_lista_feligreses(engine) -> List[Feligres]:
    """
    Obtiene todos los feligreses ordenados alfabéticamente.
    CAMBIO: Antes era obtener_lista_personas
    """
    if not engine:
        return []
    try:
        with Session(engine) as session:
            statement = select(Feligres).order_by(
                Feligres.apellido_paterno, 
                Feligres.apellido_materno,
                Feligres.nombres
            )
            return session.exec(statement).all()
    except Exception as e:
        print(f"Error al obtener feligreses: {e}")
        return []


def obtener_lista_presbiteros(engine) -> List[Tuple[Presbitero, Feligres]]:
    """
    Obtiene todos los presbíteros con su información de feligrés.
    CAMBIO: Ahora retorna (Presbitero, Feligres)
    """
    if not engine:
        return []
    try:
        with Session(engine) as session:
            presbiteros = session.exec(select(Presbitero)).all()
            resultado = []
            for pres in presbiteros:
                feligres = session.get(Feligres, pres.id_feligres)
                if feligres:
                    resultado.append((pres, feligres))
            return resultado
    except Exception as e:
        print(f"Error al obtener presbíteros: {e}")
        return []


def obtener_lista_parroquias(engine) -> List[Parroquia]:
    """Obtiene todas las parroquias ordenadas alfabéticamente."""
    if not engine:
        return []
    try:
        with Session(engine) as session:
            statement = select(Parroquia).order_by(Parroquia.nombre_parroquia)
            return session.exec(statement).all()
    except Exception as e:
        print(f"Error al obtener parroquias: {e}")
        return []


def obtener_lista_comunidades(engine, id_parroquia: Optional[int] = None) -> List[Comunidad]:
    """
    Obtiene todas las comunidades, opcionalmente filtradas por parroquia.
    """
    if not engine:
        return []
    try:
        with Session(engine) as session:
            statement = select(Comunidad).order_by(Comunidad.nombre_comunidad)
            if id_parroquia:
                statement = statement.where(Comunidad.id_parroquia == id_parroquia)
            return session.exec(statement).all()
    except Exception as e:
        print(f"Error al obtener comunidades: {e}")
        return []


# ====================================================================
# RELACIONES FAMILIARES
# ====================================================================

def obtener_padres(feligres: Feligres, engine) -> Tuple[Optional[Feligres], Optional[Feligres]]:
    """
    Obtiene los objetos Padre y Madre de un feligrés.
    CAMBIO: Ahora trabaja con Feligres
    """
    if not engine:
        return None, None
    
    try:
        with Session(engine) as session:
            padre = session.get(Feligres, feligres.id_padre) if feligres.id_padre else None
            madre = session.get(Feligres, feligres.id_madre) if feligres.id_madre else None
            return padre, madre
    except Exception as e:
        print(f"Error al obtener padres: {e}")
        return None, None


def obtener_abuelos(feligres: Feligres, engine) -> Dict[str, Optional[Feligres]]:
    """
    Obtiene los cuatro abuelos de un feligrés.
    CAMBIO: Ahora trabaja con Feligres
    """
    abuelos = {
        'abuelo_paterno': None,
        'abuela_paterna': None,
        'abuelo_materno': None,
        'abuela_materna': None
    }
    
    if not engine:
        return abuelos
    
    try:
        padre, madre = obtener_padres(feligres, engine)
        
        with Session(engine) as session:
            # Abuelos paternos
            if padre:
                abuelos['abuelo_paterno'] = session.get(Feligres, padre.id_padre) if padre.id_padre else None
                abuelos['abuela_paterna'] = session.get(Feligres, padre.id_madre) if padre.id_madre else None
            
            # Abuelos maternos
            if madre:
                abuelos['abuelo_materno'] = session.get(Feligres, madre.id_padre) if madre.id_padre else None
                abuelos['abuela_materna'] = session.get(Feligres, madre.id_madre) if madre.id_madre else None
        
        return abuelos
    except Exception as e:
        print(f"Error al obtener abuelos: {e}")
        return abuelos


# ====================================================================
# VISUALIZACIÓN DE INFORMACIÓN FAMILIAR
# ====================================================================

def mostrar_informacion_familia_completa(feligres: Feligres, todos_los_feligreses: List[Feligres]):
    """
    Muestra información familiar completa de un feligrés con formato optimizado.
    CAMBIO: Ahora trabaja con Feligres
    """
    # Crear mapa para búsquedas rápidas
    feligreses_map = {f.id_feligres: f for f in todos_los_feligreses}
    
    st.markdown(f"### 👤 Información de {feligres.nombre_completo()}")
    
    # Información básica
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📋 Datos Personales:**")
        st.markdown(f"- **CURP:** {feligres.curp or 'Sin CURP'}")
        st.markdown(f"- **Estado Canónico:** {feligres.estado_canonico}")
    
    with col2:
        st.markdown("**👨‍👩‍👧 Familiares Directos:**")
        padre = feligreses_map.get(feligres.id_padre)
        madre = feligreses_map.get(feligres.id_madre)
        st.markdown(f"- **Padre:** {padre.nombre_completo() if padre else 'No registrado'}")
        st.markdown(f"- **Madre:** {madre.nombre_completo() if madre else 'No registrada'}")
    
    # Abuelos (expandible)
    with st.expander("👴👵 Ver Abuelos", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Abuelos Paternos:**")
            if padre:
                abuelo_p = feligreses_map.get(padre.id_padre)
                abuela_p = feligreses_map.get(padre.id_madre)
                st.markdown(f"- Abuelo: {abuelo_p.nombre_completo() if abuelo_p else 'No registrado'}")
                st.markdown(f"- Abuela: {abuela_p.nombre_completo() if abuela_p else 'No registrada'}")
            else:
                st.info("No hay información de padre")
        
        with col2:
            st.markdown("**Abuelos Maternos:**")
            if madre:
                abuelo_m = feligreses_map.get(madre.id_padre)
                abuela_m = feligreses_map.get(madre.id_madre)
                st.markdown(f"- Abuelo: {abuelo_m.nombre_completo() if abuelo_m else 'No registrado'}")
                st.markdown(f"- Abuela: {abuela_m.nombre_completo() if abuela_m else 'No registrada'}")
            else:
                st.info("No hay información de madre")


# ====================================================================
# FORMATEO
# ====================================================================

def formatear_fecha(fecha: date) -> str:
    """Formatea una fecha al formato dd/mm/aaaa."""
    if not fecha:
        return "N/A"
    return fecha.strftime("%d/%m/%Y")


def formatear_nombre_completo(nombres: str, apellido_paterno: str, 
                              apellido_materno: Optional[str] = None) -> str:
    """Formatea un nombre completo."""
    partes = [nombres, apellido_paterno]
    if apellido_materno:
        partes.append(apellido_materno)
    return " ".join(partes)


# ====================================================================
# MENSAJES DE USUARIO
# ====================================================================

def mostrar_mensaje_exito(mensaje: str):
    """Muestra un mensaje de éxito."""
    st.success(f"✅ {mensaje}")


def mostrar_mensaje_error(mensaje: str):
    """Muestra un mensaje de error."""
    st.error(f"❌ {mensaje}")


def mostrar_mensaje_advertencia(mensaje: str):
    """Muestra un mensaje de advertencia."""
    st.warning(f"⚠️ {mensaje}")


def mostrar_mensaje_info(mensaje: str):
    """Muestra un mensaje informativo."""
    st.info(f"ℹ️ {mensaje}")


# ====================================================================
# COMPATIBILIDAD HACIA ATRÁS (DEPRECADO)
# ====================================================================

# Para evitar romper código existente inmediatamente
def buscar_persona_por_curp(curp: str, engine) -> Optional[Feligres]:
    """
    DEPRECADO: Usar buscar_feligres_por_curp
    Mantenido por compatibilidad temporal
    """
    import warnings
    warnings.warn(
        "buscar_persona_por_curp está deprecado. Usa buscar_feligres_por_curp",
        DeprecationWarning,
        stacklevel=2
    )
    return buscar_feligres_por_curp(curp, engine)


def obtener_lista_personas(engine) -> List[Feligres]:
    """
    DEPRECADO: Usar obtener_lista_feligreses
    Mantenido por compatibilidad temporal
    """
    import warnings
    warnings.warn(
        "obtener_lista_personas está deprecado. Usa obtener_lista_feligreses",
        DeprecationWarning,
        stacklevel=2
    )
    return obtener_lista_feligreses(engine)