# crud_finanzas.py - Módulo CRUD de Finanzas
import streamlit as st
from datetime import date, datetime
from decimal import Decimal
from models import (
    PresupuestoAnual, CategoriaFinanciera, Donador, TransaccionFinanciera
)
from models import GrupoParroquial, Usuario, Persona, Actividad
from sqlmodel import Session, select, func
from typing import Optional

# ====================================================================
# FUNCIÓN PRINCIPAL
# ====================================================================

def mostrar_crud_finanzas(db_engine, db_module, db_mode, st_display_func, usuario_actual=None):
    """Módulo completo CRUD para Finanzas"""
    st.header(f"💰 Gestión de Finanzas - Modo: {db_mode}")
    
    st.info("💡 Control financiero por grupo parroquial: presupuestos, ingresos, egresos y donadores")
    
    # Verificar permisos del usuario
    if not verificar_permisos_finanzas(db_engine, usuario_actual):
        st.error("❌ No tienes permisos para acceder a este módulo")
        return
    
    tabs = st.tabs([
        "💰 Transacciones",
        "📊 Presupuestos",
        "🏷️ Categorías",
        "🤝 Donadores",
        "📈 Reportes",
        "📋 Validaciones"
    ])
    
    # ================================================================
    # TAB 1: TRANSACCIONES
    # ================================================================
    with tabs[0]:
        crud_transacciones(db_engine, db_module, st_display_func, usuario_actual)
    
    # ================================================================
    # TAB 2: PRESUPUESTOS
    # ================================================================
    with tabs[1]:
        crud_presupuestos(db_engine, db_module, st_display_func, usuario_actual)
    
    # ================================================================
    # TAB 3: CATEGORÍAS
    # ================================================================
    with tabs[2]:
        crud_categorias(db_engine, db_module, st_display_func, usuario_actual)
    
    # ================================================================
    # TAB 4: DONADORES
    # ================================================================
    with tabs[3]:
        crud_donadores(db_engine, db_module, st_display_func, usuario_actual)
    
    # ================================================================
    # TAB 5: REPORTES
    # ================================================================
    with tabs[4]:
        mostrar_reportes(db_engine, usuario_actual)
    
    # ================================================================
    # TAB 6: VALIDACIONES
    # ================================================================
    with tabs[5]:
        validar_transacciones(db_engine, db_module, st_display_func, usuario_actual)


# ====================================================================
# GESTIÓN DE TRANSACCIONES
# ====================================================================

def crud_transacciones(db_engine, db_module, st_display_func, usuario_actual):
    st.subheader("💰 Registro de Ingresos y Egresos")
    
    subtabs = st.tabs(["➕ Registrar", "📋 Ver Transacciones", "✏️ Editar/Eliminar"])
    
    # REGISTRAR TRANSACCIÓN
    with subtabs[0]:
        st.markdown("### ➕ Nueva Transacción")
        
        with st.form("form_transaccion", clear_on_submit=True):
            # Grupo parroquial
            with Session(db_engine) as session:
                grupos = session.exec(
                    select(GrupoParroquial).where(GrupoParroquial.activo == True)
                ).all()
            
            if not grupos:
                st.error("❌ No hay grupos parroquiales registrados")
                st.form_submit_button("Guardar", disabled=True)
                return
            
            opciones_grupos = {g.id_grupo: g.nombre_grupo for g in grupos}
            id_grupo = st.selectbox(
                "Grupo Parroquial (*)",
                options=opciones_grupos.keys(),
                format_func=lambda x: opciones_grupos[x],
                key="trans_grupo"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                tipo = st.selectbox(
                    "Tipo (*)",
                    options=["Ingreso", "Egreso"],
                    key="trans_tipo"
                )
                
                fecha_trans = st.date_input(
                    "Fecha (*)",
                    value=date.today(),
                    max_value=date.today(),
                    key="trans_fecha"
                )
                
                # Categorías del grupo seleccionado
                with Session(db_engine) as session:
                    categorias = session.exec(
                        select(CategoriaFinanciera).where(
                            CategoriaFinanciera.id_grupo == id_grupo,
                            CategoriaFinanciera.tipo == tipo,
                            CategoriaFinanciera.activo == True
                        )
                    ).all()
                
                if not categorias:
                    st.warning(f"⚠️ No hay categorías de {tipo} para este grupo")
                    id_categoria = None
                else:
                    opciones_cat = {c.id_categoria: c.nombre_categoria for c in categorias}
                    id_categoria = st.selectbox(
                        "Categoría (*)",
                        options=opciones_cat.keys(),
                        format_func=lambda x: opciones_cat[x],
                        key="trans_categoria"
                    )
            
            with col2:
                monto = st.number_input(
                    "Monto (*)",
                    min_value=0.01,
                    value=100.00,
                    step=0.01,
                    format="%.2f",
                    key="trans_monto"
                )
                
                moneda = st.selectbox(
                    "Moneda (*)",
                    options=["MXN", "USD"],
                    index=0,
                    key="trans_moneda"
                )
                
                metodo_pago = st.selectbox(
                    "Método de Pago (*)",
                    options=["Efectivo", "Transferencia", "Cheque", "Tarjeta", "Otro"],
                    key="trans_metodo"
                )
            
            concepto = st.text_input(
                "Concepto (*)",
                max_chars=500,
                placeholder="Descripción breve de la transacción",
                key="trans_concepto"
            )
            
            descripcion_detallada = st.text_area(
                "Descripción Detallada",
                placeholder="Información adicional sobre la transacción",
                key="trans_desc"
            )
            
            # Donador (solo para ingresos)
            if tipo == "Ingreso":
                st.markdown("### 🤝 Donador (opcional)")
                
                with Session(db_engine) as session:
                    donadores = session.exec(
                        select(Donador).where(Donador.activo == True)
                    ).all()
                
                if donadores:
                    opciones_don = {0: "-- Sin donador --"}
                    opciones_don.update({
                        d.id_donador: f"{d.nombre_completo} ({d.tipo_donador})"
                        for d in donadores
                    })
                    id_donador = st.selectbox(
                        "Donador:",
                        options=opciones_don.keys(),
                        format_func=lambda x: opciones_don[x],
                        key="trans_donador"
                    )
                    id_donador = id_donador if id_donador != 0 else None
                else:
                    id_donador = None
            else:
                id_donador = None
            
            # Actividad (opcional)
            st.markdown("### 🎯 Asociar a Actividad (opcional)")
            
            with Session(db_engine) as session:
                actividades = session.exec(
                    select(Actividad).where(
                        Actividad.id_grupo_parroquial == id_grupo,
                        Actividad.activo == True
                    )
                ).all()
            
            if actividades:
                opciones_act = {0: "-- Sin actividad --"}
                opciones_act.update({
                    a.id_actividad: f"{a.nombre_actividad} ({a.ciclo or 'N/A'})"
                    for a in actividades
                })
                id_actividad = st.selectbox(
                    "Actividad:",
                    options=opciones_act.keys(),
                    format_func=lambda x: opciones_act[x],
                    key="trans_actividad"
                )
                id_actividad = id_actividad if id_actividad != 0 else None
            else:
                id_actividad = None
            
            referencia = st.text_input(
                "Referencia/Folio",
                max_chars=100,
                placeholder="Número de cheque, referencia bancaria, etc.",
                key="trans_ref"
            )
            
            observaciones = st.text_area(
                "Observaciones",
                key="trans_obs"
            )
            
            st.markdown("---")
            st.caption("💡 Nota: Puedes adjuntar comprobantes después de guardar")
            
            submitted = st.form_submit_button("💾 Registrar Transacción", type="primary", use_container_width=True)
            
            if submitted:
                if not concepto or not id_categoria:
                    st.error("❌ Concepto y categoría son obligatorios")
                else:
                    nueva_trans = TransaccionFinanciera(
                        id_grupo=id_grupo,
                        tipo=tipo,
                        fecha_transaccion=fecha_trans,
                        monto=Decimal(str(monto)),
                        moneda=moneda,
                        id_categoria=id_categoria,
                        id_actividad=id_actividad,
                        id_donador=id_donador,
                        concepto=concepto.strip(),
                        descripcion_detallada=descripcion_detallada.strip() if descripcion_detallada else None,
                        metodo_pago=metodo_pago,
                        referencia=referencia.strip() if referencia else None,
                        id_usuario_registro=usuario_actual.id_usuario if usuario_actual else 1,
                        estado="Registrada",
                        observaciones=observaciones.strip() if observaciones else None
                    )
                    
                    if db_module.crear_registro(nueva_trans, db_engine, st_display_func, nombre_tabla="Transacción"):
                        st.success(f"✅ {tipo} registrado exitosamente")
                        st.balloons()
                        st.rerun()
    
    # VER TRANSACCIONES
    with subtabs[1]:
        st.markdown("### 📋 Transacciones Registradas")
        
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
                key="ver_trans_grupo"
            )
        
        with col2:
            filtro_tipo = st.selectbox(
                "Tipo:",
                options=["Todos", "Ingreso", "Egreso"],
                key="ver_trans_tipo"
            )
        
        with col3:
            mes_actual = date.today().month
            filtro_mes = st.selectbox(
                "Mes:",
                options=list(range(13)),
                format_func=lambda x: "Todos" if x == 0 else [
                    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
                ][x-1],
                index=mes_actual,
                key="ver_trans_mes"
            )
        
        with col4:
            anio_actual = date.today().year
            filtro_anio = st.number_input(
                "Año:",
                min_value=2020,
                max_value=2030,
                value=anio_actual,
                key="ver_trans_anio"
            )
        
        # Consultar transacciones
        with Session(db_engine) as session:
            statement = select(TransaccionFinanciera).order_by(
                TransaccionFinanciera.fecha_transaccion.desc()
            )
            
            if filtro_grupo != 0:
                statement = statement.where(TransaccionFinanciera.id_grupo == filtro_grupo)
            
            if filtro_tipo != "Todos":
                statement = statement.where(TransaccionFinanciera.tipo == filtro_tipo)
            
            # Filtro de fecha
            if filtro_mes != 0:
                from sqlalchemy import extract
                statement = statement.where(
                    extract('month', TransaccionFinanciera.fecha_transaccion) == filtro_mes
                )
            
            statement = statement.where(
                extract('year', TransaccionFinanciera.fecha_transaccion) == filtro_anio
            )
            
            transacciones = session.exec(statement).all()
        
        if transacciones:
            st.markdown(f"**Total de transacciones:** {len(transacciones)}")
            
            # Resumen financiero
            ingresos_total = sum(
                float(t.monto) for t in transacciones 
                if t.tipo == "Ingreso" and t.moneda == "MXN"
            )
            egresos_total = sum(
                float(t.monto) for t in transacciones 
                if t.tipo == "Egreso" and t.moneda == "MXN"
            )
            balance = ingresos_total - egresos_total
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Ingresos (MXN)", f"${ingresos_total:,.2f}")
            with col2:
                st.metric("💸 Egresos (MXN)", f"${egresos_total:,.2f}")
            with col3:
                delta_color = "normal" if balance >= 0 else "inverse"
                st.metric("📊 Balance", f"${balance:,.2f}", delta=f"${balance:,.2f}")
            
            st.markdown("---")
            
            # Tabla de transacciones
            data = []
            with Session(db_engine) as session:
                for t in transacciones:
                    grupo = session.get(GrupoParroquial, t.id_grupo)
                    categoria = session.get(CategoriaFinanciera, t.id_categoria)
                    
                    icono = "💰" if t.tipo == "Ingreso" else "💸"
                    estado_icono = "✅" if t.estado == "Validada" else "📝"
                    
                    data.append({
                        "ID": t.id_transaccion,
                        "": estado_icono,
                        "Fecha": t.fecha_transaccion.strftime("%d/%m/%Y"),
                        "Tipo": f"{icono} {t.tipo}",
                        "Concepto": t.concepto[:50] + "..." if len(t.concepto) > 50 else t.concepto,
                        "Categoría": categoria.nombre_categoria if categoria else "N/A",
                        "Monto": f"${float(t.monto):,.2f} {t.moneda}",
                        "Grupo": grupo.nombre_grupo if grupo else "N/A",
                        "Estado": t.estado
                    })
            
            st.dataframe(data, use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ No hay transacciones con los filtros seleccionados")
    
    # EDITAR/ELIMINAR
    with subtabs[2]:
        st.info("💡 Edición y eliminación disponible para implementar")


# ====================================================================
# GESTIÓN DE PRESUPUESTOS
# ====================================================================

def crud_presupuestos(db_engine, db_module, st_display_func, usuario_actual):
    st.subheader("📊 Presupuestos Anuales")
    
    subtabs = st.tabs(["➕ Crear Presupuesto", "📋 Ver Presupuestos"])
    
    with subtabs[0]:
        st.markdown("### ➕ Nuevo Presupuesto Anual")
        
        with st.form("form_presupuesto", clear_on_submit=True):
            with Session(db_engine) as session:
                grupos = session.exec(
                    select(GrupoParroquial).where(GrupoParroquial.activo == True)
                ).all()
            
            if not grupos:
                st.error("❌ No hay grupos parroquiales")
                st.form_submit_button("Guardar", disabled=True)
                return
            
            col1, col2 = st.columns(2)
            
            with col1:
                opciones_grupos = {g.id_grupo: g.nombre_grupo for g in grupos}
                id_grupo = st.selectbox(
                    "Grupo Parroquial (*)",
                    options=opciones_grupos.keys(),
                    format_func=lambda x: opciones_grupos[x],
                    key="pres_grupo"
                )
                
                anio = st.number_input(
                    "Año (*)",
                    min_value=2020,
                    max_value=2030,
                    value=date.today().year,
                    key="pres_anio"
                )
            
            with col2:
                monto_total = st.number_input(
                    "Monto Total (*)",
                    min_value=0.01,
                    value=10000.00,
                    step=100.00,
                    format="%.2f",
                    key="pres_monto"
                )
                
                moneda = st.selectbox(
                    "Moneda (*)",
                    options=["MXN", "USD"],
                    key="pres_moneda"
                )
            
            descripcion = st.text_area(
                "Descripción del Presupuesto",
                placeholder="Objetivos, proyectos contemplados, etc.",
                key="pres_desc"
            )
            
            observaciones = st.text_area(
                "Observaciones",
                key="pres_obs"
            )
            
            submitted = st.form_submit_button("💾 Crear Presupuesto", type="primary", use_container_width=True)
            
            if submitted:
                # Verificar si ya existe presupuesto para ese grupo y año
                with Session(db_engine) as session:
                    existe = session.exec(
                        select(PresupuestoAnual).where(
                            PresupuestoAnual.id_grupo == id_grupo,
                            PresupuestoAnual.anio == anio
                        )
                    ).first()
                
                if existe:
                    st.error(f"❌ Ya existe un presupuesto para este grupo en {anio}")
                else:
                    nuevo_pres = PresupuestoAnual(
                        id_grupo=id_grupo,
                        anio=anio,
                        monto_total=Decimal(str(monto_total)),
                        moneda=moneda,
                        descripcion=descripcion.strip() if descripcion else None,
                        id_usuario_creador=usuario_actual.id_usuario if usuario_actual else 1,
                        estado="Borrador",
                        observaciones=observaciones.strip() if observaciones else None
                    )
                    
                    if db_module.crear_registro(nuevo_pres, db_engine, st_display_func, nombre_tabla="Presupuesto"):
                        st.success("✅ Presupuesto creado exitosamente")
                        st.rerun()
    
    with subtabs[1]:
        st.markdown("### 📋 Presupuestos Registrados")
        
        with Session(db_engine) as session:
            presupuestos = session.exec(
                select(PresupuestoAnual).order_by(
                    PresupuestoAnual.anio.desc()
                )
            ).all()
        
        if presupuestos:
            for pres in presupuestos:
                with Session(db_engine) as session:
                    grupo = session.get(GrupoParroquial, pres.id_grupo)
                
                estado_icono = {"Borrador": "📝", "Aprobado": "✅", "Vigente": "🟢"}.get(pres.estado, "📋")
                
                with st.expander(f"{estado_icono} {pres.anio} - {grupo.nombre_grupo if grupo else 'N/A'} - ${float(pres.monto_total):,.2f} {pres.moneda}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Monto:** ${float(pres.monto_total):,.2f} {pres.moneda}")
                        st.markdown(f"**Estado:** {pres.estado}")
                        if pres.descripcion:
                            st.markdown(f"**Descripción:** {pres.descripcion}")
                    
                    with col2:
                        st.caption(f"Creado: {pres.fecha_creacion.strftime('%d/%m/%Y')}")
                        if pres.fecha_aprobacion:
                            st.caption(f"Aprobado: {pres.fecha_aprobacion.strftime('%d/%m/%Y')}")
        else:
            st.info("ℹ️ No hay presupuestos registrados")


# ====================================================================
# GESTIÓN DE CATEGORÍAS
# ====================================================================

def crud_categorias(db_engine, db_module, st_display_func, usuario_actual):
    st.subheader("🏷️ Categorías Financieras por Grupo")
    st.info("💡 Cada grupo define sus propias categorías de ingresos y egresos")
    
    # ... implementación similar


# ====================================================================
# GESTIÓN DE DONADORES
# ====================================================================

def crud_donadores(db_engine, db_module, st_display_func, usuario_actual):
    st.subheader("🤝 Registro de Donadores")
    # ... implementación similar


# ====================================================================
# REPORTES
# ====================================================================

def mostrar_reportes(db_engine, usuario_actual):
    st.subheader("📈 Reportes Financieros")
    st.info("💡 Reportes mensuales y anuales disponibles para implementar")


# ====================================================================
# VALIDACIONES
# ====================================================================

def validar_transacciones(db_engine, db_module, st_display_func, usuario_actual):
    st.subheader("📋 Validación de Transacciones")
    st.info("💡 Solo usuarios autorizados pueden validar transacciones")


# ====================================================================
# VERIFICACIÓN DE PERMISOS
# ====================================================================

def verificar_permisos_finanzas(db_engine, usuario_actual) -> bool:
    """Verifica si el usuario tiene permisos para finanzas"""
    if not usuario_actual:
        return False
    
    # TODO: Implementar lógica de permisos basada en PerfilUsuario
    return True
