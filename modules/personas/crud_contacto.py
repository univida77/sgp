# crud_contacto.py - Módulo completo para gestión de contacto
import streamlit as st
from datetime import date
from models import Telefono, Direccion, Persona
from utils import buscar_persona_por_curp, obtener_lista_personas, formatear_fecha
from sqlmodel import Session, select
import re

# ====================================================================
# FUNCIONES DE VALIDACIÓN
# ====================================================================

def validar_telefono(numero: str) -> tuple[bool, str]:
    """
    Valida formato de número telefónico.
    Acepta formatos: 5512345678, 55 1234 5678, +52 55 1234 5678
    """
    # Remover espacios y guiones
    numero_limpio = re.sub(r'[\s\-()]', '', numero)
    
    # Verificar que solo contenga dígitos y opcionalmente +
    if not re.match(r'^\+?\d+$', numero_limpio):
        return False, "El número solo debe contener dígitos, espacios, guiones o +"
    
    # Remover código de país si existe
    if numero_limpio.startswith('+52'):
        numero_limpio = numero_limpio[3:]
    elif numero_limpio.startswith('52'):
        numero_limpio = numero_limpio[2:]
    
    # Validar longitud (10 dígitos para México)
    if len(numero_limpio) != 10:
        return False, f"Debe tener 10 dígitos (tiene {len(numero_limpio)})"
    
    return True, numero_limpio


def validar_codigo_postal(cp: str) -> tuple[bool, str]:
    """Valida código postal de 5 dígitos."""
    if not cp:
        return False, "El código postal es obligatorio"
    
    cp_limpio = cp.strip()
    
    if not cp_limpio.isdigit():
        return False, "El código postal solo debe contener dígitos"
    
    if len(cp_limpio) != 5:
        return False, f"Debe tener 5 dígitos (tiene {len(cp_limpio)})"
    
    return True, cp_limpio


def formatear_telefono(numero: str) -> str:
    """Formatea un número telefónico: 5512345678 -> (55) 1234-5678"""
    if len(numero) == 10:
        return f"({numero[:2]}) {numero[2:6]}-{numero[6:]}"
    return numero

# ====================================================================
# FUNCIÓN PRINCIPAL
# ====================================================================

def mostrar_crud_contacto(db_engine, db_module, db_mode, st_display_func):
    """Módulo completo CRUD para gestión de contacto."""
    st.header(f"📱 Gestión de Contacto - Modo: {db_mode}")
    
    st.info("💡 Administra teléfonos y direcciones físicas de las personas registradas")
    
    tabs = st.tabs([
        "📞 Teléfonos",
        "🏠 Direcciones",
        "👤 Ver Contacto Completo"
    ])
    
    # ================================================================
    # TAB 1: GESTIÓN DE TELÉFONOS
    # ================================================================
    with tabs[0]:
        st.subheader("📞 Gestión de Teléfonos")
        
        subtabs_tel = st.tabs(["➕ Agregar Teléfono", "📋 Ver Teléfonos", "✏️ Editar/Eliminar"])
        
        # AGREGAR TELÉFONO
        with subtabs_tel[0]:
            st.markdown("### 📱 Agregar Nuevo Teléfono")
            
            # Buscar persona
            col1, col2 = st.columns([1, 2])
            
            with col1:
                curp_busqueda = st.text_input(
                    "Buscar por CURP",
                    max_chars=18,
                    key="tel_curp_buscar"
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
                    id_persona_final = None
                else:
                    opciones = {0: "-- Selecciona una Persona --"}
                    opciones.update({
                        p.id_persona: f"{p.nombre_completo()} - {p.curp or 'Sin CURP'}"
                        for p in personas
                    })
                    id_persona_sel = st.selectbox(
                        "O selecciona de la lista:",
                        options=opciones.keys(),
                        format_func=lambda x: opciones[x],
                        key="tel_persona_sel"
                    )
                    id_persona_final = persona_encontrada.id_persona if persona_encontrada else (id_persona_sel if id_persona_sel != 0 else None)
            
            if id_persona_final:
                st.markdown("---")
                
                with st.form("form_agregar_telefono", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        numero = st.text_input(
                            "Número Telefónico (*)",
                            max_chars=20,
                            placeholder="Ej: 5512345678 o 55 1234 5678",
                            key="tel_numero"
                        )
                        
                        tipo = st.selectbox(
                            "Tipo (*)",
                            options=["Móvil", "Casa"],
                            key="tel_tipo"
                        )
                        
                        etiqueta = st.text_input(
                            "Etiqueta",
                            max_chars=50,
                            placeholder="Ej: Personal, Trabajo, Emergencia",
                            key="tel_etiqueta"
                        )
                    
                    with col2:
                        tiene_whatsapp = st.checkbox(
                            "Tiene WhatsApp",
                            disabled=(tipo != "Móvil"),
                            key="tel_whatsapp",
                            help="Solo disponible para teléfonos móviles"
                        )
                        
                        extension = st.text_input(
                            "Extensión",
                            max_chars=10,
                            placeholder="Ej: 1234",
                            key="tel_extension",
                            help="Para teléfonos de oficina"
                        )
                        
                        principal = st.checkbox(
                            "Marcar como principal",
                            key="tel_principal"
                        )
                    
                    observaciones = st.text_area(
                        "Observaciones",
                        key="tel_observaciones"
                    )
                    
                    submitted = st.form_submit_button("💾 Guardar Teléfono", type="primary", use_container_width=True)
                    
                    if submitted:
                        if not numero:
                            st.error("❌ El número telefónico es obligatorio")
                        else:
                            # Validar y limpiar número
                            es_valido, resultado = validar_telefono(numero)
                            
                            if not es_valido:
                                st.error(f"❌ {resultado}")
                            else:
                                # Verificar si ya existe
                                with Session(db_engine) as session:
                                    existe = session.exec(
                                        select(Telefono).where(
                                            Telefono.id_persona == id_persona_final,
                                            Telefono.numero_telefono == resultado,
                                            Telefono.activo == True
                                        )
                                    ).first()
                                
                                if existe:
                                    st.error("❌ Este número ya está registrado para esta persona")
                                else:
                                    # Si marca como principal, desmarcar otros
                                    if principal:
                                        with Session(db_engine) as session:
                                            otros = session.exec(
                                                select(Telefono).where(
                                                    Telefono.id_persona == id_persona_final,
                                                    Telefono.principal == True
                                                )
                                            ).all()
                                            for otro in otros:
                                                otro.principal = False
                                                session.add(otro)
                                            session.commit()
                                    
                                    nuevo_tel = Telefono(
                                        id_persona=id_persona_final,
                                        numero_telefono=resultado,
                                        tipo=tipo,
                                        tiene_whatsapp=tiene_whatsapp if tipo == "Móvil" else False,
                                        etiqueta=etiqueta.strip() if etiqueta else None,
                                        extension=extension.strip() if extension else None,
                                        principal=principal,
                                        observaciones=observaciones.strip() if observaciones else None
                                    )
                                    
                                    if db_module.crear_registro(nuevo_tel, db_engine, st_display_func, nombre_tabla="Teléfono"):
                                        st.success("✅ Teléfono registrado exitosamente")
                                        st.rerun()
            else:
                st.info("💡 Busca o selecciona una persona para agregar su teléfono")
        
        # VER TELÉFONOS
        with subtabs_tel[1]:
            st.markdown("### 📋 Teléfonos Registrados")
            
            # Filtro por persona
            personas = obtener_lista_personas(db_engine)
            if personas:
                opciones = {0: "-- Todas las Personas --"}
                opciones.update({p.id_persona: p.nombre_completo() for p in personas})
                
                filtro_persona = st.selectbox(
                    "Filtrar por Persona:",
                    options=opciones.keys(),
                    format_func=lambda x: opciones[x],
                    key="ver_tel_persona"
                )
                
                with Session(db_engine) as session:
                    statement = select(Telefono).where(Telefono.activo == True)
                    
                    if filtro_persona != 0:
                        statement = statement.where(Telefono.id_persona == filtro_persona)
                    
                    telefonos = session.exec(statement).all()
                
                if telefonos:
                    st.markdown(f"**Total:** {len(telefonos)} teléfonos")
                    
                    data = []
                    with Session(db_engine) as session:
                        for tel in telefonos:
                            persona = session.get(Persona, tel.id_persona)
                            
                            # Formatear número
                            num_formateado = formatear_telefono(tel.numero_telefono)
                            
                            # Iconos
                            icono_tipo = "📱" if tel.tipo == "Móvil" else "☎️"
                            icono_whatsapp = " 💬" if tel.tiene_whatsapp else ""
                            icono_principal = " ⭐" if tel.principal else ""
                            
                            data.append({
                                "ID": tel.id_telefono,
                                "Persona": persona.nombre_completo() if persona else "N/A",
                                "Número": f"{icono_tipo} {num_formateado}{icono_whatsapp}{icono_principal}",
                                "Tipo": tel.tipo,
                                "Etiqueta": tel.etiqueta or "N/A",
                                "Extensión": tel.extension or "N/A"
                            })
                    
                    st.dataframe(data, use_container_width=True, hide_index=True)
                else:
                    st.info("ℹ️ No hay teléfonos registrados")
            else:
                st.warning("⚠️ No hay personas registradas")
        
        # EDITAR/ELIMINAR TELÉFONO
        with subtabs_tel[2]:
            st.markdown("### ✏️ Editar o Eliminar Teléfono")
            
            with Session(db_engine) as session:
                telefonos = session.exec(
                    select(Telefono).where(Telefono.activo == True)
                ).all()
            
            if telefonos:
                opciones_tel = {}
                with Session(db_engine) as session:
                    for tel in telefonos:
                        persona = session.get(Persona, tel.id_persona)
                        num_formateado = formatear_telefono(tel.numero_telefono)
                        icono = "⭐" if tel.principal else "📞"
                        opciones_tel[tel.id_telefono] = f"{icono} {num_formateado} - {persona.nombre_completo() if persona else 'N/A'} ({tel.tipo})"
                
                id_tel_sel = st.selectbox(
                    "Selecciona el teléfono:",
                    options=opciones_tel.keys(),
                    format_func=lambda x: opciones_tel[x],
                    key="edit_tel_sel"
                )
                
                telefono = next((t for t in telefonos if t.id_telefono == id_tel_sel), None)
                
                if telefono:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("✏️ Editar", use_container_width=True):
                            st.session_state.editando_telefono = True
                    
                    with col2:
                        if st.button("🗑️ Eliminar", use_container_width=True, type="secondary"):
                            st.session_state.eliminando_telefono = True
                    
                    # EDITAR
                    if st.session_state.get("editando_telefono", False):
                        st.markdown("---")
                        with st.form("form_editar_telefono"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                upd_numero = st.text_input(
                                    "Número (*)",
                                    value=telefono.numero_telefono,
                                    key="upd_tel_numero"
                                )
                                
                                upd_tipo = st.selectbox(
                                    "Tipo (*)",
                                    options=["Móvil", "Casa"],
                                    index=0 if telefono.tipo == "Móvil" else 1,
                                    key="upd_tel_tipo"
                                )
                                
                                upd_etiqueta = st.text_input(
                                    "Etiqueta",
                                    value=telefono.etiqueta or "",
                                    key="upd_tel_etiqueta"
                                )
                            
                            with col2:
                                upd_whatsapp = st.checkbox(
                                    "Tiene WhatsApp",
                                    value=telefono.tiene_whatsapp,
                                    disabled=(upd_tipo != "Móvil"),
                                    key="upd_tel_whatsapp"
                                )
                                
                                upd_extension = st.text_input(
                                    "Extensión",
                                    value=telefono.extension or "",
                                    key="upd_tel_extension"
                                )
                                
                                upd_principal = st.checkbox(
                                    "Principal",
                                    value=telefono.principal,
                                    key="upd_tel_principal"
                                )
                            
                            upd_observaciones = st.text_area(
                                "Observaciones",
                                value=telefono.observaciones or "",
                                key="upd_tel_obs"
                            )
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("💾 Guardar Cambios", type="primary", use_container_width=True):
                                    es_valido, resultado = validar_telefono(upd_numero)
                                    
                                    if not es_valido:
                                        st.error(f"❌ {resultado}")
                                    else:
                                        datos = {
                                            "numero_telefono": resultado,
                                            "tipo": upd_tipo,
                                            "tiene_whatsapp": upd_whatsapp if upd_tipo == "Móvil" else False,
                                            "etiqueta": upd_etiqueta.strip() if upd_etiqueta else None,
                                            "extension": upd_extension.strip() if upd_extension else None,
                                            "principal": upd_principal,
                                            "observaciones": upd_observaciones.strip() if upd_observaciones else None
                                        }
                                        
                                        if db_module.actualizar_registro(
                                            Telefono,
                                            telefono.id_telefono,
                                            datos,
                                            db_engine,
                                            st_display_func,
                                            "Teléfono"
                                        ):
                                            st.session_state.editando_telefono = False
                                            st.rerun()
                            
                            with col2:
                                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                                    st.session_state.editando_telefono = False
                                    st.rerun()
                    
                    # ELIMINAR
                    if st.session_state.get("eliminando_telefono", False):
                        st.markdown("---")
                        st.error("⚠️ ¿Confirmas eliminar este teléfono?")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ SÍ, ELIMINAR", type="primary", use_container_width=True):
                                if db_module.eliminar_registro(
                                    Telefono,
                                    telefono.id_telefono,
                                    db_engine,
                                    st_display_func,
                                    nombre_tabla="Teléfono"
                                ):
                                    st.session_state.eliminando_telefono = False
                                    st.rerun()
                        
                        with col2:
                            if st.button("❌ Cancelar", use_container_width=True):
                                st.session_state.eliminando_telefono = False
                                st.rerun()
            else:
                st.info("ℹ️ No hay teléfonos para editar")
    
    # ================================================================
    # TAB 2: GESTIÓN DE DIRECCIONES
    # ================================================================
    with tabs[1]:
        st.subheader("🏠 Gestión de Direcciones Físicas")
        
        subtabs_dir = st.tabs(["➕ Agregar Dirección", "📋 Ver Direcciones", "✏️ Editar/Eliminar"])
        
        # AGREGAR DIRECCIÓN
        with subtabs_dir[0]:
            st.markdown("### 🏠 Agregar Nueva Dirección")
            
            # Buscar persona
            col1, col2 = st.columns([1, 2])
            
            with col1:
                curp_busqueda = st.text_input(
                    "Buscar por CURP",
                    max_chars=18,
                    key="dir_curp_buscar"
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
                    id_persona_final = None
                else:
                    opciones = {0: "-- Selecciona una Persona --"}
                    opciones.update({
                        p.id_persona: f"{p.nombre_completo()} - {p.curp or 'Sin CURP'}"
                        for p in personas
                    })
                    id_persona_sel = st.selectbox(
                        "O selecciona de la lista:",
                        options=opciones.keys(),
                        format_func=lambda x: opciones[x],
                        key="dir_persona_sel"
                    )
                    id_persona_final = persona_encontrada.id_persona if persona_encontrada else (id_persona_sel if id_persona_sel != 0 else None)
            
            if id_persona_final:
                st.markdown("---")
                
                with st.form("form_agregar_direccion", clear_on_submit=True):
                    st.markdown("### 📍 Datos de la Dirección")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        calle = st.text_input(
                            "Calle (*)",
                            max_chars=200,
                            key="dir_calle"
                        )
                        
                        numero_ext = st.text_input(
                            "Número Exterior (*)",
                            max_chars=20,
                            key="dir_num_ext"
                        )
                        
                        numero_int = st.text_input(
                            "Número Interior",
                            max_chars=20,
                            key="dir_num_int"
                        )
                    
                    with col2:
                        colonia = st.text_input(
                            "Colonia",
                            max_chars=100,
                            key="dir_colonia"
                        )
                        
                        comunidad = st.text_input(
                            "Comunidad",
                            max_chars=100,
                            key="dir_comunidad"
                        )
                        
                        municipio = st.text_input(
                            "Municipio (*)",
                            max_chars=100,
                            key="dir_municipio"
                        )
                    
                    with col3:
                        distrito = st.text_input(
                            "Distrito",
                            max_chars=100,
                            key="dir_distrito"
                        )
                        
                        estado = st.text_input(
                            "Estado",
                            max_chars=100,
                            value="",
                            key="dir_estado"
                        )
                        
                        codigo_postal = st.text_input(
                            "Código Postal (*)",
                            max_chars=5,
                            key="dir_cp"
                        )
                    
                    pais = st.text_input(
                        "País",
                        max_chars=100,
                        value="México",
                        key="dir_pais"
                    )
                    
                    referencias = st.text_area(
                        "Referencias / Entre Calles",
                        key="dir_referencias",
                        placeholder="Ej: Entre calle X y Y, frente al parque..."
                    )
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        tipo_direccion = st.selectbox(
                            "Tipo de Dirección",
                            options=["Casa", "Trabajo", "Otra"],
                            key="dir_tipo"
                        )
                    
                    with col2:
                        principal = st.checkbox(
                            "Dirección Principal",
                            key="dir_principal"
                        )
                    
                    with col3:
                        pass
                    
                    observaciones = st.text_area(
                        "Observaciones",
                        key="dir_observaciones"
                    )
                    
                    submitted = st.form_submit_button("💾 Guardar Dirección", type="primary", use_container_width=True)
                    
                    if submitted:
                        if not calle or not numero_ext or not municipio or not codigo_postal:
                            st.error("❌ Los campos marcados con (*) son obligatorios")
                        else:
                            # Validar código postal
                            es_valido, resultado = validar_codigo_postal(codigo_postal)
                            
                            if not es_valido:
                                st.error(f"❌ {resultado}")
                            else:
                                # Si marca como principal, desmarcar otras
                                if principal:
                                    with Session(db_engine) as session:
                                        otras = session.exec(
                                            select(Direccion).where(
                                                Direccion.id_persona == id_persona_final,
                                                Direccion.principal == True
                                            )
                                        ).all()
                                        for otra in otras:
                                            otra.principal = False
                                            session.add(otra)
                                        session.commit()
                                
                                nueva_dir = Direccion(
                                    id_persona=id_persona_final,
                                    calle=calle.strip(),
                                    numero_exterior=numero_ext.strip(),
                                    numero_interior=numero_int.strip() if numero_int else None,
                                    colonia=colonia.strip() if colonia else None,
                                    comunidad=comunidad.strip() if comunidad else None,
                                    municipio=municipio.strip(),
                                    distrito=distrito.strip() if distrito else None,
                                    estado=estado.strip() if estado else None,
                                    pais=pais.strip(),
                                    codigo_postal=resultado,
                                    referencias=referencias.strip() if referencias else None,
                                    tipo_direccion=tipo_direccion,
                                    principal=principal,
                                    observaciones=observaciones.strip() if observaciones else None
                                )
                                
                                if db_module.crear_registro(nueva_dir, db_engine, st_display_func, nombre_tabla="Dirección"):
                                    st.success("✅ Dirección registrada exitosamente")
                                    st.rerun()
            else:
                st.info("💡 Busca o selecciona una persona para agregar su dirección")
        
        # VER DIRECCIONES
        with subtabs_dir[1]:
            st.markdown("### 📋 Direcciones Registradas")
            
            # Filtro por persona
            personas = obtener_lista_personas(db_engine)
            if personas:
                opciones = {0: "-- Todas las Personas --"}
                opciones.update({p.id_persona: p.nombre_completo() for p in personas})
                
                filtro_persona = st.selectbox(
                    "Filtrar por Persona:",
                    options=opciones.keys(),
                    format_func=lambda x: opciones[x],
                    key="ver_dir_persona"
                )
                
                with Session(db_engine) as session:
                    statement = select(Direccion).where(Direccion.activo == True)
                    
                    if filtro_persona != 0:
                        statement = statement.where(Direccion.id_persona == filtro_persona)
                    
                    direcciones = session.exec(statement).all()
                
                if direcciones:
                    st.markdown(f"**Total:** {len(direcciones)} direcciones")
                    
                    for dir in direcciones:
                        with Session(db_engine) as session:
                            persona = session.get(Persona, dir.id_persona)
                        
                        icono = "⭐" if dir.principal else "🏠"
                        
                        with st.expander(f"{icono} {persona.nombre_completo() if persona else 'N/A'} - {dir.tipo_direccion}"):
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.markdown(f"**📍 Dirección Completa:**")
                                direccion_completa = f"{dir.calle} {dir.numero_exterior}"
                                if dir.numero_interior:
                                    direccion_completa += f" Int. {dir.numero_interior}"
                                if dir.colonia:
                                    direccion_completa += f", Col. {dir.colonia}"
                                if dir.comunidad:
                                    direccion_completa += f", {dir.comunidad}"
                                direccion_completa += f", {dir.municipio}"
                                if dir.distrito:
                                    direccion_completa += f", {dir.distrito}"
                                if dir.estado:
                                    direccion_completa += f", {dir.estado}"
                                direccion_completa += f", CP {dir.codigo_postal}, {dir.pais}"
                                
                                st.info(direccion_completa)
                                
                                if dir.referencias:
                                    st.caption(f"📝 Referencias: {dir.referencias}")
                            
                            with col2:
                                st.metric("Tipo", dir.tipo_direccion)
                                if dir.principal:
                                    st.success("⭐ Principal")
                                st.caption(f"ID: {dir.id_direccion}")
                else:
                    st.info("ℹ️ No hay direcciones registradas")
            else:
                st.warning("⚠️ No hay personas registradas")
        
        # EDITAR/ELIMINAR DIRECCIÓN
        with subtabs_dir[2]:
            st.markdown("### ✏️ Editar o Eliminar Dirección")
            
            with Session(db_engine) as session:
                direcciones = session.exec(
                    select(Direccion).where(Direccion.activo == True)
                ).all()
            
            if direcciones:
                opciones_dir = {}
                with Session(db_engine) as session:
                    for dir in direcciones:
                        persona = session.get(Persona, dir.id_persona)
                        icono = "⭐" if dir.principal else "🏠"
                        opciones_dir[dir.id_direccion] = f"{icono} {persona.nombre_completo() if persona else 'N/A'} - {dir.calle} {dir.numero_exterior}, {dir.municipio}"
                
                id_dir_sel = st.selectbox(
                    "Selecciona la dirección:",
                    options=opciones_dir.keys(),
                    format_func=lambda x: opciones_dir[x],
                    key="edit_dir_sel"
                )
                
                direccion = next((d for d in direcciones if d.id_direccion == id_dir_sel), None)
                
                if direccion:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("✏️ Editar", use_container_width=True, key="btn_edit_dir"):
                            st.session_state.editando_direccion = True
                    
                    with col2:
                        if st.button("🗑️ Eliminar", use_container_width=True, type="secondary", key="btn_del_dir"):
                            st.session_state.eliminando_direccion = True
                    
                    # EDITAR
                    if st.session_state.get("editando_direccion", False):
                        st.markdown("---")
                        with st.form("form_editar_direccion"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                upd_calle = st.text_input("Calle (*)", value=direccion.calle, key="upd_dir_calle")
                                upd_num_ext = st.text_input("Número Ext (*)", value=direccion.numero_exterior, key="upd_dir_numext")
                                upd_num_int = st.text_input("Número Int", value=direccion.numero_interior or "", key="upd_dir_numint")
                            
                            with col2:
                                upd_colonia = st.text_input("Colonia", value=direccion.colonia or "", key="upd_dir_colonia")
                                upd_comunidad = st.text_input("Comunidad", value=direccion.comunidad or "", key="upd_dir_comunidad")
                                upd_municipio = st.text_input("Municipio (*)", value=direccion.municipio, key="upd_dir_municipio")
                            
                            with col3:
                                upd_distrito = st.text_input("Distrito", value=direccion.distrito or "", key="upd_dir_distrito")
                                upd_estado = st.text_input("Estado", value=direccion.estado or "", key="upd_dir_estado")
                                upd_cp = st.text_input("CP (*)", value=direccion.codigo_postal, key="upd_dir_cp")
                            
                            upd_pais = st.text_input("País", value=direccion.pais, key="upd_dir_pais")
                            upd_referencias = st.text_area("Referencias", value=direccion.referencias or "", key="upd_dir_ref")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                upd_tipo = st.selectbox(
                                    "Tipo",
                                    options=["Casa", "Trabajo", "Otra"],
                                    index=["Casa", "Trabajo", "Otra"].index(direccion.tipo_direccion),
                                    key="upd_dir_tipo"
                                )
                            with col2:
                                upd_principal = st.checkbox("Principal", value=direccion.principal, key="upd_dir_principal")
                            
                            upd_obs = st.text_area("Observaciones", value=direccion.observaciones or "", key="upd_dir_obs")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("💾 Guardar Cambios", type="primary", use_container_width=True):
                                    if not upd_calle or not upd_num_ext or not upd_municipio or not upd_cp:
                                        st.error("❌ Los campos obligatorios no pueden estar vacíos")
                                    else:
                                        es_valido, cp_limpio = validar_codigo_postal(upd_cp)
                                        if not es_valido:
                                            st.error(f"❌ {cp_limpio}")
                                        else:
                                            datos = {
                                                "calle": upd_calle.strip(),
                                                "numero_exterior": upd_num_ext.strip(),
                                                "numero_interior": upd_num_int.strip() if upd_num_int else None,
                                                "colonia": upd_colonia.strip() if upd_colonia else None,
                                                "comunidad": upd_comunidad.strip() if upd_comunidad else None,
                                                "municipio": upd_municipio.strip(),
                                                "distrito": upd_distrito.strip() if upd_distrito else None,
                                                "estado": upd_estado.strip() if upd_estado else None,
                                                "pais": upd_pais.strip(),
                                                "codigo_postal": cp_limpio,
                                                "referencias": upd_referencias.strip() if upd_referencias else None,
                                                "tipo_direccion": upd_tipo,
                                                "principal": upd_principal,
                                                "observaciones": upd_obs.strip() if upd_obs else None
                                            }
                                            
                                            if db_module.actualizar_registro(
                                                Direccion,
                                                direccion.id_direccion,
                                                datos,
                                                db_engine,
                                                st_display_func,
                                                "Dirección"
                                            ):
                                                st.session_state.editando_direccion = False
                                                st.rerun()
                            
                            with col2:
                                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                                    st.session_state.editando_direccion = False
                                    st.rerun()
                    
                    # ELIMINAR
                    if st.session_state.get("eliminando_direccion", False):
                        st.markdown("---")
                        st.error("⚠️ ¿Confirmas eliminar esta dirección?")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ SÍ, ELIMINAR", type="primary", use_container_width=True, key="confirm_del_dir"):
                                if db_module.eliminar_registro(
                                    Direccion,
                                    direccion.id_direccion,
                                    db_engine,
                                    st_display_func,
                                    nombre_tabla="Dirección"
                                ):
                                    st.session_state.eliminando_direccion = False
                                    st.rerun()
                        
                        with col2:
                            if st.button("❌ Cancelar", use_container_width=True, key="cancel_del_dir"):
                                st.session_state.eliminando_direccion = False
                                st.rerun()
            else:
                st.info("ℹ️ No hay direcciones para editar")
    
    # ================================================================
    # TAB 3: VER CONTACTO COMPLETO
    # ================================================================
    with tabs[2]:
        st.subheader("👤 Ver Contacto Completo de una Persona")
        
        personas = obtener_lista_personas(db_engine)
        if personas:
            opciones = {p.id_persona: p.nombre_completo() for p in personas}
            
            id_persona_contacto = st.selectbox(
                "Selecciona la Persona:",
                options=opciones.keys(),
                format_func=lambda x: opciones[x],
                key="ver_contacto_persona"
            )
            
            with Session(db_engine) as session:
                persona = session.get(Persona, id_persona_contacto)
                
                if persona:
                    st.markdown(f"## 👤 {persona.nombre_completo()}")
                    st.caption(f"CURP: {persona.curp or 'Sin CURP'}")
                    
                    st.markdown("---")
                    
                    # TELÉFONOS
                    st.markdown("### 📞 Teléfonos")
                    telefonos = session.exec(
                        select(Telefono).where(
                            Telefono.id_persona == id_persona_contacto,
                            Telefono.activo == True
                        )
                    ).all()
                    
                    if telefonos:
                        for tel in telefonos:
                            num_formateado = formatear_telefono(tel.numero_telefono)
                            icono_tipo = "📱" if tel.tipo == "Móvil" else "☎️"
                            icono_whatsapp = " 💬 WhatsApp" if tel.tiene_whatsapp else ""
                            icono_principal = " ⭐ Principal" if tel.principal else ""
                            etiqueta_str = f" ({tel.etiqueta})" if tel.etiqueta else ""
                            
                            st.info(f"{icono_tipo} {num_formateado}{etiqueta_str}{icono_whatsapp}{icono_principal}")
                    else:
                        st.warning("⚠️ No tiene teléfonos registrados")
                    
                    st.markdown("---")
                    
                    # DIRECCIONES
                    st.markdown("### 🏠 Direcciones")
                    direcciones = session.exec(
                        select(Direccion).where(
                            Direccion.id_persona == id_persona_contacto,
                            Direccion.activo == True
                        )
                    ).all()
                    
                    if direcciones:
                        for dir in direcciones:
                            icono_principal = "⭐" if dir.principal else "🏠"
                            
                            with st.expander(f"{icono_principal} {dir.tipo_direccion}" + (" - Principal" if dir.principal else "")):
                                direccion_completa = f"{dir.calle} {dir.numero_exterior}"
                                if dir.numero_interior:
                                    direccion_completa += f" Int. {dir.numero_interior}"
                                if dir.colonia:
                                    direccion_completa += f", Col. {dir.colonia}"
                                if dir.comunidad:
                                    direccion_completa += f", {dir.comunidad}"
                                direccion_completa += f", {dir.municipio}"
                                if dir.distrito:
                                    direccion_completa += f", {dir.distrito}"
                                if dir.estado:
                                    direccion_completa += f", {dir.estado}"
                                direccion_completa += f", CP {dir.codigo_postal}, {dir.pais}"
                                
                                st.info(direccion_completa)
                                
                                if dir.referencias:
                                    st.caption(f"📝 Referencias: {dir.referencias}")
                    else:
                        st.warning("⚠️ No tiene direcciones registradas")
        else:
            st.warning("⚠️ No hay personas registradas")