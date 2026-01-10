# crud_catecumenos.py - ACTUALIZADO con Gestión de Generaciones
import streamlit as st
from datetime import date
from models import Catecumeno, Persona, CentroCatecismo, GrupoCatequesis
from utils import (
    buscar_persona_por_curp, obtener_lista_personas, 
    formatear_fecha
)
from sqlmodel import Session, select

# ====================================================================
# FUNCIONES AUXILIARES
# ====================================================================

def generar_ciclo_actual() -> str:
    """
    Genera el ciclo escolar actual basado en la fecha.
    Ejemplo: Si estamos en septiembre 2026 → "2026-2027"
    """
    hoy = date.today()
    
    # Si estamos entre enero-julio, el ciclo inició el año anterior
    if hoy.month >= 1 and hoy.month <= 7:
        year_inicio = hoy.year - 1
        year_fin = hoy.year
    else:  # agosto-diciembre, el ciclo inicia este año
        year_inicio = hoy.year
        year_fin = hoy.year + 1
    
    return f"{year_inicio}-{year_fin}"


def obtener_generaciones_disponibles(db_engine) -> list:
    """
    Obtiene todas las generaciones/ciclos únicos registrados.
    """
    if not db_engine:
        return []
    
    try:
        with Session(db_engine) as session:
            # Obtener generaciones únicas de catecúmenos
            catecumenos = session.exec(select(Catecumeno)).all()
            generaciones = set()
            
            for cat in catecumenos:
                if cat.generacion:
                    generaciones.add(cat.generacion)
            
            return sorted(list(generaciones), reverse=True)  # Más recientes primero
    except:
        return []


def sugerir_proxima_generacion(generacion_actual: str) -> str:
    """
    Sugiere la siguiente generación basada en la actual.
    Ejemplo: "2025-2026" → "2026-2027"
    """
    try:
        if "-" in generacion_actual:
            year_inicio = int(generacion_actual.split("-")[0])
            return f"{year_inicio + 1}-{year_inicio + 2}"
        return generacion_actual
    except:
        return generar_ciclo_actual()


# ====================================================================
# FUNCIÓN PRINCIPAL
# ====================================================================

def mostrar_crud_catecumenos(db_engine, db_module, db_mode, st_display_func):
    """Módulo completo CRUD para Catecúmenos con gestión de generaciones."""
    st.header(f"📚 Gestión de Catecúmenos - Modo: {db_mode}")
    
    st.info("💡 Un catecúmeno es una persona en preparación para un sacramento. Cada generación representa un ciclo escolar.")
    
    tabs = st.tabs([
        "➕ Registrar", 
        "📋 Ver por Generación", 
        "📊 Estadísticas",
        "✏️ Actualizar", 
        "🗑️ Eliminar"
    ])
    
    # ================================================================
    # TAB 1: CREAR
    # ================================================================
    with tabs[0]:
        st.subheader("➕ Registrar Nuevo Catecúmeno")
        
        st.markdown("### 🔍 Paso 1: Buscar Persona")
        st.caption("El catecúmeno debe estar registrado como persona")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            curp_busqueda = st.text_input(
                "Buscar por CURP (*)",
                max_chars=18,
                key="cat_crear_curp"
            )
        
        persona_encontrada = None
        if curp_busqueda:
            persona_encontrada = buscar_persona_por_curp(curp_busqueda, db_engine)
            if persona_encontrada:
                st.success(f"✅ {persona_encontrada.nombre_completo()}")
        
        with col2:
            personas = obtener_lista_personas(db_engine)
            
            if not personas:
                st.error("❌ No hay personas registradas")
            else:
                opciones = {0: "-- Selecciona --"}
                opciones.update({
                    p.id_persona: f"{p.nombre_completo()} - {p.curp or 'Sin CURP'}"
                    for p in personas
                })
                id_persona_sel = st.selectbox(
                    "O selecciona:",
                    options=opciones.keys(),
                    format_func=lambda x: opciones[x],
                    key="cat_crear_select"
                )
        
        id_persona_final = None
        if persona_encontrada:
            id_persona_final = persona_encontrada.id_persona
        elif id_persona_sel != 0:
            id_persona_final = id_persona_sel
        
        if id_persona_final:
            # Verificar si ya es catecúmeno activo en esta generación
            ciclo_actual = generar_ciclo_actual()
            
            with Session(db_engine) as session:
                ya_catecumeno = session.exec(
                    select(Catecumeno).where(
                        Catecumeno.id_persona == id_persona_final,
                        Catecumeno.estado == "activo",
                        Catecumeno.generacion == ciclo_actual
                    )
                ).first()
            
            if ya_catecumeno:
                st.warning(f"⚠️ Ya es catecúmeno activo en generación {ciclo_actual}: {ya_catecumeno.sacramento_preparacion}")
            
            st.markdown("---")
            st.markdown("### 📝 Paso 2: Datos del Catecumenado")
            
            with st.form("form_crear_catecumeno", clear_on_submit=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    sacramento = st.selectbox(
                        "Sacramento (*)",
                        options=["Bautizo", "Confirmación", "Eucaristía", "Renovación Bautismal"],
                        key="cat_sacramento"
                    )
                    
                    fecha_inicio = st.date_input(
                        "Fecha Inicio (*)",
                        value=date.today(),
                        key="cat_fecha_inicio"
                    )
                    
                    estado = st.selectbox(
                        "Estado (*)",
                        options=["activo", "completado", "retirado"],
                        key="cat_estado"
                    )
                
                with col2:
                    nivel = st.text_input(
                        "Nivel",
                        placeholder="Ej: Nivel 1, Grupo 300",
                        key="cat_nivel"
                    )
                    
                    fecha_fin = st.date_input(
                        "Fecha Fin",
                        value=None,
                        key="cat_fecha_fin",
                        help="Dejar vacío si aún está en proceso"
                    )
                    
                    # ✅ NUEVO: Campo generación
                    generaciones_existentes = obtener_generaciones_disponibles(db_engine)
                    
                    col2_1, col2_2 = st.columns([2, 1])
                    with col2_1:
                        if generaciones_existentes:
                            opciones_gen = ["-- Usar ciclo actual --"] + generaciones_existentes + ["-- Crear nuevo --"]
                            generacion_opcion = st.selectbox(
                                "Generación/Ciclo (*)",
                                options=opciones_gen,
                                help="Ciclo escolar o generación del catecúmeno",
                                key="cat_generacion_select"
                            )
                        else:
                            generacion_opcion = "-- Usar ciclo actual --"
                            st.info(f"💡 Primera generación: {ciclo_actual}")
                    
                    with col2_2:
                        if generacion_opcion == "-- Crear nuevo --":
                            generacion_custom = st.text_input(
                                "Nueva:",
                                value=sugerir_proxima_generacion(generaciones_existentes[0] if generaciones_existentes else ciclo_actual),
                                placeholder="2026-2027",
                                key="cat_generacion_custom"
                            )
                        else:
                            generacion_custom = None
                    
                    # Determinar generación final
                    if generacion_opcion == "-- Usar ciclo actual --":
                        generacion_final = ciclo_actual
                    elif generacion_opcion == "-- Crear nuevo --":
                        generacion_final = generacion_custom if generacion_custom else ciclo_actual
                    else:
                        generacion_final = generacion_opcion
                
                st.markdown("---")
                st.markdown("### 👥 Asignaciones")
                
                # Grupo de Catequesis
                with Session(db_engine) as session:
                    grupos = session.exec(
                        select(GrupoCatequesis).where(GrupoCatequesis.activo == True)
                    ).all()

                if grupos:
                    opciones_grupos = {0: "-- Sin Grupo --"}
                    for g in grupos:
                        # Mostrar generación activa del grupo si existe
                        nombre_grupo = g.nombre_grupo
                        if g.generacion_activa:
                            nombre_grupo += f" (Gen: {g.generacion_activa})"
                        opciones_grupos[g.id_grupo] = nombre_grupo
                    
                    id_grupo_sel = st.selectbox(
                        "Grupo de Catequesis:",
                        options=opciones_grupos.keys(),
                        format_func=lambda x: opciones_grupos[x],
                        key="cat_grupo"
                    )
                else:
                    st.info("ℹ️ No hay grupos de catequesis")
                    id_grupo_sel = 0

                # Centro de Catecismo
                with Session(db_engine) as session:
                    centros = session.exec(select(CentroCatecismo)).all()
                
                if centros:
                    opciones_centros = {0: "-- Sin Centro --"}
                    opciones_centros.update({
                        c.id_centro: f"{c.nombre_centro} - {c.clave_centro}"
                        for c in centros
                    })
                    id_centro_sel = st.selectbox(
                        "Centro de Catecismo:",
                        options=opciones_centros.keys(),
                        format_func=lambda x: opciones_centros[x],
                        key="cat_centro"
                    )
                else:
                    st.info("ℹ️ No hay centros de catecismo")
                    id_centro_sel = 0
                
                st.markdown("---")
                observaciones = st.text_area(
                    "Observaciones",
                    placeholder="Notas adicionales...",
                    key="cat_obs"
                )
                
                # Resumen antes de guardar
                st.info(f"📅 Se registrará en la generación: **{generacion_final}**")
                
                st.markdown("---")
                submitted = st.form_submit_button("💾 Registrar", type="primary", use_container_width=True)
                
                if submitted:
                    nuevo = Catecumeno(
                        id_persona=id_persona_final,
                        sacramento_preparacion=sacramento,
                        fecha_inicio=fecha_inicio,
                        fecha_fin=fecha_fin if fecha_fin else None,
                        id_grupo_catequesis=id_grupo_sel if id_grupo_sel != 0 else None,
                        id_centro_catecismo=id_centro_sel if id_centro_sel != 0 else None,
                        estado=estado,
                        nivel=nivel.strip() if nivel else None,
                        generacion=generacion_final,  # ✅ NUEVO
                        observaciones=observaciones.strip() if observaciones else None
                    )
                    
                    if db_module.crear_registro(nuevo, db_engine, st_display_func, "Catecúmeno"):
                        st.success(f"✅ Catecúmeno registrado en generación {generacion_final}")
                        st.rerun()
        else:
            st.info("💡 Busca o selecciona una persona para continuar")
    
    # ================================================================
    # TAB 2: VER POR GENERACIÓN
    # ================================================================
    with tabs[1]:
        st.subheader("📋 Catecúmenos por Generación")
        
        # Filtros
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            generaciones = obtener_generaciones_disponibles(db_engine)
            if generaciones:
                opciones_gen = ["Todas"] + generaciones
                filtro_generacion = st.selectbox(
                    "Generación:",
                    options=opciones_gen,
                    key="filtro_generacion"
                )
            else:
                filtro_generacion = "Todas"
                st.info("ℹ️ No hay generaciones registradas")
        
        with col2:
            filtro_estado = st.selectbox(
                "Estado:",
                options=["Todos", "activo", "completado", "retirado"],
                key="filtro_estado_cat"
            )
        
        with col3:
            filtro_sacramento = st.selectbox(
                "Sacramento:",
                options=["Todos", "Bautizo", "Confirmación", "Eucaristía", "Renovación Bautismal"],
                key="filtro_sacramento_cat"
            )
        
        with col4:
            buscar_curp = st.text_input("Buscar CURP:", key="buscar_curp_cat")
        
        # Consultar catecúmenos
        with Session(db_engine) as session:
            statement = select(Catecumeno)
            
            if filtro_generacion != "Todas":
                statement = statement.where(Catecumeno.generacion == filtro_generacion)
            
            if filtro_estado != "Todos":
                statement = statement.where(Catecumeno.estado == filtro_estado)
            
            if filtro_sacramento != "Todos":
                statement = statement.where(Catecumeno.sacramento_preparacion == filtro_sacramento)
            
            catecumenos = session.exec(statement).all()
            
            if buscar_curp:
                catecumenos = [
                    c for c in catecumenos 
                    if (persona := session.get(Persona, c.id_persona)) 
                    and persona.curp 
                    and buscar_curp.upper() in persona.curp.upper()
                ]
        
        if catecumenos:
            st.markdown(f"**Total:** {len(catecumenos)} catecúmenos")
            
            # Agrupar por generación
            por_generacion = {}
            for cat in catecumenos:
                gen = cat.generacion or "Sin generación"
                if gen not in por_generacion:
                    por_generacion[gen] = []
                por_generacion[gen].append(cat)
            
            # Mostrar por generación
            for gen in sorted(por_generacion.keys(), reverse=True):
                lista = por_generacion[gen]
                
                with st.expander(f"📅 Generación {gen} - {len(lista)} catecúmenos", expanded=(filtro_generacion == gen or len(por_generacion) == 1)):
                    data = []
                    with Session(db_engine) as session:
                        for cat in lista:
                            persona = session.get(Persona, cat.id_persona)
                            grupo = session.get(GrupoCatequesis, cat.id_grupo_catequesis) if cat.id_grupo_catequesis else None
                            centro = session.get(CentroCatecismo, cat.id_centro_catecismo) if cat.id_centro_catecismo else None
                            
                            dias = (date.today() - cat.fecha_inicio).days
                            estado_display = f"{'✅' if cat.estado == 'activo' else '🎓' if cat.estado == 'completado' else '❌'} {cat.estado}"
                            if cat.estado == "activo":
                                estado_display += f" ({dias} días)"
                            
                            data.append({
                                "ID": cat.id_catecumeno,
                                "Catecúmeno": persona.nombre_completo() if persona else "N/A",
                                "CURP": persona.curp or "Sin CURP",
                                "Sacramento": cat.sacramento_preparacion,
                                "Nivel": cat.nivel or "N/A",
                                "Grupo": grupo.nombre_grupo if grupo else "Sin grupo",
                                "Estado": estado_display,
                                "Centro": centro.nombre_centro if centro else "N/A",
                                "Fecha Inicio": formatear_fecha(cat.fecha_inicio)
                            })
                    
                    st.dataframe(data, use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ No hay catecúmenos con los filtros seleccionados")
    
    # ================================================================
    # TAB 3: ESTADÍSTICAS
    # ================================================================
    with tabs[2]:
        st.subheader("📊 Estadísticas por Generación")
        
        with Session(db_engine) as session:
            catecumenos = session.exec(select(Catecumeno)).all()
        
        if catecumenos:
            # Estadísticas generales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total = len(catecumenos)
                st.metric("Total Catecúmenos", total)
            
            with col2:
                activos = len([c for c in catecumenos if c.estado == "activo"])
                st.metric("Activos", activos)
            
            with col3:
                completados = len([c for c in catecumenos if c.estado == "completado"])
                st.metric("Completados", completados)
            
            with col4:
                generaciones = len(set([c.generacion for c in catecumenos if c.generacion]))
                st.metric("Generaciones", generaciones)
            
            st.markdown("---")
            
            # Por generación
            st.markdown("### 📅 Detalle por Generación")
            
            por_generacion = {}
            for cat in catecumenos:
                gen = cat.generacion or "Sin generación"
                if gen not in por_generacion:
                    por_generacion[gen] = {
                        "total": 0,
                        "activos": 0,
                        "completados": 0,
                        "retirados": 0,
                        "por_sacramento": {}
                    }
                
                por_generacion[gen]["total"] += 1
                por_generacion[gen][cat.estado + "s"] += 1
                
                if cat.sacramento_preparacion not in por_generacion[gen]["por_sacramento"]:
                    por_generacion[gen]["por_sacramento"][cat.sacramento_preparacion] = 0
                por_generacion[gen]["por_sacramento"][cat.sacramento_preparacion] += 1
            
            for gen in sorted(por_generacion.keys(), reverse=True):
                stats = por_generacion[gen]
                
                with st.expander(f"📅 {gen} - {stats['total']} catecúmenos"):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total", stats["total"])
                    with col2:
                        st.metric("Activos", stats["activos"])
                    with col3:
                        st.metric("Completados", stats["completados"])
                    with col4:
                        st.metric("Retirados", stats["retirados"])
                    
                    st.markdown("**Por Sacramento:**")
                    for sacramento, cantidad in stats["por_sacramento"].items():
                        porcentaje = (cantidad / stats["total"]) * 100
                        st.progress(porcentaje / 100)
                        st.caption(f"{sacramento}: {cantidad} ({porcentaje:.1f}%)")
        else:
            st.info("ℹ️ No hay catecúmenos registrados")
    
    # ================================================================
    # TAB 4: ACTUALIZAR
    # ================================================================
    with tabs[3]:
        st.subheader("✏️ Actualizar Catecúmeno")
        
        with Session(db_engine) as session:
            catecumenos = session.exec(select(Catecumeno)).all()
        
        if catecumenos:
            # Selector con información de generación
            opciones_cat = {}
            with Session(db_engine) as session:
                for cat in catecumenos:
                    persona = session.get(Persona, cat.id_persona)
                    nombre = persona.nombre_completo() if persona else "N/A"
                    gen_str = f" (Gen: {cat.generacion})" if cat.generacion else ""
                    opciones_cat[cat.id_catecumeno] = f"{nombre} - {cat.sacramento_preparacion}{gen_str}"
            
            id_cat_sel = st.selectbox(
                "Selecciona el catecúmeno:",
                options=opciones_cat.keys(),
                format_func=lambda x: opciones_cat[x],
                key="upd_cat_sel"
            )
            
            catecumeno = next((c for c in catecumenos if c.id_catecumeno == id_cat_sel), None)
            
            if catecumeno:
                st.markdown("---")
                
                with st.form("form_upd_catecumeno"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        upd_sacramento = st.selectbox(
                            "Sacramento",
                            options=["Bautizo", "Confirmación", "Eucaristía", "Renovación Bautismal"],
                            index=["Bautizo", "Confirmación", "Eucaristía", "Renovación Bautismal"].index(catecumeno.sacramento_preparacion),
                            key="upd_sacramento"
                        )
                        
                        upd_fecha_inicio = st.date_input(
                            "Fecha Inicio",
                            value=catecumeno.fecha_inicio,
                            key="upd_fecha_inicio"
                        )
                        
                        upd_estado = st.selectbox(
                            "Estado",
                            options=["activo", "completado", "retirado"],
                            index=["activo", "completado", "retirado"].index(catecumeno.estado),
                            key="upd_estado"
                        )
                    
                    with col2:
                        upd_nivel = st.text_input(
                            "Nivel",
                            value=catecumeno.nivel or "",
                            key="upd_nivel"
                        )
                        
                        upd_fecha_fin = st.date_input(
                            "Fecha Fin",
                            value=catecumeno.fecha_fin if catecumeno.fecha_fin else None,
                            key="upd_fecha_fin"
                        )
                        
                        # ✅ Actualizar generación
                        generaciones = obtener_generaciones_disponibles(db_engine)
                        if catecumeno.generacion and catecumeno.generacion in generaciones:
                            idx_gen = generaciones.index(catecumeno.generacion)
                        else:
                            idx_gen = 0
                        
                        upd_generacion = st.selectbox(
                            "Generación",
                            options=generaciones if generaciones else [generar_ciclo_actual()],
                            index=idx_gen,
                            key="upd_generacion"
                        )
                    
                    upd_obs = st.text_area(
                        "Observaciones",
                        value=catecumeno.observaciones or "",
                        key="upd_obs"
                    )
                    
                    submitted = st.form_submit_button("💾 Actualizar", type="primary", use_container_width=True)
                    
                    if submitted:
                        datos = {
                            "sacramento_preparacion": upd_sacramento,
                            "fecha_inicio": upd_fecha_inicio,
                            "fecha_fin": upd_fecha_fin if upd_fecha_fin else None,
                            "estado": upd_estado,
                            "nivel": upd_nivel.strip() if upd_nivel else None,
                            "generacion": upd_generacion,  # ✅ NUEVO
                            "observaciones": upd_obs.strip() if upd_obs else None
                        }
                        
                        if db_module.actualizar_registro(
                            Catecumeno,
                            catecumeno.id_catecumeno,
                            datos,
                            db_engine,
                            st_display_func,
                            "Catecúmeno"
                        ):
                            st.rerun()
        else:
            st.info("ℹ️ No hay catecúmenos para actualizar")
    
    # ================================================================
    # TAB 5: ELIMINAR
    # ================================================================
    with tabs[4]:
        st.subheader("🗑️ Eliminar Catecúmeno")
        st.info("💡 Eliminar disponible para implementar")