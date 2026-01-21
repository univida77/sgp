# modules/feligreses/crud_feligreses.py
"""
MÓDULO CRUD DE FELIGRESES
Reemplaza completamente a crud_personas.py

Gestiona el registro y administración de feligreses (miembros de la comunidad)
"""

import streamlit as st
from models import Feligres  # ⚠️ CAMBIO: Persona → Feligres
from utils import (
    buscar_feligres_por_curp, validar_curp, validar_no_auto_referencia,
    obtener_lista_feligreses, mostrar_informacion_familia_completa
)

def mostrar_crud_feligreses(db_engine, db_module, db_mode, st_display_func):
    """
    Módulo completo CRUD para Feligreses.
    CAMBIO: Antes era mostrar_crud_personas
    """
    st.header(f"👥 Gestión de Feligreses - Modo: {db_mode}")
    
    st.info("💡 Registro y administración de miembros de la comunidad parroquial")
    
    tabs = st.tabs([
        "➕ Registrar Feligrés",
        "📋 Ver Feligreses",
        "✏️ Actualizar Feligrés",
        "🗑️ Eliminar Feligrés"
    ])
    
    # ================================================================
    # TAB 1: CREAR FELIGRÉS
    # ================================================================
    with tabs[0]:
        st.subheader("➕ Registrar Nuevo Feligrés")
        
        with st.form("form_crear_feligres", clear_on_submit=True):
            st.markdown("### 📝 Datos Personales")
            
            col1, col2 = st.columns(2)
            with col1:
                nombres = st.text_input("Nombres (*)", key="crear_nombres")
                apellido_paterno = st.text_input("Apellido Paterno (*)", key="crear_paterno")
            with col2:
                apellido_materno = st.text_input("Apellido Materno", key="crear_materno")
                curp = st.text_input("CURP (*) - 18 caracteres", max_chars=18, key="crear_curp")
            
            estado_canonico = st.selectbox(
                "Estado Canónico (*)",
                options=["soltero", "casado", "union libre"],
                key="crear_estado"
            )
            
            st.markdown("---")
            st.markdown("### 👨‍👩‍👧 Datos de los Padres (Opcional)")
            
            # PADRE
            st.markdown("**👨 Padre:**")
            col1, col2 = st.columns([1, 2])
            
            with col1:
                curp_padre = st.text_input(
                    "CURP del Padre",
                    max_chars=18,
                    key="crear_padre_curp"
                )
            
            padre_encontrado = None
            if curp_padre:
                padre_encontrado = buscar_feligres_por_curp(curp_padre, db_engine)
                if padre_encontrado:
                    st.success(f"✅ {padre_encontrado.nombre_completo()}")
            
            with col2:
                feligreses = obtener_lista_feligreses(db_engine)
                opciones_padre = {0: "-- Sin Padre --"}
                opciones_padre.update({
                    f.id_feligres: f"{f.nombre_completo()} - {f.curp or 'Sin CURP'}"
                    for f in feligreses
                })
                id_padre_sel = st.selectbox(
                    "O selecciona de la lista:",
                    options=opciones_padre.keys(),
                    format_func=lambda x: opciones_padre[x],
                    key="crear_padre_select"
                )
            
            # MADRE
            st.markdown("**👩 Madre:**")
            col1, col2 = st.columns([1, 2])
            
            with col1:
                curp_madre = st.text_input(
                    "CURP de la Madre",
                    max_chars=18,
                    key="crear_madre_curp"
                )
            
            madre_encontrada = None
            if curp_madre:
                madre_encontrada = buscar_feligres_por_curp(curp_madre, db_engine)
                if madre_encontrada:
                    st.success(f"✅ {madre_encontrada.nombre_completo()}")
            
            with col2:
                opciones_madre = {0: "-- Sin Madre --"}
                opciones_madre.update({
                    f.id_feligres: f"{f.nombre_completo()} - {f.curp or 'Sin CURP'}"
                    for f in feligreses
                })
                id_madre_sel = st.selectbox(
                    "O selecciona de la lista:",
                    options=opciones_madre.keys(),
                    format_func=lambda x: opciones_madre[x],
                    key="crear_madre_select"
                )
            
            st.markdown("---")
            submitted = st.form_submit_button("💾 Guardar Feligrés", type="primary", width="stretch")
            
            if submitted:
                # Validaciones
                if not nombres or not apellido_paterno or not curp:
                    st.error("❌ Nombres, Apellido Paterno y CURP son obligatorios")
                elif not validar_curp(curp):
                    st.error("❌ El CURP debe tener 18 caracteres alfanuméricos")
                else:
                    # Determinar IDs finales
                    id_padre = padre_encontrado.id_feligres if padre_encontrado else (id_padre_sel if id_padre_sel != 0 else None)
                    id_madre = madre_encontrada.id_feligres if madre_encontrada else (id_madre_sel if id_madre_sel != 0 else None)
                    
                    # Crear feligrés
                    nuevo_feligres = Feligres(
                        nombres=nombres.strip(),
                        apellido_paterno=apellido_paterno.strip(),
                        apellido_materno=apellido_materno.strip() if apellido_materno else None,
                        curp=curp.strip().upper(),
                        estado_canonico=estado_canonico,
                        id_padre=id_padre,
                        id_madre=id_madre
                    )
                    
                    if db_module.crear_feligres(nuevo_feligres, db_engine, st_display_func):
                        st.success("✅ Feligrés registrado exitosamente")
                        st.rerun()
    
    # ================================================================
    # TAB 2: VER FELIGRESES
    # ================================================================
    with tabs[1]:
        st.subheader("📋 Lista de Feligreses Registrados")
        
        feligreses = db_module.leer_feligreses(db_engine)
        
        if feligreses:
            # Selector para ver detalles
            st.markdown("### 👁️ Ver Detalles de un Feligrés")
            feligres_sel = st.selectbox(
                "Selecciona un feligrés:",
                options=feligreses,
                format_func=lambda f: f"{f.nombre_completo()} - {f.curp or 'Sin CURP'}",
                key="ver_feligres_detalle"
            )
            
            if feligres_sel:
                with st.expander("👁️ Ver Información Familiar Completa", expanded=True):
                    mostrar_informacion_familia_completa(feligres_sel, feligreses)
            
            st.markdown("---")
            st.markdown("### 📊 Tabla de Todos los Feligreses")
            
            # Preparar datos
            data = []
            feligreses_map = {f.id_feligres: f for f in feligreses}
            
            for f in feligreses:
                padre = feligreses_map.get(f.id_padre)
                madre = feligreses_map.get(f.id_madre)
                
                data.append({
                    "ID": f.id_feligres,
                    "Nombre Completo": f.nombre_completo(),
                    "CURP": f.curp or "Sin CURP",
                    "Estado Canónico": f.estado_canonico,
                    "Padre": padre.nombre_completo() if padre else "No registrado",
                    "Madre": madre.nombre_completo() if madre else "No registrada"
                })
            
            st.dataframe(data, width="stretch", hide_index=True)
        else:
            st.info("ℹ️ No hay feligreses registrados")
    
    # ================================================================
    # TAB 3: ACTUALIZAR FELIGRÉS
    # ================================================================
    with tabs[2]:
        st.subheader("✏️ Actualizar Datos de un Feligrés")
        
        feligreses = db_module.leer_feligreses(db_engine)
        
        if feligreses:
            opciones = {f.id_feligres: f"{f.nombre_completo()} - {f.curp or 'Sin CURP'}" for f in feligreses}
            
            id_sel = st.selectbox(
                "Selecciona el Feligrés a Editar:",
                options=opciones.keys(),
                format_func=lambda x: opciones[x],
                key="actualizar_feligres_sel"
            )
            
            feligres = next((f for f in feligreses if f.id_feligres == id_sel), None)
            
            if feligres:
                st.markdown("---")
                
                with st.form("form_actualizar_feligres"):
                    st.markdown("### 📝 Datos Personales")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        upd_nombres = st.text_input("Nombres (*)", value=feligres.nombres, key=f"upd_nombres_{id_sel}")
                        upd_paterno = st.text_input("Apellido Paterno (*)", value=feligres.apellido_paterno, key=f"upd_paterno_{id_sel}")
                    with col2:
                        upd_materno = st.text_input("Apellido Materno", value=feligres.apellido_materno or "", key=f"upd_materno_{id_sel}")
                        upd_curp = st.text_input("CURP (*)", value=feligres.curp or "", max_chars=18, key=f"upd_curp_{id_sel}")
                    
                    estados = ["soltero", "casado", "union libre"]
                    idx_estado = estados.index(feligres.estado_canonico) if feligres.estado_canonico in estados else 0
                    upd_estado = st.selectbox("Estado Canónico (*)", options=estados, index=idx_estado, key=f"upd_estado_{id_sel}")
                    
                    st.markdown("---")
                    st.markdown("### 👨‍👩‍👧 Actualizar Padres")
                    
                    # PADRE
                    st.markdown("**👨 Padre:**")
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        upd_curp_padre = st.text_input("CURP del Padre", max_chars=18, key=f"upd_padre_curp_{id_sel}")
                    
                    padre_nuevo = None
                    if upd_curp_padre:
                        padre_nuevo = buscar_feligres_por_curp(upd_curp_padre, db_engine)
                        if padre_nuevo:
                            st.success(f"✅ {padre_nuevo.nombre_completo()}")
                    
                    with col2:
                        opciones_padres = {0: "-- Sin Padre --"}
                        opciones_padres.update({f.id_feligres: f"{f.nombre_completo()} - {f.curp or 'Sin CURP'}" for f in feligreses})
                        
                        idx_padre = list(opciones_padres.keys()).index(feligres.id_padre) if feligres.id_padre and feligres.id_padre in opciones_padres else 0
                        upd_id_padre = st.selectbox("O selecciona de la lista:", options=list(opciones_padres.keys()), format_func=lambda x: opciones_padres[x], index=idx_padre, key=f"upd_padre_sel_{id_sel}")
                    
                    # MADRE
                    st.markdown("**👩 Madre:**")
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        upd_curp_madre = st.text_input("CURP de la Madre", max_chars=18, key=f"upd_madre_curp_{id_sel}")
                    
                    madre_nueva = None
                    if upd_curp_madre:
                        madre_nueva = buscar_feligres_por_curp(upd_curp_madre, db_engine)
                        if madre_nueva:
                            st.success(f"✅ {madre_nueva.nombre_completo()}")
                    
                    with col2:
                        opciones_madres = {0: "-- Sin Madre --"}
                        opciones_madres.update({f.id_feligres: f"{f.nombre_completo()} - {f.curp or 'Sin CURP'}" for f in feligreses})
                        
                        idx_madre = list(opciones_madres.keys()).index(feligres.id_madre) if feligres.id_madre and feligres.id_madre in opciones_madres else 0
                        upd_id_madre = st.selectbox("O selecciona de la lista:", options=list(opciones_madres.keys()), format_func=lambda x: opciones_madres[x], index=idx_madre, key=f"upd_madre_sel_{id_sel}")
                    
                    st.markdown("---")
                    submitted_upd = st.form_submit_button("💾 Actualizar Feligrés", type="primary", width="stretch")
                    
                    if submitted_upd:
                        if not upd_nombres or not upd_paterno or not upd_curp:
                            st.error("❌ Nombres, Apellido Paterno y CURP son obligatorios")
                        elif not validar_curp(upd_curp):
                            st.error("❌ El CURP debe tener 18 caracteres alfanuméricos")
                        else:
                            id_padre_final = padre_nuevo.id_feligres if padre_nuevo else (upd_id_padre if upd_id_padre != 0 else None)
                            id_madre_final = madre_nueva.id_feligres if madre_nueva else (upd_id_madre if upd_id_madre != 0 else None)
                            
                            if not validar_no_auto_referencia(feligres.id_feligres, id_padre_final, id_madre_final):
                                st.error("❌ Un feligrés no puede ser su propio padre o madre")
                            else:
                                datos = {
                                    "nombres": upd_nombres.strip(),
                                    "apellido_paterno": upd_paterno.strip(),
                                    "apellido_materno": upd_materno.strip() if upd_materno else None,
                                    "curp": upd_curp.strip().upper(),
                                    "estado_canonico": upd_estado,
                                    "id_padre": id_padre_final,
                                    "id_madre": id_madre_final
                                }
                                
                                if db_module.actualizar_feligres(feligres.id_feligres, datos, db_engine, st_display_func):
                                    st.success("✅ Feligrés actualizado")
                                    st.rerun()
        else:
            st.info("ℹ️ No hay feligreses para actualizar")
    
    # ================================================================
    # TAB 4: ELIMINAR FELIGRÉS
    # ================================================================
    with tabs[3]:
        st.subheader("🗑️ Eliminar Feligrés")
        
        feligreses = db_module.leer_feligreses(db_engine)
        
        if feligreses:
            st.warning("⚠️ **ADVERTENCIA:** Esta acción es permanente")
            
            feligres_eliminar = st.selectbox(
                "Selecciona el feligrés a eliminar:",
                options=feligreses,
                format_func=lambda f: f"{f.nombre_completo()} - {f.curp or 'Sin CURP'}",
                key="eliminar_feligres_sel"
            )
            
            if feligres_eliminar:
                st.markdown("---")
                
                with st.expander("👁️ Ver información de este feligrés"):
                    mostrar_informacion_familia_completa(feligres_eliminar, feligreses)
                
                st.markdown("---")
                
                CONFIRM_KEY = f"confirm_delete_feligres_{feligres_eliminar.id_feligres}"
                
                if not st.session_state.get(CONFIRM_KEY, False):
                    if st.button("🗑️ Eliminar Feligrés", type="secondary", key="init_delete"):
                        st.session_state[CONFIRM_KEY] = True
                        st.rerun()
                else:
                    st.error(f"⚠️ ¿Confirmas eliminar a **{feligres_eliminar.nombre_completo()}**?")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ SÍ, ELIMINAR", type="primary", width="stretch"):
                            if db_module.eliminar_feligres(feligres_eliminar.id_feligres, db_engine, st_display_func):
                                st.session_state.pop(CONFIRM_KEY, None)
                                st.success("✅ Feligrés eliminado")
                                st.rerun()
                    with col2:
                        if st.button("❌ Cancelar", width="stretch"):
                            st.session_state[CONFIRM_KEY] = False
                            st.rerun()
        else:
            st.info("ℹ️ No hay feligreses para eliminar")