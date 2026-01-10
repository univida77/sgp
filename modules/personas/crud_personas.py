# crud_personas.py - Optimizado
import streamlit as st
from models import Persona
from utils import (
    buscar_persona_por_curp, validar_curp, validar_no_auto_referencia,
    obtener_lista_personas, mostrar_informacion_familia_completa
)

def mostrar_crud_personas(db_engine, db_module, db_mode, st_display_func):
    """Módulo completo CRUD para Personas."""
    st.header(f"👥 Gestión de Personas - Modo: {db_mode}")
    
    tabs = st.tabs([
        "➕ Crear Persona",
        "📋 Ver Personas",
        "✏️ Actualizar Persona",
        "🗑️ Eliminar Persona"
    ])
    
    # ================================================================
    # TAB 1: CREAR PERSONA
    # ================================================================
    with tabs[0]:
        st.subheader("➕ Registrar Nueva Persona")
        
        with st.form("form_crear_persona", clear_on_submit=True):
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
                padre_encontrado = buscar_persona_por_curp(curp_padre, db_engine)
                if padre_encontrado:
                    st.success(f"✅ {padre_encontrado.nombre_completo()}")
            
            with col2:
                personas = obtener_lista_personas(db_engine)
                opciones_padre = {0: "-- Sin Padre --"}
                opciones_padre.update({
                    p.id_persona: f"{p.nombre_completo()} - {p.curp or 'Sin CURP'}"
                    for p in personas
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
                madre_encontrada = buscar_persona_por_curp(curp_madre, db_engine)
                if madre_encontrada:
                    st.success(f"✅ {madre_encontrada.nombre_completo()}")
            
            with col2:
                opciones_madre = {0: "-- Sin Madre --"}
                opciones_madre.update({
                    p.id_persona: f"{p.nombre_completo()} - {p.curp or 'Sin CURP'}"
                    for p in personas
                })
                id_madre_sel = st.selectbox(
                    "O selecciona de la lista:",
                    options=opciones_madre.keys(),
                    format_func=lambda x: opciones_madre[x],
                    key="crear_madre_select"
                )
            
            st.markdown("---")
            submitted = st.form_submit_button("💾 Guardar Persona", type="primary", width="stretch")
            
            if submitted:
                # Validaciones
                if not nombres or not apellido_paterno or not curp:
                    st.error("❌ Nombres, Apellido Paterno y CURP son obligatorios")
                elif not validar_curp(curp):
                    st.error("❌ El CURP debe tener 18 caracteres alfanuméricos")
                else:
                    # Determinar IDs finales
                    id_padre = padre_encontrado.id_persona if padre_encontrado else (id_padre_sel if id_padre_sel != 0 else None)
                    id_madre = madre_encontrada.id_persona if madre_encontrada else (id_madre_sel if id_madre_sel != 0 else None)
                    
                    # Crear persona
                    nueva_persona = Persona(
                        nombres=nombres.strip(),
                        apellido_paterno=apellido_paterno.strip(),
                        apellido_materno=apellido_materno.strip() if apellido_materno else None,
                        curp=curp.strip().upper(),
                        estado_canonico=estado_canonico,
                        id_padre=id_padre,
                        id_madre=id_madre
                    )
                    
                    if db_module.crear_persona(nueva_persona, db_engine, st_display_func):
                        st.rerun()
    
    # ================================================================
    # TAB 2: VER PERSONAS
    # ================================================================
    with tabs[1]:
        st.subheader("📋 Lista de Personas Registradas")
        
        personas = db_module.leer_personas(db_engine)
        
        if personas:
            # Selector para ver detalles
            st.markdown("### 👁️ Ver Detalles de una Persona")
            persona_sel = st.selectbox(
                "Selecciona una persona:",
                options=personas,
                format_func=lambda p: f"{p.nombre_completo()} - {p.curp or 'Sin CURP'}",
                key="ver_persona_detalle"
            )
            
            if persona_sel:
                with st.expander("👁️ Ver Información Familiar Completa", expanded=True):
                    mostrar_informacion_familia_completa(persona_sel, personas)
            
            st.markdown("---")
            st.markdown("### 📊 Tabla de Todas las Personas")
            
            # Preparar datos
            data = []
            personas_map = {p.id_persona: p for p in personas}
            
            for p in personas:
                padre = personas_map.get(p.id_padre)
                madre = personas_map.get(p.id_madre)
                
                data.append({
                    "ID": p.id_persona,
                    "Nombre Completo": p.nombre_completo(),
                    "CURP": p.curp or "Sin CURP",
                    "Estado Canónico": p.estado_canonico,
                    "Padre": padre.nombre_completo() if padre else "No registrado",
                    "Madre": madre.nombre_completo() if madre else "No registrada"
                })
            
            st.dataframe(data, width="stretch", hide_index=True)
        else:
            st.info("ℹ️ No hay personas registradas")
    
    # ================================================================
    # TAB 3: ACTUALIZAR PERSONA
    # ================================================================
    with tabs[2]:
        st.subheader("✏️ Actualizar Datos de una Persona")
        
        personas = db_module.leer_personas(db_engine)
        
        if personas:
            opciones = {p.id_persona: f"{p.nombre_completo()} - {p.curp or 'Sin CURP'}" for p in personas}
            
            id_sel = st.selectbox(
                "Selecciona la Persona a Editar:",
                options=opciones.keys(),
                format_func=lambda x: opciones[x],
                key="actualizar_persona_sel"
            )
            
            persona = next((p for p in personas if p.id_persona == id_sel), None)
            
            if persona:
                st.markdown("---")
                
                with st.form("form_actualizar_persona"):
                    st.markdown("### 📝 Datos Personales")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        upd_nombres = st.text_input("Nombres (*)", value=persona.nombres, key=f"upd_nombres_{id_sel}")
                        upd_paterno = st.text_input("Apellido Paterno (*)", value=persona.apellido_paterno, key=f"upd_paterno_{id_sel}")
                    with col2:
                        upd_materno = st.text_input("Apellido Materno", value=persona.apellido_materno or "", key=f"upd_materno_{id_sel}")
                        upd_curp = st.text_input("CURP (*)", value=persona.curp or "", max_chars=18, key=f"upd_curp_{id_sel}")
                    
                    estados = ["soltero", "casado", "union libre"]
                    idx_estado = estados.index(persona.estado_canonico) if persona.estado_canonico in estados else 0
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
                        padre_nuevo = buscar_persona_por_curp(upd_curp_padre, db_engine)
                        if padre_nuevo:
                            st.success(f"✅ {padre_nuevo.nombre_completo()}")
                    
                    with col2:
                        opciones_padres = {0: "-- Sin Padre --"}
                        opciones_padres.update({p.id_persona: f"{p.nombre_completo()} - {p.curp or 'Sin CURP'}" for p in personas})
                        
                        idx_padre = list(opciones_padres.keys()).index(persona.id_padre) if persona.id_padre and persona.id_padre in opciones_padres else 0
                        upd_id_padre = st.selectbox("O selecciona de la lista:", options=list(opciones_padres.keys()), format_func=lambda x: opciones_padres[x], index=idx_padre, key=f"upd_padre_sel_{id_sel}")
                    
                    # MADRE
                    st.markdown("**👩 Madre:**")
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        upd_curp_madre = st.text_input("CURP de la Madre", max_chars=18, key=f"upd_madre_curp_{id_sel}")
                    
                    madre_nueva = None
                    if upd_curp_madre:
                        madre_nueva = buscar_persona_por_curp(upd_curp_madre, db_engine)
                        if madre_nueva:
                            st.success(f"✅ {madre_nueva.nombre_completo()}")
                    
                    with col2:
                        opciones_madres = {0: "-- Sin Madre --"}
                        opciones_madres.update({p.id_persona: f"{p.nombre_completo()} - {p.curp or 'Sin CURP'}" for p in personas})
                        
                        idx_madre = list(opciones_madres.keys()).index(persona.id_madre) if persona.id_madre and persona.id_madre in opciones_madres else 0
                        upd_id_madre = st.selectbox("O selecciona de la lista:", options=list(opciones_madres.keys()), format_func=lambda x: opciones_madres[x], index=idx_madre, key=f"upd_madre_sel_{id_sel}")
                    
                    st.markdown("---")
                    submitted_upd = st.form_submit_button("💾 Actualizar Persona", type="primary", width="stretch")
                    
                    if submitted_upd:
                        if not upd_nombres or not upd_paterno or not upd_curp:
                            st.error("❌ Nombres, Apellido Paterno y CURP son obligatorios")
                        elif not validar_curp(upd_curp):
                            st.error("❌ El CURP debe tener 18 caracteres alfanuméricos")
                        else:
                            id_padre_final = padre_nuevo.id_persona if padre_nuevo else (upd_id_padre if upd_id_padre != 0 else None)
                            id_madre_final = madre_nueva.id_persona if madre_nueva else (upd_id_madre if upd_id_madre != 0 else None)
                            
                            if not validar_no_auto_referencia(persona.id_persona, id_padre_final, id_madre_final):
                                st.error("❌ Una persona no puede ser su propio padre o madre")
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
                                
                                if db_module.actualizar_persona(persona.id_persona, datos, db_engine, st_display_func):
                                    st.rerun()
        else:
            st.info("ℹ️ No hay personas para actualizar")
    
    # ================================================================
    # TAB 4: ELIMINAR PERSONA
    # ================================================================
    with tabs[3]:
        st.subheader("🗑️ Eliminar Persona")
        
        personas = db_module.leer_personas(db_engine)
        
        if personas:
            st.warning("⚠️ **ADVERTENCIA:** Esta acción es permanente")
            
            persona_eliminar = st.selectbox(
                "Selecciona la persona a eliminar:",
                options=personas,
                format_func=lambda p: f"{p.nombre_completo()} - {p.curp or 'Sin CURP'}",
                key="eliminar_persona_sel"
            )
            
            if persona_eliminar:
                st.markdown("---")
                
                with st.expander("👁️ Ver información de esta persona"):
                    mostrar_informacion_familia_completa(persona_eliminar, personas)
                
                st.markdown("---")
                
                CONFIRM_KEY = f"confirm_delete_persona_{persona_eliminar.id_persona}"
                
                if not st.session_state.get(CONFIRM_KEY, False):
                    if st.button("🗑️ Eliminar Persona", type="secondary", key="init_delete"):
                        st.session_state[CONFIRM_KEY] = True
                        st.rerun()
                else:
                    st.error(f"⚠️ ¿Confirmas eliminar a **{persona_eliminar.nombre_completo()}**?")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ SÍ, ELIMINAR", type="primary", width="stretch"):
                            if db_module.eliminar_persona(persona_eliminar.id_persona, db_engine, st_display_func):
                                st.session_state.pop(CONFIRM_KEY, None)
                                st.rerun()
                    with col2:
                        if st.button("❌ Cancelar", width="stretch"):
                            st.session_state[CONFIRM_KEY] = False
                            st.rerun()
        else:
            st.info("ℹ️ No hay personas para eliminar")