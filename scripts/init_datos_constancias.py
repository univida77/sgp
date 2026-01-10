# init_datos_constancias.py
"""
Script de inicialización de datos para el módulo de constancias
Sistema Parroquial v4.0

USO:
python init_datos_constancias.py

Este script crea:
- Configuración inicial del módulo
- Tipos de reunión para actas
- Plantillas de correo
- Áreas parroquiales
- Bodegas (B-1 a B-6)
- Perfiles de usuario
"""

from sqlmodel import Session, select
from datetime import datetime
from decimal import Decimal
import sys

# Importar modelos
try:
    from models_constancias import (
        ConfiguracionConstancia,
        PlantillaCorreoConstancia,
        ConfiguracionCampoPlantilla
    )
    from models_financiero import (
        AreaParroquial,
        Bodega,
        PerfilUsuario,
        TipoReunion
    )
    from database.local import get_engine as get_local_engine
    from database.remote import get_engine as get_remote_engine
except ImportError as e:
    print(f"❌ Error al importar modelos: {e}")
    print("Asegúrate de ejecutar desde la raíz del proyecto")
    sys.exit(1)


# ====================================================================
# FUNCIONES DE INICIALIZACIÓN
# ====================================================================

def crear_configuracion_inicial(session: Session) -> bool:
    """Crea configuración inicial del módulo de constancias"""
    print("📋 Creando configuración inicial...")
    
    # Verificar si ya existe
    config_existe = session.exec(
        select(ConfiguracionConstancia).where(
            ConfiguracionConstancia.activo == True
        )
    ).first()
    
    if config_existe:
        print("   ℹ️  Ya existe configuración activa")
        return True
    
    # Crear configuración
    config = ConfiguracionConstancia(
        costo_base_mxn=Decimal("100.00"),
        tasa_iva=Decimal("0.16"),
        costo_total_mxn=Decimal("116.00"),
        tipo_cambio_usd=Decimal("17.00"),
        costo_base_usd=Decimal("5.88"),
        costo_total_usd=Decimal("6.82"),
        qr_pos_x=50,
        qr_pos_y=950,
        qr_size=150,
        payu_test_mode=True,
        url_verificacion_base="https://parroquia-tlacolula.com/verificar",
        activo=True
    )
    
    session.add(config)
    session.commit()
    print("   ✅ Configuración creada")
    return True


def crear_areas_parroquiales(session: Session) -> bool:
    """Crea áreas parroquiales"""
    print("🏛️  Creando áreas parroquiales...")
    
    areas = [
        {"nombre": "Pastoral Litúrgica", "desc": "Liturgia y sacramentos"},
        {"nombre": "Pastoral Profética", "desc": "Catequesis y formación"},
        {"nombre": "Pastoral Social", "desc": "Caridad y servicio"},
        {"nombre": "Pastoral Familiar", "desc": "Familia y matrimonio"},
        {"nombre": "Administrativa", "desc": "Administración y finanzas"},
        {"nombre": "Infraestructura", "desc": "Mantenimiento y construcción"}
    ]
    
    creadas = 0
    
    for area_data in areas:
        # Verificar si existe
        existe = session.exec(
            select(AreaParroquial).where(
                AreaParroquial.nombre_area == area_data["nombre"]
            )
        ).first()
        
        if not existe:
            area = AreaParroquial(
                nombre_area=area_data["nombre"],
                descripcion=area_data["desc"],
                activo=True
            )
            session.add(area)
            creadas += 1
    
    session.commit()
    print(f"   ✅ {creadas} áreas creadas ({len(areas)-creadas} ya existían)")
    return True


def crear_bodegas(session: Session) -> bool:
    """Crea bodegas B-1 a B-6"""
    print("📦 Creando bodegas...")
    
    bodegas_data = [
        {"codigo": "B-1", "nombre": "Bodega Principal", "ubicacion": "Planta baja, lado norte"},
        {"codigo": "B-2", "nombre": "Bodega de Catequesis", "ubicacion": "Segundo piso"},
        {"codigo": "B-3", "nombre": "Bodega de Liturgia", "ubicacion": "Junto a sacristía"},
        {"codigo": "B-4", "nombre": "Bodega de Mantenimiento", "ubicacion": "Patio trasero"},
        {"codigo": "B-5", "nombre": "Bodega de Eventos", "ubicacion": "Salón social"},
        {"codigo": "B-6", "nombre": "Archivo General", "ubicacion": "Oficina parroquial"}
    ]
    
    creadas = 0
    
    for bodega_data in bodegas_data:
        # Verificar si existe
        existe = session.exec(
            select(Bodega).where(
                Bodega.codigo_bodega == bodega_data["codigo"]
            )
        ).first()
        
        if not existe:
            bodega = Bodega(
                codigo_bodega=bodega_data["codigo"],
                nombre_bodega=bodega_data["nombre"],
                ubicacion=bodega_data["ubicacion"],
                activo=True
            )
            session.add(bodega)
            creadas += 1
    
    session.commit()
    print(f"   ✅ {creadas} bodegas creadas ({len(bodegas_data)-creadas} ya existían)")
    return True


def crear_perfiles_usuario(session: Session) -> bool:
    """Crea perfiles de usuario con permisos"""
    print("👥 Creando perfiles de usuario...")
    
    perfiles = [
        {
            "nombre": "Administrador General",
            "desc": "Acceso total al sistema",
            "permisos": {
                "finanzas": True, "inventario": True, "actas": True,
                "crear_presupuesto": True, "registrar_transacciones": True,
                "ver_finanzas_globales": True, "validar_transacciones": True,
                "registrar_bienes": True, "mover_bienes": True,
                "dar_baja_bienes": True, "ver_inventario_global": True,
                "crear_actas": True, "aprobar_actas": True, "consultar_actas": True
            }
        },
        {
            "nombre": "Párroco",
            "desc": "Supervisor general con validación",
            "permisos": {
                "finanzas": True, "inventario": True, "actas": True,
                "ver_finanzas_globales": True, "validar_transacciones": True,
                "ver_inventario_global": True, "aprobar_actas": True,
                "consultar_actas": True
            }
        },
        {
            "nombre": "Secretario Parroquial",
            "desc": "Gestión administrativa",
            "permisos": {
                "finanzas": True, "inventario": True, "actas": True,
                "registrar_transacciones": True, "registrar_bienes": True,
                "crear_actas": True, "consultar_actas": True
            }
        },
        {
            "nombre": "Tesorero",
            "desc": "Gestión financiera",
            "permisos": {
                "finanzas": True,
                "crear_presupuesto": True, "registrar_transacciones": True,
                "ver_finanzas_globales": True
            }
        },
        {
            "nombre": "Sacristán",
            "desc": "Gestión de inventario litúrgico",
            "permisos": {
                "inventario": True,
                "registrar_bienes": True, "mover_bienes": True
            }
        },
        {
            "nombre": "Responsable de Grupo",
            "desc": "Gestión de su grupo parroquial",
            "permisos": {
                "finanzas": False, "inventario": False, "actas": True,
                "registrar_transacciones": True, "consultar_actas": True
            }
        }
    ]
    
    creados = 0
    
    for perfil_data in perfiles:
        # Verificar si existe
        existe = session.exec(
            select(PerfilUsuario).where(
                PerfilUsuario.nombre_perfil == perfil_data["nombre"]
            )
        ).first()
        
        if not existe:
            permisos = perfil_data["permisos"]
            
            perfil = PerfilUsuario(
                nombre_perfil=perfil_data["nombre"],
                descripcion=perfil_data["desc"],
                # Permisos de finanzas
                puede_crear_presupuesto=permisos.get("crear_presupuesto", False),
                puede_registrar_transacciones=permisos.get("registrar_transacciones", False),
                puede_ver_finanzas_globales=permisos.get("ver_finanzas_globales", False),
                puede_validar_transacciones=permisos.get("validar_transacciones", False),
                # Permisos de inventario
                puede_registrar_bienes=permisos.get("registrar_bienes", False),
                puede_mover_bienes=permisos.get("mover_bienes", False),
                puede_dar_baja_bienes=permisos.get("dar_baja_bienes", False),
                puede_ver_inventario_global=permisos.get("ver_inventario_global", False),
                # Permisos de actas
                puede_crear_actas=permisos.get("crear_actas", False),
                puede_aprobar_actas=permisos.get("aprobar_actas", False),
                puede_consultar_actas=permisos.get("consultar_actas", False),
                activo=True
            )
            session.add(perfil)
            creados += 1
    
    session.commit()
    print(f"   ✅ {creados} perfiles creados ({len(perfiles)-creados} ya existían)")
    return True


def crear_tipos_reunion(session: Session) -> bool:
    """Crea tipos de reunión para actas"""
    print("📋 Creando tipos de reunión...")
    
    tipos = [
        {"nombre": "Ordinaria", "desc": "Reunión ordinaria programada"},
        {"nombre": "Mensual", "desc": "Reunión mensual regular"},
        {"nombre": "Extraordinaria", "desc": "Reunión extraordinaria"},
        {"nombre": "Asamblea General", "desc": "Asamblea general de la parroquia"},
        {"nombre": "Consejo Pastoral", "desc": "Reunión del consejo pastoral"},
        {"nombre": "Consejo Económico", "desc": "Reunión del consejo económico"}
    ]
    
    creados = 0
    
    for tipo_data in tipos:
        # Verificar si existe
        existe = session.exec(
            select(TipoReunion).where(
                TipoReunion.nombre_tipo == tipo_data["nombre"]
            )
        ).first()
        
        if not existe:
            tipo = TipoReunion(
                nombre_tipo=tipo_data["nombre"],
                descripcion=tipo_data["desc"],
                activo=True
            )
            session.add(tipo)
            creados += 1
    
    session.commit()
    print(f"   ✅ {creados} tipos de reunión creados ({len(tipos)-creados} ya existían)")
    return True


def crear_plantillas_correo(session: Session) -> bool:
    """Crea plantillas de correo electrónico"""
    print("📧 Creando plantillas de correo...")
    
    plantillas = [
        {
            "nombre": "solicitud_recibida",
            "asunto": "Solicitud de Constancia Recibida - Parroquia Santa María",
            "cuerpo": """
                <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Solicitud de Constancia Recibida</h2>
                    <p>Estimado/a <strong>{{nombre_solicitante}}</strong>,</p>
                    <p>Hemos recibido tu solicitud de constancia de <strong>{{tipo_sacramento}}</strong>.</p>
                    <p><strong>Número de solicitud:</strong> {{id_solicitud}}</p>
                    <p><strong>Estado:</strong> Pendiente de validación</p>
                    <p>Te notificaremos cuando tu solicitud sea validada.</p>
                    <br>
                    <p>Bendiciones,<br>
                    Parroquia de Santa María de la Asunción<br>
                    Tlacolula de Matamoros, Oaxaca</p>
                </body>
                </html>
            """,
            "variables": "nombre_solicitante, tipo_sacramento, id_solicitud"
        },
        {
            "nombre": "validacion_exitosa",
            "asunto": "Solicitud Validada - Proceder al Pago",
            "cuerpo": """
                <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>✅ Solicitud Validada</h2>
                    <p>Estimado/a <strong>{{nombre_solicitante}}</strong>,</p>
                    <p>Tu solicitud de constancia ha sido <strong>validada exitosamente</strong>.</p>
                    <p><strong>Siguiente paso:</strong> Realizar el pago</p>
                    <p><strong>Monto a pagar:</strong> ${{monto_total}} {{moneda}}</p>
                    <p>{{instrucciones_pago}}</p>
                    <br>
                    <p>Bendiciones,<br>
                    Parroquia de Santa María de la Asunción</p>
                </body>
                </html>
            """,
            "variables": "nombre_solicitante, monto_total, moneda, instrucciones_pago"
        },
        {
            "nombre": "constancia_lista",
            "asunto": "Tu Constancia está Lista - Descargar",
            "cuerpo": """
                <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>📄 Constancia Lista</h2>
                    <p>Estimado/a <strong>{{nombre_solicitante}}</strong>,</p>
                    <p>Tu constancia de <strong>{{tipo_sacramento}}</strong> está lista.</p>
                    <p><strong>Folio:</strong> {{folio}}</p>
                    <p><a href="{{url_descarga}}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Descargar Constancia</a></p>
                    <p>La constancia incluye un código QR de verificación.</p>
                    <br>
                    <p>Bendiciones,<br>
                    Parroquia de Santa María de la Asunción</p>
                </body>
                </html>
            """,
            "variables": "nombre_solicitante, tipo_sacramento, folio, url_descarga"
        }
    ]
    
    creadas = 0
    
    for plantilla_data in plantillas:
        # Verificar si existe
        existe = session.exec(
            select(PlantillaCorreoConstancia).where(
                PlantillaCorreoConstancia.nombre_plantilla == plantilla_data["nombre"]
            )
        ).first()
        
        if not existe:
            plantilla = PlantillaCorreoConstancia(
                nombre_plantilla=plantilla_data["nombre"],
                asunto=plantilla_data["asunto"],
                cuerpo_html=plantilla_data["cuerpo"],
                variables_disponibles=plantilla_data["variables"],
                activo=True
            )
            session.add(plantilla)
            creadas += 1
    
    session.commit()
    print(f"   ✅ {creadas} plantillas creadas ({len(plantillas)-creadas} ya existían)")
    return True


# ====================================================================
# FUNCIÓN PRINCIPAL
# ====================================================================

def main():
    """Función principal de inicialización"""
    print("=" * 60)
    print("INICIALIZACIÓN DE DATOS - MÓDULO DE CONSTANCIAS")
    print("Sistema Parroquial v4.0")
    print("=" * 60)
    print()
    
    # Preguntar modo
    print("Selecciona el modo:")
    print("1. Base de datos LOCAL (SQLite)")
    print("2. Base de datos REMOTA (MySQL)")
    print("3. Ambas")
    
    opcion = input("\nOpción (1/2/3): ").strip()
    
    engines = []
    
    if opcion in ["1", "3"]:
        print("\n🔌 Conectando a base de datos LOCAL...")
        try:
            local_engine = get_local_engine()
            engines.append(("LOCAL", local_engine))
            print("   ✅ Conectado a SQLite")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    if opcion in ["2", "3"]:
        print("\n🔌 Conectando a base de datos REMOTA...")
        try:
            remote_engine = get_remote_engine()
            if remote_engine:
                engines.append(("REMOTA", remote_engine))
                print("   ✅ Conectado a MySQL")
            else:
                print("   ⚠️  No se pudo conectar a MySQL")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    if not engines:
        print("\n❌ No se pudo conectar a ninguna base de datos")
        return
    
    # Procesar cada base de datos
    for nombre, engine in engines:
        print("\n" + "=" * 60)
        print(f"PROCESANDO BASE DE DATOS: {nombre}")
        print("=" * 60)
        
        with Session(engine) as session:
            try:
                # Crear datos
                crear_configuracion_inicial(session)
                crear_areas_parroquiales(session)
                crear_bodegas(session)
                crear_perfiles_usuario(session)
                crear_tipos_reunion(session)
                crear_plantillas_correo(session)
                
                print(f"\n✅ Inicialización completada en {nombre}")
                
            except Exception as e:
                print(f"\n❌ Error durante inicialización en {nombre}: {e}")
                session.rollback()
    
    print("\n" + "=" * 60)
    print("✅ PROCESO COMPLETADO")
    print("=" * 60)
    print()
    print("Próximos pasos:")
    print("1. Verifica los datos en el sistema")
    print("2. Sube las plantillas PNG de constancias")
    print("3. Configura las coordenadas de los campos")
    print("4. Configura PayU si usarás pago en línea")
    print()


if __name__ == "__main__":
    main()
