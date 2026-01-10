# crud_presbiteros.py - Optimizado
import streamlit as st
from datetime import date
from sqlmodel import Session, select
from models import Presbitero, Persona
from utils import obtener_lista_personas, buscar_persona_por_curp, formatear_fecha

def mostrar_crud_presbiteros(db_engine, db_module, db_mode, st_display_func):
    """Módulo completo CRUD para Presbíteros."""
    st.header(f"🙏 Gestión de Presbíteros - Modo: {db_mode}")
    
    st.info("💡 Registra y gestiona la información de los presbíteros (sacerdotes)")
    
    tabs = st.tabs(["➕ Registrar Presbítero", "📋 Ver Presbíteros", "✏️ Actualizar", "🗑️ Eliminar"])

    # ================================================================
    # TAB 1: CREAR
    # ================================================================
    with tabs[0]:
        st.subheader("➕ Registrar Nuevo Presbítero")
        st.caption("Primero busca o selecciona a la persona, luego añade los detalles del presbiterado")

        with st.form("form_crear_presbitero", clear_on_submit=True):
            # Búsqueda de persona
            col1, col2 = st.columns([1, 2])
            
            with col1:
                curp_busqueda = st.text_input("Buscar por CURP", max_chars=18, key="presb_curp_buscar")
            
            persona_encontrada = None
            if curp_busqueda:
                persona_encontrada = buscar_persona_por_curp(curp_busqueda, db_engine)
                if persona_encontrada:
                    st.success(f"✅ {persona_encontrada.nombre_completo()}")
                else:
                    st.warning("⚠️ CURP no encontrado")

            with col2:
                personas = obtener_lista_personas(db_engine)
                if not personas:
                    st.error("❌ No hay personas registradas")
                    id_persona_final = None
                else:
                    opciones = {0: "-- Selecciona una Persona --"}
                    opciones.update({
                        p.id_persona: f"{p.nombre_completo()} - {p.curp or 'Sin CURP'}" 
                        for p in personas
                    })
                    id_persona_sel = st.selectbox(
                        "O selecciona de la lista:", 
                        options=opciones.keys(), 
                        format_func=lambda x: opciones[x], 
                        key="presb_persona_sel"
                    )
                    id_persona_final = persona_encontrada.id_persona if persona_encontrada else (id_persona_sel if id_persona_sel != 0 else None)

            if id_persona_final:
                # Verificar si ya es presbítero
                with Session(db_engine) as session:
                    ya_presbitero = session.exec(
                        select(Presbitero).where(Presbitero.id_persona == id_persona_final)
                    ).first()
                
                if ya_presbitero:
                    st.warning("⚠️ Esta persona ya está registrada como presbítero")
                else:
                    st.markdown("### 📋 Detalles del Presbiterado")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        fecha_ordenacion = st.date_input(
                            "Fecha de Ordenación", 
                            value=date.today(), 
                            key="presb_fecha"
                        )
                        diocesis = st.text_input("Diócesis de Origen", key="presb_diocesis")
                    
                    with col2:
                        cargo = st.selectbox(
                            "Cargo Actual", 
                            options=[
                                "Párroco", 
                                "Vicario Parroquial", 
                                "Párroco Emérito", 
                                "Administrador Parroquial", 
                                "Otro"
                            ], 
                            key="presb_cargo"
                        )
                        
                        cargo_otro = None
                        if cargo == "Otro":
                            cargo_otro = st.text_input("Especificar Cargo", key="presb_cargo_otro")
                    
                    submitted = st.form_submit_button("💾 Registrar Presbítero", type="primary")
                    
                    if submitted:
                        cargo_final = cargo_otro if cargo == "Otro" and cargo_otro else cargo
                        
                        nuevo = Presbitero(
                            id_persona=id_persona_final,
                            fecha_ordenacion=fecha_ordenacion,
                            diocesis=diocesis.strip() if diocesis else None,
                            cargo=cargo_final
                        )
                        
                        if db_module.crear_registro(nuevo, db_engine, st_display_func, "Presbítero"):
                            st.rerun()

    # ================================================================
    # TAB 2: VER
    # ================================================================
    with tabs[1]:
        st.subheader("📋 Lista de Presbíteros Registrados")
        
        with Session(db_engine) as session:
            presbiteros = session.exec(select(Presbitero)).all()
        
        if presbiteros:
            data = []
            with Session(db_engine) as session:
                for p in presbiteros:
                    persona = session.get(Persona, p.id_persona)
                    data.append({
                        "ID": p.id_presbitero,
                        "Nombre": persona.nombre_completo() if persona else "N/A",
                        "CURP": persona.curp if persona else "N/A",
                        "Cargo": p.cargo,
                        "Diócesis": p.diocesis or "N/A",
                        "Fecha de Ordenación": formatear_fecha(p.fecha_ordenacion)
                    })
            
            st.dataframe(data, width="stretch", hide_index=True)
        else:
            st.info("ℹ️ No hay presbíteros registrados")

    # ================================================================
    # TAB 3: ACTUALIZAR
    # ================================================================
    with tabs[2]:
        st.subheader("✏️ Actualizar Presbítero")
        
        with Session(db_engine) as session:
            presbiteros = session.exec(select(Presbitero)).all()
        
        if presbiteros:
            opciones = {}
            with Session(db_engine) as session:
                for p in presbiteros:
                    persona = session.get(Persona, p.id_persona)
                    opciones[p.id_presbitero] = f"{persona.nombre_completo() if persona else 'N/A'} - {p.cargo}"
            
            id_sel = st.selectbox(
                "Selecciona el presbítero a actualizar:",
                options=opciones.keys(),
                format_func=lambda x: opciones[x],
                key="upd_presbitero_sel"
            )
            
            presbitero = next((p for p in presbiteros if p.id_presbitero == id_sel), None)
            
            if presbitero:
                st.markdown("---")
                
                with st.form("form_upd_presbitero"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        upd_fecha = st.date_input(
                            "Fecha de Ordenación", 
                            value=presbitero.fecha_ordenacion, 
                            key="upd_fecha"
                        )
                        upd_diocesis = st.text_input(
                            "Diócesis", 
                            value=presbitero.diocesis or "", 
                            key="upd_diocesis"
                        )
                    
                    with col2:
                        cargos = ["Párroco", "Vicario Parroquial", "Párroco Emérito", "Administrador Parroquial", "Otro"]
                        idx_cargo = cargos.index(presbitero.cargo) if presbitero.cargo in cargos else 0
                        upd_cargo = st.selectbox(
                            "Cargo", 
                            options=cargos, 
                            index=idx_cargo, 
                            key="upd_cargo"
                        )
                    
                    submitted = st.form_submit_button("💾 Actualizar", type="primary")
                    
                    if submitted:
                        datos = {
                            "fecha_ordenacion": upd_fecha,
                            "diocesis": upd_diocesis.strip() if upd_diocesis else None,
                            "cargo": upd_cargo
                        }
                        
                        if db_module.actualizar_registro(
                            Presbitero, 
                            presbitero.id_presbitero, 
                            datos, 
                            db_engine, 
                            st_display_func, 
                            "Presbítero"
                        ):
                            st.rerun()
        else:
            st.info("ℹ️ No hay presbíteros para actualizar")

    # ================================================================
    # TAB 4: ELIMINAR
    # ================================================================
    with tabs[3]:
        st.subheader("🗑️ Eliminar Presbítero")
        
        with Session(db_engine) as session:
            presbiteros = session.exec(select(Presbitero)).all()
        
        if presbiteros:
            st.warning("⚠️ Esta acción solo elimina el registro de presbítero, no la persona")
            
            opciones = {}
            with Session(db_engine) as session:
                for p in presbiteros:
                    persona = session.get(Persona, p.id_persona)
                    opciones[p.id_presbitero] = f"{persona.nombre_completo() if persona else 'N/A'} - {p.cargo}"
            
            id_eliminar = st.selectbox(
                "Selecciona el presbítero a eliminar:",
                options=opciones.keys(),
                format_func=lambda x: opciones[x],
                key="del_presbitero_sel"
            )
            
            presbitero = next((p for p in presbiteros if p.id_presbitero == id_eliminar), None)
            
            if presbitero:
                CONFIRM_KEY = f"confirm_del_presb_{presbitero.id_presbitero}"
                
                if not st.session_state.get(CONFIRM_KEY, False):
                    if st.button("🗑️ Eliminar", type="secondary"):
                        st.session_state[CONFIRM_KEY] = True
                        st.rerun()
                else:
                    st.error("⚠️ ¿Confirmas eliminar este presbítero?")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ SÍ, ELIMINAR", type="primary", width="stretch"):
                            if db_module.eliminar_registro(
                                Presbitero, 
                                presbitero.id_presbitero, 
                                db_engine, 
                                st_display_func, 
                                "Presbítero"
                            ):
                                st.session_state.pop(CONFIRM_KEY, None)
                                st.rerun()
                    with col2:
                        if st.button("❌ Cancelar", width="stretch"):
                            st.session_state[CONFIRM_KEY] = False
                            st.rerun()
        else:
            st.info("ℹ️ No hay presbíteros para eliminar")