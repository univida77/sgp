# crud_usuarios.py - MEJORADO CON VISUALIZACIÓN COMPLETA
import streamlit as st
from datetime import date
from models import Usuario, Persona
from utils import buscar_persona_por_curp, obtener_lista_personas
from sqlmodel import Session, select
import hashlib

# ====================================================================
# FUNCIONES AUXILIARES
# ====================================================================

def hash_password(password: str) -> str:
    """Genera un hash SHA-256 de la contraseña."""
    return hashlib.sha256(password.encode()).hexdigest()

def validar_password(password: str) -> tuple[bool, str]:
    """Valida que la contraseña cumpla con requisitos mínimos."""
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    if not any(c.isupper() for c in password):
        return False, "La contraseña debe contener al menos una mayúscula"
    if not any(c.islower() for c in password):
        return False, "La contraseña debe contener al menos una minúscula"
    if not any(c.isdigit() for c in password):
        return False, "La contraseña debe contener al menos un número"
    return True, ""

def validar_email(email: str) -> bool:
    """Validación básica de formato de email."""
    return '@' in email and '.' in email.split('@')[1]

def mostrar_info_persona(persona: Persona):
    """Muestra información detallada de una persona."""
    with st.container():
        st.markdown("---")
        st.markdown("### 👤 Información de la Persona Seleccionada")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📝 Datos Personales**")
            st.markdown(f"• **Nombres:** {persona.nombres}")
            st.markdown(f"• **Apellido Paterno:** {persona.apellido_paterno}")
            st.markdown(f"• **Apellido Materno:** {persona.apellido_materno or 'N/A'}")
        
        with col2:
            st.markdown("**🆔 Identificación**")
            st.markdown(f"• **CURP:** {persona.curp or 'Sin CURP'}")
            st.markdown(f"• **ID:** {persona.id_persona}")
        
        with col3:
            st.markdown("**⛪ Estado**")
            st.markdown(f"• **Canónico:** {persona.estado_canonico}")
        
        st.markdown("---")

# ====================================================================
# FUNCIÓN PRINCIPAL
# ====================================================================

def mostrar_crud_usuarios(db_engine, db_module, db_mode, st_display_func):
    """Módulo completo CRUD para Usuarios del sistema."""
    st.header(f"👤 Gestión de Usuarios del Sistema - Modo: {db_mode}")
    
    st.info("🔒 Los usuarios pueden acceder al sistema con credenciales únicas vinculadas a una persona registrada.")
    
    tabs = st.tabs(["➕ Crear Usuario", "📋 Ver Usuarios", "✏️ Actualizar", "🗑️ Eliminar"])
    
    # ================================================================
    # TAB 1: CREAR USUARIO
    # ================================================================
    with tabs[0]:
        st.subheader("➕ Crear Nuevo Usuario")
        
        st.markdown("### 🔍 Paso 1: Buscar o Seleccionar Persona")
        
        # Buscar persona
        col1, col2 = st.columns([1, 2])
        
        with col1:
            curp_busqueda = st.text_input(
                "Buscar por CURP",
                max_chars=18,
                key="usuario_crear_curp",
                help="Ingresa el CURP de la persona (18 caracteres)"
            )
        
        persona_encontrada = None
        if curp_busqueda:
            persona_encontrada = buscar_persona_por_curp(curp_busqueda, db_engine)
            if persona_encontrada:
                st.success(f"✅ ¡Persona encontrada!")
                mostrar_info_persona(persona_encontrada)
            else:
                st.error("❌ No se encontró ninguna persona con ese CURP")
                st.info("💡 Verifica que el CURP esté correcto o registra primero a la persona en el módulo 'Personas'")
        
        with col2:
            personas = obtener_lista_personas(db_engine)
            
            if not personas:
                st.error("❌ No hay personas registradas")
                st.info("💡 Primero debes registrar personas en el módulo 'Gestión de Personas'")
                id_persona_final = None
            else:
                opciones_personas = {0: "-- Selecciona una Persona --"}
                opciones_personas.update({
                    p.id_persona: f"{p.nombre_completo()} - {p.curp or 'Sin CURP'}"
                    for p in personas
                })
                
                id_persona_sel = st.selectbox(
                    "O selecciona de la lista:",
                    options=opciones_personas.keys(),
                    format_func=lambda x: opciones_personas[x],
                    key="usuario_crear_select"
                )
                
                id_persona_final = persona_encontrada.id_persona if persona_encontrada else (id_persona_sel if id_persona_sel != 0 else None)
                
                # Mostrar información de la persona seleccionada de la lista
                if id_persona_sel != 0 and not persona_encontrada:
                    persona_seleccionada = next((p for p in personas if p.id_persona == id_persona_sel), None)
                    if persona_seleccionada:
                        st.success(f"✅ Persona seleccionada")
                        mostrar_info_persona(persona_seleccionada)
        
        if id_persona_final:
            # Verificar si ya existe usuario
            with Session(db_engine) as session:
                usuario_existente = session.exec(
                    select(Usuario).where(Usuario.id_persona == id_persona_final)
                ).first()
            
            if usuario_existente:
                st.error(f"❌ Esta persona ya tiene un usuario registrado")
                st.warning(f"**Username existente:** {usuario_existente.username}")
                st.info("💡 No puedes crear dos usuarios para la misma persona. Si necesitas cambiar el usuario, usa la opción 'Actualizar' o 'Eliminar'.")
            else:
                st.markdown("### 🔐 Paso 2: Configurar Credenciales")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    username = st.text_input(
                        "Nombre de Usuario (*)",
                        max_chars=50,
                        key="usuario_username",
                        help="Debe ser único, sin espacios"
                    )
                    
                    password = st.text_input(
                        "Contraseña (*)",
                        type="password",
                        key="usuario_password",
                        help="Mínimo 8 caracteres: mayúsculas, minúsculas y números"
                    )
                    
                    password_confirm = st.text_input(
                        "Confirmar Contraseña (*)",
                        type="password",
                        key="usuario_password_confirm"
                    )
                
                with col2:
                    email = st.text_input(
                        "Email (*)",
                        max_chars=100,
                        key="usuario_email",
                        help="Correo electrónico único"
                    )
                    
                    activo = st.checkbox(
                        "Usuario Activo",
                        value=True,
                        key="usuario_activo",
                        help="Solo usuarios activos pueden iniciar sesión"
                    )
                    
                    # Mostrar indicadores de validez de contraseña
                    if password:
                        st.markdown("**Validación de Contraseña:**")
                        checks = []
                        checks.append("✅ Longitud ≥ 8" if len(password) >= 8 else "❌ Longitud ≥ 8")
                        checks.append("✅ Mayúscula" if any(c.isupper() for c in password) else "❌ Mayúscula")
                        checks.append("✅ Minúscula" if any(c.islower() for c in password) else "❌ Minúscula")
                        checks.append("✅ Número" if any(c.isdigit() for c in password) else "❌ Número")
                        for check in checks:
                            st.caption(check)
                
                st.markdown("---")
                
                if st.button("💾 Crear Usuario", type="primary", width="stretch", key="btn_crear_usuario"):
                    if not username or not password or not email:
                        st.error("❌ Todos los campos marcados con (*) son obligatorios")
                    elif ' ' in username:
                        st.error("❌ El nombre de usuario no puede contener espacios")
                    elif password != password_confirm:
                        st.error("❌ Las contraseñas no coinciden")
                    else:
                        es_valida, mensaje = validar_password(password)
                        if not es_valida:
                            st.error(f"❌ {mensaje}")
                        elif not validar_email(email):
                            st.error("❌ El formato del email no es válido")
                        else:
                            # Verificar que el username no exista
                            with Session(db_engine) as session:
                                username_existe = session.exec(
                                    select(Usuario).where(Usuario.username == username.strip())
                                ).first()
                            
                            if username_existe:
                                st.error(f"❌ El nombre de usuario '{username}' ya está en uso")
                                st.info("💡 Elige otro nombre de usuario diferente")
                            else:
                                nuevo_usuario = Usuario(
                                    id_persona=id_persona_final,
                                    username=username.strip(),
                                    email=email.strip().lower(),
                                    password_hash=hash_password(password),
                                    activo=activo
                                )
                                
                                if db_module.crear_registro(nuevo_usuario, db_engine, st_display_func, nombre_tabla="Usuario"):
                                    st.success("✅ Usuario creado exitosamente")
                                    st.balloons()
                                    st.info("💡 El usuario ya puede iniciar sesión con sus credenciales")
                                    st.rerun()
        else:
            st.info("💡 Para crear un usuario, primero busca o selecciona una persona")
    
    # ================================================================
    # TAB 2: VER USUARIOS
    # ================================================================
    with tabs[1]:
        st.subheader("📋 Lista de Usuarios Registrados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            filtro_activo = st.selectbox(
                "Filtrar por Estado:",
                options=["Todos", "Activos", "Inactivos"],
                key="filtro_usuario_activo"
            )
        
        with col2:
            buscar_username = st.text_input(
                "Buscar por Username:",
                key="buscar_usuario_username"
            )
        
        with Session(db_engine) as session:
            statement = select(Usuario)
            
            if filtro_activo == "Activos":
                statement = statement.where(Usuario.activo == True)
            elif filtro_activo == "Inactivos":
                statement = statement.where(Usuario.activo == False)
            
            usuarios = session.exec(statement).all()
            
            if buscar_username:
                usuarios = [u for u in usuarios if buscar_username.lower() in u.username.lower()]
        
        if usuarios:
            st.markdown(f"**Total de Usuarios:** {len(usuarios)}")
            
            data = []
            with Session(db_engine) as session:
                for u in usuarios:
                    persona = session.get(Persona, u.id_persona)
                    estado_display = "✅ Activo" if u.activo else "❌ Inactivo"
                    
                    data.append({
                        "ID": u.id_usuario,
                        "Username": u.username,
                        "Nombre Completo": persona.nombre_completo() if persona else "N/A",
                        "Email": u.email,
                        "Estado": estado_display
                    })
            
            st.dataframe(data, width="stretch", hide_index=True)
        else:
            st.info("ℹ️ No hay usuarios registrados")
    
    # ================================================================
    # TAB 3: ACTUALIZAR USUARIO
    # ================================================================
    with tabs[2]:
        st.subheader("✏️ Actualizar Usuario")
        
        with Session(db_engine) as session:
            usuarios = session.exec(select(Usuario)).all()
        
        if usuarios:
            opciones_usuarios = {}
            with Session(db_engine) as session:
                for u in usuarios:
                    persona = session.get(Persona, u.id_persona)
                    estado = "✅" if u.activo else "❌"
                    opciones_usuarios[u.id_usuario] = f"{estado} {u.username} - {persona.nombre_completo() if persona else 'N/A'}"
            
            id_usuario_sel = st.selectbox(
                "Selecciona el usuario a actualizar:",
                options=opciones_usuarios.keys(),
                format_func=lambda x: opciones_usuarios[x],
                key="actualizar_usuario_select"
            )
            
            usuario_actualizar = next((u for u in usuarios if u.id_usuario == id_usuario_sel), None)
            
            if usuario_actualizar:
                # Mostrar info de la persona asociada
                with Session(db_engine) as session:
                    persona_asociada = session.get(Persona, usuario_actualizar.id_persona)
                
                if persona_asociada:
                    mostrar_info_persona(persona_asociada)
                
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    upd_username = st.text_input(
                        "Nombre de Usuario (*)",
                        value=usuario_actualizar.username,
                        max_chars=50,
                        key=f"upd_username_{id_usuario_sel}"
                    )
                    
                    upd_email = st.text_input(
                        "Email (*)",
                        value=usuario_actualizar.email,
                        max_chars=100,
                        key=f"upd_email_{id_usuario_sel}"
                    )
                    
                    upd_activo = st.checkbox(
                        "Usuario Activo",
                        value=usuario_actualizar.activo,
                        key=f"upd_activo_{id_usuario_sel}"
                    )
                
                with col2:
                    st.markdown("**Cambiar Contraseña (Opcional)**")
                    
                    upd_password = st.text_input(
                        "Nueva Contraseña",
                        type="password",
                        key=f"upd_password_{id_usuario_sel}"
                    )
                    
                    upd_password_confirm = st.text_input(
                        "Confirmar Nueva Contraseña",
                        type="password",
                        key=f"upd_password_confirm_{id_usuario_sel}"
                    )
                
                if st.button("💾 Actualizar", type="primary", width="stretch", key=f"btn_upd_usuario_{id_usuario_sel}"):
                    if not upd_username or not upd_email:
                        st.error("❌ El username y email son obligatorios")
                    elif ' ' in upd_username:
                        st.error("❌ El nombre de usuario no puede contener espacios")
                    elif not validar_email(upd_email):
                        st.error("❌ El formato del email no es válido")
                    else:
                        data_to_update = {
                            "username": upd_username.strip(),
                            "email": upd_email.strip().lower(),
                            "activo": upd_activo
                        }
                        
                        if upd_password:
                            if upd_password != upd_password_confirm:
                                st.error("❌ Las contraseñas no coinciden")
                            else:
                                es_valida, mensaje = validar_password(upd_password)
                                if not es_valida:
                                    st.error(f"❌ {mensaje}")
                                else:
                                    data_to_update["password_hash"] = hash_password(upd_password)
                                    
                                    if db_module.actualizar_registro(
                                        Usuario,
                                        usuario_actualizar.id_usuario,
                                        data_to_update,
                                        db_engine,
                                        st_display_func,
                                        nombre_tabla="Usuario"
                                    ):
                                        st.success("✅ Usuario actualizado")
                                        st.rerun()
                        else:
                            if db_module.actualizar_registro(
                                Usuario,
                                usuario_actualizar.id_usuario,
                                data_to_update,
                                db_engine,
                                st_display_func,
                                nombre_tabla="Usuario"
                            ):
                                st.success("✅ Usuario actualizado")
                                st.rerun()
        else:
            st.info("ℹ️ No hay usuarios para actualizar")
    
    # ================================================================
    # TAB 4: ELIMINAR USUARIO
    # ================================================================
    with tabs[3]:
        st.subheader("🗑️ Eliminar Usuario")
        
        with Session(db_engine) as session:
            usuarios = session.exec(select(Usuario)).all()
        
        if usuarios:
            st.warning("⚠️ Esta acción eliminará el usuario pero NO eliminará a la persona asociada.")
            
            opciones_usuarios = {}
            with Session(db_engine) as session:
                for u in usuarios:
                    persona = session.get(Persona, u.id_persona)
                    estado = "✅" if u.activo else "❌"
                    opciones_usuarios[u.id_usuario] = f"{estado} {u.username} - {persona.nombre_completo() if persona else 'N/A'}"
            
            id_usuario_eliminar = st.selectbox(
                "Selecciona el usuario a eliminar:",
                options=opciones_usuarios.keys(),
                format_func=lambda x: opciones_usuarios[x],
                key="eliminar_usuario_select"
            )
            
            usuario_eliminar = next((u for u in usuarios if u.id_usuario == id_usuario_eliminar), None)
            
            if usuario_eliminar:
                st.markdown("---")
                
                with Session(db_engine) as session:
                    persona = session.get(Persona, usuario_eliminar.id_persona)
                
                st.markdown(f"**Username:** {usuario_eliminar.username}")
                st.markdown(f"**Email:** {usuario_eliminar.email}")
                st.markdown(f"**Persona:** {persona.nombre_completo() if persona else 'N/A'}")
                st.markdown(f"**Estado:** {'✅ Activo' if usuario_eliminar.activo else '❌ Inactivo'}")
                
                st.markdown("---")
                
                CONFIRM_KEY = f"confirm_delete_usuario_{usuario_eliminar.id_usuario}"
                
                if not st.session_state.get(CONFIRM_KEY, False):
                    if st.button(
                        "🗑️ Eliminar Usuario",
                        type="secondary",
                        key=f"init_delete_usuario_{usuario_eliminar.id_usuario}"
                    ):
                        st.session_state[CONFIRM_KEY] = True
                        st.rerun()
                else:
                    st.error(f"⚠️ ¿Confirmas eliminar el usuario **{usuario_eliminar.username}**?")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button(
                            "✅ SÍ, ELIMINAR",
                            type="primary",
                            width="stretch",
                            key=f"confirm_yes_usuario_{usuario_eliminar.id_usuario}"
                        ):
                            if db_module.eliminar_registro(
                                Usuario,
                                usuario_eliminar.id_usuario,
                                db_engine,
                                st_display_func,
                                nombre_tabla="Usuario"
                            ):
                                st.session_state.pop(CONFIRM_KEY, None)
                                st.success("✅ Usuario eliminado")
                                st.rerun()
                    
                    with col2:
                        if st.button(
                            "❌ Cancelar",
                            width="stretch",
                            key=f"confirm_no_usuario_{usuario_eliminar.id_usuario}"
                        ):
                            st.session_state[CONFIRM_KEY] = False
                            st.rerun()
        else:
            st.info("ℹ️ No hay usuarios para eliminar")