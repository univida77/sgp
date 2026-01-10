# crud_sacramentos.py - Optimizado y simplificado
import streamlit as st
from datetime import date
from models import (
    SacramentoBautizo, SacramentoConfirmacion, SacramentoEucaristia,
    SacramentoMatrimonio, RenovacionBautismal,
    Parroquia, Comunidad, Presbitero, Persona
)
from utils import (
    buscar_persona_por_curp, obtener_lista_personas,
    obtener_lista_comunidades, obtener_lista_presbiteros,
    formatear_fecha
)
from sqlmodel import Session, select

# ====================================================================
# COMPONENTES REUTILIZABLES
# ====================================================================

def selector_persona(label: str, key_prefix: str, db_engine, requerido: bool = True):
    """Componente reutilizable para seleccionar persona."""
    st.markdown(f"**{label}:**")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        curp = st.text_input(f"CURP", max_chars=18, key=f"{key_prefix}_curp")
    
    persona_encontrada = None
    if curp:
        persona_encontrada = buscar_persona_por_curp(curp, db_engine)
        if persona_encontrada:
            st.success(f"✅ {persona_encontrada.nombre_completo()}")
    
    with col2:
        personas = obtener_lista_personas(db_engine)
        opciones = {0: f"-- {'Obligatorio' if requerido else 'Opcional'} --"}
        opciones.update({
            p.id_persona: f"{p.nombre_completo()} - {p.curp or 'Sin CURP'}"
            for p in personas
        })
        id_sel = st.selectbox(
            "O selecciona:", 
            options=opciones.keys(), 
            format_func=lambda x: opciones[x],
            key=f"{key_prefix}_sel"
        )
    
    return persona_encontrada.id_persona if persona_encontrada else (id_sel if id_sel != 0 else None)


def selector_comunidad(db_engine, key_prefix: str):
    """Componente para seleccionar comunidad."""
    st.markdown("### 📍 Lugar de Celebración")
    
    comunidades = obtener_lista_comunidades(db_engine)
    if not comunidades:
        st.error("❌ No hay comunidades registradas")
        return None
    
    with Session(db_engine) as session:
        opciones = {}
        for c in comunidades:
            parroquia = session.get(Parroquia, c.id_parroquia)
            opciones[c.id_comunidad] = f"{c.nombre_comunidad} ({c.clave_comunidad}) - {parroquia.nombre_parroquia if parroquia else 'N/A'}"
    
    return st.selectbox(
        "Comunidad (*)",
        options=opciones.keys(),
        format_func=lambda x: opciones[x],
        key=f"{key_prefix}_comunidad"
    )


def selector_ministro(db_engine, key_prefix: str):
    """Componente para seleccionar ministro."""
    presbiteros = obtener_lista_presbiteros(db_engine)
    
    if not presbiteros:
        st.info("ℹ️ No hay presbíteros registrados")
        return None
    
    opciones = {0: "-- Sin Ministro --"}
    opciones.update({
        pres[0].id_presbitero: f"{pres[1].nombre_completo()} - {pres[0].cargo}"
        for pres in presbiteros
    })
    
    id_sel = st.selectbox(
        "Ministro Celebrante",
        options=opciones.keys(),
        format_func=lambda x: opciones[x],
        key=f"{key_prefix}_ministro"
    )
    
    return id_sel if id_sel != 0 else None


def datos_libro_parroquial(key_prefix: str):
    """Componente para datos del libro parroquial."""
    st.markdown("### 📖 Registro Parroquial")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        libro = st.text_input("Libro", max_chars=10, key=f"{key_prefix}_libro")
    with col2:
        folio = st.text_input("Folio", max_chars=10, key=f"{key_prefix}_folio")
    with col3:
        partida = st.text_input("Partida", max_chars=10, key=f"{key_prefix}_partida")
    
    return {
        "libro": libro.strip() if libro else None,
        "folio": folio.strip() if folio else None,
        "partida": partida.strip() if partida else None
    }

# ====================================================================
# FUNCIÓN PRINCIPAL
# ====================================================================

def mostrar_crud_sacramentos(db_engine, db_module, db_mode, st_display_func):
    """Módulo principal para gestión de sacramentos."""
    st.header(f"✝️ Gestión de Sacramentos - Modo: {db_mode}")
    
    sacramento_tipo = st.selectbox(
        "Selecciona el Sacramento:",
        [
            "Bautizo",
            "Confirmación",
            "Eucaristía (Primera Comunión)",
            "Matrimonio",
            "Renovación Bautismal"
        ],
        key="sacramento_selector"
    )
    
    st.markdown("---")
    
    if sacramento_tipo == "Bautizo":
        crud_bautizo(db_engine, db_module, st_display_func)
    elif sacramento_tipo == "Confirmación":
        crud_confirmacion(db_engine, db_module, st_display_func)
    elif sacramento_tipo == "Eucaristía (Primera Comunión)":
        crud_eucaristia(db_engine, db_module, st_display_func)
    elif sacramento_tipo == "Matrimonio":
        crud_matrimonio(db_engine, db_module, st_display_func)
    else:
        crud_renovacion(db_engine, db_module, st_display_func)

# ====================================================================
# CRUD BAUTIZO
# ====================================================================

def crud_bautizo(db_engine, db_module, st_display_func):
    st.subheader("💧 Sacramento del Bautizo")
    
    tabs = st.tabs(["➕ Registrar", "📋 Ver", "✏️ Actualizar", "🗑️ Eliminar"])
    
    with tabs[0]:
        with st.form("form_bautizo", clear_on_submit=False):
            st.markdown("### 👶 Persona Bautizada")
            id_bautizado = selector_persona("Bautizado/a", "bautizo_bautizado", db_engine, True)
            
            st.markdown("---")
            st.markdown("### 📅 Datos de la Celebración")
            
            fecha = st.date_input("Fecha (*)", value=date.today(), max_value=date.today(), key="bautizo_fecha")
            id_comunidad = selector_comunidad(db_engine, "bautizo")
            id_ministro = selector_ministro(db_engine, "bautizo")
            
            st.markdown("---")
            st.markdown("### 🙏 Padrinos")
            id_padrino = selector_persona("Padrino", "bautizo_padrino", db_engine, False)
            id_madrina = selector_persona("Madrina", "bautizo_madrina", db_engine, False)
            
            st.markdown("---")
            datos_libro = datos_libro_parroquial("bautizo")
            url_cert = st.text_input("URL Certificado Digital", key="bautizo_url")
            
            st.markdown("---")
            if st.form_submit_button("💾 Registrar Bautizo", type="primary", width="stretch"):
                if not id_bautizado or not id_comunidad:
                    st.error("❌ Bautizado y comunidad son obligatorios")
                else:
                    nuevo = SacramentoBautizo(
                        id_bautizado=id_bautizado,
                        fecha_celebracion=fecha,
                        id_comunidad=id_comunidad,
                        id_ministro=id_ministro,
                        id_padrino=id_padrino,
                        id_madrina=id_madrina,
                        libro=datos_libro["libro"],
                        folio=datos_libro["folio"],
                        partida=datos_libro["partida"],
                        url_certificado=url_cert.strip() if url_cert else None
                    )
                    if db_module.crear_registro(nuevo, db_engine, st_display_func, "Bautizo"):
                        st.rerun()
    
    with tabs[1]:
        ver_sacramentos(db_engine, SacramentoBautizo, "Bautizo", "id_bautizado")
    
    with tabs[2]:
        st.info("💡 Actualización disponible para implementar")
    
    with tabs[3]:
        st.info("💡 Eliminación disponible para implementar")

# ====================================================================
# CRUD CONFIRMACIÓN
# ====================================================================

def crud_confirmacion(db_engine, db_module, st_display_func):
    st.subheader("🕊️ Sacramento de la Confirmación")
    
    tabs = st.tabs(["➕ Registrar", "📋 Ver", "✏️ Actualizar", "🗑️ Eliminar"])
    
    with tabs[0]:
        with st.form("form_confirmacion", clear_on_submit=False):
            st.markdown("### 👤 Persona Confirmada")
            id_confirmado = selector_persona("Confirmado/a", "conf_confirmado", db_engine, True)
            
            st.markdown("---")
            st.markdown("### 📅 Datos de la Celebración")
            
            fecha = st.date_input("Fecha (*)", value=date.today(), max_value=date.today(), key="conf_fecha")
            id_comunidad = selector_comunidad(db_engine, "conf")
            id_ministro = selector_ministro(db_engine, "conf")
            
            st.markdown("---")
            st.markdown("### 🙏 Padrinos")
            id_padrino = selector_persona("Padrino", "conf_padrino", db_engine, False)
            id_madrina = selector_persona("Madrina", "conf_madrina", db_engine, False)
            
            st.markdown("---")
            datos_libro = datos_libro_parroquial("conf")
            url_cert = st.text_input("URL Certificado Digital", key="conf_url")
            
            st.markdown("---")
            if st.form_submit_button("💾 Registrar Confirmación", type="primary", width="stretch"):
                if not id_confirmado or not id_comunidad:
                    st.error("❌ Confirmado y comunidad son obligatorios")
                else:
                    nuevo = SacramentoConfirmacion(
                        id_confirmado=id_confirmado,
                        fecha_celebracion=fecha,
                        id_comunidad=id_comunidad,
                        id_ministro=id_ministro,
                        id_padrino=id_padrino,
                        id_madrina=id_madrina,
                        libro=datos_libro["libro"],
                        folio=datos_libro["folio"],
                        partida=datos_libro["partida"],
                        url_certificado=url_cert.strip() if url_cert else None
                    )
                    if db_module.crear_registro(nuevo, db_engine, st_display_func, "Confirmación"):
                        st.rerun()
    
    with tabs[1]:
        ver_sacramentos(db_engine, SacramentoConfirmacion, "Confirmación", "id_confirmado")
    
    with tabs[2]:
        st.info("💡 Actualización disponible para implementar")
    
    with tabs[3]:
        st.info("💡 Eliminación disponible para implementar")

# ====================================================================
# CRUD EUCARISTÍA
# ====================================================================

def crud_eucaristia(db_engine, db_module, st_display_func):
    st.subheader("🍞 Sacramento de la Eucaristía")
    
    tabs = st.tabs(["➕ Registrar", "📋 Ver", "✏️ Actualizar", "🗑️ Eliminar"])
    
    with tabs[0]:
        with st.form("form_eucaristia", clear_on_submit=False):
            st.markdown("### 👤 Persona que Comulga")
            id_comulgado = selector_persona("Comulgado/a", "euc_comulgado", db_engine, True)
            
            st.markdown("---")
            st.markdown("### 📅 Datos de la Celebración")
            
            fecha = st.date_input("Fecha (*)", value=date.today(), max_value=date.today(), key="euc_fecha")
            id_comunidad = selector_comunidad(db_engine, "euc")
            id_ministro = selector_ministro(db_engine, "euc")
            
            st.markdown("---")
            st.markdown("### 🙏 Padrinos")
            id_padrino = selector_persona("Padrino", "euc_padrino", db_engine, False)
            id_madrina = selector_persona("Madrina", "euc_madrina", db_engine, False)
            
            st.markdown("---")
            datos_libro = datos_libro_parroquial("euc")
            url_cert = st.text_input("URL Certificado Digital", key="euc_url")
            
            st.markdown("---")
            if st.form_submit_button("💾 Registrar Eucaristía", type="primary", width="stretch"):
                if not id_comulgado or not id_comunidad:
                    st.error("❌ Comulgado y comunidad son obligatorios")
                else:
                    nuevo = SacramentoEucaristia(
                        id_comulgado=id_comulgado,
                        fecha_celebracion=fecha,
                        id_comunidad=id_comunidad,
                        id_ministro=id_ministro,
                        id_padrino=id_padrino,
                        id_madrina=id_madrina,
                        libro=datos_libro["libro"],
                        folio=datos_libro["folio"],
                        partida=datos_libro["partida"],
                        url_certificado=url_cert.strip() if url_cert else None
                    )
                    if db_module.crear_registro(nuevo, db_engine, st_display_func, "Eucaristía"):
                        st.rerun()
    
    with tabs[1]:
        ver_sacramentos(db_engine, SacramentoEucaristia, "Eucaristía", "id_comulgado")
    
    with tabs[2]:
        st.info("💡 Actualización disponible para implementar")
    
    with tabs[3]:
        st.info("💡 Eliminación disponible para implementar")

# ====================================================================
# CRUD MATRIMONIO
# ====================================================================

def crud_matrimonio(db_engine, db_module, st_display_func):
    st.subheader("💍 Sacramento del Matrimonio")
    
    tabs = st.tabs(["➕ Registrar", "📋 Ver", "✏️ Actualizar", "🗑️ Eliminar"])
    
    with tabs[0]:
        with st.form("form_matrimonio", clear_on_submit=False):
            st.markdown("### 👰🤵 Contrayentes")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**🤵 Cónyuge Varón:**")
                id_varon = selector_persona("Varón", "matri_varon", db_engine, True)
            with col2:
                st.markdown("**👰 Cónyuge Mujer:**")
                id_mujer = selector_persona("Mujer", "matri_mujer", db_engine, True)
            
            st.markdown("---")
            st.markdown("### 📅 Datos de la Celebración")
            
            fecha = st.date_input("Fecha (*)", value=date.today(), max_value=date.today(), key="matri_fecha")
            id_comunidad = selector_comunidad(db_engine, "matri")
            id_ministro = selector_ministro(db_engine, "matri")
            
            st.markdown("---")
            st.markdown("### 👥 Testigos")
            id_test1 = selector_persona("Testigo 1", "matri_test1", db_engine, False)
            id_test2 = selector_persona("Testigo 2", "matri_test2", db_engine, False)
            
            st.markdown("---")
            datos_libro = datos_libro_parroquial("matri")
            url_cert = st.text_input("URL Certificado Digital", key="matri_url")
            
            st.markdown("---")
            if st.form_submit_button("💾 Registrar Matrimonio", type="primary", width="stretch"):
                if not id_varon or not id_mujer or not id_comunidad:
                    st.error("❌ Contrayentes y comunidad son obligatorios")
                elif id_varon == id_mujer:
                    st.error("❌ Los contrayentes no pueden ser la misma persona")
                else:
                    nuevo = SacramentoMatrimonio(
                        id_ConyugeVaron=id_varon,
                        id_ConyugeMujer=id_mujer,
                        fecha_celebracion=fecha,
                        id_comunidad=id_comunidad,
                        id_ministro=id_ministro,
                        id_padrino=id_test1,
                        id_madrina=id_test2,
                        libro=datos_libro["libro"],
                        folio=datos_libro["folio"],
                        partida=datos_libro["partida"],
                        url_certificado=url_cert.strip() if url_cert else None
                    )
                    if db_module.crear_registro(nuevo, db_engine, st_display_func, "Matrimonio"):
                        st.rerun()
    
    with tabs[1]:
        ver_matrimonios(db_engine)
    
    with tabs[2]:
        st.info("💡 Actualización disponible para implementar")
    
    with tabs[3]:
        st.info("💡 Eliminación disponible para implementar")

# ====================================================================
# CRUD RENOVACIÓN BAUTISMAL
# ====================================================================

def crud_renovacion(db_engine, db_module, st_display_func):
    st.subheader("✨ Renovación Bautismal")
    
    tabs = st.tabs(["➕ Registrar", "📋 Ver", "✏️ Actualizar", "🗑️ Eliminar"])
    
    with tabs[0]:
        with st.form("form_renovacion", clear_on_submit=False):
            st.markdown("### 👤 Persona que Renueva")
            id_persona = selector_persona("Persona", "renov_persona", db_engine, True)
            
            st.markdown("---")
            st.markdown("### 📅 Datos de la Celebración")
            
            fecha = st.date_input("Fecha (*)", value=date.today(), max_value=date.today(), key="renov_fecha")
            id_comunidad = selector_comunidad(db_engine, "renov")
            id_ministro = selector_ministro(db_engine, "renov")
            
            st.markdown("---")
            st.markdown("### 🙏 Padrinos")
            id_padrino = selector_persona("Padrino", "renov_padrino", db_engine, False)
            id_madrina = selector_persona("Madrina", "renov_madrina", db_engine, False)
            
            st.markdown("---")
            datos_libro = datos_libro_parroquial("renov")
            url_cert = st.text_input("URL Certificado Digital", key="renov_url")
            
            st.markdown("---")
            if st.form_submit_button("💾 Registrar Renovación", type="primary", width="stretch"):
                if not id_persona or not id_comunidad:
                    st.error("❌ Persona y comunidad son obligatorios")
                else:
                    nuevo = RenovacionBautismal(
                        id_persona=id_persona,
                        fecha_celebracion=fecha,
                        id_comunidad=id_comunidad,
                        id_ministro=id_ministro,
                        id_padrino=id_padrino,
                        id_madrina=id_madrina,
                        libro=datos_libro["libro"],
                        folio=datos_libro["folio"],
                        partida=datos_libro["partida"],
                        url_certificado=url_cert.strip() if url_cert else None
                    )
                    if db_module.crear_registro(nuevo, db_engine, st_display_func, "Renovación Bautismal"):
                        st.rerun()
    
    with tabs[1]:
        ver_sacramentos(db_engine, RenovacionBautismal, "Renovación", "id_persona")
    
    with tabs[2]:
        st.info("💡 Actualización disponible para implementar")
    
    with tabs[3]:
        st.info("💡 Eliminación disponible para implementar")

# ====================================================================
# FUNCIONES DE VISUALIZACIÓN
# ====================================================================

def ver_sacramentos(db_engine, modelo, nombre_sacramento, campo_persona):
    """Función genérica para ver sacramentos."""
    st.subheader(f"📋 Lista de {nombre_sacramento}s")
    
    with Session(db_engine) as session:
        registros = session.exec(select(modelo)).all()
    
    if registros:
        st.markdown(f"**Total:** {len(registros)}")
        
        data = []
        with Session(db_engine) as session:
            for r in registros:
                persona = session.get(Persona, getattr(r, campo_persona))
                comunidad = session.get(Comunidad, r.id_comunidad)
                
                data.append({
                    "ID": getattr(r, f"id_{nombre_sacramento.lower()}") if hasattr(r, f"id_{nombre_sacramento.lower()}") else r.id_registro,
                    "Persona": persona.nombre_completo() if persona else "N/A",
                    "Fecha": formatear_fecha(r.fecha_celebracion),
                    "Comunidad": comunidad.nombre_comunidad if comunidad else "N/A",
                    "Libro": r.libro or "N/A",
                    "Folio": r.folio or "N/A"
                })
        
        st.dataframe(data, width="stretch", hide_index=True)
    else:
        st.info(f"ℹ️ No hay {nombre_sacramento.lower()}s registrados")


def ver_matrimonios(db_engine):
    """Visualización específica para matrimonios."""
    st.subheader("📋 Lista de Matrimonios")
    
    with Session(db_engine) as session:
        matrimonios = session.exec(select(SacramentoMatrimonio)).all()
    
    if matrimonios:
        st.markdown(f"**Total:** {len(matrimonios)}")
        
        data = []
        for m in matrimonios:
            varon = session.get(Persona, m.id_ConyugeVaron)
            mujer = session.get(Persona, m.id_ConyugeMujer)
            comunidad = session.get(Comunidad, m.id_comunidad)
            
            data.append({
                "ID": m.id_matrimonio,
                "Cónyuge Varón": varon.nombre_completo() if varon else "N/A",
                "Cónyuge Mujer": mujer.nombre_completo() if mujer else "N/A",
                "Fecha": formatear_fecha(m.fecha_celebracion),
                "Comunidad": comunidad.nombre_comunidad if comunidad else "N/A",
                "Libro": m.libro or "N/A"
            })
        
        st.dataframe(data, width="stretch", hide_index=True)
    else:
        st.info("ℹ️ No hay matrimonios registrados")