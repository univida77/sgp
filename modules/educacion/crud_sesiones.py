# crud_sesiones.py
import streamlit as st
from datetime import date, time
from models import Sesion, Actividad, Tema, Horario, Salon, Persona
from sqlmodel import Session, select

def mostrar_crud_sesiones(db_engine, db_module, db_mode, st_display_func):
    """Módulo completo CRUD para Sesiones"""
    st.header(f"📅 Gestión de Sesiones - Modo: {db_mode}")
    
    st.info("💡 Administra las clases/reuniones específicas de cada actividad")
    
    tabs = st.tabs([
        "📋 Ver Sesiones",
        "✏️ Modificar Sesión",
        "⚠️ Crear Excepción",
        "✅ Marcar Realizada",
        "📊 Calendario"
    ])
    
    # ================================================================
    # TAB 1: VER SESIONES
    # ================================================================
    with tabs[0]:
        st.subheader("📋 Lista de Sesiones")
        
        # Filtros
        col1, col2 = st.columns(2)
        
        with col1:
            with Session(db_engine) as session:
                actividades = session.exec(select(Actividad).where(Actividad.activo == True)).all()
            
            if not actividades:
                st.warning("⚠️ No hay actividades activas")
                return
            
            opciones_act = {0: "Todas las Actividades"}
            opciones_act.update({a.id_actividad: a.nombre_actividad for a in actividades})
            
            filtro_actividad = st.selectbox(
                "Filtrar por Actividad:",
                options=opciones_act.keys(),
                format_func=lambda x: opciones_act[x],
                key="filtro_act_sesion"
            )
        
        with col2:
            filtro_estado = st.selectbox(
                "Filtrar por Estado:",
                options=["Todas", "Programada", "Realizada", "Cancelada", "Reprogramada"],
                key="filtro_estado_sesion"
            )
        
        # Filtro por rango de fechas
        col1, col2 = st.columns(2)
        with col1:
            fecha_desde = st.date_input("Desde:", value=date.today(), key="sesion_desde")
        with col2:
            fecha_hasta = st.date_input("Hasta:", value=None, key="sesion_hasta")
        
        # Consultar sesiones
        with Session(db_engine) as session:
            statement = select(Sesion).order_by(Sesion.fecha_sesion)
            
            if filtro_actividad != 0:
                statement = statement.where(Sesion.id_actividad == filtro_actividad)
            
            if filtro_estado != "Todas":
                statement = statement.where(Sesion.estado == filtro_estado)
            
            statement = statement.where(Sesion.fecha_sesion >= fecha_desde)
            
            if fecha_hasta:
                statement = statement.where(Sesion.fecha_sesion <= fecha_hasta)
            
            sesiones = session.exec(statement).all()
        
        if sesiones:
            st.markdown(f"**Total de Sesiones:** {len(sesiones)}")
            
            # Agrupar por actividad
            sesiones_por_actividad = {}
            with Session(db_engine) as session:
                for sesion in sesiones:
                    actividad = session.get(Actividad, sesion.id_actividad)
                    act_nombre = actividad.nombre_actividad if actividad else "Sin actividad"
                    
                    if act_nombre not in sesiones_por_actividad:
                        sesiones_por_actividad[act_nombre] = []
                    sesiones_por_actividad[act_nombre].append(sesion)
            
            # Mostrar por actividad
            for act_nombre, lista_sesiones in sesiones_por_actividad.items():
                with st.expander(f"📚 {act_nombre} - {len(lista_sesiones)} sesiones"):
                    for sesion in lista_sesiones:
                        with Session(db_engine) as session:
                            tema = session.get(Tema, sesion.id_tema) if sesion.id_tema else None
                            horario = session.get(Horario, sesion.id_horario) if sesion.id_horario else None
                            salon = session.get(Salon, horario.id_salon) if horario else None
                            salon_exc = session.get(Salon, sesion.id_salon_excepcion) if sesion.id_salon_excepcion else None
                            responsable = session.get(Persona, sesion.id_responsable) if sesion.id_responsable else None
                        
                        # Icono según estado
                        if sesion.estado == "Programada":
                            icono = "📅"
                        elif sesion.estado == "Realizada":
                            icono = "✅"
                        elif sesion.estado == "Cancelada":
                            icono = "❌"
                        else:
                            icono = "🔄"
                        
                        col1, col2, col3 = st.columns([2, 2, 1])
                        
                        with col1:
                            st.markdown(f"{icono} **Sesión {sesion.numero_sesion}: {sesion.nombre_sesion}**")
                            st.caption(f"📅 {sesion.fecha_sesion.strftime('%d/%m/%Y')} - {obtener_dia_semana_str(sesion.fecha_sesion)}")
                        
                        with col2:
                            # Mostrar horario
                            if sesion.hora_inicio_excepcion:
                                st.markdown(f"⚠️ **Horario Especial:** {sesion.hora_inicio_excepcion.strftime('%H:%M')} - {sesion.hora_fin_excepcion.strftime('%H:%M')}")
                            elif horario:
                                st.markdown(f"⏰ {horario.hora_inicio.strftime('%H:%M')} - {horario.hora_fin.strftime('%H:%M')}")
                            
                            # Mostrar salón
                            if salon_exc:
                                st.markdown(f"⚠️ **Salón Especial:** {salon_exc.nombre_salon}")
                            elif salon:
                                st.markdown(f"🏫 {salon.nombre_salon}")
                        
                        with col3:
                            st.caption(f"Estado: {sesion.estado}")
                            if responsable:
                                st.caption(f"👤 {responsable.nombre_completo()}")
                        
                        if sesion.motivo_excepcion:
                            st.info(f"💡 Excepción: {sesion.motivo_excepcion}")
                        
                        if sesion.observaciones:
                            st.caption(f"📝 {sesion.observaciones}")
                        
                        st.markdown("---")
        else:
            st.info("ℹ️ No hay sesiones con los filtros seleccionados")
    
    # ================================================================
    # TAB 2: MODIFICAR SESIÓN
    # ================================================================
    with tabs[1]:
        st.subheader("✏️ Modificar Sesión Existente")
        
        # Seleccionar sesión
        with Session(db_engine) as session:
            sesiones = session.exec(
                select(Sesion).where(Sesion.estado == "Programada").order_by(Sesion.fecha_sesion)
            ).all()
        
        if not sesiones:
            st.info("ℹ️ No hay sesiones programadas para modificar")
            return
        
        opciones_sesiones = {}
        with Session(db_engine) as session:
            for s in sesiones:
                actividad = session.get(Actividad, s.id_actividad)
                opciones_sesiones[s.id_sesion] = f"Sesión {s.numero_sesion}: {s.nombre_sesion} - {s.fecha_sesion.strftime('%d/%m/%Y')} ({actividad.nombre_actividad if actividad else 'N/A'})"
        
        id_sesion_mod = st.selectbox(
            "Selecciona la Sesión:",
            options=opciones_sesiones.keys(),
            format_func=lambda x: opciones_sesiones[x],
            key="mod_sesion_select"
        )
        
        sesion_modificar = next((s for s in sesiones if s.id_sesion == id_sesion_mod), None)
        
        if sesion_modificar:
            st.markdown("---")
            
            with st.form("form_modificar_sesion"):
                st.markdown("### 📝 Datos Básicos")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    mod_nombre = st.text_input(
                        "Nombre de la Sesión",
                        value=sesion_modificar.nombre_sesion,
                        key="mod_nombre_sesion"
                    )
                    
                    mod_fecha = st.date_input(
                        "Fecha",
                        value=sesion_modificar.fecha_sesion,
                        key="mod_fecha_sesion"
                    )
                
                with col2:
                    mod_estado = st.selectbox(
                        "Estado",
                        options=["Programada", "Realizada", "Cancelada", "Reprogramada"],
                        index=["Programada", "Realizada", "Cancelada", "Reprogramada"].index(sesion_modificar.estado),
                        key="mod_estado_sesion"
                    )
                    
                    # Responsable
                    with Session(db_engine) as session:
                        personas = session.exec(select(Persona)).all()
                    
                    opciones_personas = {0: "-- Sin Responsable --"}
                    opciones_personas.update({p.id_persona: p.nombre_completo() for p in personas})
                    
                    indice_resp = 0
                    if sesion_modificar.id_responsable and sesion_modificar.id_responsable in opciones_personas:
                        indice_resp = list(opciones_personas.keys()).index(sesion_modificar.id_responsable)
                    
                    mod_responsable = st.selectbox(
                        "Responsable",
                        options=list(opciones_personas.keys()),
                        format_func=lambda x: opciones_personas[x],
                        index=indice_resp,
                        key="mod_responsable_sesion"
                    )
                
                mod_observaciones = st.text_area(
                    "Observaciones",
                    value=sesion_modificar.observaciones or "",
                    key="mod_observaciones_sesion"
                )
                
                submitted_mod = st.form_submit_button("💾 Actualizar Sesión", type="primary", width="stretch")
                
                if submitted_mod:
                    data_actualizar = {
                        "nombre_sesion": mod_nombre.strip(),
                        "fecha_sesion": mod_fecha,
                        "estado": mod_estado,
                        "id_responsable": mod_responsable if mod_responsable != 0 else None,
                        "observaciones": mod_observaciones.strip() if mod_observaciones else None
                    }
                    
                    if db_module.actualizar_registro(
                        Sesion,
                        sesion_modificar.id_sesion,
                        data_actualizar,
                        db_engine,
                        st_display_func,
                        nombre_tabla="Sesión"
                    ):
                        st.success("✅ Sesión actualizada exitosamente")
                        st.rerun()
    
    # ================================================================
    # TAB 3: CREAR EXCEPCIÓN
    # ================================================================
    with tabs[2]:
        st.subheader("⚠️ Crear Excepción de Horario/Salón")
        
        st.info("💡 Usa esto cuando una sesión necesite cambiar su horario o salón puntualmente")
        
        # Seleccionar sesión
        with Session(db_engine) as session:
            sesiones = session.exec(
                select(Sesion).where(Sesion.estado == "Programada").order_by(Sesion.fecha_sesion)
            ).all()
        
        if not sesiones:
            st.info("ℹ️ No hay sesiones programadas")
            return
        
        opciones_sesiones = {}
        with Session(db_engine) as session:
            for s in sesiones:
                actividad = session.get(Actividad, s.id_actividad)
                opciones_sesiones[s.id_sesion] = f"{s.nombre_sesion} - {s.fecha_sesion.strftime('%d/%m/%Y')} ({actividad.nombre_actividad if actividad else 'N/A'})"
        
        id_sesion_exc = st.selectbox(
            "Selecciona la Sesión:",
            options=opciones_sesiones.keys(),
            format_func=lambda x: opciones_sesiones[x],
            key="exc_sesion_select"
        )
        
        sesion_excepcion = next((s for s in sesiones if s.id_sesion == id_sesion_exc), None)
        
        if sesion_excepcion:
            st.markdown("---")
            
            with st.form("form_crear_excepcion"):
                st.markdown("### ⚠️ Datos de Excepción")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    cambiar_horario = st.checkbox("Cambiar Horario", key="exc_cambiar_horario")
                    
                    if cambiar_horario:
                        hora_inicio_exc = st.time_input(
                            "Nueva Hora de Inicio",
                            value=time(10, 0),
                            key="exc_hora_inicio"
                        )
                        
                        hora_fin_exc = st.time_input(
                            "Nueva Hora de Fin",
                            value=time(12, 0),
                            key="exc_hora_fin"
                        )
                    else:
                        hora_inicio_exc = None
                        hora_fin_exc = None
                
                with col2:
                    cambiar_salon = st.checkbox("Cambiar Salón", key="exc_cambiar_salon")
                    
                    if cambiar_salon:
                        with Session(db_engine) as session:
                            actividad = session.get(Actividad, sesion_excepcion.id_actividad)
                            
                            if actividad and actividad.id_centro:
                                salones = session.exec(
                                    select(Salon).where(
                                        Salon.id_centro == actividad.id_centro,
                                        Salon.activo == True
                                    )
                                ).all()
                                
                                opciones_salones = {s.id_salon: s.nombre_salon for s in salones}
                                id_salon_exc = st.selectbox(
                                    "Nuevo Salón",
                                    options=opciones_salones.keys(),
                                    format_func=lambda x: opciones_salones[x],
                                    key="exc_salon"
                                )
                            else:
                                st.warning("⚠️ Actividad sin centro asignado")
                                id_salon_exc = None
                    else:
                        id_salon_exc = None
                
                motivo_excepcion = st.text_input(
                    "Motivo de la Excepción (*)",
                    placeholder="Ej: Celebración especial, evento parroquial...",
                    key="exc_motivo"
                )
                
                submitted_exc = st.form_submit_button("⚠️ Aplicar Excepción", type="primary", width="stretch")
                
                if submitted_exc:
                    if not motivo_excepcion:
                        st.error("❌ El motivo de la excepción es obligatorio")
                    elif cambiar_horario and hora_fin_exc <= hora_inicio_exc:
                        st.error("❌ La hora de fin debe ser posterior a la hora de inicio")
                    else:
                        data_excepcion = {
                            "hora_inicio_excepcion": hora_inicio_exc if cambiar_horario else None,
                            "hora_fin_excepcion": hora_fin_exc if cambiar_horario else None,
                            "id_salon_excepcion": id_salon_exc if cambiar_salon else None,
                            "motivo_excepcion": motivo_excepcion.strip(),
                            "estado": "Reprogramada"
                        }
                        
                        if db_module.actualizar_registro(
                            Sesion,
                            sesion_excepcion.id_sesion,
                            data_excepcion,
                            db_engine,
                            st_display_func,
                            nombre_tabla="Sesión"
                        ):
                            st.success("✅ Excepción aplicada exitosamente")
                            st.rerun()
    
    # ================================================================
    # TAB 4: MARCAR REALIZADA
    # ================================================================
    with tabs[3]:
        st.subheader("✅ Marcar Sesiones como Realizadas")
        
        # Mostrar sesiones de hoy o pasadas que están programadas
        with Session(db_engine) as session:
            sesiones_pendientes = session.exec(
                select(Sesion).where(
                    Sesion.fecha_sesion <= date.today(),
                    Sesion.estado == "Programada"
                ).order_by(Sesion.fecha_sesion.desc())
            ).all()
        
        if not sesiones_pendientes:
            st.success("✅ No hay sesiones pendientes de marcar como realizadas")
            return
        
        st.markdown(f"**Sesiones Pendientes:** {len(sesiones_pendientes)}")
        
        for sesion in sesiones_pendientes:
            with Session(db_engine) as session:
                actividad = session.get(Actividad, sesion.id_actividad)
            
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.markdown(f"**{sesion.nombre_sesion}**")
                st.caption(f"{actividad.nombre_actividad if actividad else 'N/A'}")
            
            with col2:
                st.markdown(f"📅 {sesion.fecha_sesion.strftime('%d/%m/%Y')}")
            
            with col3:
                if st.button("✅ Realizada", key=f"realizada_{sesion.id_sesion}", width="stretch"):
                    if db_module.actualizar_registro(
                        Sesion,
                        sesion.id_sesion,
                        {"estado": "Realizada"},
                        db_engine,
                        st_display_func,
                        nombre_tabla="Sesión"
                    ):
                        st.success("✅ Sesión marcada como realizada")
                        st.rerun()
            
            st.markdown("---")
    
    # ================================================================
    # TAB 5: CALENDARIO
    # ================================================================
    with tabs[4]:
        st.subheader("📊 Calendario de Sesiones")
        
        # Selector de mes
        col1, col2 = st.columns(2)
        
        with col1:
            mes_seleccionado = st.selectbox(
                "Mes:",
                options=range(1, 13),
                format_func=lambda x: [
                    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
                ][x-1],
                index=date.today().month - 1,
                key="cal_mes"
            )
        
        with col2:
            año_seleccionado = st.number_input(
                "Año:",
                min_value=2020,
                max_value=2030,
                value=date.today().year,
                key="cal_año"
            )
        
        # Calcular primer y último día del mes
        from datetime import datetime
        primer_dia = datetime(año_seleccionado, mes_seleccionado, 1).date()
        
        if mes_seleccionado == 12:
            ultimo_dia = datetime(año_seleccionado + 1, 1, 1).date()
        else:
            ultimo_dia = datetime(año_seleccionado, mes_seleccionado + 1, 1).date()
        
        # Consultar sesiones del mes
        with Session(db_engine) as session:
            sesiones_mes = session.exec(
                select(Sesion).where(
                    Sesion.fecha_sesion >= primer_dia,
                    Sesion.fecha_sesion < ultimo_dia
                ).order_by(Sesion.fecha_sesion)
            ).all()
        
        if sesiones_mes:
            st.markdown(f"**Sesiones en este mes:** {len(sesiones_mes)}")
            
            # Agrupar por día
            sesiones_por_dia = {}
            for sesion in sesiones_mes:
                dia = sesion.fecha_sesion.day
                if dia not in sesiones_por_dia:
                    sesiones_por_dia[dia] = []
                sesiones_por_dia[dia].append(sesion)
            
            # Mostrar calendario simple
            st.markdown("---")
            for dia in range(1, 32):
                try:
                    fecha_dia = datetime(año_seleccionado, mes_seleccionado, dia).date()
                except ValueError:
                    break
                
                if dia in sesiones_por_dia:
                    with st.expander(f"📅 {fecha_dia.strftime('%d/%m/%Y')} - {obtener_dia_semana_str(fecha_dia)} ({len(sesiones_por_dia[dia])} sesiones)"):
                        for sesion in sesiones_por_dia[dia]:
                            with Session(db_engine) as session:
                                actividad = session.get(Actividad, sesion.id_actividad)
                            
                            icono = "✅" if sesion.estado == "Realizada" else "📅"
                            st.markdown(f"{icono} **{sesion.nombre_sesion}** - {actividad.nombre_actividad if actividad else 'N/A'}")
        else:
            st.info("ℹ️ No hay sesiones programadas en este mes")


# ====================================================================
# FUNCIONES AUXILIARES
# ====================================================================

def obtener_dia_semana_str(fecha: date) -> str:
    """Convierte fecha a día de la semana en español"""
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    return dias[fecha.weekday()]