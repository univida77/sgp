# crud_grupo_parroquial.py - Optimizado
import streamlit as st
from datetime import date
from models import GrupoParroquial, MembresiaGrupo, Persona, Comunidad, Decanato, Rol, Parroquia
from utils import buscar_persona_por_curp, obtener_lista_personas
from sqlmodel import Session, select

# ====================================================================
# FUNCIONES AUXILIARES
# ====================================================================

def ensure_lider_role_exists(db_engine):
    """Asegura que exista el rol de líder."""
    with Session(db_engine) as session:
        lider = session.exec(select(Rol).where(Rol.nombre_rol == "Líder")).first()
        if not lider:
            nuevo = Rol(nombre_rol="Líder", descripcion="Líder principal del grupo")
            session.add(nuevo)
            session.commit()
            return nuevo.id_rol
        return lider.id_rol

# ====================================================================
# FUNCIÓN PRINCIPAL
# ====================================================================

def mostrar_crud_grupos_parroquiales(db_engine, db_module, db_mode, st_display_func):
    """Módulo completo CRUD para Grupos Parroquiales."""
    id_lider_global = ensure_lider_role_exists(db_engine)
    
    st.header(f"⛪ Gestión de Grupos Parroquiales - Modo: {db_mode}")
    
    st.info("💡 Agrupa personas en actividades o pastorales de la iglesia")
    
    tabs = st.tabs(["➕ Crear Grupo", "📋 Ver Grupos", "✏️ Actualizar", "🗑️ Eliminar"])
    
    # ================================================================
    # TAB 1: CREAR
    # ================================================================
    with tabs[0]:
        st.subheader("➕ Crear Nuevo Grupo Parroquial")
        
        # Obtener datos
        personas = obtener_lista_personas(db_engine)
        
        with Session(db_engine) as session:
            comunidades = session.exec(select(Comunidad)).all()
            decanatos = session.exec(select(Decanato)).all()
        
        with st.form("form_crear_grupo_parro", clear_on_submit=True):
            st.markdown("### 📋 Datos del Grupo")
            
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("Nombre del Grupo (*)", key="gp_nombre")
                tipo = st.selectbox(
                    "Tipo de Grupo",
                    options=["Pastoral Litúrgico", "Pastoral Profético", "Pastoral Social", "Comité", "Asociación"],
                    key="gp_tipo"
                )
                alcance = st.selectbox(
                    "Alcance",
                    options=["Local (Comunidad)", "Parroquial", "Inter-parroquial (Decanato)"],
                    key="gp_alcance"
                )
            
            with col2:
                fecha = st.date_input("Fecha de Creación", value=date.today(), key="gp_fecha")
                activo = st.checkbox("Activo", value=True, key="gp_activo")
                
                # Comunidad
                opciones_com = {0: "-- Sin Comunidad --"}
                opciones_com.update({c.id_comunidad: c.nombre_comunidad for c in comunidades})
                id_com = st.selectbox(
                    "Comunidad:",
                    options=opciones_com.keys(),
                    format_func=lambda x: opciones_com[x],
                    key="gp_comunidad"
                )
                
                # Decanato
                opciones_dec = {0: "-- Sin Decanato --"}
                opciones_dec.update({d.id_decanato: d.nombre_decanato for d in decanatos})
                id_dec = st.selectbox(
                    "Decanato:",
                    options=opciones_dec.keys(),
                    format_func=lambda x: opciones_dec[x],
                    key="gp_decanato"
                )
            
            descripcion = st.text_area("Descripción", key="gp_desc")
            
            st.markdown("---")
            st.markdown("### 👤 Líder del Grupo")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                curp_lider = st.text_input("CURP del Líder", max_chars=18, key="gp_lider_curp")
            
            lider_encontrado = None
            if curp_lider:
                lider_encontrado = buscar_persona_por_curp(curp_lider, db_engine)
                if lider_encontrado:
                    st.success(f"✅ {lider_encontrado.nombre_completo()}")
            
            with col2:
                if not personas:
                    st.error("❌ No hay personas registradas")
                    id_lider = None
                else:
                    opciones_pers = {0: "-- Selecciona --"}
                    opciones_pers.update({
                        p.id_persona: f"{p.nombre_completo()} - {p.curp or 'Sin CURP'}"
                        for p in personas
                    })
                    id_lider_sel = st.selectbox(
                        "O selecciona:",
                        options=opciones_pers.keys(),
                        format_func=lambda x: opciones_pers[x],
                        key="gp_lider_sel"
                    )
                    id_lider = lider_encontrado.id_persona if lider_encontrado else (id_lider_sel if id_lider_sel != 0 else None)
            
            st.markdown("---")
            submitted = st.form_submit_button("💾 Crear Grupo y Líder", type="primary", width="stretch")
            
            if submitted:
                if not nombre:
                    st.error("❌ El nombre es obligatorio")
                elif not id_lider:
                    st.error("❌ Debes seleccionar un líder")
                else:
                    # Crear grupo
                    nuevo_grupo = GrupoParroquial(
                        nombre_grupo=nombre.strip(),
                        descripcion=descripcion.strip() if descripcion else None,
                        tipo_grupo=tipo,
                        alcance=alcance,
                        id_comunidad=id_com if id_com != 0 else None,
                        id_decanato=id_dec if id_dec != 0 else None,
                        fecha_creacion=fecha,
                        activo=activo
                    )
                    
                    if db_module.crear_registro(nuevo_grupo, db_engine, st_display_func, "Grupo Parroquial"):
                        # Obtener primera parroquia
                        with Session(db_engine) as session:
                            parroquia_id = session.exec(select(Parroquia.id_parroquia)).first()
                        
                        # Crear membresía del líder
                        nueva_membresia = MembresiaGrupo(
                            id_persona=id_lider,
                            id_grupo=nuevo_grupo.id_grupo,
                            id_rol=id_lider_global,
                            id_parroquia=parroquia_id,
                            fecha_inicio=date.today()
                        )
                        
                        if db_module.crear_registro(nueva_membresia, db_engine, st_display_func, "Membresía Líder"):
                            st.rerun()
    
    # ================================================================
    # TAB 2: VER
    # ================================================================
    with tabs[1]:
        st.subheader("📋 Grupos Parroquiales Registrados")
        
        with Session(db_engine) as session:
            grupos = session.exec(select(GrupoParroquial)).all()
        
        if grupos:
            st.markdown(f"**Total:** {len(grupos)}")
            
            data = []
            with Session(db_engine) as session:
                for g in grupos:
                    comunidad = session.get(Comunidad, g.id_comunidad) if g.id_comunidad else None
                    decanato = session.get(Decanato, g.id_decanato) if g.id_decanato else None
                    
                    # Contar miembros
                    miembros = session.exec(
                        select(MembresiaGrupo).where(MembresiaGrupo.id_grupo == g.id_grupo)
                    ).all()
                    
                    data.append({
                        "ID": g.id_grupo,
                        "Nombre": g.nombre_grupo,
                        "Tipo": g.tipo_grupo,
                        "Alcance": g.alcance,
                        "Activo": "Sí" if g.activo else "No",
                        "Miembros": len(miembros),
                        "Comunidad": comunidad.nombre_comunidad if comunidad else "N/A",
                        "Decanato": decanato.nombre_decanato if decanato else "N/A",
                        "Fecha": g.fecha_creacion.strftime("%d/%m/%Y")
                    })
            
            st.dataframe(data, width="stretch", hide_index=True)
        else:
            st.info("ℹ️ No hay grupos parroquiales registrados")
    
    # ================================================================
    # TAB 3: ACTUALIZAR
    # ================================================================
    with tabs[2]:
        st.subheader("✏️ Actualizar Grupo Parroquial")
        st.info("💡 Actualización disponible para implementar")
    
    # ================================================================
    # TAB 4: ELIMINAR
    # ================================================================
    with tabs[3]:
        st.subheader("🗑️ Eliminar Grupo Parroquial")
        
        with Session(db_engine) as session:
            grupos = session.exec(select(GrupoParroquial)).all()
        
        if grupos:
            opciones = {g.id_grupo: g.nombre_grupo for g in grupos}
            id_grupo_sel = st.selectbox(
                "Selecciona el grupo:",
                options=opciones.keys(),
                format_func=lambda x: opciones[x],
                key="del_gp_sel"
            )
            
            grupo = next((g for g in grupos if g.id_grupo == id_grupo_sel), None)
            
            if grupo:
                with Session(db_engine) as session:
                    miembros = session.exec(
                        select(MembresiaGrupo).where(MembresiaGrupo.id_grupo == grupo.id_grupo)
                    ).all()
                
                st.warning("⚠️ Esta acción eliminará:")
                st.markdown(f"- **Grupo:** {grupo.nombre_grupo}")
                st.markdown(f"- **Membresías:** {len(miembros)}")
                
                st.markdown("---")
                
                CONFIRM_KEY = f"confirm_del_gp_{grupo.id_grupo}"
                
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
                                GrupoParroquial,
                                grupo.id_grupo,
                                db_engine,
                                st_display_func,
                                "Grupo Parroquial"
                            ):
                                st.session_state.pop(CONFIRM_KEY, None)
                                st.rerun()
                    with col2:
                        if st.button("❌ Cancelar", width="stretch"):
                            st.session_state[CONFIRM_KEY] = False
                            st.rerun()
        else:
            st.info("ℹ️ No hay grupos para eliminar")