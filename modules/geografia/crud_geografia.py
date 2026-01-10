# crud_geografia.py - Optimizado
import streamlit as st
from sqlmodel import Session, select
from models import (
    Arquidiocesis, Decanato, Parroquia, Comunidad, Capilla, CentroCatecismo
)

def crear_geografia_basica(session):
    """Crea geografía eclesiástica básica"""
    print("🌎 Geografía eclesiástica...")
    
    # País
    pais = session.exec(select(Pais).where(Pais.nombre_pais == "México")).first()
    if not pais:
        pais = Pais(nombre_pais="México", codigo_iso="MEX", activo=True)
        session.add(pais)
        session.flush()
        print("   ✅ País creado")
    
    # Provincia
    provincia = session.exec(select(Provincia).where(
        Provincia.nombre_provincia == "Antequera"
    )).first()
    if not provincia:
        provincia = Provincia(
            id_pais=pais.id_pais,
            nombre_provincia="Antequera",
            activo=True
        )
        session.add(provincia)
        session.flush()
        print("   ✅ Provincia creada")
    
    # Arquidiócesis
    arqui = session.exec(select(Arquidiocesis).where(
        Arquidiocesis.nombre_arquidiocesis == "Antequera-Oaxaca"
    )).first()
    if not arqui:
        arqui = Arquidiocesis(
            id_provincia=provincia.id_provincia,
            nombre_arquidiocesis="Antequera-Oaxaca",
            activo=True
        )
        session.add(arqui)
        session.flush()
        print("   ✅ Arquidiócesis creada")
    
    # Decanato
    decanato = session.exec(select(Decanato).where(
        Decanato.nombre_decanato == "Tlacolula"
    )).first()
    if not decanato:
        decanato = Decanato(
            id_arquidiocesis=arqui.id_arquidiocesis,
            nombre_decanato="Tlacolula",
            activo=True
        )
        session.add(decanato)
        session.flush()
        print("   ✅ Decanato creado")
    
    # Parroquia
    parroquia = session.exec(select(Parroquia).where(
        Parroquia.nombre_parroquia.like("%Santa María%")
    )).first()
    if not parroquia:
        parroquia = Parroquia(
            id_arquidiocesis=arqui.id_arquidiocesis,
            id_decanato=decanato.id_decanato,
            nombre_parroquia="Parroquia de Santa María de la Asunción",
            direccion="Av. 2 de abril No. 22, Tlacolula de Matamoros",
            telefono="9515620019",
            activo=True
        )
        session.add(parroquia)
        session.flush()
        print("   ✅ Parroquia creada")

# ====================================================================
# COMUNIDADES
# ====================================================================
def crud_comunidades(db_engine, db_module, st_display_func):
    with st.expander("🏘️ Comunidades", expanded=False):
        with Session(db_engine) as session:
            comunidades = session.exec(select(Comunidad)).all()
            parroquias = session.exec(select(Parroquia)).all()

        if not parroquias:
            st.warning("⚠️ Primero registra una Parroquia")
            return

        if st.button("➕ Añadir Comunidad", key="add_com"):
            st.session_state.show_com_form = True

        if st.session_state.get("show_com_form", False):
            with st.form("form_com"):
                nombre = st.text_input("Nombre de la Comunidad")
                clave = st.text_input("Clave de la Comunidad")
                opciones_parro = {p.id_parroquia: p.nombre_parroquia for p in parroquias}
                parro_sel = st.selectbox(
                    "Pertenece a Parroquia", 
                    options=opciones_parro.keys(), 
                    format_func=lambda x: opciones_parro[x]
                )
                
                if st.form_submit_button("Guardar"):
                    if nombre and clave and parro_sel:
                        nueva = Comunidad(
                            nombre_comunidad=nombre.strip(), 
                            clave_comunidad=clave.strip(), 
                            id_parroquia=parro_sel
                        )
                        db_module.crear_registro(nueva, db_engine, st_display_func, "Comunidad")
                        st.session_state.show_com_form = False
                        st.rerun()

        with Session(db_engine) as session:
            for com in comunidades:
                par = session.get(Parroquia, com.id_parroquia)
                st.write(f"- {com.nombre_comunidad} ({com.clave_comunidad}) - {par.nombre_parroquia if par else 'N/A'}")

# ====================================================================
# CAPILLAS
# ====================================================================
def crud_capillas(db_engine, db_module, st_display_func):
    with st.expander("⛪ Capillas", expanded=False):
        with Session(db_engine) as session:
            capillas = session.exec(select(Capilla)).all()
            comunidades = session.exec(select(Comunidad)).all()

        if not comunidades:
            st.warning("⚠️ Primero registra una Comunidad")
            return

        if st.button("➕ Añadir Capilla", key="add_cap"):
            st.session_state.show_cap_form = True

        if st.session_state.get("show_cap_form", False):
            with st.form("form_cap"):
                nombre = st.text_input("Nombre de la Capilla")
                ubicacion = st.text_input("Ubicación")
                opciones_com = {c.id_comunidad: f"{c.nombre_comunidad} ({c.clave_comunidad})" for c in comunidades}
                com_sel = st.selectbox(
                    "Pertenece a Comunidad", 
                    options=opciones_com.keys(), 
                    format_func=lambda x: opciones_com[x]
                )
                
                if st.form_submit_button("Guardar"):
                    if nombre and com_sel:
                        nueva = Capilla(
                            nombre_capilla=nombre.strip(), 
                            ubicacion=ubicacion.strip() if ubicacion else None, 
                            id_comunidad=com_sel
                        )
                        db_module.crear_registro(nueva, db_engine, st_display_func, "Capilla")
                        st.session_state.show_cap_form = False
                        st.rerun()
        
        with Session(db_engine) as session:
            for cap in capillas:
                com = session.get(Comunidad, cap.id_comunidad)
                st.write(f"- {cap.nombre_capilla} - {com.nombre_comunidad if com else 'N/A'}")

# ====================================================================
# CENTROS DE CATECISMO
# ====================================================================
def crud_centros_catecismo(db_engine, db_module, st_display_func):
    with st.expander("📚 Centros de Catecismo", expanded=False):
        with Session(db_engine) as session:
            centros = session.exec(select(CentroCatecismo)).all()
            comunidades = session.exec(select(Comunidad)).all()

        if not comunidades:
            st.warning("⚠️ Primero registra una Comunidad")
            return

        if st.button("➕ Añadir Centro", key="add_centro"):
            st.session_state.show_centro_form = True

        if st.session_state.get("show_centro_form", False):
            with st.form("form_centro"):
                nombre = st.text_input("Nombre del Centro")
                clave = st.text_input("Clave del Centro")
                responsable = st.text_input("Responsable")
                opciones_com = {c.id_comunidad: f"{c.nombre_comunidad} ({c.clave_comunidad})" for c in comunidades}
                com_sel = st.selectbox(
                    "Ubicado en Comunidad", 
                    options=opciones_com.keys(), 
                    format_func=lambda x: opciones_com[x]
                )
                
                if st.form_submit_button("Guardar"):
                    if nombre and clave and com_sel:
                        nuevo = CentroCatecismo(
                            nombre_centro=nombre.strip(), 
                            clave_centro=clave.strip(), 
                            responsable=responsable.strip() if responsable else None, 
                            id_comunidad=com_sel
                        )
                        db_module.crear_registro(nuevo, db_engine, st_display_func, "Centro de Catecismo")
                        st.session_state.show_centro_form = False
                        st.rerun()
        
        with Session(db_engine) as session:
            for cen in centros:
                com = session.get(Comunidad, cen.id_comunidad)
                st.write(f"- {cen.nombre_centro} ({cen.clave_centro}) - {com.nombre_comunidad if com else 'N/A'}")