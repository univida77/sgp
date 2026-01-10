# crud_asistencia.py - LIMPIO SIN BOTONES EXTRA
import streamlit as st
from datetime import date, time, datetime
from models import (
    RegistroAsistencia, Sesion, Actividad, Persona, Inscripcion,
    ReunionGrupal, AsistenciaReunion, GrupoParroquial, Salon
)
from sqlmodel import Session, select, func

def mostrar_crud_asistencia(db_engine, db_module, db_mode, st_display_func):
    """Módulo completo CRUD para Asistencia"""
    st.header(f"✅ Gestión de Asistencia - Modo: {db_mode}")
    
    st.info("💡 Registra asistencia individual (catequesis) o grupal (grupos parroquiales)")
    
    tabs = st.tabs([
        "✅ Tomar Asistencia",
        "👥 Reunión Grupal",
        "📊 Reportes",
        "📋 Historial"
    ])
    
    # ================================================================
    # TAB 1: TOMAR ASISTENCIA
    # ================================================================
    with tabs[0]:
        st.subheader("✅ Tomar Asistencia en Sesión")
        
        with Session(db_engine) as session:
            sesiones_disponibles = session.exec(
                select(Sesion).where(
                    Sesion.fecha_sesion >= date.today(),
                    Sesion.estado.in_(["Programada", "Realizada"])
                ).order_by(Sesion.fecha_sesion)
            ).all()
        
        if not sesiones_disponibles:
            st.warning("⚠️ No hay sesiones disponibles")
            return
        
        opciones_sesiones = {}
        with Session(db_engine) as session:
            for s in sesiones_disponibles:
                actividad = session.get(Actividad, s.id_actividad)
                opciones_sesiones[s.id_sesion] = f"{s.nombre_sesion} - {s.fecha_sesion.strftime('%d/%m/%Y')} ({actividad.nombre_actividad if actividad else 'N/A'})"
        
        id_sesion_asist = st.selectbox(
            "Selecciona la Sesión:",
            options=opciones_sesiones.keys(),
            format_func=lambda x: opciones_sesiones[x],
            key="asist_sesion"
        )
        
        with Session(db_engine) as session:
            sesion_seleccionada = session.get(Sesion, id_sesion_asist)
            actividad = session.get(Actividad, sesion_seleccionada.id_actividad)
            
            inscripciones = session.exec(
                select(Inscripcion).where(
                    Inscripcion.id_actividad == actividad.id_actividad,
                    Inscripcion.estado == "Activo"
                )
            ).all()
            
            asistencias_registradas = session.exec(
                select(RegistroAsistencia).where(RegistroAsistencia.id_sesion == id_sesion_asist)
            ).all()
            
            asistencias_dict = {a.id_persona: a for a in asistencias_registradas}
        
        st.markdown("---")
        st.markdown(f"### 📅 {sesion_seleccionada.nombre_sesion}")
        st.markdown(f"**Fecha:** {sesion_seleccionada.fecha_sesion.strftime('%d/%m/%Y')}")
        st.markdown(f"**Actividad:** {actividad.nombre_actividad}")
        
        if inscripciones:
            st.markdown(f"**Total Inscritos:** {len(inscripciones)}")
            st.markdown(f"**Registrados:** {len(asistencias_registradas)}/{len(inscripciones)}")
            
            st.markdown("---")
            
            asistencias_nuevas = {}
            
            for inscripcion in inscripciones:
                with Session(db_engine) as session:
                    persona = session.get(Persona, inscripcion.id_persona)
                
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"**{persona.nombre_completo() if persona else 'N/A'}**")
                
                with col2:
                    if inscripcion.id_persona in asistencias_dict:
                        estado_actual = asistencias_dict[inscripcion.id_persona].estado_asistencia
                        indice_actual = ["Presente", "Ausente", "Retardo", "Permiso"].index(estado_actual)
                    else:
                        indice_actual = 0
                    
                    estado = st.selectbox(
                        "Estado",
                        options=["Presente", "Ausente", "Retardo", "Permiso"],
                        index=indice_actual,
                        key=f"estado_{inscripcion.id_persona}_{id_sesion_asist}",
                        label_visibility="collapsed"
                    )
                    
                    asistencias_nuevas[inscripcion.id_persona] = estado
                
                with col3:
                    if inscripcion.id_persona in asistencias_dict:
                        st.caption("✅")
                
                st.markdown("---")
            
            # Registrador
            st.markdown("### 👤 Registrador")
            
            with Session(db_engine) as session:
                personas = session.exec(select(Persona)).all()
            
            opciones_registrador = {p.id_persona: p.nombre_completo() for p in personas}
            id_registrador = st.selectbox(
                "¿Quién toma lista?",
                options=opciones_registrador.keys(),
                format_func=lambda x: opciones_registrador[x],
                key=f"asist_registrador_{id_sesion_asist}"
            )
            
            metodo = st.selectbox(
                "Método de Registro",
                options=["Manual", "QR", "Facial"],
                key=f"asist_metodo_{id_sesion_asist}"
            )
            
            if st.button(
                "💾 Guardar Asistencia",
                type="primary",
                width="stretch",
                key=f"btn_guardar_asist_{id_sesion_asist}"
            ):
                registros_creados = 0
                registros_actualizados = 0
                
                for id_persona, estado in asistencias_nuevas.items():
                    if id_persona in asistencias_dict:
                        if db_module.actualizar_registro(
                            RegistroAsistencia,
                            asistencias_dict[id_persona].id_asistencia,
                            {
                                "estado_asistencia": estado,
                                "fecha_registro": datetime.now(),
                                "metodo_registro": metodo
                            },
                            db_engine,
                            st_display_func,
                            nombre_tabla="Asistencia"
                        ):
                            registros_actualizados += 1
                    else:
                        nuevo_registro = RegistroAsistencia(
                            id_sesion=id_sesion_asist,
                            id_persona=id_persona,
                            estado_asistencia=estado,
                            fecha_registro=datetime.now(),
                            metodo_registro=metodo,
                            id_registrador=id_registrador
                        )
                        
                        if db_module.crear_registro(nuevo_registro, db_engine, st_display_func, synchronize=True, nombre_tabla="Asistencia"):
                            registros_creados += 1
                
                st.success(f"✅ Guardado: {registros_creados} nuevos, {registros_actualizados} actualizados")
                st.rerun()
        else:
            st.info("ℹ️ No hay personas inscritas")
    
    # ================================================================
    # TAB 2: REUNIÓN GRUPAL
    # ================================================================
    with tabs[1]:
        st.subheader("👥 Registrar Reunión de Grupo Parroquial")
        
        subtabs = st.tabs(["➕ Nueva Reunión", "📋 Ver Reuniones"])
        
        with subtabs[0]:
            with Session(db_engine) as session:
                grupos = session.exec(select(GrupoParroquial).where(GrupoParroquial.activo == True)).all()
            
            if not grupos:
                st.warning("⚠️ No hay grupos parroquiales activos")
            else:
                opciones_grupos = {g.id_grupo: g.nombre_grupo for g in grupos}
                id_grupo_reunion = st.selectbox(
                    "Grupo (*)",
                    options=opciones_grupos.keys(),
                    format_func=lambda x: opciones_grupos[x],
                    key="reunion_grupo"
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    nombre_reunion = st.text_input(
                        "Nombre de la Reunión (*)",
                        key="reunion_nombre"
                    )
                    
                    fecha_reunion = st.date_input(
                        "Fecha (*)",
                        value=date.today(),
                        key="reunion_fecha"
                    )
                    
                    hora_inicio_reunion = st.time_input(
                        "Hora de Inicio",
                        value=time(19, 0),
                        key="reunion_hora_inicio"
                    )
                
                with col2:
                    tema_reunion = st.text_input(
                        "Tema",
                        key="reunion_tema"
                    )
                    
                    with Session(db_engine) as session:
                        personas = session.exec(select(Persona)).all()
                    
                    opciones_personas = {p.id_persona: p.nombre_completo() for p in personas}
                    id_responsable_reunion = st.selectbox(
                        "Responsable (*)",
                        options=opciones_personas.keys(),
                        format_func=lambda x: opciones_personas[x],
                        key="reunion_responsable"
                    )
                    
                    hora_fin_reunion = st.time_input(
                        "Hora de Fin",
                        value=time(21, 0),
                        key="reunion_hora_fin"
                    )
                
                tipo_asistencia = st.radio(
                    "Tipo de Asistencia (*)",
                    options=["Individual", "Estadística"],
                    key="reunion_tipo_asist"
                )
                
                if tipo_asistencia == "Estadística":
                    col1, col2 = st.columns(2)
                    with col1:
                        total_esperados = st.number_input(
                            "Total Esperados",
                            min_value=0,
                            value=0,
                            key="reunion_esperados"
                        )
                    with col2:
                        total_asistentes = st.number_input(
                            "Total Asistentes",
                            min_value=0,
                            value=0,
                            key="reunion_asistentes"
                        )
                else:
                    total_esperados = None
                    total_asistentes = None
                
                descripcion_reunion = st.text_area(
                    "Descripción",
                    key="reunion_descripcion"
                )
                
                if st.button("💾 Registrar Reunión", type="primary", width="stretch", key="btn_registrar_reunion"):
                    if not nombre_reunion:
                        st.error("❌ El nombre es obligatorio")
                    else:
                        nueva_reunion = ReunionGrupal(
                            id_grupo=id_grupo_reunion,
                            nombre_reunion=nombre_reunion.strip(),
                            fecha_reunion=fecha_reunion,
                            hora_inicio=hora_inicio_reunion,
                            hora_fin=hora_fin_reunion,
                            tema=tema_reunion.strip() if tema_reunion else None,
                            descripcion=descripcion_reunion.strip() if descripcion_reunion else None,
                            id_responsable=id_responsable_reunion,
                            tipo_asistencia=tipo_asistencia,
                            total_esperados=total_esperados if tipo_asistencia == "Estadística" else None,
                            total_asistentes=total_asistentes if tipo_asistencia == "Estadística" else None
                        )
                        
                        if db_module.crear_registro(nueva_reunion, db_engine, st_display_func, nombre_tabla="Reunión Grupal"):
                            st.success("✅ Reunión registrada")
                            st.rerun()
        
        with subtabs[1]:
            with Session(db_engine) as session:
                reuniones = session.exec(
                    select(ReunionGrupal).order_by(ReunionGrupal.fecha_reunion.desc())
                ).all()
            
            if reuniones:
                for reunion in reuniones:
                    with Session(db_engine) as session:
                        grupo = session.get(GrupoParroquial, reunion.id_grupo)
                        responsable = session.get(Persona, reunion.id_responsable)
                    
                    with st.expander(f"📅 {reunion.nombre_reunion} - {reunion.fecha_reunion.strftime('%d/%m/%Y')}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**Grupo:** {grupo.nombre_grupo if grupo else 'N/A'}")
                            st.markdown(f"**Fecha:** {reunion.fecha_reunion.strftime('%d/%m/%Y')}")
                            st.markdown(f"**Horario:** {reunion.hora_inicio.strftime('%H:%M')} - {reunion.hora_fin.strftime('%H:%M') if reunion.hora_fin else 'N/A'}")
                        
                        with col2:
                            st.markdown(f"**Responsable:** {responsable.nombre_completo() if responsable else 'N/A'}")
                            
                            if reunion.tipo_asistencia == "Estadística":
                                st.metric("Asistencia", f"{reunion.total_asistentes or 0}/{reunion.total_esperados or 0}")
            else:
                st.info("ℹ️ No hay reuniones registradas")
    
    # ================================================================
    # TAB 3: REPORTES
    # ================================================================
    with tabs[2]:
        st.subheader("📊 Reportes de Asistencia")
        
        tipo_reporte = st.selectbox(
            "Tipo de Reporte:",
            options=["Por Persona", "Por Actividad"],
            key="tipo_reporte"
        )
        
        if tipo_reporte == "Por Persona":
            with Session(db_engine) as session:
                personas = session.exec(select(Persona)).all()
            
            opciones_personas = {p.id_persona: p.nombre_completo() for p in personas}
            id_persona_reporte = st.selectbox(
                "Selecciona la Persona:",
                options=opciones_personas.keys(),
                format_func=lambda x: opciones_personas[x],
                key="reporte_persona"
            )
            
            with Session(db_engine) as session:
                asistencias = session.exec(
                    select(RegistroAsistencia).where(RegistroAsistencia.id_persona == id_persona_reporte)
                ).all()
            
            if asistencias:
                total = len(asistencias)
                presentes = len([a for a in asistencias if a.estado_asistencia == "Presente"])
                ausentes = len([a for a in asistencias if a.estado_asistencia == "Ausente"])
                retardos = len([a for a in asistencias if a.estado_asistencia == "Retardo"])
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total", total)
                col2.metric("Presentes", presentes, f"{(presentes/total*100):.1f}%")
                col3.metric("Ausentes", ausentes)
                col4.metric("Retardos", retardos)
            else:
                st.info("ℹ️ No hay registros")
    
    # ================================================================
    # TAB 4: HISTORIAL
    # ================================================================
    with tabs[3]:
        st.info("💡 Historial disponible para implementar")