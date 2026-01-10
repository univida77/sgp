# crud_cursos_catequesis.py - Optimizado
import streamlit as st
from datetime import date
from models import GrupoCatequesis, RolCatequista, RolCatequistaIntegrante, Persona
from utils import buscar_persona_por_curp, obtener_lista_personas, formatear_fecha
from sqlmodel import Session, select

def mostrar_crud_cursos_catequesis(db_engine, db_module, db_mode, st_display_func):
    """Módulo completo CRUD para Grupos de Catequesis."""
    st.header(f"👥 Gestión de Grupos de Catequesis - Modo: {db_mode}")
    
    st.info("💡 Agrupa catequistas y catecúmenos para preparación sacramental")
    
    tabs = st.tabs(["➕ Crear Grupo", "📋 Ver Grupos", "✏️ Actualizar", "🗑️ Eliminar"])
    
    # ================================================================
    # TAB 1: CREAR
    # ================================================================
    with tabs[0]:
        st.subheader("➕ Crear Nuevo Grupo de Catequesis")
        
        with st.form("form_crear_grupo_cat", clear_on_submit=True):
            st.markdown("### 📋 Datos del Grupo")
            
            nombre = st.text_input(
                "Nombre del Grupo (*)",
                placeholder="Ej: Primera Comunión 2024",
                key="grupo_cat_nombre"
            )
            
            descripcion = st.text_area(
                "Descripción",
                placeholder="Descripción y objetivos...",
                key="grupo_cat_desc"
            )
            
            fecha_creacion = st.date_input(
                "Fecha de Creación (*)",
                value=date.today(),
                key="grupo_cat_fecha"
            )
            
            st.markdown("---")
            st.markdown("### 👨‍🏫 Titular del Grupo")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                curp_titular = st.text_input(
                    "CURP del Titular",
                    max_chars=18,
                    key="grupo_cat_titular_curp"
                )
            
            titular_encontrado = None
            if curp_titular:
                titular_encontrado = buscar_persona_por_curp(curp_titular, db_engine)
                if titular_encontrado:
                    st.success(f"✅ {titular_encontrado.nombre_completo()}")
            
            with col2:
                personas = obtener_lista_personas(db_engine)
                
                if not personas:
                    st.error("❌ No hay personas registradas")
                    id_titular_final = None
                else:
                    opciones = {0: "-- Selecciona --"}
                    opciones.update({
                        p.id_persona: f"{p.nombre_completo()} - {p.curp or 'Sin CURP'}"
                        for p in personas
                    })
                    id_titular_sel = st.selectbox(
                        "O selecciona:",
                        options=opciones.keys(),
                        format_func=lambda x: opciones[x],
                        key="grupo_cat_titular_sel"
                    )
                    id_titular_final = titular_encontrado.id_persona if titular_encontrado else (id_titular_sel if id_titular_sel != 0 else None)
            
            st.markdown("---")
            st.markdown("### 👨‍🏫 Auxiliar (Opcional)")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                curp_auxiliar = st.text_input(
                    "CURP del Auxiliar",
                    max_chars=18,
                    key="grupo_cat_auxiliar_curp"
                )
            
            auxiliar_encontrado = None
            if curp_auxiliar:
                auxiliar_encontrado = buscar_persona_por_curp(curp_auxiliar, db_engine)
                if auxiliar_encontrado:
                    st.success(f"✅ {auxiliar_encontrado.nombre_completo()}")
            
            with col2:
                opciones_aux = {0: "-- Sin Auxiliar --"}
                opciones_aux.update({
                    p.id_persona: f"{p.nombre_completo()} - {p.curp or 'Sin CURP'}"
                    for p in personas
                })
                id_auxiliar_sel = st.selectbox(
                    "O selecciona:",
                    options=opciones_aux.keys(),
                    format_func=lambda x: opciones_aux[x],
                    key="grupo_cat_auxiliar_sel"
                )
                id_auxiliar_final = auxiliar_encontrado.id_persona if auxiliar_encontrado else (id_auxiliar_sel if id_auxiliar_sel != 0 else None)
            
            st.markdown("---")
            submitted = st.form_submit_button("💾 Crear Grupo", type="primary", width="stretch")
            
            if submitted:
                if not nombre or not id_titular_final:
                    st.error("❌ Nombre y titular son obligatorios")
                else:
                    nuevo = GrupoCatequesis(
                        nombre_grupo=nombre.strip(),
                        descripcion=descripcion.strip() if descripcion else None,
                        fecha_creacion=fecha_creacion,
                        id_titular=id_titular_final,
                        id_auxiliar=id_auxiliar_final,
                        activo=True
                    )
                    
                    if db_module.crear_registro(nuevo, db_engine, st_display_func, "Grupo de Catequesis"):
                        st.rerun()
    
    # ================================================================
    # TAB 2: VER
    # ================================================================
    with tabs[1]:
        st.subheader("📋 Grupos de Catequesis Registrados")
        
        with Session(db_engine) as session:
            grupos = session.exec(
                select(GrupoCatequesis).where(GrupoCatequesis.activo == True)
            ).all()
        
        if grupos:
            st.markdown(f"**Total de Grupos Activos:** {len(grupos)}")
            
            data = []
            with Session(db_engine) as session:
                for grupo in grupos:
                    titular = session.get(Persona, grupo.id_titular) if grupo.id_titular else None
                    auxiliar = session.get(Persona, grupo.id_auxiliar) if grupo.id_auxiliar else None
                    
                    data.append({
                        "ID": grupo.id_grupo,
                        "Nombre": grupo.nombre_grupo,
                        "Descripción": grupo.descripcion or "Sin descripción",
                        "Fecha Creación": formatear_fecha(grupo.fecha_creacion),
                        "Titular": titular.nombre_completo() if titular else "N/A",
                        "Auxiliar": auxiliar.nombre_completo() if auxiliar else "N/A",
                        "Activo": "Sí" if grupo.activo else "No"
                    })
            
            st.dataframe(data, width="stretch", hide_index=True)
        else:
            st.info("ℹ️ No hay grupos de catequesis activos")
    
   # ================================================================
    # TAB 3: ACTUALIZAR
    # ================================================================
    with tabs[2]:
        st.subheader("✏️ Actualizar Grupo de Catequesis")
        
        with Session(db_engine) as session:
            grupos = session.exec(select(GrupoCatequesis)).all()
        
        if grupos:
            opciones = {g.id_grupo: g.nombre_grupo for g in grupos}
            id_grupo_sel = st.selectbox(
                "Selecciona el grupo:",
                options=opciones.keys(),
                format_func=lambda x: opciones[x],
                key="upd_grupo_sel"
            )
            
            # Obtener el grupo seleccionado de la sesión actual
            with Session(db_engine) as session:
                grupo = session.get(GrupoCatequesis, id_grupo_sel)
            
            if grupo:
                st.markdown("---")
                st.info(f"📝 Editando: {grupo.nombre_grupo}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    upd_nombre = st.text_input(
                        "Nombre (*)", 
                        value=grupo.nombre_grupo, 
                        key=f"upd_nombre_{id_grupo_sel}"
                    )
                    
                    upd_desc = st.text_area(
                        "Descripción", 
                        value=grupo.descripcion or "", 
                        key=f"upd_desc_{id_grupo_sel}"
                    )
                    
                    upd_fecha = st.date_input(
                        "Fecha Creación (*)", 
                        value=grupo.fecha_creacion, 
                        key=f"upd_fecha_{id_grupo_sel}"
                    )
                    
                    upd_activo = st.checkbox(
                        "Activo", 
                        value=grupo.activo, 
                        key=f"upd_activo_{id_grupo_sel}"
                    )
                
                with col2:
                    # Generación activa
                    upd_generacion = st.text_input(
                        "Generación Activa",
                        value=grupo.generacion_activa or "",
                        placeholder="Ej: 2026-2027",
                        key=f"upd_gen_{id_grupo_sel}"
                    )
                    
                    # Historial de niveles
                    upd_historial = st.text_area(
                        "Historial de Niveles",
                        value=grupo.historial_niveles or "",
                        placeholder="Ej: 2024: Nivel 1, 2025: Nivel 2",
                        key=f"upd_hist_{id_grupo_sel}"
                    )
                
                st.markdown("### 👥 Catequistas")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Titular
                    personas = obtener_lista_personas(db_engine)
                    opciones_pers = {0: "-- Sin asignar --"}
                    opciones_pers.update({p.id_persona: p.nombre_completo() for p in personas})
                    
                    idx_titular = list(opciones_pers.keys()).index(grupo.id_titular) if grupo.id_titular in opciones_pers else 0
                    upd_titular = st.selectbox(
                        "Titular", 
                        options=list(opciones_pers.keys()), 
                        format_func=lambda x: opciones_pers[x], 
                        index=idx_titular, 
                        key=f"upd_titular_{id_grupo_sel}"
                    )
                
                with col2:
                    # Auxiliar
                    idx_auxiliar = list(opciones_pers.keys()).index(grupo.id_auxiliar) if grupo.id_auxiliar in opciones_pers else 0
                    upd_auxiliar = st.selectbox(
                        "Auxiliar", 
                        options=list(opciones_pers.keys()), 
                        format_func=lambda x: opciones_pers[x], 
                        index=idx_auxiliar, 
                        key=f"upd_auxiliar_{id_grupo_sel}"
                    )
                
                st.markdown("### 🏫 Salón Asignado")
                
                # Obtener salones
                with Session(db_engine) as session:
                    salones = session.exec(
                        select(Salon).where(Salon.activo == True)
                    ).all()
                
                if salones:
                    opciones_salones = {0: "-- Sin Salón --"}
                    with Session(db_engine) as session:
                        for salon in salones:
                            centro = session.get(CentroCatecismo, salon.id_centro)
                            nombre_salon = f"{salon.nombre_salon}"
                            if centro:
                                nombre_salon += f" ({centro.nombre_centro})"
                            opciones_salones[salon.id_salon] = nombre_salon
                    
                    idx_salon = list(opciones_salones.keys()).index(grupo.id_salon) if grupo.id_salon in opciones_salones else 0
                    upd_salon = st.selectbox(
                        "Salón:",
                        options=list(opciones_salones.keys()),
                        format_func=lambda x: opciones_salones[x],
                        index=idx_salon,
                        key=f"upd_salon_{id_grupo_sel}"
                    )
                else:
                    st.info("ℹ️ No hay salones registrados")
                    upd_salon = 0
                
                st.markdown("---")
                
                if st.button(
                    "💾 Guardar Cambios", 
                    type="primary", 
                    use_container_width=True,
                    key=f"btn_upd_{id_grupo_sel}"
                ):
                    if not upd_nombre:
                        st.error("❌ El nombre es obligatorio")
                    else:
                        datos = {
                            "nombre_grupo": upd_nombre.strip(),
                            "descripcion": upd_desc.strip() if upd_desc else None,
                            "fecha_creacion": upd_fecha,
                            "id_titular": upd_titular if upd_titular != 0 else None,
                            "id_auxiliar": upd_auxiliar if upd_auxiliar != 0 else None,
                            "id_salon": upd_salon if upd_salon != 0 else None,
                            "activo": upd_activo,
                            "generacion_activa": upd_generacion.strip() if upd_generacion else None,
                            "historial_niveles": upd_historial.strip() if upd_historial else None
                        }
                        
                        if db_module.actualizar_registro(
                            GrupoCatequesis,
                            grupo.id_grupo,
                            datos,
                            db_engine,
                            st_display_func,
                            "Grupo de Catequesis"
                        ):
                            st.success("✅ Grupo actualizado exitosamente")
                            st.rerun()
        else:
            st.info("ℹ️ No hay grupos para actualizar")
            
    # ================================================================
    # TAB 4: ELIMINAR
    # ================================================================
    with tabs[3]:
        st.subheader("🗑️ Eliminar Grupo de Catequesis")
        
        with Session(db_engine) as session:
            grupos = session.exec(select(GrupoCatequesis)).all()
        
        if grupos:
            opciones = {g.id_grupo: g.nombre_grupo for g in grupos}
            id_grupo_sel = st.selectbox(
                "Selecciona el grupo:",
                options=opciones.keys(),
                format_func=lambda x: opciones[x],
                key="del_grupo_sel"
            )
            
            grupo = next((g for g in grupos if g.id_grupo == id_grupo_sel), None)
            
            if grupo:
                st.warning("⚠️ Esta acción eliminará el grupo y sus registros asociados")
                st.markdown(f"**Grupo:** {grupo.nombre_grupo}")
                
                st.markdown("---")
                
                CONFIRM_KEY = f"confirm_del_grupo_{grupo.id_grupo}"
                
                if not st.session_state.get(CONFIRM_KEY, False):
                    if st.button("🗑️ Eliminar", type="secondary"):
                        st.session_state[CONFIRM_KEY] = True
                        st.rerun()
                else:
                    st.error(f"⚠️ ¿Confirmas eliminar **{grupo.nombre_grupo}**?")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ SÍ, ELIMINAR", type="primary", width="stretch"):
                            if db_module.eliminar_registro(
                                GrupoCatequesis,
                                grupo.id_grupo,
                                db_engine,
                                st_display_func,
                                "Grupo de Catequesis"
                            ):
                                st.session_state.pop(CONFIRM_KEY, None)
                                st.rerun()
                    with col2:
                        if st.button("❌ Cancelar", width="stretch"):
                            st.session_state[CONFIRM_KEY] = False
                            st.rerun()
        else:
            st.info("ℹ️ No hay grupos para eliminar")