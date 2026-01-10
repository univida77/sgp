# crud_actividades.py
import streamlit as st
from datetime import date, time, timedelta
from models import (
    Actividad, Curso, GrupoCatequesis, GrupoParroquial, CentroCatecismo,
    Horario, Salon, Inscripcion, Persona, Sesion, Tema
)
from sqlmodel import Session, select

def mostrar_crud_actividades(db_engine, db_module, db_mode, st_display_func):
    """Módulo completo CRUD para Actividades"""
    st.header(f"🎯 Gestión de Actividades - Modo: {db_mode}")
    
    st.info("💡 Las actividades son la implementación concreta de cursos o eventos")
    
    tabs = st.tabs([
        "➕ Crear Actividad",
        "📋 Ver Actividades",
        "👥 Inscripciones",
        "⏰ Horarios",
        "📅 Generar Sesiones",
        "✏️ Actualizar"
    ])
    
    # ================================================================
    # TAB 1: CREAR ACTIVIDAD
    # ================================================================
    with tabs[0]:
        st.subheader("➕ Crear Nueva Actividad")
        
        with st.form("form_crear_actividad", clear_on_submit=True):
            st.markdown("### 📝 Información Básica")
            
            col1, col2 = st.columns(2)
            
            with col1:
                nombre_actividad = st.text_input(
                    "Nombre de la Actividad (*)",
                    max_chars=200,
                    placeholder="Ej: colocar sillas",
                    key="act_nombre"
                )
                
                tipo_actividad = st.selectbox(
                    "Tipo de Actividad (*)",
                    options=["Curso", "Reunión", "-Taller", "Retiro", "Evento", "otro"],
                    key="act_tipo"
                )
                
                # Si es curso, mostrar selector de cursos
                if tipo_actividad == "Curso":
                    with Session(db_engine) as session:
                        cursos = session.exec(select(Curso).where(Curso.activo == True)).all()
                    
                    if not cursos:
                        st.warning("⚠️ No hay cursos activos. Crea un curso primero.")
                        id_curso_sel = None
                    else:
                        opciones_cursos = {0: "-- Sin Curso Asociado --"}
                        opciones_cursos.update({c.id_curso: f"{c.nombre_curso} ({c.tipo_curso})" for c in cursos})
                        
                        id_curso_sel = st.selectbox(
                            "Curso a Implementar",
                            options=opciones_cursos.keys(),
                            format_func=lambda x: opciones_cursos[x],
                            key="act_curso"
                        )
                        
                        if id_curso_sel != 0:
                            curso_sel = next((c for c in cursos if c.id_curso == id_curso_sel), None)
                            if curso_sel:
                                st.info(f"📚 {curso_sel.total_sesiones or 0} sesiones programadas")
                else:
                    id_curso_sel = None
            
            with col2:
                fecha_inicio = st.date_input(
                    "Fecha de Inicio (*)",
                    value=date.today(),
                    key="act_fecha_inicio"
                )
                
                fecha_fin = st.date_input(
                    "Fecha de Fin",
                    value=None,
                    key="act_fecha_fin"
                )
                
                ciclo = st.text_input(
                    "Ciclo/Período",
                    placeholder="Ej: 2024-A, Cuaresma 2024",
                    key="act_ciclo"
                )
            
            descripcion = st.text_area(
                "Descripción",
                placeholder="Detalles de la actividad...",
                key="act_descripcion"
            )
            
            st.markdown("---")
            st.markdown("### 👥 Asignación de Grupo")
            
            tipo_grupo = st.radio(
                "Tipo de Grupo (*)",
                options=["Grupo de Catequesis", "Grupo Parroquial"],
                key="act_tipo_grupo"
            )
            
            if tipo_grupo == "Grupo de Catequesis":
                with Session(db_engine) as session:
                    grupos_cat = session.exec(
                        select(GrupoCatequesis).where(GrupoCatequesis.activo == True)
                    ).all()
                
                if not grupos_cat:
                    st.warning("⚠️ No hay grupos de catequesis activos")
                    id_grupo_final = None
                    tipo_grupo_final = None
                else:
                    opciones_grupos = {g.id_grupo: g.nombre_grupo for g in grupos_cat}
                    id_grupo_cat_sel = st.selectbox(
                        "Selecciona el Grupo de Catequesis (*)",
                        options=opciones_grupos.keys(),
                        format_func=lambda x: opciones_grupos[x],
                        key="act_grupo_cat"
                    )
                    
                    # VALIDACIÓN: Solo 1 curso activo para grupo catequesis
                    if tipo_actividad == "Curso":
                        with Session(db_engine) as session:
                            curso_activo = session.exec(
                                select(Actividad).where(
                                    Actividad.id_grupo_catequesis == id_grupo_cat_sel,
                                    Actividad.tipo_actividad == "Curso",
                                    Actividad.estado.in_(["Programada", "En Curso"]),
                                    Actividad.activo == True
                                )
                            ).first()
                        
                        if curso_activo:
                            st.error(f"❌ Este grupo ya tiene un curso activo: '{curso_activo.nombre_actividad}'")
                            st.info("💡 Finaliza el curso actual antes de crear uno nuevo para este grupo")
                            id_grupo_final = None
                            tipo_grupo_final = None
                        else:
                            id_grupo_final = id_grupo_cat_sel
                            tipo_grupo_final = "catequesis"
                    else:
                        id_grupo_final = id_grupo_cat_sel
                        tipo_grupo_final = "catequesis"
            
            else:  # Grupo Parroquial
                with Session(db_engine) as session:
                    grupos_parr = session.exec(
                        select(GrupoParroquial).where(GrupoParroquial.activo == True)
                    ).all()
                
                if not grupos_parr:
                    st.warning("⚠️ No hay grupos parroquiales activos")
                    id_grupo_final = None
                    tipo_grupo_final = None
                else:
                    opciones_grupos = {g.id_grupo: g.nombre_grupo for g in grupos_parr}
                    id_grupo_parr_sel = st.selectbox(
                        "Selecciona el Grupo Parroquial (*)",
                        options=opciones_grupos.keys(),
                        format_func=lambda x: opciones_grupos[x],
                        key="act_grupo_parr"
                    )
                    
                    id_grupo_final = id_grupo_parr_sel
                    tipo_grupo_final = "parroquial"
            
            st.markdown("---")
            st.markdown("### 🏫 Centro de Catecismo")
            
            with Session(db_engine) as session:
                centros = session.exec(select(CentroCatecismo)).all()
            
            if centros:
                opciones_centros = {0: "-- Sin Centro Asignado --"}
                opciones_centros.update({c.id_centro: f"{c.nombre_centro} ({c.clave_centro})" for c in centros})
                
                id_centro_sel = st.selectbox(
                    "Centro donde se realizará",
                    options=opciones_centros.keys(),
                    format_func=lambda x: opciones_centros[x],
                    key="act_centro"
                )
            else:
                st.warning("⚠️ No hay centros de catecismo registrados")
                id_centro_sel = 0
            
            st.markdown("---")
            submitted = st.form_submit_button("💾 Crear Actividad", type="primary", width="stretch")
            
            if submitted:
                if not nombre_actividad:
                    st.error("❌ El nombre de la actividad es obligatorio")
                elif not id_grupo_final:
                    st.error("❌ Debes seleccionar un grupo")
                else:
                    nueva_actividad = Actividad(
                        nombre_actividad=nombre_actividad.strip(),
                        descripcion=descripcion.strip() if descripcion else None,
                        tipo_actividad=tipo_actividad,
                        id_curso=id_curso_sel if tipo_actividad == "Curso" and id_curso_sel != 0 else None,
                        id_grupo_catequesis=id_grupo_final if tipo_grupo_final == "catequesis" else None,
                        id_grupo_parroquial=id_grupo_final if tipo_grupo_final == "parroquial" else None,
                        fecha_inicio=fecha_inicio,
                        fecha_fin=fecha_fin,
                        ciclo=ciclo.strip() if ciclo else None,
                        estado="Programada",
                        activo=True,
                        id_centro=id_centro_sel if id_centro_sel != 0 else None
                    )
                    
                    if db_module.crear_registro(nueva_actividad, db_engine, st_display_func, nombre_tabla="Actividad"):
                        st.success("✅ Actividad creada exitosamente")
                        st.info("💡 Ahora puedes asignar horarios en la pestaña 'Horarios'")
                        st.rerun()
    
    # ================================================================
    # TAB 2: VER ACTIVIDADES
    # ================================================================
    with tabs[1]:
        st.subheader("📋 Lista de Actividades")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filtro_tipo = st.selectbox(
                "Tipo:",
                options=["Todas", "Curso", "Reunión", "Taller", "Retiro", "Evento"],
                key="filtro_tipo_act"
            )
        
        with col2:
            filtro_estado = st.selectbox(
                "Estado:",
                options=["Todas", "Programada", "En Curso", "Finalizada", "Cancelada"],
                key="filtro_estado_act"
            )
        
        with col3:
            filtro_activo = st.selectbox(
                "Activo:",
                options=["Todas", "Activas", "Inactivas"],
                key="filtro_activo_act"
            )
        
        # Consultar actividades
        with Session(db_engine) as session:
            statement = select(Actividad).order_by(Actividad.fecha_inicio.desc())
            
            if filtro_tipo != "Todas":
                statement = statement.where(Actividad.tipo_actividad == filtro_tipo)
            
            if filtro_estado != "Todas":
                statement = statement.where(Actividad.estado == filtro_estado)
            
            if filtro_activo == "Activas":
                statement = statement.where(Actividad.activo == True)
            elif filtro_activo == "Inactivas":
                statement = statement.where(Actividad.activo == False)
            
            actividades = session.exec(statement).all()
        
        if actividades:
            st.markdown(f"**Total:** {len(actividades)} actividades")
            
            for act in actividades:
                with Session(db_engine) as session:
                    # Obtener datos relacionados
                    curso = session.get(Curso, act.id_curso) if act.id_curso else None
                    grupo_cat = session.get(GrupoCatequesis, act.id_grupo_catequesis) if act.id_grupo_catequesis else None
                    grupo_parr = session.get(GrupoParroquial, act.id_grupo_parroquial) if act.id_grupo_parroquial else None
                    centro = session.get(CentroCatecismo, act.id_centro) if act.id_centro else None
                    
                    # Contar inscripciones
                    inscripciones = session.exec(
                        select(Inscripcion).where(
                            Inscripcion.id_actividad == act.id_actividad,
                            Inscripcion.estado == "Activo"
                        )
                    ).all()
                    
                    # Contar horarios
                    horarios = session.exec(
                        select(Horario).where(
                            Horario.id_actividad == act.id_actividad,
                            Horario.activo == True
                        )
                    ).all()
                    
                    # Contar sesiones
                    sesiones = session.exec(
                        select(Sesion).where(Sesion.id_actividad == act.id_actividad)
                    ).all()
                
                # Iconos de estado
                if act.estado == "Programada":
                    icono_estado = "📅"
                elif act.estado == "En Curso":
                    icono_estado = "▶️"
                elif act.estado == "Finalizada":
                    icono_estado = "✅"
                else:
                    icono_estado = "❌"
                
                with st.expander(f"{icono_estado} {act.nombre_actividad} ({act.tipo_actividad})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("**📊 Información:**")
                        st.markdown(f"Tipo: {act.tipo_actividad}")
                        st.markdown(f"Estado: {act.estado}")
                        if curso:
                            st.markdown(f"Curso: {curso.nombre_curso}")
                        st.markdown(f"Ciclo: {act.ciclo or 'N/A'}")
                    
                    with col2:
                        st.markdown("**👥 Grupo:**")
                        if grupo_cat:
                            st.markdown(f"Catequesis: {grupo_cat.nombre_grupo}")
                        elif grupo_parr:
                            st.markdown(f"Parroquial: {grupo_parr.nombre_grupo}")
                        
                        if centro:
                            st.markdown(f"Centro: {centro.nombre_centro}")
                    
                    with col3:
                        st.metric("Inscritos", len(inscripciones))
                        st.metric("Horarios", len(horarios))
                        st.metric("Sesiones", len(sesiones))
                    
                    st.markdown(f"**Fechas:** {act.fecha_inicio.strftime('%d/%m/%Y')} - {act.fecha_fin.strftime('%d/%m/%Y') if act.fecha_fin else 'Sin fecha fin'}")
                    
                    if act.descripcion:
                        st.caption(act.descripcion)
        else:
            st.info("ℹ️ No hay actividades con los filtros seleccionados")
    
    # ================================================================
    # TAB 3: INSCRIPCIONES
    # ================================================================
    with tabs[2]:
        st.subheader("👥 Gestión de Inscripciones")
        
        # Seleccionar actividad
        with Session(db_engine) as session:
            actividades = session.exec(
                select(Actividad).where(Actividad.activo == True)
            ).all()
        
        if not actividades:
            st.warning("⚠️ No hay actividades activas")
            return
        
        opciones_act = {a.id_actividad: f"{a.nombre_actividad} ({a.tipo_actividad})" for a in actividades}
        id_act_insc = st.selectbox(
            "Selecciona la Actividad:",
            options=opciones_act.keys(),
            format_func=lambda x: opciones_act[x],
            key="insc_actividad"
        )
        
        st.markdown("---")
        
        subtabs = st.tabs(["➕ Nueva Inscripción", "📋 Ver Inscritos"])
        
        # Nueva inscripción
        with subtabs[0]:
            with st.form("form_nueva_inscripcion", clear_on_submit=True):
                st.markdown("### ➕ Inscribir Participante")
                
                # Seleccionar persona
                with Session(db_engine) as session:
                    personas = session.exec(select(Persona)).all()
                
                opciones_personas = {p.id_persona: p.nombre_completo() for p in personas}
                id_persona_insc = st.selectbox(
                    "Persona a inscribir (*)",
                    options=opciones_personas.keys(),
                    format_func=lambda x: opciones_personas[x],
                    key="insc_persona"
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    rol_actividad = st.selectbox(
                        "Rol en la Actividad",
                        options=["Participante", "Coordinador", "Apoyo"],
                        key="insc_rol"
                    )
                
                with col2:
                    fecha_inscripcion = st.date_input(
                        "Fecha de Inscripción",
                        value=date.today(),
                        key="insc_fecha"
                    )
                
                observaciones_insc = st.text_area(
                    "Observaciones",
                    key="insc_observaciones"
                )
                
                submitted_insc = st.form_submit_button("💾 Inscribir", type="primary", width="stretch")
                
                if submitted_insc:
                    # Verificar si ya está inscrito
                    with Session(db_engine) as session:
                        ya_inscrito = session.exec(
                            select(Inscripcion).where(
                                Inscripcion.id_persona == id_persona_insc,
                                Inscripcion.id_actividad == id_act_insc,
                                Inscripcion.estado == "Activo"
                            )
                        ).first()
                    
                    if ya_inscrito:
                        st.error("❌ Esta persona ya está inscrita en esta actividad")
                    else:
                        nueva_inscripcion = Inscripcion(
                            id_persona=id_persona_insc,
                            id_actividad=id_act_insc,
                            rol_actividad=rol_actividad,
                            fecha_inscripcion=fecha_inscripcion,
                            estado="Activo",
                            observaciones=observaciones_insc.strip() if observaciones_insc else None
                        )
                        
                        if db_module.crear_registro(nueva_inscripcion, db_engine, st_display_func, nombre_tabla="Inscripción"):
                            st.success("✅ Persona inscrita exitosamente")
                            st.rerun()
        
        # Ver inscritos
        with subtabs[1]:
            with Session(db_engine) as session:
                inscripciones = session.exec(
                    select(Inscripcion).where(
                        Inscripcion.id_actividad == id_act_insc,
                        Inscripcion.estado == "Activo"
                    )
                ).all()
            
            if inscripciones:
                st.markdown(f"**Total de Inscritos:** {len(inscripciones)}")
                
                data = []
                with Session(db_engine) as session:
                    for insc in inscripciones:
                        persona = session.get(Persona, insc.id_persona)
                        data.append({
                            "Nombre": persona.nombre_completo() if persona else "N/A",
                            "Rol": insc.rol_actividad,
                            "Fecha Inscripción": insc.fecha_inscripcion.strftime("%d/%m/%Y"),
                            "Estado": insc.estado
                        })
                
                st.dataframe(data, width="stretch", hide_index=True)
            else:
                st.info("ℹ️ No hay personas inscritas aún")
    
    # ================================================================
    # TAB 4: HORARIOS
    # ================================================================
    with tabs[3]:
        st.subheader("⏰ Gestión de Horarios")
        
        # Seleccionar actividad
        with Session(db_engine) as session:
            actividades = session.exec(select(Actividad).where(Actividad.activo == True)).all()
        
        if not actividades:
            st.warning("⚠️ No hay actividades activas")
            return
        
        opciones_act = {a.id_actividad: f"{a.nombre_actividad}" for a in actividades}
        id_act_hor = st.selectbox(
            "Selecciona la Actividad:",
            options=opciones_act.keys(),
            format_func=lambda x: opciones_act[x],
            key="hor_actividad"
        )
        
        st.markdown("---")
        
        subtabs_hor = st.tabs(["➕ Nuevo Horario", "📋 Ver Horarios"])
        
        # Nuevo horario
        with subtabs_hor[0]:
            with st.form("form_nuevo_horario", clear_on_submit=True):
                st.markdown("### ➕ Asignar Horario")
                
                # Obtener actividad y centro
                with Session(db_engine) as session:
                    actividad = session.get(Actividad, id_act_hor)
                    
                    if not actividad.id_centro:
                        st.error("❌ Esta actividad no tiene un centro asignado")
                        salones = []
                    else:
                        # Obtener salones del centro
                        salones = session.exec(
                            select(Salon).where(
                                Salon.id_centro == actividad.id_centro,
                                Salon.activo == True
                            )
                        ).all()
                
                if not salones:
                    st.warning("⚠️ No hay salones disponibles en el centro de esta actividad")
                else:
                    opciones_salones = {s.id_salon: f"{s.nombre_salon} (Cap: {s.capacidad or 'N/A'})" for s in salones}
                    id_salon_hor = st.selectbox(
                        "Salón (*)",
                        options=opciones_salones.keys(),
                        format_func=lambda x: opciones_salones[x],
                        key="hor_salon"
                    )
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        dia_semana = st.selectbox(
                            "Día de la Semana (*)",
                            options=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
                            key="hor_dia"
                        )
                    
                    with col2:
                        hora_inicio = st.time_input(
                            "Hora de Inicio (*)",
                            value=time(16, 0),
                            key="hor_inicio"
                        )
                    
                    with col3:
                        hora_fin = st.time_input(
                            "Hora de Fin (*)",
                            value=time(18, 0),
                            key="hor_fin"
                        )
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fecha_inicio_vigencia = st.date_input(
                            "Vigente desde",
                            value=date.today(),
                            key="hor_vigencia_inicio"
                        )
                    
                    with col2:
                        fecha_fin_vigencia = st.date_input(
                            "Vigente hasta",
                            value=None,
                            key="hor_vigencia_fin"
                        )
                    
                    submitted_hor = st.form_submit_button("💾 Asignar Horario", type="primary", width="stretch")
                    
                    if submitted_hor:
                        if hora_fin <= hora_inicio:
                            st.error("❌ La hora de fin debe ser posterior a la hora de inicio")
                        else:
                            # TODO: Validar conflictos
                            nuevo_horario = Horario(
                                id_actividad=id_act_hor,
                                id_salon=id_salon_hor,
                                dia_semana=dia_semana,
                                hora_inicio=hora_inicio,
                                hora_fin=hora_fin,
                                fecha_inicio_vigencia=fecha_inicio_vigencia,
                                fecha_fin_vigencia=fecha_fin_vigencia,
                                activo=True
                            )
                            
                            if db_module.crear_registro(nuevo_horario, db_engine, st_display_func, nombre_tabla="Horario"):
                                st.success("✅ Horario asignado exitosamente")
                                st.rerun()
        
        # Ver horarios
        with subtabs_hor[1]:
            with Session(db_engine) as session:
                horarios = session.exec(
                    select(Horario).where(
                        Horario.id_actividad == id_act_hor,
                        Horario.activo == True
                    )
                ).all()
            
            if horarios:
                st.markdown(f"**Total de Horarios:** {len(horarios)}")
                
                for horario in horarios:
                    with Session(db_engine) as session:
                        salon = session.get(Salon, horario.id_salon)
                    
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.markdown(f"**📅 {horario.dia_semana}**")
                        st.caption(f"⏰ {horario.hora_inicio.strftime('%H:%M')} - {horario.hora_fin.strftime('%H:%M')}")
                    
                    with col2:
                        st.markdown(f"**🏫 {salon.nombre_salon if salon else 'N/A'}**")
                        st.caption(f"Vigencia: {horario.fecha_inicio_vigencia.strftime('%d/%m/%Y')} - {horario.fecha_fin_vigencia.strftime('%d/%m/%Y') if horario.fecha_fin_vigencia else 'Sin fin'}")
                    
                    with col3:
                        st.caption(f"ID: {horario.id_horario}")
                    
                    st.markdown("---")
            else:
                st.info("ℹ️ No hay horarios asignados")
    
    # ================================================================
    # TAB 5: GENERAR SESIONES
    # ================================================================
    with tabs[4]:
        st.subheader("📅 Generar Sesiones Automáticamente")
        
        # Seleccionar actividad tipo curso
        with Session(db_engine) as session:
            actividades_curso = session.exec(
                select(Actividad).where(
                    Actividad.tipo_actividad == "Curso",
                    Actividad.id_curso.isnot(None),
                    Actividad.activo == True
                )
            ).all()
        
        if not actividades_curso:
            st.warning("⚠️ No hay actividades de tipo 'Curso' con un curso asociado")
            return
        
        opciones_act = {a.id_actividad: f"{a.nombre_actividad}" for a in actividades_curso}
        id_act_ses = st.selectbox(
            "Selecciona la Actividad:",
            options=opciones_act.keys(),
            format_func=lambda x: opciones_act[x],
            key="ses_actividad"
        )
        
        with Session(db_engine) as session:
            actividad = session.get(Actividad, id_act_ses)
            curso = session.get(Curso, actividad.id_curso)
            
            # Contar sesiones existentes
            sesiones_existentes = session.exec(
                select(Sesion).where(Sesion.id_actividad == id_act_ses)
            ).all()
            
            # Obtener horarios
            horarios = session.exec(
                select(Horario).where(
                    Horario.id_actividad == id_act_ses,
                    Horario.activo == True
                )
            ).all()
            
            # Obtener temas del curso
            temas = session.exec(
                select(Tema).where(Tema.id_curso == actividad.id_curso).order_by(Tema.numero_sesion)
            ).all()
        
        st.info(f"📚 Curso: {curso.nombre_curso if curso else 'N/A'} - {len(temas)} temas")
        st.info(f"📅 {len(sesiones_existentes)} sesiones ya generadas")
        st.info(f"⏰ {len(horarios)} horarios asignados")
        
        if not horarios:
            st.warning("⚠️ Esta actividad no tiene horarios asignados. Asigna horarios primero.")
            return
        
        if len(sesiones_existentes) >= len(temas):
            st.success("✅ Todas las sesiones ya han sido generadas")
            return
        
        st.markdown("---")
        st.markdown("### 🔄 Generar Sesiones Faltantes")
        
        if st.button("🚀 Generar Sesiones Automáticamente", type="primary", width="stretch"):
            sesiones_creadas = 0
            fecha