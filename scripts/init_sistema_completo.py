# scripts/init_sistema_completo.py
"""
Script de inicialización completa del sistema
Sistema Parroquial v4.0

EJECUTAR DESPUÉS DE INSTALAR:
python scripts/init_sistema_completo.py

Este script crea:
- Configuración de constancias
- Áreas parroquiales
- Bodegas (B-1 a B-6)
- Perfiles de usuario con permisos
- Tipos de reunión
- Plantillas de correo
- Categorías de inventario
- Datos básicos de geografía
"""

from sqlmodel import Session, select
from datetime import datetime, date
from decimal import Decimal
import sys
import os

# Añadir ruta del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar modelos SOLO los que EXISTEN
try:
    from models import (
        # Geografía
        Pais, Provincia, Arquidiocesis, Decanato, Parroquia, Comunidad, Capilla,
        
        # Personas
        Persona,
        
        # Catequesis
        RolCatequista,
        
        # Grupos
        Rol,
        
        # Sistema
        Usuario,
        
        # Finanzas e inventario
        PerfilUsuario, AreaParroquial, Bodega, CategoriaInventario,
        
        # Actas
        TipoReunion,
        
        # Constancias
        ConfiguracionConstancia, PlantillaCorreoConstancia
    )
    
    from database.local import get_engine as get_local_engine
    from database.remote import get_engine as get_remote_engine
except ImportError as e:
    print(f"❌ Error al importar: {e}")
    print("Asegúrate de ejecutar desde la raíz del proyecto")
    sys.exit(1)


def crear_configuracion_constancias(session):
    """Crea configuración inicial de constancias"""
    print("📄 Configuración de constancias...")
    
    existe = session.exec(select(ConfiguracionConstancia).where(
        ConfiguracionConstancia.activo == True
    )).first()
    
    if not existe:
        config = ConfiguracionConstancia(
            costo_base_mxn=Decimal("100.00"),
            tasa_iva=Decimal("0.16"),
            costo_total_mxn=Decimal("116.00"),
            tipo_cambio_usd=Decimal("17.00"),
            costo_base_usd=Decimal("5.88"),
            costo_total_usd=Decimal("6.82"),
            payu_test_mode=True,
            url_verificacion_base="https://parroquia-tlacolula.com/verificar",
            activo=True
        )
        session.add(config)
        print("   ✅ Configuración creada")
    else:
        print("   ℹ️  Ya existe")


def crear_areas_parroquiales(session):
    """Crea áreas parroquiales"""
    print("🛐 Áreas parroquiales...")
    
    areas = [
        ("Pastoral Litúrgica", "Liturgia y sacramentos"),
        ("Pastoral Profética", "Catequesis y formación"),
        ("Pastoral Social", "Caridad y servicio"),
        ("Pastoral Familiar", "Familia y matrimonio"),
        ("Administrativa", "Administración y finanzas"),
        ("Infraestructura", "Mantenimiento")
    ]
    
    creadas = 0
    for nombre, desc in areas:
        existe = session.exec(select(AreaParroquial).where(
            AreaParroquial.nombre_area == nombre
        )).first()
        
        if not existe:
            session.add(AreaParroquial(nombre_area=nombre, descripcion=desc, activo=True))
            creadas += 1
    
    print(f"   ✅ {creadas} creadas")


def crear_bodegas(session):
    """Crea bodegas B-1 a B-6"""
    print("📦 Bodegas...")
    
    bodegas = [
        ("B-1", "Bodega Principal", "Planta baja, lado norte"),
        ("B-2", "Bodega de Catequesis", "Segundo piso"),
        ("B-3", "Bodega de Liturgia", "Junto a sacristía"),
        ("B-4", "Bodega de Mantenimiento", "Patio trasero"),
        ("B-5", "Bodega de Eventos", "Salón social"),
        ("B-6", "Archivo General", "Oficina parroquial")
    ]
    
    creadas = 0
    for codigo, nombre, ubicacion in bodegas:
        existe = session.exec(select(Bodega).where(
            Bodega.codigo_bodega == codigo
        )).first()
        
        if not existe:
            session.add(Bodega(
                codigo_bodega=codigo,
                nombre_bodega=nombre,
                ubicacion=ubicacion,
                activo=True
            ))
            creadas += 1
    
    print(f"   ✅ {creadas} creadas")


def crear_perfiles_usuario(session):
    """Crea perfiles con permisos"""
    print("👥 Perfiles de usuario...")
    
    perfiles = [
        {
            "nombre": "Administrador General",
            "desc": "Acceso total",
            "p": {
                "crear_presupuesto": True, "registrar_transacciones": True,
                "ver_finanzas_globales": True, "validar_transacciones": True,
                "registrar_bienes": True, "mover_bienes": True,
                "dar_baja_bienes": True, "ver_inventario_global": True,
                "crear_actas": True, "aprobar_actas": True, "consultar_actas": True
            }
        },
        {
            "nombre": "Párroco",
            "desc": "Supervisor",
            "p": {
                "ver_finanzas_globales": True, "validar_transacciones": True,
                "ver_inventario_global": True, "aprobar_actas": True, "consultar_actas": True
            }
        },
        {
            "nombre": "Secretario Parroquial",
            "desc": "Gestión administrativa",
            "p": {
                "registrar_transacciones": True, "registrar_bienes": True,
                "crear_actas": True, "consultar_actas": True
            }
        },
        {
            "nombre": "Tesorero",
            "desc": "Gestión financiera",
            "p": {
                "crear_presupuesto": True, "registrar_transacciones": True,
                "ver_finanzas_globales": True
            }
        },
        {
            "nombre": "Sacristán",
            "desc": "Inventario litúrgico",
            "p": {
                "registrar_bienes": True, "mover_bienes": True
            }
        },
        {
            "nombre": "Responsable de Grupo",
            "desc": "Gestión de grupo",
            "p": {
                "consultar_actas": True
            }
        }
    ]
    
    creados = 0
    for perfil_data in perfiles:
        existe = session.exec(select(PerfilUsuario).where(
            PerfilUsuario.nombre_perfil == perfil_data["nombre"]
        )).first()
        
        if not existe:
            p = perfil_data["p"]
            perfil = PerfilUsuario(
                nombre_perfil=perfil_data["nombre"],
                descripcion=perfil_data["desc"],
                puede_crear_presupuesto=p.get("crear_presupuesto", False),
                puede_registrar_transacciones=p.get("registrar_transacciones", False),
                puede_ver_finanzas_globales=p.get("ver_finanzas_globales", False),
                puede_validar_transacciones=p.get("validar_transacciones", False),
                puede_registrar_bienes=p.get("registrar_bienes", False),
                puede_mover_bienes=p.get("mover_bienes", False),
                puede_dar_baja_bienes=p.get("dar_baja_bienes", False),
                puede_ver_inventario_global=p.get("ver_inventario_global", False),
                puede_crear_actas=p.get("crear_actas", False),
                puede_aprobar_actas=p.get("aprobar_actas", False),
                puede_consultar_actas=p.get("consultar_actas", False),
                activo=True
            )
            session.add(perfil)
            creados += 1
    
    print(f"   ✅ {creados} creados")


def crear_tipos_reunion(session):
    """Crea tipos de reunión"""
    print("📋 Tipos de reunión...")
    
    tipos = [
        ("Ordinaria", "Reunión ordinaria"),
        ("Mensual", "Reunión mensual"),
        ("Extraordinaria", "Reunión extraordinaria"),
        ("Asamblea General", "Asamblea general"),
        ("Consejo Pastoral", "Consejo pastoral"),
        ("Consejo Económico", "Consejo económico")
    ]
    
    creados = 0
    for nombre, desc in tipos:
        existe = session.exec(select(TipoReunion).where(
            TipoReunion.nombre_tipo == nombre
        )).first()
        
        if not existe:
            session.add(TipoReunion(nombre_tipo=nombre, descripcion=desc, activo=True))
            creados += 1
    
    print(f"   ✅ {creados} creados")


def crear_categorias_inventario(session):
    """Crea categorías de inventario"""
    print("📂 Categorías de inventario...")
    
    categorias = [
        ("Muebles", "Mesas, sillas, escritorios"),
        ("Electrónicos", "Bocinas, proyectores, computadoras"),
        ("Litúrgicos", "Cálices, custodias, vestimentas"),
        ("Instrumentos Musicales", "Guitarras, teclados"),
        ("Vajilla y Trastes", "Platos, vasos, cubiertos"),
        ("Herramientas", "Martillos, taladros"),
        ("Inmuebles", "Edificios, terrenos"),
        ("Vehículos", "Autos, camionetas"),
        ("Libros y Material", "Biblias, catecismos"),
        ("Otros", "Diversos")
    ]
    
    creadas = 0
    for nombre, desc in categorias:
        existe = session.exec(select(CategoriaInventario).where(
            CategoriaInventario.nombre_categoria == nombre
        )).first()
        
        if not existe:
            session.add(CategoriaInventario(nombre_categoria=nombre, descripcion=desc, activo=True))
            creadas += 1
    
    print(f"   ✅ {creadas} creadas")


def crear_geografia_basica(session):
    """Crea geografía eclesiástica básica"""
    print("🌎 Geografía eclesiástica...")
    
    # País
    pais = session.exec(select(Pais).where(Pais.nombre_pais == "México")).first()
    if not pais:
        pais = Pais(nombre_pais="México", codigo_iso="MEX", activo=True)
        session.add(pais)
        session.flush()
        print("   ✅ País creado")
    
    # Provincia
    provincia = session.exec(select(Provincia).where(
        Provincia.nombre_provincia == "Antequera"
    )).first()
    if not provincia:
        provincia = Provincia(
            id_pais=pais.id_pais,
            nombre_provincia="Antequera",
            activo=True
        )
        session.add(provincia)
        session.flush()
        print("   ✅ Provincia creada")
    
    # Arquidiócesis
    arqui = session.exec(select(Arquidiocesis).where(
        Arquidiocesis.nombre_arquidiocesis == "Antequera-Oaxaca"
    )).first()
    if not arqui:
        arqui = Arquidiocesis(
            id_provincia=provincia.id_provincia,
            nombre_arquidiocesis="Antequera-Oaxaca",
            arzobispo="Pedro Vázquez Villalobos",
            activo=True
        )
        session.add(arqui)
        session.flush()
        print("   ✅ Arquidiócesis creada")
    
    # Decanato
    decanato = session.exec(select(Decanato).where(
        Decanato.nombre_decanato == "Tlacolula"
    )).first()
    if not decanato:
        decanato = Decanato(
            id_arquidiocesis=arqui.id_arquidiocesis,
            nombre_decanato="Tlacolula",
            activo=True
        )
        session.add(decanato)
        session.flush()
        print("   ✅ Decanato creado")
    
    # Parroquia
    parroquia = session.exec(select(Parroquia).where(
        Parroquia.nombre_parroquia.like("%Santa María%")
    )).first()
    if not parroquia:
        parroquia = Parroquia(
            id_arquidiocesis=arqui.id_arquidiocesis,
            id_decanato=decanato.id_decanato,
            nombre_parroquia="Parroquia de Santa María de la Asunción",
            direccion="Av. 2 de abril No. 22, Tlacolula de Matamoros",
            telefono="9515620019",
            activo=True
        )
        session.add(parroquia)
        session.flush()
        print("   ✅ Parroquia creada")


def crear_plantillas_correo(session):
    """Crea plantillas de correo para constancias"""
    print("📧 Plantillas de correo...")
    
    plantillas = [
        {
            "nombre": "solicitud_recibida",
            "asunto": "Solicitud de Constancia Recibida",
            "cuerpo": """
                <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Solicitud de Constancia Recibida</h2>
                    <p>Estimado/a <strong>{{nombre_solicitante}}</strong>,</p>
                    <p>Hemos recibido tu solicitud de constancia de <strong>{{tipo_sacramento}}</strong>.</p>
                    <p><strong>Número de solicitud:</strong> {{id_solicitud}}</p>
                    <p>Te notificaremos cuando sea validada.</p>
                    <br>
                    <p>Bendiciones,<br>
                    Parroquia de Santa María de la Asunción</p>
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
                    <p>Tu solicitud ha sido <strong>validada exitosamente</strong>.</p>
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
            "asunto": "Tu Constancia está Lista",
            "cuerpo": """
                <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>📄 Constancia Lista</h2>
                    <p>Estimado/a <strong>{{nombre_solicitante}}</strong>,</p>
                    <p>Tu constancia de <strong>{{tipo_sacramento}}</strong> está lista.</p>
                    <p><strong>Folio:</strong> {{folio}}</p>
                    <p><a href="{{url_descarga}}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Descargar Constancia</a></p>
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
        existe = session.exec(select(PlantillaCorreoConstancia).where(
            PlantillaCorreoConstancia.nombre_plantilla == plantilla_data["nombre"]
        )).first()
        
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
    
    print(f"   ✅ {creadas} creadas")


def crear_roles_catequista(session):
    """Crea roles de catequista"""
    print("👨‍🏫 Roles de catequista...")
    
    roles = [
        ("Catequista Titular", "Responsable principal del grupo"),
        ("Catequista Asistente", "Apoyo al catequista titular"),
        ("Coordinador de Área", "Coordina varios grupos"),
        ("Catequista Sustituto", "Suplente ocasional"),
    ]
    
    creados = 0
    for nombre, desc in roles:
        existe = session.exec(select(RolCatequista).where(
            RolCatequista.nombre_rol == nombre
        )).first()
        
        if not existe:
            session.add(RolCatequista(nombre_rol=nombre, descripcion=desc, activo=True))
            creados += 1
    
    print(f"   ✅ {creados} creados")


def crear_roles_grupo_parroquial(session):
    """Crea roles de grupos parroquiales"""
    print("👥 Roles de grupos parroquiales...")
    
    roles = [
        ("Coordinador", "Responsable y representante del grupo"),
        ("Secretario", "Lleva actas y registros"),
        ("Tesorero", "Maneja finanzas del grupo"),
        ("Vocal", "Miembro activo del grupo"),
        ("Catequista", "Imparte catequesis"),
        ("Colaborador", "Apoya en actividades"),
    ]
    
    creados = 0
    for nombre, desc in roles:
        existe = session.exec(select(Rol).where(
            Rol.nombre_rol == nombre
        )).first()
        
        if not existe:
            session.add(Rol(nombre_rol=nombre, descripcion=desc, activo=True))
            creados += 1
    
    print(f"   ✅ {creados} creados")


def main():
    """Función principal"""
    print("=" * 60)
    print("INICIALIZACIÓN COMPLETA DEL SISTEMA")
    print("Sistema Parroquial v4.0")
    print("=" * 60)
    print()
    
    # Preguntar modo
    print("Selecciona:")
    print("1. Base de datos LOCAL (SQLite)")
    print("2. Base de datos REMOTA (MySQL)")
    print("3. Ambas")
    
    opcion = input("\nOpción (1/2/3): ").strip()
    
    engines = []
    
    if opcion in ["1", "3"]:
        print("\n🔌 Conectando a LOCAL...")
        try:
            engines.append(("LOCAL", get_local_engine()))
            print("   ✅ Conectado")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    if opcion in ["2", "3"]:
        print("\n🔌 Conectando a REMOTA...")
        try:
            remote = get_remote_engine()
            if remote:
                engines.append(("REMOTA", remote))
                print("   ✅ Conectado")
            else:
                print("   ⚠️  No se pudo conectar")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    if not engines:
        print("\n❌ No se pudo conectar")
        return
    
    # Procesar
    for nombre, engine in engines:
        print("\n" + "=" * 60)
        print(f"PROCESANDO: {nombre}")
        print("=" * 60)
        
        with Session(engine) as session:
            try:
                crear_geografia_basica(session)
                crear_areas_parroquiales(session)
                crear_bodegas(session)
                crear_perfiles_usuario(session)
                crear_tipos_reunion(session)
                crear_categorias_inventario(session)
                crear_roles_catequista(session)
                crear_roles_grupo_parroquial(session)
                crear_configuracion_constancias(session)
                crear_plantillas_correo(session)
                
                session.commit()
                print(f"\n✅ Completado en {nombre}")
                
            except Exception as e:
                print(f"\n❌ Error en {nombre}: {e}")
                import traceback
                traceback.print_exc()
                session.rollback()
    
    print("\n" + "=" * 60)
    print("✅ INICIALIZACIÓN COMPLETADA")
    print("=" * 60)
    print()
    print("Próximos pasos:")
    print("1. Ejecutar: streamlit run app.py")
    print("2. Subir plantillas PNG de constancias")
    print("3. Crear usuarios en el sistema")
    print("4. Configurar campos de plantillas")
    print()


if __name__ == "__main__":
    main()