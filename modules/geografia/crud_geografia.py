# modules/geografia/crud_geografia.py - CORREGIDO
import streamlit as st
from sqlmodel import Session, select
from models import (
    Pais, Provincia, Arquidiocesis, Decanato, Parroquia, 
    Comunidad, Capilla, CentroCatecismo
)

def mostrar_crud_geografia(db_engine, db_module, db_mode, st_display_func):
    """Módulo completo CRUD para Geografía Eclesiástica"""
    st.header(f"🌎 Geografía Eclesiástica - Modo: {db_mode}")
    
    st.info("💡 Estructura jerárquica: País → Provincia → Arquidiócesis → Decanato → Parroquia → Comunidad")
    
    tabs = st.tabs([
        "📋 Ver Todo",
        "🌍 Países",
        "⛪ Comunidades",
        "🏰 Capillas",
        "📚 Centros de Catecismo"
    ])
    
    # ================================================================
    # TAB 1: VER TODO
    # ================================================================
    with tabs[0]:
        st.subheader("📋 Estructura Completa")
        
        with Session(db_engine) as session:
            pais = session.exec(select(Pais).where(Pais.nombre_pais == "México")).first()
            
            if pais:
                st.markdown(f"### 🌍 {pais.nombre_pais}")
                
                provincias = session.exec(
                    select(Provincia).where(Provincia.id_pais == pais.id_pais)
                ).all()
                
                for provincia in provincias:
                    with st.expander(f"📍 Provincia: {provincia.nombre_provincia}"):
                        arquidiocesis = session.exec(
                            select(Arquidiocesis).where(
                                Arquidiocesis.id_provincia == provincia.id_provincia
                            )
                        ).all()
                        
                        for arqui in arquidiocesis:
                            st.markdown(f"**⛪ Arquidiócesis:** {arqui.nombre_arquidiocesis}")
                            
                            decanatos = session.exec(
                                select(Decanato).where(
                                    Decanato.id_arquidiocesis == arqui.id_arquidiocesis
                                )
                            ).all()
                            
                            for decanato in decanatos:
                                st.markdown(f"  • **Decanato:** {decanato.nombre_decanato}")
                                
                                parroquias = session.exec(
                                    select(Parroquia).where(
                                        Parroquia.id_decanato == decanato.id_decanato
                                    )
                                ).all()
                                
                                for parroquia in parroquias:
                                    st.markdown(f"    ◦ {parroquia.nombre_parroquia}")
            else:
                st.warning("⚠️ No hay datos de geografía. Ejecuta la inicialización.")
    
    # ================================================================
    # TAB 2: PAÍSES
    # ================================================================
    with tabs[1]:
        st.subheader("🌍 Gestión de Países")
        
        with Session(db_engine) as session:
            paises = session.exec(select(Pais)).all()
        
        if paises:
            for p in paises:
                st.info(f"🌍 {p.nombre_pais} ({p.codigo_iso})")
        else:
            st.warning("⚠️ No hay países registrados")
            
            if st.button("🔧 Inicializar México"):
                with Session(db_engine) as session:
                    mexico = Pais(nombre_pais="México", codigo_iso="MEX", activo=True)
                    session.add(mexico)
                    session.commit()
                    st.success("✅ México inicializado")
                    st.rerun()
    
    # ================================================================
    # TAB 3: COMUNIDADES
    # ================================================================
    with tabs[2]:
        crud_comunidades(db_engine, db_module, st_display_func)
    
    # ================================================================
    # TAB 4: CAPILLAS
    # ================================================================
    with tabs[3]:
        crud_capillas(db_engine, db_module, st_display_func)
    
    # ================================================================
    # TAB 5: CENTROS DE CATECISMO
    # ================================================================
    with tabs[4]:
        crud_centros_catecismo(db_engine, db_module, st_display_func)


# ====================================================================
# COMUNIDADES
# ====================================================================
def crud_comunidades(db_engine, db_module, st_display_func):
    st.subheader("🏘️ Gestión de Comunidades")
    
    subtabs = st.tabs(["➕ Crear", "📋 Ver"])
    
    with subtabs[0]:
        with Session(db_engine) as session:
            parroquias = session.exec(select(Parroquia)).all()
        
        if not parroquias:
            st.warning("⚠️ Primero registra una Parroquia")
            return
        
        with st.form("form_comunidad"):
            nombre = st.text_input("Nombre de la Comunidad (*)", key="com_nombre")
            clave = st.text_input("Clave (*)", key="com_clave")
            
            opciones = {p.id_parroquia: p.nombre_parroquia for p in parroquias}
            id_parroquia = st.selectbox(
                "Parroquia (*)",
                options=opciones.keys(),
                format_func=lambda x: opciones[x],
                key="com_parroquia"
            )
            
            if st.form_submit_button("💾 Guardar"):
                if nombre and clave:
                    nueva = Comunidad(
                        nombre_comunidad=nombre.strip(),
                        clave_comunidad=clave.strip().upper(),
                        id_parroquia=id_parroquia,
                        activo=True
                    )
                    if db_module.crear_registro(nueva, db_engine, st_display_func, "Comunidad"):
                        st.rerun()
    
    with subtabs[1]:
        with Session(db_engine) as session:
            comunidades = session.exec(select(Comunidad)).all()
        
        if comunidades:
            data = []
            with Session(db_engine) as session:
                for c in comunidades:
                    parroquia = session.get(Parroquia, c.id_parroquia)
                    data.append({
                        "ID": c.id_comunidad,
                        "Nombre": c.nombre_comunidad,
                        "Clave": c.clave_comunidad,
                        "Parroquia": parroquia.nombre_parroquia if parroquia else "N/A"
                    })
            
            st.dataframe(data, use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ No hay comunidades")


# ====================================================================
# CAPILLAS
# ====================================================================
def crud_capillas(db_engine, db_module, st_display_func):
    st.subheader("⛪ Gestión de Capillas")
    
    subtabs = st.tabs(["➕ Crear", "📋 Ver"])
    
    with subtabs[0]:
        with Session(db_engine) as session:
            comunidades = session.exec(select(Comunidad)).all()
        
        if not comunidades:
            st.warning("⚠️ Primero registra una Comunidad")
            return
        
        with st.form("form_capilla"):
            nombre = st.text_input("Nombre de la Capilla (*)", key="cap_nombre")
            ubicacion = st.text_input("Ubicación", key="cap_ubicacion")
            
            opciones = {c.id_comunidad: c.nombre_comunidad for c in comunidades}
            id_comunidad = st.selectbox(
                "Comunidad (*)",
                options=opciones.keys(),
                format_func=lambda x: opciones[x],
                key="cap_comunidad"
            )
            
            if st.form_submit_button("💾 Guardar"):
                if nombre:
                    nueva = Capilla(
                        nombre_capilla=nombre.strip(),
                        ubicacion=ubicacion.strip() if ubicacion else None,
                        id_comunidad=id_comunidad,
                        activo=True
                    )
                    if db_module.crear_registro(nueva, db_engine, st_display_func, "Capilla"):
                        st.rerun()
    
    with subtabs[1]:
        with Session(db_engine) as session:
            capillas = session.exec(select(Capilla)).all()
        
        if capillas:
            data = []
            with Session(db_engine) as session:
                for cap in capillas:
                    comunidad = session.get(Comunidad, cap.id_comunidad)
                    data.append({
                        "ID": cap.id_capilla,
                        "Nombre": cap.nombre_capilla,
                        "Ubicación": cap.ubicacion or "N/A",
                        "Comunidad": comunidad.nombre_comunidad if comunidad else "N/A"
                    })
            
            st.dataframe(data, use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ No hay capillas")


# ====================================================================
# CENTROS DE CATECISMO
# ====================================================================
def crud_centros_catecismo(db_engine, db_module, st_display_func):
    st.subheader("📚 Gestión de Centros de Catecismo")
    
    subtabs = st.tabs(["➕ Crear", "📋 Ver"])
    
    with subtabs[0]:
        with Session(db_engine) as session:
            comunidades = session.exec(select(Comunidad)).all()
        
        if not comunidades:
            st.warning("⚠️ Primero registra una Comunidad")
            return
        
        with st.form("form_centro"):
            nombre = st.text_input("Nombre del Centro (*)", key="cen_nombre")
            clave = st.text_input("Clave (*)", key="cen_clave")
            responsable = st.text_input("Responsable", key="cen_responsable")
            
            opciones = {c.id_comunidad: c.nombre_comunidad for c in comunidades}
            id_comunidad = st.selectbox(
                "Comunidad (*)",
                options=opciones.keys(),
                format_func=lambda x: opciones[x],
                key="cen_comunidad"
            )
            
            if st.form_submit_button("💾 Guardar"):
                if nombre and clave:
                    nuevo = CentroCatecismo(
                        nombre_centro=nombre.strip(),
                        clave_centro=clave.strip().upper(),
                        responsable=responsable.strip() if responsable else None,
                        id_comunidad=id_comunidad,
                        activo=True
                    )
                    if db_module.crear_registro(nuevo, db_engine, st_display_func, "Centro"):
                        st.rerun()
    
    with subtabs[1]:
        with Session(db_engine) as session:
            centros = session.exec(select(CentroCatecismo)).all()
        
        if centros:
            data = []
            with Session(db_engine) as session:
                for cen in centros:
                    comunidad = session.get(Comunidad, cen.id_comunidad)
                    data.append({
                        "ID": cen.id_centro,
                        "Nombre": cen.nombre_centro,
                        "Clave": cen.clave_centro,
                        "Responsable": cen.responsable or "N/A",
                        "Comunidad": comunidad.nombre_comunidad if comunidad else "N/A"
                    })
            
            st.dataframe(data, use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ No hay centros")