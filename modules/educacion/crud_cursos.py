# crud_cursos.py
import streamlit as st
from datetime import date
from models import Curso, Tema
from sqlmodel import Session, select

def mostrar_crud_cursos(db_engine, db_module, db_mode, st_display_func):
    """Módulo completo CRUD para Cursos y Temas"""
    st.header(f"📚 Gestión de Cursos - Modo: {db_mode}")
    
    st.info("💡 Crea plantillas de cursos reutilizables con sus temas/sesiones")
    
    tabs = st.tabs([
        "➕ Crear Curso",
        "📋 Ver Cursos",
        "📝 Gestionar Temas",
        "📋 Ver Temas por Curso",
        "✏️ Actualizar",
        "🗑️ Eliminar"
    ])
    
    # ================================================================
    # TAB 1: CREAR CURSO
    # ================================================================
    with tabs[0]:
        st.subheader("➕ Crear Nuevo Curso")
        
        with st.form("form_crear_curso", clear_on_submit=True):
            st.markdown("### 📖 Información del Curso")
            
            col1, col2 = st.columns(2)
            
            with col1:
                nombre_curso = st.text_input(
                    "Nombre del Curso (*)",
                    max_chars=200,
                    placeholder="Ej: Primera Comunión - Nivel 1",
                    key="curso_nombre"
                )
                
                tipo_curso = st.selectbox(
                    "Tipo de Curso (*)",
                    options=["Sacramental", "Bíblico", "Formación", "Taller", "Retiro"],
                    key="curso_tipo"
                )
                
                if tipo_curso == "Sacramental":
                    sacramento_asociado = st.selectbox(
                        "Sacramento Asociado",
                        options=["Bautismo", "Primera Comunión", "Confirmación", "Matrimonio", "Otro"],
                        key="curso_sacramento"
                    )
                else:
                    sacramento_asociado = None
            
            with col2:
                nivel = st.selectbox(
                    "Nivel",
                    options=["Niños", "Adolescentes", "Adultos", "Familias", "Mixto"],
                    key="curso_nivel"
                )
                
                duracion_semanas = st.number_input(
                    "Duración (semanas)",
                    min_value=1,
                    max_value=52,
                    value=20,
                    key="curso_duracion"
                )
                
                total_sesiones = st.number_input(
                    "Total de Sesiones",
                    min_value=1,
                    max_value=100,
                    value=20,
                    key="curso_total_sesiones"
                )
            
            descripcion = st.text_area(
                "Descripción del Curso",
                placeholder="Objetivos, metodología, contenido general...",
                key="curso_descripcion"
            )
            
            activo = st.checkbox("Curso Activo", value=True, key="curso_activo")
            
            st.markdown("---")
            submitted = st.form_submit_button("💾 Crear Curso", type="primary", width="stretch")
            
            if submitted:
                if not nombre_curso:
                    st.error("❌ El nombre del curso es obligatorio")
                else:
                    nuevo_curso = Curso(
                        nombre_curso=nombre_curso.strip(),
                        descripcion=descripcion.strip() if descripcion else None,
                        tipo_curso=tipo_curso,
                        sacramento_asociado=sacramento_asociado if tipo_curso == "Sacramental" else None,
                        duracion_semanas=duracion_semanas,
                        total_sesiones=total_sesiones,
                        nivel=nivel,
                        activo=activo
                    )
                    
                    if db_module.crear_registro(nuevo_curso, db_engine, st_display_func, nombre_tabla="Curso"):
                        st.success("✅ Curso creado exitosamente")
                        st.info("💡 Ahora puedes agregar temas/sesiones en la pestaña 'Gestionar Temas'")
                        st.rerun()
    
    # ================================================================
    # TAB 2: VER CURSOS
    # ================================================================
    with tabs[1]:
        st.subheader("📋 Lista de Cursos Registrados")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filtro_tipo = st.selectbox(
                "Filtrar por Tipo:",
                options=["Todos", "Sacramental", "Bíblico", "Formación", "Taller", "Retiro"],
                key="filtro_tipo_curso"
            )
        
        with col2:
            filtro_nivel = st.selectbox(
                "Filtrar por Nivel:",
                options=["Todos", "Niños", "Adolescentes", "Adultos", "Familias", "Mixto"],
                key="filtro_nivel_curso"
            )
        
        with col3:
            filtro_estado = st.selectbox(
                "Filtrar por Estado:",
                options=["Todos", "Activos", "Inactivos"],
                key="filtro_estado_curso"
            )
        
        # Consultar cursos
        with Session(db_engine) as session:
            statement = select(Curso)
            
            if filtro_tipo != "Todos":
                statement = statement.where(Curso.tipo_curso == filtro_tipo)
            
            if filtro_nivel != "Todos":
                statement = statement.where(Curso.nivel == filtro_nivel)
            
            if filtro_estado == "Activos":
                statement = statement.where(Curso.activo == True)
            elif filtro_estado == "Inactivos":
                statement = statement.where(Curso.activo == False)
            
            cursos = session.exec(statement).all()
        
        if cursos:
            st.markdown(f"**Total de Cursos:** {len(cursos)}")
            
            for curso in cursos:
                with Session(db_engine) as session:
                    # Contar temas
                    temas = session.exec(
                        select(Tema).where(Tema.id_curso == curso.id_curso)
                    ).all()
                    total_temas = len(temas)
                
                estado_icon = "✅" if curso.activo else "❌"
                
                with st.expander(f"{estado_icon} {curso.nombre_curso}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**Tipo:** {curso.tipo_curso}")
                        st.markdown(f"**Nivel:** {curso.nivel or 'N/A'}")
                        if curso.sacramento_asociado:
                            st.markdown(f"**Sacramento:** {curso.sacramento_asociado}")
                        if curso.descripcion:
                            st.markdown(f"**Descripción:** {curso.descripcion}")
                    
                    with col2:
                        st.metric("Duración", f"{curso.duracion_semanas or 0} semanas")
                        st.metric("Sesiones", f"{total_temas}/{curso.total_sesiones or 0}")
                        
                        if total_temas < (curso.total_sesiones or 0):
                            st.warning(f"⚠️ Faltan {(curso.total_sesiones or 0) - total_temas} temas")
                        elif total_temas == (curso.total_sesiones or 0):
                            st.success("✅ Curso completo")
                    
                    st.caption(f"ID: {curso.id_curso}")
        else:
            st.info("ℹ️ No hay cursos registrados con los filtros seleccionados")
    
    # ================================================================
    # TAB 3: GESTIONAR TEMAS
    # ================================================================
    with tabs[2]:
        st.subheader("📝 Agregar Temas al Curso")
        
        # Seleccionar curso
        with Session(db_engine) as session:
            cursos = session.exec(select(Curso).where(Curso.activo == True)).all()
        
        if not cursos:
            st.warning("⚠️ No hay cursos activos. Crea un curso primero.")
            return
        
        opciones_cursos = {c.id_curso: f"{c.nombre_curso} ({c.tipo_curso})" for c in cursos}
        id_curso_sel = st.selectbox(
            "Selecciona el Curso:",
            options=opciones_cursos.keys(),
            format_func=lambda x: opciones_cursos[x],
            key="tema_curso_sel"
        )
        
        curso_seleccionado = next((c for c in cursos if c.id_curso == id_curso_sel), None)
        
        if curso_seleccionado:
            # Mostrar progreso
            with Session(db_engine) as session:
                temas_existentes = session.exec(
                    select(Tema).where(Tema.id_curso == id_curso_sel).order_by(Tema.numero_sesion)
                ).all()
            
            st.markdown(f"**Progreso:** {len(temas_existentes)}/{curso_seleccionado.total_sesiones or 0} sesiones")
            st.progress(len(temas_existentes) / (curso_seleccionado.total_sesiones or 1))
            
            st.markdown("---")
            st.markdown("### ➕ Agregar Nueva Sesión/Tema")
            
            with st.form("form_crear_tema", clear_on_submit=True):
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    # Calcular siguiente número de sesión
                    siguiente_numero = len(temas_existentes) + 1
                    
                    numero_sesion = st.number_input(
                        "Número de Sesión (*)",
                        min_value=1,
                        max_value=100,
                        value=siguiente_numero,
                        key="tema_numero"
                    )
                
                with col2:
                    nombre_tema = st.text_input(
                        "Nombre del Tema (*)",
                        max_chars=255,
                        placeholder="Ej: Jesús nos ama",
                        key="tema_nombre"
                    )
                
                objetivo = st.text_area(
                    "Objetivo de la Sesión",
                    placeholder="¿Qué se espera que los participantes aprendan?",
                    key="tema_objetivo"
                )
                
                descripcion_tema = st.text_area(
                    "Descripción/Contenido",
                    placeholder="Detalles del tema, puntos a tratar...",
                    key="tema_descripcion"
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    material_sugerido = st.text_area(
                        "Material Sugerido",
                        placeholder="Biblia, cuadernos, hojas de actividades...",
                        key="tema_material"
                    )
                
                with col2:
                    duracion_sugerida = st.number_input(
                        "Duración Sugerida (minutos)",
                        min_value=15,
                        max_value=240,
                        value=60,
                        step=15,
                        key="tema_duracion"
                    )
                
                st.markdown("---")
                submitted_tema = st.form_submit_button("💾 Agregar Tema", type="primary", width="stretch")
                
                if submitted_tema:
                    if not nombre_tema:
                        st.error("❌ El nombre del tema es obligatorio")
                    else:
                        # Verificar si ya existe ese número de sesión
                        with Session(db_engine) as session:
                            existe = session.exec(
                                select(Tema).where(
                                    Tema.id_curso == id_curso_sel,
                                    Tema.numero_sesion == numero_sesion
                                )
                            ).first()
                        
                        if existe:
                            st.error(f"❌ Ya existe una sesión con el número {numero_sesion} en este curso")
                        else:
                            nuevo_tema = Tema(
                                id_curso=id_curso_sel,
                                numero_sesion=numero_sesion,
                                nombre_tema=nombre_tema.strip(),
                                descripcion=descripcion_tema.strip() if descripcion_tema else None,
                                objetivo=objetivo.strip() if objetivo else None,
                                material_sugerido=material_sugerido.strip() if material_sugerido else None,
                                duracion_sugerida=duracion_sugerida
                            )
                            
                            if db_module.crear_registro(nuevo_tema, db_engine, st_display_func, nombre_tabla="Tema"):
                                st.success("✅ Tema agregado exitosamente")
                                st.rerun()
    
    # ================================================================
    # TAB 4: VER TEMAS POR CURSO
    # ================================================================
    with tabs[3]:
        st.subheader("📋 Temas por Curso")
        
        # Seleccionar curso
        with Session(db_engine) as session:
            cursos = session.exec(select(Curso)).all()
        
        if not cursos:
            st.info("ℹ️ No hay cursos registrados")
            return
        
        opciones_cursos = {c.id_curso: f"{c.nombre_curso}" for c in cursos}
        id_curso_ver = st.selectbox(
            "Selecciona el Curso:",
            options=opciones_cursos.keys(),
            format_func=lambda x: opciones_cursos[x],
            key="ver_temas_curso"
        )
        
        with Session(db_engine) as session:
            temas = session.exec(
                select(Tema).where(Tema.id_curso == id_curso_ver).order_by(Tema.numero_sesion)
            ).all()
            
            curso = session.get(Curso, id_curso_ver)
        
        if temas:
            st.markdown(f"**Total de Temas:** {len(temas)}/{curso.total_sesiones or 0}")
            
            for tema in temas:
                with st.expander(f"Sesión {tema.numero_sesion}: {tema.nombre_tema}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        if tema.objetivo:
                            st.markdown(f"**Objetivo:** {tema.objetivo}")
                        
                        if tema.descripcion:
                            st.markdown(f"**Contenido:** {tema.descripcion}")
                        
                        if tema.material_sugerido:
                            st.markdown(f"**Material:** {tema.material_sugerido}")
                    
                    with col2:
                        if tema.duracion_sugerida:
                            st.metric("Duración", f"{tema.duracion_sugerida} min")
                        
                        st.caption(f"ID: {tema.id_tema}")
        else:
            st.info("ℹ️ Este curso no tiene temas asignados aún")
    
    # TAB 5 y 6: Actualizar y Eliminar (simplificados)
    with tabs[4]:
        st.info("💡 Funcionalidad de actualización disponible para implementar")
    
    with tabs[5]:
        st.info("💡 Funcionalidad de eliminación disponible para implementar")