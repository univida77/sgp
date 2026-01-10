# crud_inventario.py - Módulo CRUD de Inventario
import streamlit as st
from datetime import date, datetime
from decimal import Decimal
from models import (
    BienInventario, MovimientoBien, Bodega, AreaParroquial, CategoriaInventario
)
from models import GrupoParroquial, Usuario
from sqlmodel import Session, select, func

# ====================================================================
# FUNCIÓN PRINCIPAL
# ====================================================================

def mostrar_crud_inventario(db_engine, db_module, db_mode, st_display_func, usuario_actual=None):
    """Módulo completo CRUD para Inventario"""
    st.header(f"📦 Gestión de Inventario - Modo: {db_mode}")
    
    st.info("💡 Control integral de bienes patrimoniales: registro, ubicación y trazabilidad")
    
    tabs = st.tabs([
        "📦 Bienes",
        "🚚 Movimientos",
        "🏢 Bodegas",
        "📂 Categorías",
        "🔍 Búsqueda Avanzada",
        "📊 Reportes"
    ])
    
    # ================================================================
    # TAB 1: BIENES
    # ================================================================
    with tabs[0]:
        crud_bienes(db_engine, db_module, st_display_func, usuario_actual)
    
    # ================================================================
    # TAB 2: MOVIMIENTOS
    # ================================================================
    with tabs[1]:
        crud_movimientos(db_engine, db_module, st_display_func, usuario_actual)
    
    # ================================================================
    # TAB 3: BODEGAS
    # ================================================================
    with tabs[2]:
        crud_bodegas(db_engine, db_module, st_display_func, usuario_actual)
    
    # ================================================================
    # TAB 4: CATEGORÍAS
    # ================================================================
    with tabs[3]:
        crud_categorias_inventario(db_engine, db_module, st_display_func, usuario_actual)
    
    # ================================================================
    # TAB 5: BÚSQUEDA AVANZADA
    # ================================================================
    with tabs[4]:
        busqueda_avanzada(db_engine, usuario_actual)
    
    # ================================================================
    # TAB 6: REPORTES
    # ================================================================
    with tabs[5]:
        reportes_inventario(db_engine, usuario_actual)


# ====================================================================
# GESTIÓN DE BIENES
# ====================================================================

def crud_bienes(db_engine, db_module, st_display_func, usuario_actual):
    st.subheader("📦 Registro de Bienes")
    
    subtabs = st.tabs(["➕ Registrar Bien", "📋 Ver Bienes", "✏️ Editar"])
    
    # REGISTRAR BIEN
    with subtabs[0]:
        st.markdown("### ➕ Nuevo Bien")
        
        with st.form("form_bien", clear_on_submit=True):
            st.markdown("#### 📝 Información Básica")
            
            col1, col2 = st.columns(2)
            
            with col1:
                nombre_bien = st.text_input(
                    "Nombre del Bien (*)",
                    max_chars=300,
                    placeholder="Ej: Mesa de madera grande",
                    key="bien_nombre"
                )
                
                # Categoría
                with Session(db_engine) as session:
                    categorias = session.exec(
                        select(CategoriaInventario).where(
                            CategoriaInventario.activo == True
                        )
                    ).all()
                
                if not categorias:
                    st.error("❌ No hay categorías de inventario. Créalas primero.")
                    st.form_submit_button("Guardar", disabled=True)
                    return
                
                opciones_cat = {c.id_categoria_inv: c.nombre_categoria for c in categorias}
                id_categoria = st.selectbox(
                    "Categoría (*)",
                    options=opciones_cat.keys(),
                    format_func=lambda x: opciones_cat[x],
                    key="bien_categoria"
                )
                
                cantidad = st.number_input(
                    "Cantidad",
                    min_value=1,
                    value=1,
                    help="Para bienes contables (sillas, trastes, etc.)",
                    key="bien_cantidad"
                )
            
            with col2:
                marca = st.text_input(
                    "Marca",
                    max_chars=100,
                    key="bien_marca"
                )
                
                modelo = st.text_input(
                    "Modelo",
                    max_chars=100,
                    key="bien_modelo"
                )
                
                numero_serie = st.text_input(
                    "Número de Serie",
                    max_chars=100,
                    key="bien_serie"
                )
            
            descripcion = st.text_area(
                "Descripción",
                placeholder="Características, dimensiones, condiciones...",
                key="bien_desc"
            )
            
            st.markdown("---")
            st.markdown("#### 📍 Ubicación Actual")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Grupo responsable
                with Session(db_engine) as session:
                    grupos = session.exec(
                        select(GrupoParroquial).where(GrupoParroquial.activo == True)
                    ).all()
                
                opciones_grupos = {g.id_grupo: g.nombre_grupo for g in grupos}
                id_grupo_responsable = st.selectbox(
                    "Grupo Responsable (*)",
                    options=opciones_grupos.keys(),
                    format_func=lambda x: opciones_grupos[x],
                    key="bien_grupo"
                )
            
            with col2:
                # Área
                with Session(db_engine) as session:
                    areas = session.exec(
                        select(AreaParroquial).where(AreaParroquial.activo == True)
                    ).all()
                
                if not areas:
                    st.error("❌ No hay áreas parroquiales. Créalas primero.")
                    id_area = None
                else:
                    opciones_areas = {a.id_area: a.nombre_area for a in areas}
                    id_area = st.selectbox(
                        "Área (*)",
                        options=opciones_areas.keys(),
                        format_func=lambda x: opciones_areas[x],
                        key="bien_area"
                    )
            
            with col3:
                # Bodega
                with Session(db_engine) as session:
                    bodegas = session.exec(
                        select(Bodega).where(Bodega.activo == True)
                    ).all()
                
                if bodegas:
                    opciones_bodegas = {0: "-- Sin bodega --"}
                    opciones_bodegas.update({
                        b.id_bodega: f"{b.codigo_bodega} - {b.nombre_bodega}"
                        for b in bodegas
                    })
                    id_bodega = st.selectbox(
                        "Bodega:",
                        options=opciones_bodegas.keys(),
                        format_func=lambda x: opciones_bodegas[x],
                        key="bien_bodega"
                    )
                    id_bodega = id_bodega if id_bodega != 0 else None
                else:
                    id_bodega = None
            
            ubicacion_especifica = st.text_input(
                "Ubicación Específica",
                max_chars=300,
                placeholder="Ej: Estante 3, nivel 2, caja azul",
                key="bien_ubicacion"
            )
            
            st.markdown("---")
            st.markdown("#### 🔧 Estado y Valor")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                estado_bien = st.selectbox(
                    "Estado del Bien (*)",
                    options=["En uso", "Almacenado", "Prestado", "En reparación", "Dado de baja"],
                    key="bien_estado"
                )
            
            with col2:
                valor_aproximado = st.number_input(
                    "Valor Aproximado",
                    min_value=0.00,
                    value=0.00,
                    step=100.00,
                    format="%.2f",
                    key="bien_valor"
                )
                
                moneda = st.selectbox(
                    "Moneda",
                    options=["MXN", "USD"],
                    key="bien_moneda"
                )
            
            with col3:
                fecha_adquisicion = st.date_input(
                    "Fecha de Adquisición",
                    value=None,
                    max_value=date.today(),
                    key="bien_fecha_adq"
                )
            
            observaciones = st.text_area(
                "Observaciones",
                key="bien_obs"
            )
            
            st.markdown("---")
            st.caption("💡 Nota: Podrás adjuntar fotografías y ficha técnica después de guardar")
            
            submitted = st.form_submit_button("💾 Registrar Bien", type="primary", use_container_width=True)
            
            if submitted:
                if not nombre_bien or not id_area:
                    st.error("❌ Nombre del bien y área son obligatorios")
                else:
                    # Generar código único
                    with Session(db_engine) as session:
                        ultimo_bien = session.exec(
                            select(BienInventario).order_by(
                                BienInventario.id_bien.desc()
                            )
                        ).first()
                        
                        proximo_id = (ultimo_bien.id_bien + 1) if ultimo_bien else 1
                        codigo_bien = f"INV-{proximo_id:06d}"
                    
                    nuevo_bien = BienInventario(
                        codigo_bien=codigo_bien,
                        nombre_bien=nombre_bien.strip(),
                        descripcion=descripcion.strip() if descripcion else None,
                        id_categoria=id_categoria,
                        id_grupo_responsable=id_grupo_responsable,
                        id_area=id_area,
                        id_bodega=id_bodega,
                        ubicacion_especifica=ubicacion_especifica.strip() if ubicacion_especifica else None,
                        estado_bien=estado_bien,
                        cantidad=cantidad,
                        marca=marca.strip() if marca else None,
                        modelo=modelo.strip() if modelo else None,
                        numero_serie=numero_serie.strip() if numero_serie else None,
                        valor_aproximado=Decimal(str(valor_aproximado)) if valor_aproximado > 0 else None,
                        moneda=moneda,
                        fecha_adquisicion=fecha_adquisicion,
                        id_usuario_registro=usuario_actual.id_usuario if usuario_actual else 1,
                        observaciones=observaciones.strip() if observaciones else None,
                        activo=True
                    )
                    
                    if db_module.crear_registro(nuevo_bien, db_engine, st_display_func, nombre_tabla="Bien"):
                        # Crear registro inicial en historial
                        movimiento_inicial = MovimientoBien(
                            id_bien=nuevo_bien.id_bien,
                            id_usuario=usuario_actual.id_usuario if usuario_actual else 1,
                            tipo_movimiento="Registro inicial",
                            grupo_nuevo=id_grupo_responsable,
                            area_nueva=id_area,
                            bodega_nueva=id_bodega,
                            estado_nuevo=estado_bien,
                            motivo="Registro inicial del bien en el sistema",
                            observaciones="Registro automático al crear el bien"
                        )
                        
                        db_module.crear_registro(movimiento_inicial, db_engine, st_display_func, nombre_tabla="Movimiento")
                        
                        st.success(f"✅ Bien registrado con código: {codigo_bien}")
                        st.balloons()
                        st.rerun()
    
    # VER BIENES
    with subtabs[1]:
        st.markdown("### 📋 Inventario de Bienes")
        
        # Filtros
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            with Session(db_engine) as session:
                grupos = session.exec(select(GrupoParroquial)).all()
            
            opciones_grupos = {0: "Todos los grupos"}
            opciones_grupos.update({g.id_grupo: g.nombre_grupo for g in grupos})
            filtro_grupo = st.selectbox(
                "Grupo:",
                options=opciones_grupos.keys(),
                format_func=lambda x: opciones_grupos[x],
                key="ver_bien_grupo"
            )
        
        with col2:
            with Session(db_engine) as session:
                bodegas = session.exec(select(Bodega)).all()
            
            opciones_bodegas = {0: "Todas las bodegas"}
            opciones_bodegas.update({b.id_bodega: b.codigo_bodega for b in bodegas})
            filtro_bodega = st.selectbox(
                "Bodega:",
                options=opciones_bodegas.keys(),
                format_func=lambda x: opciones_bodegas[x],
                key="ver_bien_bodega"
            )
        
        with col3:
            filtro_estado = st.selectbox(
                "Estado:",
                options=["Todos", "En uso", "Almacenado", "Prestado", "En reparación", "Dado de baja"],
                key="ver_bien_estado"
            )
        
        with col4:
            with Session(db_engine) as session:
                categorias = session.exec(select(CategoriaInventario)).all()
            
            opciones_cat = {0: "Todas las categorías"}
            opciones_cat.update({c.id_categoria_inv: c.nombre_categoria for c in categorias})
            filtro_categoria = st.selectbox(
                "Categoría:",
                options=opciones_cat.keys(),
                format_func=lambda x: opciones_cat[x],
                key="ver_bien_cat"
            )
        
        # Búsqueda por código o nombre
        buscar_texto = st.text_input(
            "🔍 Buscar por código o nombre:",
            key="buscar_bien"
        )
        
        # Consultar bienes
        with Session(db_engine) as session:
            statement = select(BienInventario).where(BienInventario.activo == True)
            
            if filtro_grupo != 0:
                statement = statement.where(BienInventario.id_grupo_responsable == filtro_grupo)
            
            if filtro_bodega != 0:
                statement = statement.where(BienInventario.id_bodega == filtro_bodega)
            
            if filtro_estado != "Todos":
                statement = statement.where(BienInventario.estado_bien == filtro_estado)
            
            if filtro_categoria != 0:
                statement = statement.where(BienInventario.id_categoria == filtro_categoria)
            
            bienes = session.exec(statement).all()
            
            # Filtro de texto
            if buscar_texto:
                bienes = [
                    b for b in bienes
                    if buscar_texto.upper() in b.codigo_bien.upper()
                    or buscar_texto.upper() in b.nombre_bien.upper()
                ]
        
        if bienes:
            st.markdown(f"**Total de bienes:** {len(bienes)}")
            
            # Estadísticas rápidas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                en_uso = len([b for b in bienes if b.estado_bien == "En uso"])
                st.metric("🔧 En uso", en_uso)
            
            with col2:
                almacenados = len([b for b in bienes if b.estado_bien == "Almacenado"])
                st.metric("📦 Almacenados", almacenados)
            
            with col3:
                prestados = len([b for b in bienes if b.estado_bien == "Prestado"])
                st.metric("🤝 Prestados", prestados)
            
            with col4:
                reparacion = len([b for b in bienes if b.estado_bien == "En reparación"])
                st.metric("🔧 En reparación", reparacion)
            
            st.markdown("---")
            
            # Tabla de bienes
            for bien in bienes:
                with Session(db_engine) as session:
                    grupo = session.get(GrupoParroquial, bien.id_grupo_responsable)
                    area = session.get(AreaParroquial, bien.id_area)
                    bodega = session.get(Bodega, bien.id_bodega) if bien.id_bodega else None
                    categoria = session.get(CategoriaInventario, bien.id_categoria)
                
                # Icono según estado
                iconos_estado = {
                    "En uso": "🔧",
                    "Almacenado": "📦",
                    "Prestado": "🤝",
                    "En reparación": "🔨",
                    "Dado de baja": "❌"
                }
                icono = iconos_estado.get(bien.estado_bien, "📦")
                
                with st.expander(f"{icono} {bien.codigo_bien} - {bien.nombre_bien} (x{bien.cantidad})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("**📝 Información Básica**")
                        st.markdown(f"• **Categoría:** {categoria.nombre_categoria if categoria else 'N/A'}")
                        st.markdown(f"• **Estado:** {bien.estado_bien}")
                        st.markdown(f"• **Cantidad:** {bien.cantidad}")
                        if bien.marca:
                            st.markdown(f"• **Marca:** {bien.marca}")
                        if bien.modelo:
                            st.markdown(f"• **Modelo:** {bien.modelo}")
                    
                    with col2:
                        st.markdown("**📍 Ubicación**")
                        st.markdown(f"• **Grupo:** {grupo.nombre_grupo if grupo else 'N/A'}")
                        st.markdown(f"• **Área:** {area.nombre_area if area else 'N/A'}")
                        if bodega:
                            st.markdown(f"• **Bodega:** {bodega.codigo_bodega}")
                        if bien.ubicacion_especifica:
                            st.markdown(f"• **Ubicación específica:** {bien.ubicacion_especifica}")
                    
                    with col3:
                        st.markdown("**💰 Valor y Fecha**")
                        if bien.valor_aproximado:
                            st.markdown(f"• **Valor:** ${float(bien.valor_aproximado):,.2f} {bien.moneda}")
                        if bien.fecha_adquisicion:
                            st.markdown(f"• **Adquisición:** {bien.fecha_adquisicion.strftime('%d/%m/%Y')}")
                        st.caption(f"Registrado: {bien.fecha_registro.strftime('%d/%m/%Y')}")
                    
                    if bien.descripcion:
                        st.markdown("---")
                        st.markdown(f"**Descripción:** {bien.descripcion}")
                    
                    # Botones de acción
                    st.markdown("---")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("📋 Ver Historial", key=f"hist_{bien.id_bien}"):
                            mostrar_historial_bien(db_engine, bien.id_bien)
                    with col2:
                        if st.button("🚚 Mover", key=f"mover_{bien.id_bien}"):
                            st.session_state[f"mover_bien_{bien.id_bien}"] = True
                    with col3:
                        if st.button("✏️ Editar", key=f"edit_{bien.id_bien}"):
                            st.session_state[f"editar_bien_{bien.id_bien}"] = True
        else:
            st.info("ℹ️ No hay bienes con los filtros seleccionados")
    
    # EDITAR
    with subtabs[2]:
        st.info("💡 Edición disponible para implementar")


# ====================================================================
# GESTIÓN DE MOVIMIENTOS
# ====================================================================

def crud_movimientos(db_engine, db_module, st_display_func, usuario_actual):
    st.subheader("🚚 Movimientos de Bienes")
    st.info("💡 Registra cambios de ubicación, préstamos y devoluciones")
    
    # ... implementación similar


# ====================================================================
# GESTIÓN DE BODEGAS
# ====================================================================

def crud_bodegas(db_engine, db_module, st_display_func, usuario_actual):
    st.subheader("🏢 Gestión de Bodegas (B-1 a B-6)")
    
    subtabs = st.tabs(["➕ Crear Bodega", "📋 Ver Bodegas"])
    
    with subtabs[0]:
        st.markdown("### ➕ Nueva Bodega")
        
        with st.form("form_bodega", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                codigo_bodega = st.text_input(
                    "Código de Bodega (*)",
                    max_chars=10,
                    placeholder="Ej: B-1, B-2, B-3...",
                    key="bodega_codigo"
                )
                
                nombre_bodega = st.text_input(
                    "Nombre de la Bodega (*)",
                    max_chars=200,
                    placeholder="Ej: Bodega Principal",
                    key="bodega_nombre"
                )
            
            with col2:
                ubicacion = st.text_input(
                    "Ubicación",
                    max_chars=500,
                    placeholder="Descripción de la ubicación física",
                    key="bodega_ubicacion"
                )
                
                responsable = st.text_input(
                    "Responsable",
                    max_chars=200,
                    key="bodega_responsable"
                )
            
            capacidad = st.text_area(
                "Capacidad Aproximada",
                placeholder="Descripción del espacio disponible",
                key="bodega_capacidad"
            )
            
            observaciones = st.text_area(
                "Observaciones",
                key="bodega_obs"
            )
            
            submitted = st.form_submit_button("💾 Crear Bodega", type="primary", use_container_width=True)
            
            if submitted:
                if not codigo_bodega or not nombre_bodega:
                    st.error("❌ Código y nombre son obligatorios")
                else:
                    # Verificar que no exista el código
                    with Session(db_engine) as session:
                        existe = session.exec(
                            select(Bodega).where(Bodega.codigo_bodega == codigo_bodega.strip().upper())
                        ).first()
                    
                    if existe:
                        st.error(f"❌ Ya existe una bodega con el código {codigo_bodega}")
                    else:
                        nueva_bodega = Bodega(
                            codigo_bodega=codigo_bodega.strip().upper(),
                            nombre_bodega=nombre_bodega.strip(),
                            ubicacion=ubicacion.strip() if ubicacion else None,
                            responsable=responsable.strip() if responsable else None,
                            capacidad_aproximada=capacidad.strip() if capacidad else None,
                            observaciones=observaciones.strip() if observaciones else None,
                            activo=True
                        )
                        
                        if db_module.crear_registro(nueva_bodega, db_engine, st_display_func, nombre_tabla="Bodega"):
                            st.success("✅ Bodega creada exitosamente")
                            st.rerun()
    
    with subtabs[1]:
        st.markdown("### 📋 Bodegas Registradas")
        
        with Session(db_engine) as session:
            bodegas = session.exec(
                select(Bodega).where(Bodega.activo == True)
            ).all()
        
        if bodegas:
            for bodega in bodegas:
                # Contar bienes en esta bodega
                with Session(db_engine) as session:
                    total_bienes = session.exec(
                        select(func.count(BienInventario.id_bien)).where(
                            BienInventario.id_bodega == bodega.id_bodega,
                            BienInventario.activo == True
                        )
                    ).first()
                
                with st.expander(f"🏢 {bodega.codigo_bodega} - {bodega.nombre_bodega} ({total_bienes or 0} bienes)"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if bodega.ubicacion:
                            st.markdown(f"**📍 Ubicación:** {bodega.ubicacion}")
                        if bodega.responsable:
                            st.markdown(f"**👤 Responsable:** {bodega.responsable}")
                    
                    with col2:
                        if bodega.capacidad_aproximada:
                            st.markdown(f"**📦 Capacidad:** {bodega.capacidad_aproximada}")
                        st.metric("Bienes almacenados", total_bienes or 0)
        else:
            st.info("ℹ️ No hay bodegas registradas")
            st.caption("💡 Crea las bodegas B-1, B-2, B-3, B-4, B-5 y B-6")


# ====================================================================
# GESTIÓN DE CATEGORÍAS
# ====================================================================

def crud_categorias_inventario(db_engine, db_module, st_display_func, usuario_actual):
    st.subheader("📂 Categorías de Inventario")
    st.info("💡 Muebles, Electrónicos, Inmuebles, etc.")
    # ... implementación similar


# ====================================================================
# BÚSQUEDA AVANZADA
# ====================================================================

def busqueda_avanzada(db_engine, usuario_actual):
    st.subheader("🔍 Búsqueda Avanzada de Bienes")
    st.info("💡 Disponible para implementar")


# ====================================================================
# REPORTES
# ====================================================================

def reportes_inventario(db_engine, usuario_actual):
    st.subheader("📊 Reportes de Inventario")
    st.info("💡 Reportes por grupo, bodega, estado, etc.")


# ====================================================================
# FUNCIONES AUXILIARES
# ====================================================================

def mostrar_historial_bien(db_engine, id_bien):
    """Muestra el historial de movimientos de un bien"""
    with Session(db_engine) as session:
        movimientos = session.exec(
            select(MovimientoBien).where(
                MovimientoBien.id_bien == id_bien
            ).order_by(MovimientoBien.fecha_movimiento.desc())
        ).all()
    
    if movimientos:
        st.markdown("### 📋 Historial de Movimientos")
        
        for mov in movimientos:
            with Session(db_engine) as session:
                usuario = session.get(Usuario, mov.id_usuario)
                persona_usuario = session.get(Persona, usuario.id_persona) if usuario else None
            
            st.markdown(f"**{mov.tipo_movimiento}** - {mov.fecha_movimiento.strftime('%d/%m/%Y %H:%M')}")
            st.caption(f"Por: {persona_usuario.nombre_completo() if persona_usuario else 'N/A'}")
            
            if mov.motivo:
                st.caption(f"Motivo: {mov.motivo}")
            
            st.markdown("---")
    else:
        st.info("ℹ️ No hay movimientos registrados")
