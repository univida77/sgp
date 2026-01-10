# crud_actas.py - Módulo CRUD de Archivo de Actas
import streamlit as st
from datetime import date, datetime, time
from models import (
    ActaReunion, AsistenteActa, HistorialActa, TipoReunion, AreaParroquial
)
from models import GrupoParroquial, Persona, Usuario
from sqlmodel import Session, select
from typing import Optional

# ====================================================================
# FUNCIÓN PRINCIPAL
# ====================================================================

def mostrar_crud_actas(db_engine, db_module, db_mode, st_display_func, usuario_actual=None):
    """Módulo completo CRUD para Archivo de Actas"""
    st.header(f"📄 Archivo Digital de Actas - Modo: {db_mode}")
    
    st.info("💡 Preservación de la memoria histórica, pastoral y administrativa de la parroquia")
    
    tabs = st.tabs([
        "📝 Registrar Acta",
        "📋 Ver Actas",
        "✅ Aprobar",
        "🔍 Búsqueda",
        "📊 Estadísticas"
    ])
    
    # ================================================================
    # TAB 1: REGISTRAR ACTA
    # ================================================================
    with tabs[0]:
        registrar_acta(db_engine, db_module, st_display_func, usuario_actual)
    
    # ================================================================
    # TAB 2: VER ACTAS
    # ================================================================
    with tabs[1]:
        ver_actas(db_engine, usuario_actual)
    
    # ================================================================
    # TAB 3: APROBAR
    # ================================================================
    with tabs[2]:
        aprobar_actas(db_engine, db_module, st_display_func, usuario_actual)
    
    # ================================================================
    # TAB 4: BÚSQUEDA
    # ================================================================
    with tabs[3]:
        buscar_actas(db_engine, usuario_actual)
    
    # ================================================================
    # TAB 5: ESTADÍSTICAS
    # ================================================================
    with tabs[4]:
        estadisticas_actas(db_engine)


# ====================================================================
# REGISTRAR ACTA
# ====================================================================

def registrar_acta(db_engine, db_module, st_display_func, usuario_actual):
    st.subheader("📝 Registrar Nueva Acta")
    
    with st.form("form_acta", clear_on_submit=False):
        st.markdown("### 📋 Datos Generales del Acta")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Tipo de reunión
            with Session(db_engine) as session:
                tipos = session.exec(
                    select(TipoReunion).where(TipoReunion.activo == True)
                ).all()
            
            if not tipos:
                st.error("❌ No hay tipos de reunión registrados")
                st.info("💡 Crea primero los tipos: Ordinaria, Mensual, Extraordinaria")
                st.form_submit_button("Guardar", disabled=True)
                return
            
            opciones_tipos = {t.id_tipo_reunion: t.nombre_tipo for t in tipos}
            id_tipo_reunion = st.selectbox(
                "Tipo de Reunión (*)",
                options=opciones_tipos.keys(),
                format_func=lambda x: opciones_tipos[x],
                key="acta_tipo"
            )
        
        with col2:
            fecha_reunion = st.date_input(
                "Fecha de la Reunión (*)",
                value=date.today(),
                max_value=date.today(),
                key="acta_fecha"
            )
        
        with col3:
            lugar_reunion = st.text_input(
                "Lugar (*)",
                max_chars=300,
                placeholder="Ej: Salón parroquial",
                key="acta_lugar"
            )
        
        col1, col2 = st.columns(2)
        
        with col1:
            hora_inicio = st.time_input(
                "Hora de Inicio",
                value=time(19, 0),
                key="acta_hora_inicio"
            )
        
        with col2:
            hora_cierre = st.time_input(
                "Hora de Cierre",
                value=time(21, 0),
                key="acta_hora_cierre"
            )
        
        st.markdown("---")
        st.markdown("### 🏢 Grupo y Área")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Grupo parroquial
            with Session(db_engine) as session:
                grupos = session.exec(
                    select(GrupoParroquial).where(GrupoParroquial.activo == True)
                ).all()
            
            if not grupos:
                st.error("❌ No hay grupos parroquiales registrados")
                id_grupo = None
            else:
                opciones_grupos = {g.id_grupo: g.nombre_grupo for g in grupos}
                id_grupo = st.selectbox(
                    "Grupo que Sesiona (*)",
                    options=opciones_grupos.keys(),
                    format_func=lambda x: opciones_grupos[x],
                    key="acta_grupo"
                )
        
        with col2:
            # Área parroquial
            with Session(db_engine) as session:
                areas = session.exec(
                    select(AreaParroquial).where(AreaParroquial.activo == True)
                ).all()
            
            if not areas:
                st.error("❌ No hay áreas parroquiales registradas")
                id_area = None
            else:
                opciones_areas = {a.id_area: a.nombre_area for a in areas}
                id_area = st.selectbox(
                    "Área (*)",
                    options=opciones_areas.keys(),
                    format_func=lambda x: opciones_areas[x],
                    key="acta_area"
                )
        
        st.markdown("---")
        st.markdown("### 📝 Contenido del Acta")
        
        orden_dia = st.text_area(
            "Orden del Día (*)",
            height=150,
            placeholder="Lista de temas a tratar en la reunión...",
            key="acta_orden"
        )
        
        desarrollo_reunion = st.text_area(
            "Desarrollo o Síntesis de la Reunión (*)",
            height=200,
            placeholder="Resumen de lo discutido, puntos relevantes...",
            key="acta_desarrollo"
        )
        
        acuerdos_principales = st.text_area(
            "Acuerdos Principales (*)",
            height=150,
            placeholder="Lista de acuerdos tomados, compromisos, responsables...",
            key="acta_acuerdos"
        )
        
        observaciones = st.text_area(
            "Observaciones",
            height=100,
            placeholder="Comentarios adicionales, asistencias especiales...",
            key="acta_obs"
        )
        
        st.markdown("---")
        st.markdown("### 👤 Responsable de la Reunión")
        
        with Session(db_engine) as session:
            personas = session.exec(select(Persona)).all()
        
        if not personas:
            st.error("❌ No hay personas registradas")
            id_responsable = None
        else:
            opciones_personas = {p.id_persona: p.nombre_completo() for p in personas}
            id_responsable = st.selectbox(
                "Presidente/Coordinador (*)",
                options=opciones_personas.keys(),
                format_func=lambda x: opciones_personas[x],
                key="acta_responsable",
                help="Presidente, coordinador o párroco que presidió la reunión"
            )
        
        st.markdown("---")
        st.markdown("### 👥 Lista de Asistentes")
        
        asistentes_seleccionados = st.multiselect(
            "Selecciona los asistentes:",
            options=opciones_personas.keys(),
            format_func=lambda x: opciones_personas[x],
            key="acta_asistentes",
            help="Puedes seleccionar múltiples personas"
        )
        
        # Roles de asistentes (opcional)
        if asistentes_seleccionados:
            st.caption("Opcionalmente, especifica roles de los asistentes:")
            roles_asistentes = {}
            for id_asist in asistentes_seleccionados:
                roles_asistentes[id_asist] = st.text_input(
                    f"Rol de {opciones_personas[id_asist]}:",
                    placeholder="Ej: Coordinador, Secretario, Vocal...",
                    key=f"rol_asist_{id_asist}"
                )
        
        st.markdown("---")
        st.markdown("### 📎 Archivo Digital del Acta")
        
        st.info("💡 Después de guardar el borrador, podrás adjuntar el documento PDF")
        
        url_documento = st.text_input(
            "URL del Documento (PDF)",
            max_chars=500,
            placeholder="https://...",
            help="Guarda primero como borrador, luego sube el documento y actualiza esta URL",
            key="acta_url"
        )
        
        formato_documento = st.selectbox(
            "Formato del Documento",
            options=["PDF", "JPG", "PNG"],
            key="acta_formato"
        )
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            guardar_como_borrador = st.form_submit_button(
                "💾 Guardar como Borrador",
                type="secondary",
                use_container_width=True
            )
        
        with col2:
            enviar_revision = st.form_submit_button(
                "📤 Enviar a Revisión",
                type="primary",
                use_container_width=True
            )
        
        if guardar_como_borrador or enviar_revision:
            # Validaciones
            if not all([id_tipo_reunion, fecha_reunion, lugar_reunion, id_grupo, id_area,
                       orden_dia, desarrollo_reunion, acuerdos_principales, id_responsable]):
                st.error("❌ Todos los campos marcados con (*) son obligatorios")
            else:
                estatus = "En revisión" if enviar_revision else "Borrador"
                
                nueva_acta = ActaReunion(
                    id_tipo_reunion=id_tipo_reunion,
                    fecha_reunion=fecha_reunion,
                    hora_inicio=hora_inicio,
                    hora_cierre=hora_cierre,
                    lugar_reunion=lugar_reunion.strip(),
                    id_grupo=id_grupo,
                    id_area=id_area,
                    orden_dia=orden_dia.strip(),
                    desarrollo_reunion=desarrollo_reunion.strip(),
                    acuerdos_principales=acuerdos_principales.strip(),
                    observaciones=observaciones.strip() if observaciones else None,
                    id_responsable_reunion=id_responsable,
                    url_documento_acta=url_documento.strip() if url_documento else "pendiente",
                    version_documento=1,
                    formato_documento=formato_documento,
                    id_usuario_registro=usuario_actual.id_usuario if usuario_actual else 1,
                    estatus=estatus
                )
                
                if db_module.crear_registro(nueva_acta, db_engine, st_display_func, nombre_tabla="Acta"):
                    # Registrar asistentes
                    if asistentes_seleccionados:
                        for id_asist in asistentes_seleccionados:
                            rol = roles_asistentes.get(id_asist, "").strip() if roles_asistentes.get(id_asist) else None
                            
                            asistente = AsistenteActa(
                                id_acta=nueva_acta.id_acta,
                                id_persona=id_asist,
                                presente=True,
                                rol_en_reunion=rol
                            )
                            
                            db_module.crear_registro(asistente, db_engine, st_display_func, nombre_tabla="Asistente")
                    
                    # Crear registro en historial
                    historial = HistorialActa(
                        id_acta=nueva_acta.id_acta,
                        id_usuario=usuario_actual.id_usuario if usuario_actual else 1,
                        tipo_accion="Creación",
                        estatus_nuevo=estatus,
                        version_nueva=1,
                        descripcion_cambio=f"Acta creada en estado: {estatus}"
                    )
                    
                    db_module.crear_registro(historial, db_engine, st_display_func, nombre_tabla="Historial")
                    
                    st.success(f"✅ Acta registrada como {estatus}")
                    st.balloons()
                    st.rerun()


# ====================================================================
# VER ACTAS
# ====================================================================

def ver_actas(db_engine, usuario_actual):
    st.subheader("📋 Archivo de Actas")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with Session(db_engine) as session:
            grupos = session.exec(select(GrupoParroquial)).all()
        
        opciones_grupos = {0: "Todos los grupos"}
        opciones_grupos.update({g.id_grupo: g.nombre_grupo for g in grupos})
        filtro_grupo = st.selectbox(
            "Grupo:",
            options=opciones_grupos.keys(),
            format_func=lambda x: opciones_grupos[x],
            key="ver_acta_grupo"
        )
    
    with col2:
        filtro_estatus = st.selectbox(
            "Estatus:",
            options=["Todos", "Borrador", "En revisión", "Aprobada", "Archivada"],
            key="ver_acta_estatus"
        )
    
    with col3:
        anio = st.number_input(
            "Año:",
            min_value=2020,
            max_value=2030,
            value=date.today().year,
            key="ver_acta_anio"
        )
    
    # Consultar actas
    with Session(db_engine) as session:
        statement = select(ActaReunion).order_by(ActaReunion.fecha_reunion.desc())
        
        if filtro_grupo != 0:
            statement = statement.where(ActaReunion.id_grupo == filtro_grupo)
        
        if filtro_estatus != "Todos":
            statement = statement.where(ActaReunion.estatus == filtro_estatus)
        
        from sqlalchemy import extract
        statement = statement.where(extract('year', ActaReunion.fecha_reunion) == anio)
        
        actas = session.exec(statement).all()
    
    if actas:
        st.markdown(f"**Total de actas:** {len(actas)}")
        
        # Estadísticas rápidas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            borradores = len([a for a in actas if a.estatus == "Borrador"])
            st.metric("📝 Borradores", borradores)
        
        with col2:
            revision = len([a for a in actas if a.estatus == "En revisión"])
            st.metric("👀 En revisión", revision)
        
        with col3:
            aprobadas = len([a for a in actas if a.estatus == "Aprobada"])
            st.metric("✅ Aprobadas", aprobadas)
        
        with col4:
            archivadas = len([a for a in actas if a.estatus == "Archivada"])
            st.metric("📦 Archivadas", archivadas)
        
        st.markdown("---")
        
        # Mostrar actas
        for acta in actas:
            with Session(db_engine) as session:
                grupo = session.get(GrupoParroquial, acta.id_grupo)
                area = session.get(AreaParroquial, acta.id_area)
                tipo = session.get(TipoReunion, acta.id_tipo_reunion)
                responsable = session.get(Persona, acta.id_responsable_reunion)
                
                # Contar asistentes
                asistentes = session.exec(
                    select(AsistenteActa).where(AsistenteActa.id_acta == acta.id_acta)
                ).all()
            
            # Icono según estatus
            iconos_estatus = {
                "Borrador": "📝",
                "En revisión": "👀",
                "Aprobada": "✅",
                "Archivada": "📦"
            }
            icono = iconos_estatus.get(acta.estatus, "📄")
            
            titulo = f"{icono} {acta.fecha_reunion.strftime('%d/%m/%Y')} - {tipo.nombre_tipo if tipo else 'N/A'} - {grupo.nombre_grupo if grupo else 'N/A'}"
            
            with st.expander(titulo):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**📋 Información General**")
                    st.markdown(f"• **Tipo:** {tipo.nombre_tipo if tipo else 'N/A'}")
                    st.markdown(f"• **Grupo:** {grupo.nombre_grupo if grupo else 'N/A'}")
                    st.markdown(f"• **Área:** {area.nombre_area if area else 'N/A'}")
                    st.markdown(f"• **Lugar:** {acta.lugar_reunion}")
                
                with col2:
                    st.markdown("**⏰ Horario**")
                    st.markdown(f"• **Inicio:** {acta.hora_inicio.strftime('%H:%M') if acta.hora_inicio else 'N/A'}")
                    st.markdown(f"• **Cierre:** {acta.hora_cierre.strftime('%H:%M') if acta.hora_cierre else 'N/A'}")
                    st.markdown(f"• **Responsable:** {responsable.nombre_completo() if responsable else 'N/A'}")
                
                with col3:
                    st.markdown("**📊 Estado**")
                    st.markdown(f"• **Estatus:** {acta.estatus}")
                    st.markdown(f"• **Asistentes:** {len(asistentes)}")
                    st.markdown(f"• **Versión:** {acta.version_documento}")
                
                st.markdown("---")
                
                # Contenido
                with st.expander("📋 Ver Orden del Día"):
                    st.markdown(acta.orden_dia)
                
                with st.expander("📝 Ver Desarrollo"):
                    st.markdown(acta.desarrollo_reunion)
                
                with st.expander("✅ Ver Acuerdos"):
                    st.markdown(acta.acuerdos_principales)
                
                # Asistentes
                if asistentes:
                    with st.expander(f"👥 Ver Asistentes ({len(asistentes)})"):
                        for asist in asistentes:
                            persona = session.get(Persona, asist.id_persona)
                            rol = f" - {asist.rol_en_reunion}" if asist.rol_en_reunion else ""
                            st.markdown(f"• {persona.nombre_completo() if persona else 'N/A'}{rol}")
                
                # Documento
                st.markdown("---")
                if acta.url_documento_acta and acta.url_documento_acta != "pendiente":
                    st.markdown(f"📎 [Ver Documento ({acta.formato_documento})]({acta.url_documento_acta})")
                else:
                    st.caption("📎 Documento pendiente de adjuntar")
                
                # Acciones
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📋 Ver Historial", key=f"hist_acta_{acta.id_acta}"):
                        mostrar_historial_acta(db_engine, acta.id_acta)
                
                with col2:
                    if acta.estatus == "Borrador":
                        if st.button("✏️ Editar", key=f"edit_acta_{acta.id_acta}"):
                            st.info("💡 Edición disponible")
                
                with col3:
                    if acta.estatus in ["Borrador", "En revisión"]:
                        if st.button("✅ Aprobar", key=f"apr_acta_{acta.id_acta}"):
                            st.session_state[f"aprobar_acta_{acta.id_acta}"] = True
    else:
        st.info("ℹ️ No hay actas con los filtros seleccionados")


# ====================================================================
# APROBAR ACTAS
# ====================================================================

def aprobar_actas(db_engine, db_module, st_display_func, usuario_actual):
    st.subheader("✅ Aprobación de Actas")
    
    st.info("💡 Solo usuarios autorizados pueden aprobar actas")
    
    # Actas pendientes de aprobación
    with Session(db_engine) as session:
        actas_pendientes = session.exec(
            select(ActaReunion).where(
                ActaReunion.estatus.in_(["Borrador", "En revisión"])
            ).order_by(ActaReunion.fecha_reunion.desc())
        ).all()
    
    if actas_pendientes:
        st.markdown(f"**Actas pendientes:** {len(actas_pendientes)}")
        
        for acta in actas_pendientes:
            with Session(db_engine) as session:
                grupo = session.get(GrupoParroquial, acta.id_grupo)
                tipo = session.get(TipoReunion, acta.id_tipo_reunion)
            
            with st.expander(f"📋 {acta.fecha_reunion.strftime('%d/%m/%Y')} - {tipo.nombre_tipo if tipo else 'N/A'} - {grupo.nombre_grupo if grupo else 'N/A'}"):
                st.markdown(f"**Estatus actual:** {acta.estatus}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✅ Aprobar", key=f"aprobar_{acta.id_acta}", type="primary"):
                        # Actualizar estatus
                        with Session(db_engine) as session:
                            acta_actualizar = session.get(ActaReunion, acta.id_acta)
                            if acta_actualizar:
                                acta_actualizar.estatus = "Aprobada"
                                acta_actualizar.fecha_aprobacion = datetime.now()
                                acta_actualizar.id_usuario_aprobador = usuario_actual.id_usuario if usuario_actual else 1
                                session.add(acta_actualizar)
                                session.commit()
                                
                                # Registrar en historial
                                historial = HistorialActa(
                                    id_acta=acta.id_acta,
                                    id_usuario=usuario_actual.id_usuario if usuario_actual else 1,
                                    tipo_accion="Aprobación",
                                    estatus_anterior=acta.estatus,
                                    estatus_nuevo="Aprobada",
                                    descripcion_cambio="Acta aprobada"
                                )
                                session.add(historial)
                                session.commit()
                                
                                st.success("✅ Acta aprobada")
                                st.rerun()
                
                with col2:
                    if st.button("↩️ Regresar a Borrador", key=f"regresar_{acta.id_acta}"):
                        with Session(db_engine) as session:
                            acta_actualizar = session.get(ActaReunion, acta.id_acta)
                            if acta_actualizar:
                                acta_actualizar.estatus = "Borrador"
                                session.add(acta_actualizar)
                                
                                historial = HistorialActa(
                                    id_acta=acta.id_acta,
                                    id_usuario=usuario_actual.id_usuario if usuario_actual else 1,
                                    tipo_accion="Cambio de estatus",
                                    estatus_anterior=acta.estatus,
                                    estatus_nuevo="Borrador",
                                    descripcion_cambio="Acta regresada a borrador para correcciones"
                                )
                                session.add(historial)
                                session.commit()
                                
                                st.info("ℹ️ Acta regresada a borrador")
                                st.rerun()
    else:
        st.info("ℹ️ No hay actas pendientes de aprobación")


# ====================================================================
# BÚSQUEDA
# ====================================================================

def buscar_actas(db_engine, usuario_actual):
    st.subheader("🔍 Búsqueda de Actas")
    st.info("💡 Búsqueda avanzada disponible para implementar")


# ====================================================================
# ESTADÍSTICAS
# ====================================================================

def estadisticas_actas(db_engine):
    st.subheader("📊 Estadísticas del Archivo de Actas")
    
    with Session(db_engine) as session:
        total_actas = session.exec(select(ActaReunion)).all()
    
    if total_actas:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📄 Total Actas", len(total_actas))
        
        with col2:
            aprobadas = len([a for a in total_actas if a.estatus == "Aprobada"])
            st.metric("✅ Aprobadas", aprobadas)
        
        with col3:
            archivadas = len([a for a in total_actas if a.estatus == "Archivada"])
            st.metric("📦 Archivadas", archivadas)
        
        with col4:
            anio_actual = date.today().year
            este_anio = len([a for a in total_actas if a.fecha_reunion.year == anio_actual])
            st.metric(f"📅 {anio_actual}", este_anio)
    else:
        st.info("ℹ️ No hay actas registradas")


# ====================================================================
# FUNCIONES AUXILIARES
# ====================================================================

def mostrar_historial_acta(db_engine, id_acta):
    """Muestra el historial inalterable de cambios de un acta"""
    with Session(db_engine) as session:
        historial = session.exec(
            select(HistorialActa).where(
                HistorialActa.id_acta == id_acta
            ).order_by(HistorialActa.fecha_accion.desc())
        ).all()
    
    if historial:
        st.markdown("### 📋 Historial de Cambios (Inalterable)")
        
        for registro in historial:
            with Session(db_engine) as session:
                usuario = session.get(Usuario, registro.id_usuario)
                persona = session.get(Persona, usuario.id_persona) if usuario else None
            
            st.markdown(f"**{registro.tipo_accion}** - {registro.fecha_accion.strftime('%d/%m/%Y %H:%M')}")
            st.caption(f"Por: {persona.nombre_completo() if persona else 'N/A'}")
            
            if registro.estatus_anterior and registro.estatus_nuevo:
                st.caption(f"Estatus: {registro.estatus_anterior} → {registro.estatus_nuevo}")
            
            if registro.descripcion_cambio:
                st.caption(f"Detalle: {registro.descripcion_cambio}")
            
            st.markdown("---")
    else:
        st.info("ℹ️ No hay historial disponible")
