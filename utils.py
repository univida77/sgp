# utils.py - Funciones auxiliares optimizadas
import streamlit as st
from typing import Optional, Dict, List, Tuple
from sqlmodel import Session, select
from models import Persona, Presbitero, Parroquia, Comunidad
from datetime import date

# ====================================================================
# BÚSQUEDA Y VALIDACIÓN
# ====================================================================

def buscar_persona_por_curp(curp: str, engine) -> Optional[Persona]:
    """Busca una persona por su CURP."""
    if not engine or not curp:
        return None
    
    try:
        with Session(engine) as session:
            statement = select(Persona).where(Persona.curp == curp.strip().upper())
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


def validar_no_auto_referencia(persona_id: int, id_padre: Optional[int], 
                               id_madre: Optional[int]) -> bool:
    """Valida que una persona no sea su propio padre o madre."""
    if id_padre and id_padre == persona_id:
        return False
    if id_madre and id_madre == persona_id:
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

def obtener_lista_personas(engine) -> List[Persona]:
    """Obtiene todas las personas ordenadas alfabéticamente."""
    if not engine:
        return []
    try:
        with Session(engine) as session:
            statement = select(Persona).order_by(
                Persona.apellido_paterno, 
                Persona.apellido_materno,
                Persona.nombres
            )
            return session.exec(statement).all()
    except Exception as e:
        print(f"Error al obtener personas: {e}")
        return []


def obtener_lista_presbiteros(engine) -> List[Tuple[Presbitero, Persona]]:
    """Obtiene todos los presbíteros con su información de persona."""
    if not engine:
        return []
    try:
        with Session(engine) as session:
            presbiteros = session.exec(select(Presbitero)).all()
            resultado = []
            for pres in presbiteros:
                persona = session.get(Persona, pres.id_persona)
                if persona:
                    resultado.append((pres, persona))
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

def obtener_padres(persona: Persona, engine) -> Tuple[Optional[Persona], Optional[Persona]]:
    """Obtiene los objetos Padre y Madre de una persona."""
    if not engine:
        return None, None
    
    try:
        with Session(engine) as session:
            padre = session.get(Persona, persona.id_padre) if persona.id_padre else None
            madre = session.get(Persona, persona.id_madre) if persona.id_madre else None
            return padre, madre
    except Exception as e:
        print(f"Error al obtener padres: {e}")
        return None, None


def obtener_abuelos(persona: Persona, engine) -> Dict[str, Optional[Persona]]:
    """
    Obtiene los cuatro abuelos de una persona.
    Retorna un diccionario con las claves:
    - abuelo_paterno, abuela_paterna
    - abuelo_materno, abuela_materna
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
        padre, madre = obtener_padres(persona, engine)
        
        with Session(engine) as session:
            # Abuelos paternos
            if padre:
                abuelos['abuelo_paterno'] = session.get(Persona, padre.id_padre) if padre.id_padre else None
                abuelos['abuela_paterna'] = session.get(Persona, padre.id_madre) if padre.id_madre else None
            
            # Abuelos maternos
            if madre:
                abuelos['abuelo_materno'] = session.get(Persona, madre.id_padre) if madre.id_padre else None
                abuelos['abuela_materna'] = session.get(Persona, madre.id_madre) if madre.id_madre else None
        
        return abuelos
    except Exception as e:
        print(f"Error al obtener abuelos: {e}")
        return abuelos

# ====================================================================
# VISUALIZACIÓN DE INFORMACIÓN FAMILIAR
# ====================================================================

def mostrar_informacion_familia_completa(persona: Persona, todas_las_personas: List[Persona]):
    """
    Muestra información familiar completa de una persona con formato optimizado.
    """
    # Crear mapa para búsquedas rápidas
    personas_map = {p.id_persona: p for p in todas_las_personas}
    
    st.markdown(f"### 👤 Información de {persona.nombre_completo()}")
    
    # Información básica
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📋 Datos Personales:**")
        st.markdown(f"- **CURP:** {persona.curp or 'Sin CURP'}")
        st.markdown(f"- **Estado Canónico:** {persona.estado_canonico}")
    
    with col2:
        st.markdown("**👨‍👩‍👧 Familiares Directos:**")
        padre = personas_map.get(persona.id_padre)
        madre = personas_map.get(persona.id_madre)
        st.markdown(f"- **Padre:** {padre.nombre_completo() if padre else 'No registrado'}")
        st.markdown(f"- **Madre:** {madre.nombre_completo() if madre else 'No registrada'}")
    
    # Abuelos (expandible)
    with st.expander("👴👵 Ver Abuelos", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Abuelos Paternos:**")
            if padre:
                abuelo_p = personas_map.get(padre.id_padre)
                abuela_p = personas_map.get(padre.id_madre)
                st.markdown(f"- Abuelo: {abuelo_p.nombre_completo() if abuelo_p else 'No registrado'}")
                st.markdown(f"- Abuela: {abuela_p.nombre_completo() if abuela_p else 'No registrada'}")
            else:
                st.info("No hay información de padre")
        
        with col2:
            st.markdown("**Abuelos Maternos:**")
            if madre:
                abuelo_m = personas_map.get(madre.id_padre)
                abuela_m = personas_map.get(madre.id_madre)
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