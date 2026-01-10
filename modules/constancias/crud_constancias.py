# modules/constancias/crud_constancias_completo.py
"""
Módulo Completo de Constancias Sacramentales con:
- Validación de seguridad (CURP + apellido padrino/madrina)
- Desglose de IVA
- Generación de PDF con plantilla PNG
- Código QR integrado
- Pago en línea (PayU) y efectivo
"""

import streamlit as st
from datetime import datetime, date
from decimal import Decimal
import json
import hashlib
import qrcode
from io import BytesIO
import base64
from PIL import Image, ImageDraw, ImageFont
from sqlmodel import Session, select, func
from typing import Optional, Dict, Tuple

from models import (
    SolicitudConstancia, ConstanciaEmitida, HistorialTransaccionConstancia,
    ConfiguracionConstancia, VerificacionConstancia, ConfiguracionCampoPlantilla
)
from models import (
    SacramentoBautizo, SacramentoConfirmacion, SacramentoEucaristia,
    SacramentoMatrimonio, Persona, Comunidad, Presbitero
)
from components.validadores import validar_curp, validar_email

# ====================================================================
# CONSTANTES
# ====================================================================

ESTADOS_SOLICITUD = {
    "Pendiente_Validacion": "🔒 Pendiente de Validación",
    "Validada": "✅ Validada",
    "Pendiente_Pago": "💳 Pendiente de Pago",
    "Pagada": "✅ Pagada",
    "Procesando": "⏳ Procesando",
    "Emitida": "📄 Emitida",
    "Cancelada": "❌ Cancelada",
    "Rechazada": "🚫 Rechazada"
}

TIPOS_SACRAMENTO = ["Bautizo", "Confirmación", "Eucaristía", "Matrimonio"]

# ====================================================================
# FUNCIÓN PRINCIPAL
# ====================================================================

def mostrar_crud_constancias(db_engine, db_module, db_mode, st_display_func, usuario_actual=None):
    """Módulo principal de constancias"""
    st.header(f"📄 Constancias Sacramentales - Modo: {db_mode}")
    
    st.info("""
    💡 **Sistema de Constancias Oficiales**
    - Validación de seguridad con CURP o datos personales
    - Verificación de padrino/madrina
    - Pago en línea o efectivo con desglose de IVA
    - Código QR de autenticidad
    """)
    
    tabs = st.tabs([
        "📝 Solicitar",
        "🔐 Validar",
        "💳 Pagos",
        "📄 Emitidas",
        "🔍 Verificar QR",
        "⚙️ Configuración",
        "📊 Reportes"
    ])
    
    with tabs[0]:
        solicitar_constancia(db_engine, db_module, st_display_func)
    
    with tabs[1]:
        validar_solicitudes(db_engine, db_module, st_display_func, usuario_actual)
    
    with tabs[2]:
        gestionar_pagos(db_engine, db_module, st_display_func, usuario_actual)
    
    with tabs[3]:
        constancias_emitidas(db_engine, db_module, st_display_func, usuario_actual)
    
    with tabs[4]:
        verificar_qr_publico(db_engine)
    
    with tabs[5]:
        configuracion_constancias(db_engine, db_module, st_display_func, usuario_actual)
    
    with tabs[6]:
        reportes_constancias(db_engine)


# ====================================================================
# PASO 1: SOLICITAR CONSTANCIA (PÚBLICO)
# ====================================================================

def solicitar_constancia(db_engine, db_module, st_display_func):
    """Formulario público para solicitar constancia"""
    st.subheader("📝 Solicitar Constancia Sacramental")
    
    # Obtener configuración
    with Session(db_engine) as session:
        config = session.exec(
            select(ConfiguracionConstancia).where(
                ConfiguracionConstancia.activo == True
            )
        ).first()
    
    if not config:
        st.error("❌ El sistema no está configurado. Contacta al administrador.")
        return
    
    # Mostrar costos
    st.markdown("### 💰 Costo del Servicio")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Base", f"${float(config.costo_base_mxn):,.2f} MXN")
    with col2:
        iva = float(config.costo_base_mxn) * float(config.tasa_iva)
        st.metric(f"IVA ({float(config.tasa_iva)*100:.0f}%)", f"${iva:,.2f} MXN")
    with col3:
        st.metric("**TOTAL**", f"${float(config.costo_total_mxn):,.2f} MXN")
    
    if config.costo_total_usd:
        st.caption(f"≈ ${float(config.costo_total_usd):,.2f} USD")
    
    st.markdown("---")
    
    with st.form("form_solicitud"):
        # PASO 1: Tipo de Sacramento
        st.markdown("### 1️⃣ Tipo de Sacramento")
        tipo_sacramento = st.selectbox(
            "Selecciona:",
            options=TIPOS_SACRAMENTO,
            key="tipo_sacr"
        )
        
        st.markdown("---")
        
        # PASO 2: Búsqueda y Validación de Seguridad
        st.markdown("### 2️⃣ Validación de Seguridad")
        st.info("🔒 Por seguridad, debes proporcionar tu CURP o nombre completo + fecha de nacimiento")
        
        metodo_validacion = st.radio(
            "Método de validación:",
            options=["CURP", "Nombre y Fecha de Nacimiento"],
            horizontal=True,
            key="metodo_val"
        )
        
        curp_validacion = None
        nombre_validacion = None
        fecha_nac_validacion = None
        
        if metodo_validacion == "CURP":
            curp_validacion = st.text_input(
                "CURP:",
                max_chars=18,
                placeholder="ABCD123456HDFRRL00",
                key="curp_val",
                help="18 caracteres"
            )
            
            if curp_validacion:
                es_valido, mensaje = validar_curp(curp_validacion)
                if not es_valido:
                    st.error(f"❌ {mensaje}")
                else:
                    st.success(f"✅ CURP válido: {mensaje}")
                    curp_validacion = mensaje  # CURP limpio
        else:
            col1, col2 = st.columns(2)
            with col1:
                nombre_validacion = st.text_input(
                    "Nombre completo:",
                    max_chars=300,
                    placeholder="Juan Pérez López",
                    key="nombre_val"
                )
            with col2:
                fecha_nac_validacion = st.date_input(
                    "Fecha de nacimiento:",
                    min_value=date(1900, 1, 1),
                    max_value=date.today(),
                    value=None,
                    key="fecha_nac_val"
                )
        
        st.markdown("---")
        
        # PASO 3: Validación Adicional con Padrino/Madrina
        st.markdown("### 3️⃣ Verificación Adicional")
        st.info("🛡️ Como medida de seguridad adicional, ingresa el **primer apellido** de tu padrino o madrina")
        
        apellido_padrino_madrina = st.text_input(
            "Primer apellido del padrino o madrina:",
            max_chars=100,
            placeholder="Ej: García, López, etc.",
            key="apellido_pad",
            help="Este dato se verificará contra el registro del sacramento"
        )
        
        st.markdown("---")
        
        # PASO 4: Buscar Sacramento
        st.markdown("### 4️⃣ Buscar tu Sacramento")
        
        busqueda_sacramento = st.text_input(
            "Buscar por nombre:",
            placeholder="Escribe el nombre para buscar el registro",
            key="buscar_sacr"
        )
        
        id_sacramento_sel = None
        datos_sacramento = None
        
        if busqueda_sacramento and len(busqueda_sacramento) >= 3:
            sacramentos_encontrados = buscar_sacramentos_con_validacion(
                db_engine, tipo_sacramento, busqueda_sacramento,
                curp_validacion, nombre_validacion, fecha_nac_validacion
            )
            
            if sacramentos_encontrados:
                st.success(f"✅ Encontrados {len(sacramentos_encontrados)} registros")
                
                opciones_sacr = {
                    s['id']: s['descripcion'] for s in sacramentos_encontrados
                }
                
                id_sacramento_sel = st.selectbox(
                    "Selecciona tu registro:",
                    options=opciones_sacr.keys(),
                    format_func=lambda x: opciones_sacr[x],
                    key="sacr_sel"
                )
                
                # Vista previa SIN FORMATO OFICIAL
                if id_sacramento_sel:
                    datos_sacramento = obtener_datos_sacramento(
                        db_engine, tipo_sacramento, id_sacramento_sel
                    )
                    
                    if st.checkbox("👁️ Ver vista previa de datos", key="ver_prev"):
                        mostrar_vista_previa(datos_sacramento, sin_formato=True)
            else:
                st.warning("⚠️ No se encontraron registros que coincidan con tus datos de validación")
        
        st.markdown("---")
        
        # PASO 5: Datos del Solicitante
        st.markdown("### 5️⃣ Datos del Solicitante")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_solicitante = st.text_input(
                "Nombre completo (*)",
                max_chars=300,
                key="nom_sol"
            )
            
            email_solicitante = st.text_input(
                "Correo electrónico (*)",
                max_chars=100,
                key="email_sol",
                help="Recibirás notificaciones aquí"
            )
        
        with col2:
            telefono_solicitante = st.text_input(
                "Teléfono (10 dígitos)",
                max_chars=10,
                key="tel_sol"
            )
        
        st.markdown("---")
        
        # PASO 6: Método de Pago
        st.markdown("### 6️⃣ Método de Pago")
        
        metodo_pago = st.radio(
            "Selecciona cómo deseas pagar:",
            options=[
                "💳 Pago en línea con tarjeta (PayU)",
                "💵 Pago en efectivo en oficina parroquial"
            ],
            key="metodo_pago"
        )
        
        if "efectivo" in metodo_pago.lower():
            st.info("""
            📍 **Información para pago en efectivo:**
            
            **Dirección:**  
            Av. 2 de abril No. 22  
            Tlacolula de Matamoros, Oaxaca
            
            **Horarios de atención:**  
            📅 Lunes a Viernes: 9:00 AM - 2:00 PM y 4:00 PM - 7:00 PM  
            📅 Sábado: 9:00 AM - 1:00 PM  
            📞 Tel: 951 56 200 19
            
            Menciona tu correo electrónico para localizar tu solicitud.
            """)
        
        st.markdown("---")
        
        # Términos
        aceptar_terminos = st.checkbox(
            "✅ Acepto que los datos proporcionados son correctos y autorizo la emisión de la constancia",
            key="terminos"
        )
        
        st.caption("⚠️ La información proporcionada será verificada antes de procesar tu solicitud")
        
        submitted = st.form_submit_button(
            "📝 Enviar Solicitud",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            # Validaciones
            errores = []
            
            if not id_sacramento_sel:
                errores.append("Debes buscar y seleccionar tu registro de sacramento")
            
            if metodo_validacion == "CURP" and not curp_validacion:
                errores.append("CURP es requerido")
            elif metodo_validacion != "CURP" and (not nombre_validacion or not fecha_nac_validacion):
                errores.append("Nombre y fecha de nacimiento son requeridos")
            
            if not apellido_padrino_madrina or len(apellido_padrino_madrina.strip()) < 3:
                errores.append("Primer apellido de padrino/madrina es requerido (mínimo 3 caracteres)")
            
            if not nombre_solicitante or not email_solicitante:
                errores.append("Nombre y correo del solicitante son obligatorios")
            
            es_email_valido, email_limpio = validar_email(email_solicitante)
            if not es_email_valido:
                errores.append("Formato de correo electrónico inválido")
            
            if not aceptar_terminos:
                errores.append("Debes aceptar los términos para continuar")
            
            if errores:
                for error in errores:
                    st.error(f"❌ {error}")
            else:
                # Crear solicitud
                crear_solicitud_constancia(
                    db_engine, db_module, st_display_func,
                    tipo_sacramento, id_sacramento_sel, datos_sacramento,
                    curp_validacion, nombre_validacion, fecha_nac_validacion,
                    apellido_padrino_madrina,
                    nombre_solicitante, email_limpio, telefono_solicitante,
                    metodo_pago, config
                )


# ====================================================================
# CREAR SOLICITUD
# ====================================================================

def crear_solicitud_constancia(
    db_engine, db_module, st_display_func,
    tipo_sacramento, id_sacramento, datos_sacramento,
    curp_val, nombre_val, fecha_nac_val,
    apellido_pad_mad,
    nombre_sol, email_sol, tel_sol,
    metodo_pago, config
):
    """Crea la solicitud de constancia"""
    
    # Calcular costos
    costo_base = config.costo_base_mxn
    tasa_iva = config.tasa_iva
    monto_iva = costo_base * tasa_iva
    monto_total = costo_base + monto_iva
    
    # Determinar método de pago
    metodo = "PayU_Tarjeta" if "línea" in metodo_pago else "Efectivo_Oficina"
    
    # Generar reference code único para PayU
    reference_code = None
    if metodo == "PayU_Tarjeta":
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        reference_code = f"CONST-{timestamp}-{id_sacramento}"
    
    # Crear solicitud
    nueva_solicitud = SolicitudConstancia(
        tipo_sacramento=tipo_sacramento,
        id_sacramento=id_sacramento,
        nombre_solicitante=nombre_sol.strip(),
        email_solicitante=email_sol.strip().lower(),
        telefono_solicitante=tel_sol.strip() if tel_sol else None,
        curp_validacion=curp_val,
        nombre_validacion=nombre_val.strip() if nombre_val else None,
        fecha_nacimiento_validacion=fecha_nac_val,
        apellido_padrino_madrina=apellido_pad_mad.strip().upper(),
        validacion_exitosa=False,  # Se validará después
        intentos_validacion=0,
        estado="Pendiente_Validacion",
        metodo_pago=metodo,
        costo_base=costo_base,
        tasa_iva=tasa_iva,
        monto_iva=monto_iva,
        monto_total=monto_total,
        moneda_pago="MXN",
        payu_reference_code=reference_code
    )
    
    if db_module.crear_registro(nueva_solicitud, db_engine, st_display_func, nombre_tabla="Solicitud"):
        # Registrar en historial
        historial = HistorialTransaccionConstancia(
            id_solicitud=nueva_solicitud.id_solicitud,
            tipo_evento="Solicitud_Creada",
            descripcion=f"Solicitud de constancia de {tipo_sacramento} creada",
            resultado="Exitoso",
            datos_evento_json=json.dumps({
                "tipo_sacramento": tipo_sacramento,
                "metodo_pago": metodo,
                "metodo_validacion": "CURP" if curp_val else "Nombre_FechaNac"
            })
        )
        db_module.crear_registro(historial, db_engine, st_display_func)
        
        st.success(f"""
        ✅ **Solicitud creada exitosamente**
        
        **Número de solicitud:** {nueva_solicitud.id_solicitud}  
        **Estado:** Pendiente de validación
        
        📧 Recibirás un correo electrónico con más información.
        """)
        
        if metodo == "PayU_Tarjeta":
            st.info("""
            💳 **Siguiente paso: Pago en línea**
            
            Tu solicitud será validada primero. Si la validación es exitosa,
            recibirás un correo con el enlace de pago.
            """)
        else:
            st.info(f"""
            💵 **Siguiente paso: Pago en oficina**
            
            1. Acude a la oficina parroquial
            2. Menciona tu correo: **{email_sol}**
            3. Realiza el pago de **${float(monto_total):,.2f} MXN**
            4. Recibirás tu constancia de inmediato
            """)
        
        st.balloons()
        return True
    
    return False


# ====================================================================
# VALIDAR SOLICITUDES (SECRETARÍA)
# ====================================================================

def validar_solicitudes(db_engine, db_module, st_display_func, usuario_actual):
    """Validación de solicitudes por secretaría"""
    st.subheader("🔐 Validación de Solicitudes")
    
    st.info("💡 Verifica que los datos proporcionados coincidan con el registro del sacramento")
    
    # Solicitudes pendientes de validación
    with Session(db_engine) as session:
        pendientes = session.exec(
            select(SolicitudConstancia).where(
                SolicitudConstancia.estado == "Pendiente_Validacion"
            ).order_by(SolicitudConstancia.fecha_solicitud.desc())
        ).all()
    
    if not pendientes:
        st.success("✅ No hay solicitudes pendientes de validación")
        return
    
    st.markdown(f"**📋 Solicitudes pendientes:** {len(pendientes)}")
    
    for solicitud in pendientes:
        with st.expander(
            f"🔒 #{solicitud.id_solicitud} - {solicitud.nombre_solicitante} - {solicitud.tipo_sacramento}"
        ):
            # Obtener datos del sacramento
            datos_sacramento = obtener_datos_sacramento(
                db_engine, solicitud.tipo_sacramento, solicitud.id_sacramento
            )
            
            if not datos_sacramento:
                st.error("❌ No se pudo obtener datos del sacramento")
                continue
            
            # Mostrar datos de la solicitud
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📝 Datos de la Solicitud")
                st.markdown(f"**Solicitante:** {solicitud.nombre_solicitante}")
                st.markdown(f"**Email:** {solicitud.email_solicitante}")
                st.markdown(f"**Teléfono:** {solicitud.telefono_solicitante or 'N/A'}")
                st.markdown(f"**Fecha:** {solicitud.fecha_solicitud.strftime('%d/%m/%Y %H:%M')}")
                
                st.markdown("### 🔐 Datos de Validación Proporcionados")
                if solicitud.curp_validacion:
                    st.markdown(f"**CURP:** {solicitud.curp_validacion}")
                else:
                    st.markdown(f"**Nombre:** {solicitud.nombre_validacion}")
                    st.markdown(f"**Fecha Nac:** {solicitud.fecha_nacimiento_validacion.strftime('%d/%m/%Y')}")
                
                st.markdown(f"**Apellido Padrino/Madrina:** {solicitud.apellido_padrino_madrina}")
            
            with col2:
                st.markdown("### 📄 Datos del Sacramento en Sistema")
                mostrar_vista_previa(datos_sacramento, sin_formato=True)
                
                # Validación automática
                st.markdown("---")
                st.markdown("### ✅ Verificación Automática")
                
                resultado_val = verificar_datos_validacion(
                    solicitud, datos_sacramento
                )
                
                if resultado_val['curp_coincide']:
                    st.success("✅ CURP coincide")
                elif resultado_val['curp_coincide'] is False:
                    st.error("❌ CURP no coincide")
                
                if resultado_val['fecha_coincide']:
                    st.success("✅ Fecha de nacimiento coincide")
                elif resultado_val['fecha_coincide'] is False:
                    st.error("❌ Fecha de nacimiento no coincide")
                
                if resultado_val['apellido_padrino_coincide']:
                    st.success("✅ Apellido de padrino/madrina coincide")
                else:
                    st.error("❌ Apellido de padrino/madrina NO coincide")
            
            # Botones de acción
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(
                    "✅ APROBAR",
                    key=f"aprobar_{solicitud.id_solicitud}",
                    type="primary",
                    use_container_width=True
                ):
                    aprobar_solicitud(
                        db_engine, db_module, solicitud, usuario_actual, st_display_func
                    )
                    st.rerun()
            
            with col2:
                if st.button(
                    "🔄 Solicitar Corrección",
                    key=f"corregir_{solicitud.id_solicitud}",
                    use_container_width=True
                ):
                    st.session_state[f"corregir_{solicitud.id_solicitud}"] = True
            
            with col3:
                if st.button(
                    "❌ RECHAZAR",
                    key=f"rechazar_{solicitud.id_solicitud}",
                    use_container_width=True
                ):
                    st.session_state[f"rechazar_{solicitud.id_solicitud}"] = True


# ====================================================================
# GESTIONAR PAGOS (SECRETARÍA)
# ====================================================================

def gestionar_pagos(db_engine, db_module, st_display_func, usuario_actual):
    """Gestión de pagos en efectivo y generación de constancias"""
    st.subheader("💳 Gestión de Pagos")
    
    # Solicitudes validadas pendientes de pago
    with Session(db_engine) as session:
        pendientes_pago = session.exec(
            select(SolicitudConstancia).where(
                SolicitudConstancia.estado == "Validada",
                SolicitudConstancia.metodo_pago == "Efectivo_Oficina"
            ).order_by(SolicitudConstancia.fecha_solicitud.desc())
        ).all()
    
    if pendientes_pago:
        st.markdown(f"**💵 Pendientes de pago en efectivo:** {len(pendientes_pago)}")
        
        for sol in pendientes_pago:
            with st.expander(
                f"💵 #{sol.id_solicitud} - {sol.nombre_solicitante} - "
                f"${float(sol.monto_total):,.2f} MXN"
            ):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Solicitante:** {sol.nombre_solicitante}")
                    st.markdown(f"**Email:** {sol.email_solicitante}")
                    st.markdown(f"**Tipo:** {sol.tipo_sacramento}")
                    
                    # Desglose de pago
                    st.markdown("### 💰 Desglose del Pago")
                    st.markdown(f"**Subtotal:** ${float(sol.costo_base):,.2f} MXN")
                    st.markdown(f"**IVA ({float(sol.tasa_iva)*100:.0f}%):** ${float(sol.monto_iva):,.2f} MXN")
                    st.markdown(f"**TOTAL:** ${float(sol.monto_total):,.2f} MXN")
                
                with col2:
                    st.metric("Total a cobrar", f"${float(sol.monto_total):,.2f}")
                    st.caption("MXN")
                    
                    comprobante = st.text_input(
                        "No. de Recibo:",
                        key=f"recibo_{sol.id_solicitud}",
                        placeholder="Opcional"
                    )
                    
                    if st.button(
                        "💵 Registrar Pago",
                        key=f"pagar_{sol.id_solicitud}",
                        type="primary",
                        use_container_width=True
                    ):
                        registrar_pago_efectivo(
                            db_engine, db_module, sol, comprobante,
                            usuario_actual, st_display_func
                        )
                        st.rerun()
    else:
        st.info("ℹ️ No hay solicitudes pendientes de pago en efectivo")
    
    st.markdown("---")
    
    # Solicitudes pagadas pendientes de emisión
    with Session(db_engine) as session:
        pagadas = session.exec(
            select(SolicitudConstancia).where(
                SolicitudConstancia.estado == "Pagada"
            ).order_by(SolicitudConstancia.fecha_pago.desc())
        ).all()
    
    if pagadas:
        st.markdown(f"**✅ Pagadas - Pendientes de emisión:** {len(pagadas)}")
        
        for sol in pagadas:
            with st.expander(f"✅ #{sol.id_solicitud} - {sol.nombre_solicitante}"):
                st.markdown(f"**Fecha pago:** {sol.fecha_pago.strftime('%d/%m/%Y %H:%M')}")
                st.markdown(f"**Método:** {sol.metodo_pago}")
                
                if st.button(
                    "📄 Generar Constancia",
                    key=f"generar_{sol.id_solicitud}",
                    type="primary"
                ):
                    if generar_constancia_completa(
                        db_engine, db_module, sol, usuario_actual, st_display_func
                    ):
                        st.success("✅ Constancia generada exitosamente")
                        st.rerun()


# ====================================================================
# CONSTANCIAS EMITIDAS
# ====================================================================

def constancias_emitidas(db_engine, db_module, st_display_func, usuario_actual):
    """Visualización y gestión de constancias emitidas"""
    st.subheader("📄 Constancias Emitidas")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filtro_tipo = st.selectbox(
            "Tipo:",
            options=["Todos"] + TIPOS_SACRAMENTO,
            key="filtro_tipo"
        )
    
    with col2:
        filtro_estado = st.selectbox(
            "Estado:",
            options=["Todos", "Vigente", "Cancelada", "Reemplazada"],
            key="filtro_estado"
        )
    
    with col3:
        filtro_mes = st.number_input(
            "Mes:",
            min_value=0,
            max_value=12,
            value=datetime.now().month,
            key="filtro_mes"
        )
    
    # Consultar constancias
    with Session(db_engine) as session:
        statement = select(ConstanciaEmitida).order_by(
            ConstanciaEmitida.fecha_emision.desc()
        )
        
        if filtro_tipo != "Todos":
            statement = statement.where(ConstanciaEmitida.tipo_sacramento == filtro_tipo)
        
        if filtro_estado != "Todos":
            statement = statement.where(ConstanciaEmitida.estado == filtro_estado)
        
        constancias = session.exec(statement).all()
    
    if constancias:
        st.markdown