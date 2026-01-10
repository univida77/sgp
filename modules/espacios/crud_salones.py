# crud_salones.py
import streamlit as st
from datetime import date, time, datetime
from models import Salon, CentroCatecismo, Horario, ReservacionSalon, Actividad, Persona
from sqlmodel import Session, select

def mostrar_crud_salones(db_engine, db_module, db_mode, st_display_func):
    """Módulo completo CRUD para Salones"""
    st.header(f"🏫 Gestión de Salones - Modo: {db_mode}")
    
    st.info("💡 Administra los espacios físicos de cada centro de catecismo")
    
    tabs = st.tabs([
        "➕ Crear Salón",
        "📋 Ver Salones",
        "🗓️ Calendario de Uso",
        "📝 Reservaciones",
        "✏️ Actualizar",
        "🗑️ Eliminar"
    ])
    
    # ================================================================
    # TAB 1: CREAR SALÓN
    # ================================================================
    with tabs[0]:
        st.subheader("➕ Registrar Nuevo Salón")
        
        # Obtener centros
        with Session(db_engine) as session:
            centros = session.exec(select(CentroCatecismo)).all()
        
        if not centros:
            st.warning("⚠️ No hay centros de catecismo registrados. Crea uno primero.")
            return
        
        with st.form("form_crear_salon", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                opciones_centros = {c.id_centro: f"{c.nombre_centro} ({c.clave_centro})" for c in centros}
                id_centro_sel = st.selectbox(
                    "Centro de Catecismo (*)",
                    options=opciones_centros.keys(),
                    format_func=lambda x: opciones_centros[x],
                    key="salon_centro"
                )
                
                nombre_salon = st.text_input(
                    "Nombre del Salón (*)",
                    max_chars=100,
                    placeholder="Ej: Salón San Pablo",
                    key="salon_nombre"
                )
            
            with col2:
                capacidad = st.number_input(
                    "Capacidad",
                    min_value=1,
                    max_value=500,
                    value=30,
                    key="salon_capacidad"
                )
                
                activo = st.checkbox("Salón Activo", value=True, key="salon_activo")
            
            descripcion = st.text_area(
                "Descripción",
                placeholder="Características del salón, ubicación específica, equipamiento...",
                key="salon_descripcion"
            )
            
            submitted = st.form_submit_button("💾 Crear Salón", type="primary", width="stretch")
            
            if submitted:
                if not nombre_salon:
                    st.error("❌ El nombre del salón es obligatorio")
                else:
                    # Verificar si ya existe en ese centro
                    with Session(db_engine) as session:
                        existe = session.exec(
                            select(Salon).where(
                                Salon.id_centro == id_centro_sel,
                                Salon.nombre_salon == nombre_salon.strip()
                            )
                        ).first()
                    
                    if existe:
                        st.error(f"❌ Ya existe un salón con el nombre '{nombre_salon}' en este centro")
                    else:
                        nuevo_salon = Salon(
                            id_centro=id_centro_sel,
                            nombre_salon=nombre_salon.strip(),
                            capacidad=capacidad,
                            descripcion=descripcion.strip() if descripcion else None,
                            activo=activo
                        )
                        
                        if db_module.crear_registro(nuevo_salon, db_engine, st_display_func, nombre_tabla="Salón"):
                            st.success("✅ Salón registrado exitosamente")
                            st.rerun()
    
    # ================================================================
    # TAB 2: VER SALONES
    # ================================================================
    with tabs[1]:
        st.subheader("📋 Lista de Salones Registrados")
        
        # Filtros
        col1, col2 = st.columns(2)
        
        with col1:
            with Session(db_engine) as session:
                centros = session.exec(select(CentroCatecismo)).all()
            
            opciones_filtro = {0: "Todos los Centros"}
            opciones_filtro.update({c.id_centro: f"{c.nombre_centro}" for c in centros})
            
            filtro_centro = st.selectbox(
                "Filtrar por Centro:",
                options=opciones_filtro.keys(),
                format_func=lambda x: opciones_filtro[x],
                key="filtro_centro_salon"
            )
        
        with col2:
            filtro_estado = st.selectbox(
                "Filtrar por Estado:",
                options=["Todos", "Activos", "Inactivos"],
                key="filtro_estado_salon"
            )
        
        # Consultar salones
        with Session(db_engine) as session:
            statement = select(Salon)
            
            if filtro_centro != 0:
                statement = statement.where(Salon.id_centro == filtro_centro)
            
            if filtro_estado == "Activos":
                statement = statement.where(Salon.activo == True)
            elif filtro_estado == "Inactivos":
                statement = statement.where(Salon.activo == False)
            
            salones = session.exec(statement).all()
        
        if salones:
            st.markdown(f"**Total de Salones:** {len(salones)}")
            
            # Agrupar por centro
            salones_por_centro = {}
            with Session(db_engine) as session:
                for salon in salones:
                    centro = session.get(CentroCatecismo, salon.id_centro)
                    centro_nombre = centro.nombre_centro if centro else "Sin Centro"
                    
                    if centro_nombre not in salones_por_centro:
                        salones_por_centro[centro_nombre] = []
                    salones_por_centro[centro_nombre].append(salon)
            
            # Mostrar por centro
            for centro_nombre, lista_salones in salones_por_centro.items():
                with st.expander(f"🏫 {centro_nombre} - {len(lista_salones)} salones"):
                    for salon in lista_salones:
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            estado_icon = "✅" if salon.activo else "❌"
                            st.markdown(f"{estado_icon} **{salon.nombre_salon}**")
                            if salon.descripcion:
                                st.caption(salon.descripcion)
                        
                        with col2:
                            st.metric("Capacidad", salon.capacidad or "N/A")
                        
                        with col3:
                            st.caption(f"ID: {salon.id_salon}")
        else:
            st.info("ℹ️ No hay salones registrados con los filtros seleccionados")
    
    # ================================================================
    # TAB 3: CALENDARIO DE USO
    # ================================================================
    with tabs[2]:
        st.subheader("🗓️ Calendario de Uso de Salones")
        
        # Selector de fecha
        fecha_consulta = st.date_input(
            "Fecha a consultar:",
            value=date.today(),
            key="fecha_calendario_salones"
        )
        
        dia_semana = obtener_dia_semana(fecha_consulta)
        
        st.info(f"📅 Mostrando ocupación para {dia_semana} {fecha_consulta.strftime('%d/%m/%Y')}")
        
        # Obtener todos los salones
        with Session(db_engine) as session:
            salones = session.exec(select(Salon).where(Salon.activo == True)).all()
            
            if not salones:
                st.warning("⚠️ No hay salones activos registrados")
                return
            
            for salon in salones:
                centro = session.get(CentroCatecismo, salon.id_centro)
                
                st.markdown(f"### 🏛️ {salon.nombre_salon} - {centro.nombre_centro if centro else 'N/A'}")
                
                # Obtener horarios regulares para este día
                horarios_regulares = session.exec(
                    select(Horario).where(
                        Horario.id_salon == salon.id_salon,
                        Horario.dia_semana == dia_semana,
                        Horario.activo == True
                    )
                ).all()
                
                # Obtener reservaciones para esta fecha
                reservaciones = session.exec(
                    select(ReservacionSalon).where(
                        ReservacionSalon.id_salon == salon.id_salon,
                        ReservacionSalon.fecha_reservacion == fecha_consulta,
                        ReservacionSalon.estado == "Aprobada"
                    )
                ).all()
                
                if not horarios_regulares and not reservaciones:
                    st.success("✅ Salón disponible todo el día")
                else:
                    # Mostrar horarios
                    st.markdown("**Ocupación:**")
                    
                    # Horarios regulares
                    for horario in horarios_regulares:
                        actividad = session.get(Actividad, horario.id_actividad)
                        col1, col2, col3 = st.columns([2, 2, 1])
                        
                        with col1:
                            st.markdown(f"🔵 {horario.hora_inicio.strftime('%H:%M')} - {horario.hora_fin.strftime('%H:%M')}")
                        with col2:
                            st.markdown(f"**{actividad.nombre_actividad if actividad else 'N/A'}**")
                        with col3:
                            st.caption("Regular")
                    
                    # Reservaciones
                    for reserva in reservaciones:
                        solicitante = session.get(Persona, reserva.id_solicitante)
                        col1, col2, col3 = st.columns([2, 2, 1])
                        
                        with col1:
                            st.markdown(f"🟡 {reserva.hora_inicio.strftime('%H:%M')} - {reserva.hora_fin.strftime('%H:%M')}")
                        with col2:
                            st.markdown(f"**{reserva.motivo}**")
                            st.caption(f"Solicitado por: {solicitante.nombre_completo() if solicitante else 'N/A'}")
                        with col3:
                            st.caption("Reserva")
                
                st.markdown("---")
    
    # ================================================================
    # TAB 4: RESERVACIONES
    # ================================================================
    with tabs[3]:
        st.subheader("📝 Sistema de Reservaciones")
        
        subtabs = st.tabs(["Nueva Reservación", "Ver Reservaciones", "Aprobar/Rechazar"])
        
        # NUEVA RESERVACIÓN
        with subtabs[0]:
            st.markdown("### ➕ Nueva Reservación")
            
            with st.form("form_nueva_reservacion", clear_on_submit=True):
                # Selección de salón
                with Session(db_engine) as session:
                    salones = session.exec(select(Salon).where(Salon.activo == True)).all()
                
                opciones_salones = {}
                for s in salones:
                    centro = session.get(CentroCatecismo, s.id_centro)
                    opciones_salones[s.id_salon] = f"{s.nombre_salon} - {centro.nombre_centro if centro else 'N/A'}"
                
                id_salon_reserva = st.selectbox(
                    "Salón a reservar (*)",
                    options=opciones_salones.keys(),
                    format_func=lambda x: opciones_salones[x],
                    key="reserva_salon"
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fecha_reserva = st.date_input(
                        "Fecha (*)",
                        min_value=date.today(),
                        key="reserva_fecha"
                    )
                    
                    hora_inicio_reserva = st.time_input(
                        "Hora de Inicio (*)",
                        value=time(9, 0),
                        key="reserva_hora_inicio"
                    )
                
                with col2:
                    # Solicitante
                    personas = obtener_lista_personas(db_engine)
                    opciones_personas = {p.id_persona: p.nombre_completo() for p in personas}
                    
                    id_solicitante = st.selectbox(
                        "Solicitante (*)",
                        options=opciones_personas.keys(),
                        format_func=lambda x: opciones_personas[x],
                        key="reserva_solicitante"
                    )
                    
                    hora_fin_reserva = st.time_input(
                        "Hora de Fin (*)",
                        value=time(11, 0),
                        key="reserva_hora_fin"
                    )
                
                motivo_reserva = st.text_input(
                    "Motivo (*)",
                    max_chars=255,
                    placeholder="Ej: Reunión de padres de familia",
                    key="reserva_motivo"
                )
                
                observaciones_reserva = st.text_area(
                    "Observaciones",
                    key="reserva_observaciones"
                )
                
                submitted_reserva = st.form_submit_button("📝 Solicitar Reservación", type="primary", width="stretch")
                
                if submitted_reserva:
                    if not motivo_reserva:
                        st.error("❌ El motivo es obligatorio")
                    elif hora_fin_reserva <= hora_inicio_reserva:
                        st.error("❌ La hora de fin debe ser posterior a la hora de inicio")
                    else:
                        # Validar conflictos
                        conflicto = verificar_conflicto_salon(
                            db_engine,
                            id_salon_reserva,
                            fecha_reserva,
                            hora_inicio_reserva,
                            hora_fin_reserva
                        )
                        
                        if conflicto:
                            st.error(f"❌ Conflicto: {conflicto}")
                        else:
                            nueva_reservacion = ReservacionSalon(
                                id_salon=id_salon_reserva,
                                fecha_reservacion=fecha_reserva,
                                hora_inicio=hora_inicio_reserva,
                                hora_fin=hora_fin_reserva,
                                id_solicitante=id_solicitante,
                                motivo=motivo_reserva.strip(),
                                estado="Pendiente",
                                observaciones=observaciones_reserva.strip() if observaciones_reserva else None
                            )
                            
                            if db_module.crear_registro(nueva_reservacion, db_engine, st_display_func, nombre_tabla="Reservación"):
                                st.success("✅ Reservación solicitada. Pendiente de aprobación.")
                                st.rerun()
        
        # VER RESERVACIONES
        with subtabs[1]:
            st.markdown("### 📋 Lista de Reservaciones")
            
            with Session(db_engine) as session:
                reservaciones = session.exec(
                    select(ReservacionSalon).order_by(ReservacionSalon.fecha_reservacion.desc())
                ).all()
            
            if reservaciones:
                for reserva in reservaciones:
                    with Session(db_engine) as session:
                        salon = session.get(Salon, reserva.id_salon)
                        solicitante = session.get(Persona, reserva.id_solicitante)
                    
                    # Color según estado
                    if reserva.estado == "Aprobada":
                        color = "🟢"
                    elif reserva.estado == "Pendiente":
                        color = "🟡"
                    elif reserva.estado == "Rechazada":
                        color = "🔴"
                    else:
                        color = "⚪"
                    
                    with st.expander(f"{color} {reserva.motivo} - {reserva.fecha_reservacion.strftime('%d/%m/%Y')}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**Salón:** {salon.nombre_salon if salon else 'N/A'}")
                            st.markdown(f"**Horario:** {reserva.hora_inicio.strftime('%H:%M')} - {reserva.hora_fin.strftime('%H:%M')}")
                            st.markdown(f"**Estado:** {reserva.estado}")
                        
                        with col2:
                            st.markdown(f"**Solicitante:** {solicitante.nombre_completo() if solicitante else 'N/A'}")
                            st.markdown(f"**Fecha Solicitud:** {reserva.fecha_solicitud.strftime('%d/%m/%Y %H:%M')}")
                            if reserva.observaciones:
                                st.caption(f"Observaciones: {reserva.observaciones}")
            else:
                st.info("ℹ️ No hay reservaciones registradas")
        
        # APROBAR/RECHAZAR
        with subtabs[2]:
            st.markdown("### ✅ Gestionar Reservaciones Pendientes")
            
            with Session(db_engine) as session:
                pendientes = session.exec(
                    select(ReservacionSalon).where(ReservacionSalon.estado == "Pendiente")
                ).all()
            
            if pendientes:
                for reserva in pendientes:
                    with Session(db_engine) as session:
                        salon = session.get(Salon, reserva.id_salon)
                        solicitante = session.get(Persona, reserva.id_solicitante)
                    
                    st.markdown(f"### 📝 {reserva.motivo}")
                    st.markdown(f"**Salón:** {salon.nombre_salon if salon else 'N/A'}")
                    st.markdown(f"**Fecha:** {reserva.fecha_reservacion.strftime('%d/%m/%Y')}")
                    st.markdown(f"**Horario:** {reserva.hora_inicio.strftime('%H:%M')} - {reserva.hora_fin.strftime('%H:%M')}")
                    st.markdown(f"**Solicitante:** {solicitante.nombre_completo() if solicitante else 'N/A'}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button(f"✅ Aprobar", key=f"aprobar_{reserva.id_reservacion}", width="stretch"):
                            if db_module.actualizar_registro(
                                ReservacionSalon,
                                reserva.id_reservacion,
                                {"estado": "Aprobada"},
                                db_engine,
                                st_display_func,
                                nombre_tabla="Reservación"
                            ):
                                st.success("✅ Reservación aprobada")
                                st.rerun()
                    
                    with col2:
                        if st.button(f"❌ Rechazar", key=f"rechazar_{reserva.id_reservacion}", width="stretch"):
                            if db_module.actualizar_registro(
                                ReservacionSalon,
                                reserva.id_reservacion,
                                {"estado": "Rechazada"},
                                db_engine,
                                st_display_func,
                                nombre_tabla="Reservación"
                            ):
                                st.warning("⚠️ Reservación rechazada")
                                st.rerun()
                    
                    st.markdown("---")
            else:
                st.success("✅ No hay reservaciones pendientes")
    
    # TAB 5 y 6: Actualizar y Eliminar (simplificados)
    with tabs[4]:
        st.info("💡 Funcionalidad de actualización disponible para implementar")
    
    with tabs[5]:
        st.info("💡 Funcionalidad de eliminación disponible para implementar")


# ====================================================================
# FUNCIONES AUXILIARES
# ====================================================================

def obtener_lista_personas(engine):
    """Obtiene lista de personas"""
    if not engine:
        return []
    try:
        with Session(engine) as session:
            from models import Persona
            return session.exec(select(Persona)).all()
    except:
        return []

def obtener_dia_semana(fecha: date) -> str:
    """Convierte fecha a día de la semana en español"""
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    return dias[fecha.weekday()]

def verificar_conflicto_salon(engine, id_salon, fecha, hora_inicio, hora_fin) -> str:
    """
    Verifica si hay conflictos de horario para un salón.
    Retorna mensaje de error si hay conflicto, None si está libre.
    """
    dia_semana = obtener_dia_semana(fecha)
    
    with Session(engine) as session:
        # Verificar horarios regulares
        horarios = session.exec(
            select(Horario).where(
                Horario.id_salon == id_salon,
                Horario.dia_semana == dia_semana,
                Horario.activo == True
            )
        ).all()
        
        for horario in horarios:
            if hay_traslape_horario(hora_inicio, hora_fin, horario.hora_inicio, horario.hora_fin):
                actividad = session.get(Actividad, horario.id_actividad)
                return f"Conflicto con actividad '{actividad.nombre_actividad if actividad else 'N/A'}' ({horario.hora_inicio.strftime('%H:%M')}-{horario.hora_fin.strftime('%H:%M')})"
        
        # Verificar reservaciones aprobadas
        reservaciones = session.exec(
            select(ReservacionSalon).where(
                ReservacionSalon.id_salon == id_salon,
                ReservacionSalon.fecha_reservacion == fecha,
                ReservacionSalon.estado == "Aprobada"
            )
        ).all()
        
        for reserva in reservaciones:
            if hay_traslape_horario(hora_inicio, hora_fin, reserva.hora_inicio, reserva.hora_fin):
                return f"Conflicto con reservación '{reserva.motivo}' ({reserva.hora_inicio.strftime('%H:%M')}-{reserva.hora_fin.strftime('%H:%M')})"
    
    return None

def hay_traslape_horario(inicio1, fin1, inicio2, fin2) -> bool:
    """Verifica si dos rangos de horario se traslapan"""
    return not (fin1 <= inicio2 or inicio1 >= fin2)