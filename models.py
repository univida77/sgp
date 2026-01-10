# models.py - SISTEMA PARROQUIAL V4.0 - CONSOLIDADO COMPLETO
"""
Modelos de Base de Datos Consolidados
Sistema Parroquial v4.0

TODOS LOS MODELOS EN UN SOLO ARCHIVO
Incluye: Geografía, Personas, Sacramentos, Grupos, Educación, 
         Finanzas, Inventario, Actas, Constancias, Sistema

SINCRONIZACIÓN:
Todos los modelos están en SYNC_ORDER_COMPLETE al final
"""

from typing import Optional
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Text
from datetime import date, datetime, time
from decimal import Decimal

# ====================================================================
# MÓDULO: GEOGRAFÍA ECLESIÁSTICA
# ====================================================================

class Pais(SQLModel, table=True):
    __tablename__ = "pais"
    id_pais: Optional[int] = Field(default=None, primary_key=True)
    nombre_pais: str = Field(max_length=100, unique=True)
    codigo_iso: str = Field(max_length=3)
    activo: bool = Field(default=True)

class Provincia(SQLModel, table=True):
    __tablename__ = "provincia"
    id_provincia: Optional[int] = Field(default=None, primary_key=True)
    id_pais: int = Field(foreign_key="pais.id_pais")
    nombre_provincia: str = Field(max_length=150)
    activo: bool = Field(default=True)

class Arquidiocesis(SQLModel, table=True):
    __tablename__ = "arquidiocesis"
    id_arquidiocesis: Optional[int] = Field(default=None, primary_key=True)
    id_provincia: int = Field(foreign_key="provincia.id_provincia")
    nombre_arquidiocesis: str = Field(max_length=150)
    arzobispo: Optional[str] = Field(default=None, max_length=200)
    activo: bool = Field(default=True)

class Decanato(SQLModel, table=True):
    __tablename__ = "decanato"
    id_decanato: Optional[int] = Field(default=None, primary_key=True)
    id_arquidiocesis: int = Field(foreign_key="arquidiocesis.id_arquidiocesis")
    nombre_decanato: str = Field(max_length=150)
    decano: Optional[str] = Field(default=None, max_length=200)
    activo: bool = Field(default=True)

class Parroquia(SQLModel, table=True):
    __tablename__ = "parroquia"
    id_parroquia: Optional[int] = Field(default=None, primary_key=True)
    id_decanato: Optional[int] = Field(default=None, foreign_key="decanato.id_decanato")
    id_arquidiocesis: int = Field(foreign_key="arquidiocesis.id_arquidiocesis")
    nombre_parroquia: str = Field(max_length=200)
    direccion: Optional[str] = None
    telefono: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=100)
    parroco_actual: Optional[str] = Field(default=None, max_length=200)
    activo: bool = Field(default=True)

class Comunidad(SQLModel, table=True):
    __tablename__ = "comunidad"
    id_comunidad: Optional[int] = Field(default=None, primary_key=True)
    id_parroquia: int = Field(foreign_key="parroquia.id_parroquia")
    nombre_comunidad: str = Field(max_length=200)
    clave_comunidad: str = Field(max_length=20, unique=True)
    direccion: Optional[str] = None
    activo: bool = Field(default=True)

class Capilla(SQLModel, table=True):
    __tablename__ = "capilla"
    id_capilla: Optional[int] = Field(default=None, primary_key=True)
    id_comunidad: int = Field(foreign_key="comunidad.id_comunidad")
    nombre_capilla: str = Field(max_length=200)
    direccion: Optional[str] = None
    activo: bool = Field(default=True)

# ====================================================================
# MÓDULO: PERSONAS Y FAMILIAS
# ====================================================================

class Persona(SQLModel, table=True):
    __tablename__ = "persona"
    id_persona: Optional[int] = Field(default=None, primary_key=True)
    
    # Datos personales
    nombres: str = Field(max_length=100)
    primer_apellido: str = Field(max_length=100)
    segundo_apellido: Optional[str] = Field(default=None, max_length=100)
    curp: Optional[str] = Field(default=None, max_length=18, unique=True, index=True)
    fecha_nacimiento: Optional[date] = None
    sexo: Optional[str] = Field(default=None, max_length=1)
    
    # Familia
    id_padre: Optional[int] = Field(default=None, foreign_key="persona.id_persona")
    id_madre: Optional[int] = Field(default=None, foreign_key="persona.id_persona")
    id_comunidad: Optional[int] = Field(default=None, foreign_key="comunidad.id_comunidad")
    
    # Control
    activo: bool = Field(default=True)
    fecha_registro: datetime = Field(default_factory=datetime.now)
    
    def nombre_completo(self) -> str:
        return f"{self.nombres} {self.primer_apellido} {self.segundo_apellido or ''}".strip()

class Telefono(SQLModel, table=True):
    __tablename__ = "telefono"
    id_telefono: Optional[int] = Field(default=None, primary_key=True)
    id_persona: int = Field(foreign_key="persona.id_persona", index=True)
    numero_telefono: str = Field(max_length=20)
    tipo_telefono: str = Field(default="Celular", max_length=50)
    tiene_whatsapp: bool = Field(default=False)
    etiqueta: Optional[str] = Field(default=None, max_length=50)
    extension: Optional[str] = Field(default=None, max_length=10)
    principal: bool = Field(default=False)
    observaciones: Optional[str] = None
    activo: bool = Field(default=True)

class Direccion(SQLModel, table=True):
    __tablename__ = "direccion"
    id_direccion: Optional[int] = Field(default=None, primary_key=True)
    id_persona: int = Field(foreign_key="persona.id_persona", index=True)
    calle: str = Field(max_length=200)
    numero_exterior: Optional[str] = Field(default=None, max_length=20)
    numero_interior: Optional[str] = Field(default=None, max_length=20)
    colonia: Optional[str] = Field(default=None, max_length=100)
    comunidad: Optional[str] = Field(default=None, max_length=100)
    municipio: Optional[str] = Field(default=None, max_length=100)
    distrito: Optional[str] = Field(default=None, max_length=100)
    estado: Optional[str] = Field(default=None, max_length=100)
    pais: str = Field(default="México", max_length=100)
    codigo_postal: Optional[str] = Field(default=None, max_length=10)
    referencias: Optional[str] = None
    tipo_direccion: str = Field(default="Casa", max_length=50)
    principal: bool = Field(default=False)
    observaciones: Optional[str] = None
    activo: bool = Field(default=True)

# ====================================================================
# MÓDULO: CATEQUESIS
# ====================================================================

class CentroCatecismo(SQLModel, table=True):
    __tablename__ = "centro_catecismo"
    id_centro: Optional[int] = Field(default=None, primary_key=True)
    id_comunidad: int = Field(foreign_key="comunidad.id_comunidad")
    nombre_centro: str = Field(max_length=200)
    direccion: Optional[str] = None
    activo: bool = Field(default=True)

class Catecumeno(SQLModel, table=True):
    __tablename__ = "catecumeno"
    id_catecumeno: Optional[int] = Field(default=None, primary_key=True)
    id_persona: int = Field(foreign_key="persona.id_persona", unique=True)
    sacramento_preparacion: str = Field(max_length=100)
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    id_grupo_catequesis: Optional[int] = Field(default=None, foreign_key="grupo_catequesis.id_grupo")
    id_centro_catecismo: Optional[int] = Field(default=None, foreign_key="centro_catecismo.id_centro")
    estado: str = Field(default="activo", max_length=50)
    nivel: Optional[str] = Field(default=None, max_length=100)
    generacion: Optional[str] = Field(default=None, max_length=50)  # ✅ NUEVO: ciclo escolar
    observaciones: Optional[str] = None
    activo: bool = Field(default=True)

# ====================================================================
# MÓDULO: SACRAMENTOS
# ====================================================================

class SacramentoBautizo(SQLModel, table=True):
    __tablename__ = "sacramento_bautizo"
    id_bautizo: Optional[int] = Field(default=None, primary_key=True)
    id_bautizado: int = Field(foreign_key="persona.id_persona")
    id_comunidad: int = Field(foreign_key="comunidad.id_comunidad")
    fecha_celebracion: date
    id_padrino: Optional[int] = Field(default=None, foreign_key="persona.id_persona")
    id_madrina: Optional[int] = Field(default=None, foreign_key="persona.id_persona")
    id_ministro: Optional[int] = Field(default=None, foreign_key="presbitero.id_presbitero")
    libro: Optional[int] = None
    folio: Optional[int] = None
    partida: Optional[int] = None
    observaciones: Optional[str] = None

class SacramentoConfirmacion(SQLModel, table=True):
    __tablename__ = "sacramento_confirmacion"
    id_confirmacion: Optional[int] = Field(default=None, primary_key=True)
    id_confirmado: int = Field(foreign_key="persona.id_persona")
    id_comunidad: int = Field(foreign_key="comunidad.id_comunidad")
    fecha_confirmacion: date
    id_padrino: Optional[int] = Field(default=None, foreign_key="persona.id_persona")
    id_ministro: Optional[int] = Field(default=None, foreign_key="presbitero.id_presbitero")
    nombre_confirmacion: Optional[str] = Field(default=None, max_length=100)
    libro: Optional[int] = None
    folio: Optional[int] = None
    partida: Optional[int] = None
    observaciones: Optional[str] = None

class SacramentoEucaristia(SQLModel, table=True):
    __tablename__ = "sacramento_eucaristia"
    id_eucaristia: Optional[int] = Field(default=None, primary_key=True)
    id_comulgante: int = Field(foreign_key="persona.id_persona")
    id_comunidad: int = Field(foreign_key="comunidad.id_comunidad")
    fecha_eucaristia: date
    id_ministro: Optional[int] = Field(default=None, foreign_key="presbitero.id_presbitero")
    observaciones: Optional[str] = None

class SacramentoMatrimonio(SQLModel, table=True):
    __tablename__ = "sacramento_matrimonio"
    id_matrimonio: Optional[int] = Field(default=None, primary_key=True)
    id_esposo: int = Field(foreign_key="persona.id_persona")
    id_esposa: int = Field(foreign_key="persona.id_persona")
    id_comunidad: int = Field(foreign_key="comunidad.id_comunidad")
    fecha_matrimonio: date
    id_testigo1: Optional[int] = Field(default=None, foreign_key="persona.id_persona")
    id_testigo2: Optional[int] = Field(default=None, foreign_key="persona.id_persona")
    id_ministro: Optional[int] = Field(default=None, foreign_key="presbitero.id_presbitero")
    libro: Optional[int] = None
    folio: Optional[int] = None
    partida: Optional[int] = None
    observaciones: Optional[str] = None

class RenovacionBautismal(SQLModel, table=True):
    __tablename__ = "renovacion_bautismal"
    id_renovacion: Optional[int] = Field(default=None, primary_key=True)
    id_persona: int = Field(foreign_key="persona.id_persona")
    id_comunidad: int = Field(foreign_key="comunidad.id_comunidad")
    fecha_celebracion: date
    id_padrino: Optional[int] = Field(default=None, foreign_key="persona.id_persona")
    id_madrina: Optional[int] = Field(default=None, foreign_key="persona.id_persona")
    id_ministro: Optional[int] = Field(default=None, foreign_key="presbitero.id_presbitero")
    libro: Optional[int] = None
    folio: Optional[int] = None
    partida: Optional[int] = None
    observaciones: Optional[str] = None

# ====================================================================
# MÓDULO: CLERO
# ====================================================================

class Presbitero(SQLModel, table=True):
    __tablename__ = "presbitero"
    id_presbitero: Optional[int] = Field(default=None, primary_key=True)
    id_persona: int = Field(foreign_key="persona.id_persona", unique=True)
    fecha_ordenacion: date
    cargo: str = Field(max_length=100)
    id_parroquia_actual: Optional[int] = Field(default=None, foreign_key="parroquia.id_parroquia")
    activo: bool = Field(default=True)

# ====================================================================
# MÓDULO: GRUPOS Y EDUCACIÓN
# ====================================================================

class GrupoParroquial(SQLModel, table=True):
    __tablename__ = "grupo_parroquial"
    id_grupo: Optional[int] = Field(default=None, primary_key=True)
    nombre_grupo: str = Field(max_length=200)
    descripcion: Optional[str] = None
    id_coordinador: Optional[int] = Field(default=None, foreign_key="persona.id_persona")
    activo: bool = Field(default=True)

class Rol(SQLModel, table=True):
    __tablename__ = "rol"
    id_rol: Optional[int] = Field(default=None, primary_key=True)
    nombre_rol: str = Field(max_length=100, unique=True)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    activo: bool = Field(default=True)

class MembresiaGrupo(SQLModel, table=True):
    __tablename__ = "membresia_grupo"
    id_membresia: Optional[int] = Field(default=None, primary_key=True)
    id_grupo: int = Field(foreign_key="grupo_parroquial.id_grupo")
    id_persona: int = Field(foreign_key="persona.id_persona")
    id_rol: int = Field(foreign_key="rol.id_rol")
    fecha_ingreso: date = Field(default_factory=date.today)
    fecha_salida: Optional[date] = None
    activo: bool = Field(default=True)

class GrupoCatequesis(SQLModel, table=True):
    __tablename__ = "grupo_catequesis"
    id_grupo: Optional[int] = Field(default=None, primary_key=True)
    nombre_grupo: str = Field(max_length=200)
    nivel: str = Field(max_length=100)
    id_centro: int = Field(foreign_key="centro_catecismo.id_centro")
    ciclo_escolar: str = Field(max_length=20)
    generacion_activa: Optional[str] = Field(default=None, max_length=50)  # ✅ ciclo actual
    id_catequista: Optional[int] = Field(default=None, foreign_key="persona.id_persona")
    activo: bool = Field(default=True)

class RolCatequista(SQLModel, table=True):
    __tablename__ = "rol_catequista"
    id_rol_catequista: Optional[int] = Field(default=None, primary_key=True)
    nombre_rol: str = Field(max_length=100, unique=True)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    activo: bool = Field(default=True)

class RolCatequistaIntegrante(SQLModel, table=True):
    __tablename__ = "rol_catequista_integrante"
    id_rol_integrante: Optional[int] = Field(default=None, primary_key=True)
    id_grupo: int = Field(foreign_key="grupo_catequesis.id_grupo")
    id_persona: int = Field(foreign_key="persona.id_persona")
    id_rol_catequista: int = Field(foreign_key="rol_catequista.id_rol_catequista")
    fecha_asignacion: date = Field(default_factory=date.today)
    fecha_fin: Optional[date] = None
    activo: bool = Field(default=True)

class Curso(SQLModel, table=True):
    __tablename__ = "curso"
    id_curso: Optional[int] = Field(default=None, primary_key=True)
    nombre_curso: str = Field(max_length=200)
    descripcion: Optional[str] = None
    activo: bool = Field(default=True)

class TemaCurso(SQLModel, table=True):
    __tablename__ = "tema_curso"
    id_tema: Optional[int] = Field(default=None, primary_key=True)
    id_curso: int = Field(foreign_key="curso.id_curso")
    numero_tema: int
    nombre_tema: str = Field(max_length=200)
    descripcion: Optional[str] = None

# Alias para compatibilidad con código existente
Tema = TemaCurso

class Actividad(SQLModel, table=True):
    __tablename__ = "actividad"
    id_actividad: Optional[int] = Field(default=None, primary_key=True)
    nombre_actividad: str = Field(max_length=200)
    descripcion: Optional[str] = None
    id_grupo_parroquial: int = Field(foreign_key="grupo_parroquial.id_grupo")
    id_curso: Optional[int] = Field(default=None, foreign_key="curso.id_curso")
    ciclo: Optional[str] = Field(default=None, max_length=50)
    activo: bool = Field(default=True)

class Horario(SQLModel, table=True):
    __tablename__ = "horario"
    id_horario: Optional[int] = Field(default=None, primary_key=True)
    id_actividad: int = Field(foreign_key="actividad.id_actividad")
    dia_semana: str = Field(max_length=20)
    hora_inicio: time
    hora_fin: time
    activo: bool = Field(default=True)

class Salon(SQLModel, table=True):
    __tablename__ = "salon"
    id_salon: Optional[int] = Field(default=None, primary_key=True)
    nombre_salon: str = Field(max_length=100)
    id_centro: int = Field(foreign_key="centro_catecismo.id_centro")
    capacidad: Optional[int] = None
    activo: bool = Field(default=True)

class ReservacionSalon(SQLModel, table=True):
    __tablename__ = "reservacion_salon"
    id_reservacion: Optional[int] = Field(default=None, primary_key=True)
    id_salon: int = Field(foreign_key="salon.id_salon")
    id_actividad: Optional[int] = Field(default=None, foreign_key="actividad.id_actividad")
    id_sesion: Optional[int] = Field(default=None, foreign_key="sesion.id_sesion")
    fecha_reservacion: date
    hora_inicio: time
    hora_fin: time
    id_responsable: int = Field(foreign_key="persona.id_persona")
    proposito: Optional[str] = Field(default=None, max_length=300)
    estado: str = Field(default="Confirmada", max_length=50)
    observaciones: Optional[str] = None

class Sesion(SQLModel, table=True):
    __tablename__ = "sesion"
    id_sesion: Optional[int] = Field(default=None, primary_key=True)
    id_actividad: int = Field(foreign_key="actividad.id_actividad")
    id_tema: Optional[int] = Field(default=None, foreign_key="tema_curso.id_tema")
    numero_sesion: int
    nombre_sesion: str = Field(max_length=200)
    fecha_sesion: date
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    id_salon: Optional[int] = Field(default=None, foreign_key="salon.id_salon")
    estado: str = Field(default="Programada", max_length=50)
    observaciones: Optional[str] = None

class Inscripcion(SQLModel, table=True):
    __tablename__ = "inscripcion"
    id_inscripcion: Optional[int] = Field(default=None, primary_key=True)
    id_actividad: int = Field(foreign_key="actividad.id_actividad")
    id_persona: int = Field(foreign_key="persona.id_persona")
    fecha_inscripcion: date = Field(default_factory=date.today)
    estado: str = Field(default="Activo", max_length=50)

class RegistroAsistencia(SQLModel, table=True):
    __tablename__ = "registro_asistencia"
    id_asistencia: Optional[int] = Field(default=None, primary_key=True)
    id_sesion: int = Field(foreign_key="sesion.id_sesion")
    id_persona: int = Field(foreign_key="persona.id_persona")
    estado_asistencia: str = Field(max_length=50)
    fecha_registro: datetime = Field(default_factory=datetime.now)
    metodo_registro: str = Field(default="Manual", max_length=50)
    id_registrador: Optional[int] = Field(default=None, foreign_key="persona.id_persona")
    observaciones: Optional[str] = None

class ReunionGrupal(SQLModel, table=True):
    __tablename__ = "reunion_grupal"
    id_reunion: Optional[int] = Field(default=None, primary_key=True)
    id_grupo: int = Field(foreign_key="grupo_parroquial.id_grupo")
    nombre_reunion: str = Field(max_length=200)
    fecha_reunion: date
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    tema: Optional[str] = Field(default=None, max_length=300)
    descripcion: Optional[str] = None
    id_responsable: int = Field(foreign_key="persona.id_persona")
    tipo_asistencia: str = Field(default="Individual", max_length=50)
    total_esperados: Optional[int] = None
    total_asistentes: Optional[int] = None

class AsistenciaReunion(SQLModel, table=True):
    __tablename__ = "asistencia_reunion"
    id_asistencia_reunion: Optional[int] = Field(default=None, primary_key=True)
    id_reunion: int = Field(foreign_key="reunion_grupal.id_reunion")
    id_persona: int = Field(foreign_key="persona.id_persona")
    presente: bool = Field(default=True)
    observaciones: Optional[str] = None

# ====================================================================
# MÓDULO: SISTEMA
# ====================================================================

class Usuario(SQLModel, table=True):
    __tablename__ = "usuario"
    id_usuario: Optional[int] = Field(default=None, primary_key=True)
    id_persona: int = Field(foreign_key="persona.id_persona", unique=True)
    nombre_usuario: str = Field(max_length=50, unique=True)
    password_hash: str = Field(max_length=255)
    es_administrador: bool = Field(default=False)
    activo: bool = Field(default=True)
    fecha_creacion: datetime = Field(default_factory=datetime.now)

# ====================================================================
# MÓDULO: FINANZAS E INVENTARIO
# ====================================================================

class PerfilUsuario(SQLModel, table=True):
    __tablename__ = "perfil_usuario"
    id_perfil: Optional[int] = Field(default=None, primary_key=True)
    nombre_perfil: str = Field(max_length=100, unique=True)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    puede_crear_presupuesto: bool = Field(default=False)
    puede_registrar_transacciones: bool = Field(default=False)
    puede_ver_finanzas_globales: bool = Field(default=False)
    puede_validar_transacciones: bool = Field(default=False)
    puede_registrar_bienes: bool = Field(default=False)
    puede_mover_bienes: bool = Field(default=False)
    puede_dar_baja_bienes: bool = Field(default=False)
    puede_ver_inventario_global: bool = Field(default=False)
    puede_crear_actas: bool = Field(default=False)
    puede_aprobar_actas: bool = Field(default=False)
    puede_consultar_actas: bool = Field(default=False)
    activo: bool = Field(default=True)

class UsuarioPerfil(SQLModel, table=True):
    __tablename__ = "usuario_perfil"
    id_usuario_perfil: Optional[int] = Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="usuario.id_usuario")
    id_perfil: int = Field(foreign_key="perfil_usuario.id_perfil")
    id_grupo: Optional[int] = Field(default=None, foreign_key="grupo_parroquial.id_grupo")
    fecha_asignacion: date = Field(default_factory=date.today)
    fecha_fin: Optional[date] = None
    activo: bool = Field(default=True)

class PresupuestoAnual(SQLModel, table=True):
    __tablename__ = "presupuesto_anual"
    id_presupuesto: Optional[int] = Field(default=None, primary_key=True)
    id_grupo: int = Field(foreign_key="grupo_parroquial.id_grupo", index=True)
    anio: int = Field(index=True)
    monto_total: Decimal = Field(max_digits=12, decimal_places=2)
    moneda: str = Field(default="MXN", max_length=3)
    descripcion: Optional[str] = Field(default=None, max_length=1000)
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    id_usuario_creador: int = Field(foreign_key="usuario.id_usuario")
    estado: str = Field(default="Borrador", max_length=50)
    fecha_aprobacion: Optional[datetime] = None
    id_usuario_aprobador: Optional[int] = Field(default=None, foreign_key="usuario.id_usuario")
    observaciones: Optional[str] = None

class CategoriaFinanciera(SQLModel, table=True):
    __tablename__ = "categoria_financiera"
    id_categoria: Optional[int] = Field(default=None, primary_key=True)
    id_grupo: int = Field(foreign_key="grupo_parroquial.id_grupo", index=True)
    nombre_categoria: str = Field(max_length=200)
    tipo: str = Field(max_length=20)
    descripcion: Optional[str] = None
    activo: bool = Field(default=True)

class Donador(SQLModel, table=True):
    __tablename__ = "donador"
    id_donador: Optional[int] = Field(default=None, primary_key=True)
    id_persona: Optional[int] = Field(default=None, foreign_key="persona.id_persona")
    nombre_completo: str = Field(max_length=300)
    es_anonimo: bool = Field(default=False)
    telefono: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=100)
    direccion: Optional[str] = None
    tipo_donador: str = Field(default="Individual", max_length=50)
    observaciones: Optional[str] = None
    activo: bool = Field(default=True)

class TransaccionFinanciera(SQLModel, table=True):
    __tablename__ = "transaccion_financiera"
    id_transaccion: Optional[int] = Field(default=None, primary_key=True)
    id_grupo: int = Field(foreign_key="grupo_parroquial.id_grupo", index=True)
    tipo: str = Field(max_length=20, index=True)
    fecha_transaccion: date = Field(index=True)
    monto: Decimal = Field(max_digits=12, decimal_places=2)
    moneda: str = Field(default="MXN", max_length=3)
    id_categoria: int = Field(foreign_key="categoria_financiera.id_categoria")
    id_actividad: Optional[int] = Field(default=None, foreign_key="actividad.id_actividad")
    id_donador: Optional[int] = Field(default=None, foreign_key="donador.id_donador")
    concepto: str = Field(max_length=500)
    descripcion_detallada: Optional[str] = None
    metodo_pago: str = Field(default="Efectivo", max_length=50)
    referencia: Optional[str] = Field(default=None, max_length=100)
    url_comprobante: Optional[str] = Field(default=None, max_length=500)
    fecha_registro: datetime = Field(default_factory=datetime.now)
    id_usuario_registro: int = Field(foreign_key="usuario.id_usuario")
    estado: str = Field(default="Registrada", max_length=50)
    fecha_validacion: Optional[datetime] = None
    id_usuario_validador: Optional[int] = Field(default=None, foreign_key="usuario.id_usuario")
    observaciones: Optional[str] = None

class Bodega(SQLModel, table=True):
    __tablename__ = "bodega"
    id_bodega: Optional[int] = Field(default=None, primary_key=True)
    codigo_bodega: str = Field(max_length=10, unique=True, index=True)
    nombre_bodega: str = Field(max_length=200)
    ubicacion: Optional[str] = Field(default=None, max_length=500)
    responsable: Optional[str] = Field(default=None, max_length=200)
    capacidad_aproximada: Optional[str] = None
    observaciones: Optional[str] = None
    activo: bool = Field(default=True)

class AreaParroquial(SQLModel, table=True):
    __tablename__ = "area_parroquial"
    id_area: Optional[int] = Field(default=None, primary_key=True)
    nombre_area: str = Field(max_length=200, unique=True)
    descripcion: Optional[str] = None
    activo: bool = Field(default=True)

class CategoriaInventario(SQLModel, table=True):
    __tablename__ = "categoria_inventario"
    id_categoria_inv: Optional[int] = Field(default=None, primary_key=True)
    nombre_categoria: str = Field(max_length=200)
    descripcion: Optional[str] = None
    activo: bool = Field(default=True)

class BienInventario(SQLModel, table=True):
    __tablename__ = "bien_inventario"
    id_bien: Optional[int] = Field(default=None, primary_key=True)
    codigo_bien: str = Field(max_length=50, unique=True, index=True)
    nombre_bien: str = Field(max_length=300)
    descripcion: Optional[str] = None
    id_categoria: int = Field(foreign_key="categoria_inventario.id_categoria_inv")
    id_grupo_responsable: int = Field(foreign_key="grupo_parroquial.id_grupo", index=True)
    id_area: int = Field(foreign_key="area_parroquial.id_area")
    id_bodega: Optional[int] = Field(default=None, foreign_key="bodega.id_bodega")
    ubicacion_especifica: Optional[str] = Field(default=None, max_length=300)
    estado_bien: str = Field(max_length=50, index=True)
    cantidad: int = Field(default=1)
    marca: Optional[str] = Field(default=None, max_length=100)
    modelo: Optional[str] = Field(default=None, max_length=100)
    numero_serie: Optional[str] = Field(default=None, max_length=100)
    valor_aproximado: Optional[Decimal] = Field(default=None, max_digits=12, decimal_places=2)
    moneda: str = Field(default="MXN", max_length=3)
    fecha_adquisicion: Optional[date] = None
    url_fotografia: Optional[str] = Field(default=None, max_length=500)
    fecha_registro: datetime = Field(default_factory=datetime.now)
    id_usuario_registro: int = Field(foreign_key="usuario.id_usuario")
    observaciones: Optional[str] = None
    activo: bool = Field(default=True)

class MovimientoBien(SQLModel, table=True):
    __tablename__ = "movimiento_bien"
    id_movimiento: Optional[int] = Field(default=None, primary_key=True)
    id_bien: int = Field(foreign_key="bien_inventario.id_bien", index=True)
    fecha_movimiento: datetime = Field(default_factory=datetime.now)
    id_usuario: int = Field(foreign_key="usuario.id_usuario")
    tipo_movimiento: str = Field(max_length=50)
    grupo_anterior: Optional[int] = Field(default=None, foreign_key="grupo_parroquial.id_grupo")
    area_anterior: Optional[int] = Field(default=None, foreign_key="area_parroquial.id_area")
    bodega_anterior: Optional[int] = Field(default=None, foreign_key="bodega.id_bodega")
    estado_anterior: Optional[str] = Field(default=None, max_length=50)
    grupo_nuevo: Optional[int] = Field(default=None, foreign_key="grupo_parroquial.id_grupo")
    area_nueva: Optional[int] = Field(default=None, foreign_key="area_parroquial.id_area")
    bodega_nueva: Optional[int] = Field(default=None, foreign_key="bodega.id_bodega")
    estado_nuevo: Optional[str] = Field(default=None, max_length=50)
    motivo: Optional[str] = Field(default=None, max_length=500)
    observaciones: Optional[str] = None

# ====================================================================
# MÓDULO: ACTAS
# ====================================================================

class TipoReunion(SQLModel, table=True):
    __tablename__ = "tipo_reunion"
    id_tipo_reunion: Optional[int] = Field(default=None, primary_key=True)
    nombre_tipo: str = Field(max_length=100, unique=True)
    descripcion: Optional[str] = None
    activo: bool = Field(default=True)

class ActaReunion(SQLModel, table=True):
    __tablename__ = "acta_reunion"
    id_acta: Optional[int] = Field(default=None, primary_key=True)
    id_tipo_reunion: int = Field(foreign_key="tipo_reunion.id_tipo_reunion")
    fecha_reunion: date = Field(index=True)
    hora_inicio: Optional[time] = None
    hora_cierre: Optional[time] = None
    lugar_reunion: str = Field(max_length=300)
    id_grupo: int = Field(foreign_key="grupo_parroquial.id_grupo", index=True)
    id_area: int = Field(foreign_key="area_parroquial.id_area")
    orden_dia: str
    desarrollo_reunion: str
    acuerdos_principales: str
    observaciones: Optional[str] = None
    id_responsable_reunion: int = Field(foreign_key="persona.id_persona")
    url_documento_acta: str = Field(max_length=500)
    version_documento: int = Field(default=1)
    formato_documento: str = Field(default="PDF", max_length=10)
    fecha_registro: datetime = Field(default_factory=datetime.now)
    id_usuario_registro: int = Field(foreign_key="usuario.id_usuario")
    estatus: str = Field(default="Borrador", max_length=50, index=True)
    fecha_aprobacion: Optional[datetime] = None
    id_usuario_aprobador: Optional[int] = Field(default=None, foreign_key="usuario.id_usuario")
    observaciones_validacion: Optional[str] = None

class AsistenteActa(SQLModel, table=True):
    __tablename__ = "asistente_acta"
    id_asistente_acta: Optional[int] = Field(default=None, primary_key=True)
    id_acta: int = Field(foreign_key="acta_reunion.id_acta", index=True)
    id_persona: int = Field(foreign_key="persona.id_persona")
    presente: bool = Field(default=True)
    rol_en_reunion: Optional[str] = Field(default=None, max_length=100)
    observaciones: Optional[str] = None

class HistorialActa(SQLModel, table=True):
    __tablename__ = "historial_acta"
    id_historial_acta: Optional[int] = Field(default=None, primary_key=True)
    id_acta: int = Field(foreign_key="acta_reunion.id_acta", index=True)
    fecha_accion: datetime = Field(default_factory=datetime.now)
    id_usuario: int = Field(foreign_key="usuario.id_usuario")
    tipo_accion: str = Field(max_length=50)
    estatus_anterior: Optional[str] = Field(default=None, max_length=50)
    estatus_nuevo: Optional[str] = Field(default=None, max_length=50)
    version_anterior: Optional[int] = None
    version_nueva: Optional[int] = None
    descripcion_cambio: Optional[str] = None
    observaciones: Optional[str] = None

# ====================================================================
# MÓDULO: CONSTANCIAS (CONSOLIDADO)
# ====================================================================

class ConfiguracionConstancia(SQLModel, table=True):
    __tablename__ = "configuracion_constancia"
    id_configuracion: Optional[int] = Field(default=None, primary_key=True)
    
    # Costos
    costo_base_mxn: Decimal = Field(max_digits=10, decimal_places=2)
    tasa_iva: Decimal = Field(default=Decimal("0.16"), max_digits=5, decimal_places=4)
    costo_total_mxn: Decimal = Field(max_digits=10, decimal_places=2)
    tipo_cambio_usd: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=4)
    costo_base_usd: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    costo_total_usd: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    
    # Plantillas
    url_plantilla_bautizo: Optional[str] = Field(default=None, max_length=500)
    url_plantilla_confirmacion: Optional[str] = Field(default=None, max_length=500)
    url_plantilla_eucaristia: Optional[str] = Field(default=None, max_length=500)
    url_plantilla_matrimonio: Optional[str] = Field(default=None, max_length=500)
    
    # QR
    qr_pos_x: int = Field(default=800)
    qr_pos_y: int = Field(default=1000)
    qr_size: int = Field(default=150)
    
    # PayU
    payu_merchant_id: Optional[str] = Field(default=None, max_length=100)
    payu_account_id: Optional[str] = Field(default=None, max_length=100)
    payu_api_key: Optional[str] = Field(default=None, max_length=200)
    payu_api_login: Optional[str] = Field(default=None, max_length=100)
    payu_test_mode: bool = Field(default=True)
    
    url_verificacion_base: str = Field(default="https://parroquia-tlacolula.com/verificar", max_length=200)
    
    activo: bool = Field(default=True)
    fecha_actualizacion: datetime = Field(default_factory=datetime.now)
    id_usuario_actualizacion: Optional[int] = Field(default=None, foreign_key="usuario.id_usuario")

class SolicitudConstancia(SQLModel, table=True):
    __tablename__ = "solicitud_constancia"
    id_solicitud: Optional[int] = Field(default=None, primary_key=True)
    
    tipo_sacramento: str = Field(max_length=50, index=True)
    id_sacramento: int = Field(index=True)
    
    # Solicitante
    id_persona_solicitante: Optional[int] = Field(default=None, foreign_key="persona.id_persona")
    nombre_solicitante: str = Field(max_length=300)
    email_solicitante: str = Field(max_length=100)
    telefono_solicitante: Optional[str] = Field(default=None, max_length=20)
    
    # Validación
    curp_validacion: Optional[str] = Field(default=None, max_length=18, index=True)
    nombre_validacion: Optional[str] = Field(default=None, max_length=300)
    fecha_nacimiento_validacion: Optional[date] = None
    apellido_padrino_madrina: str = Field(max_length=100)
    
    validacion_exitosa: bool = Field(default=False)
    intentos_validacion: int = Field(default=0)
    fecha_ultima_validacion: Optional[datetime] = None
    
    # Estado y pago
    estado: str = Field(default="Pendiente_Validacion", max_length=50, index=True)
    metodo_pago: Optional[str] = Field(default=None, max_length=50)
    
    costo_base: Decimal = Field(max_digits=10, decimal_places=2)
    tasa_iva: Decimal = Field(max_digits=5, decimal_places=4)
    monto_iva: Decimal = Field(max_digits=10, decimal_places=2)
    monto_total: Decimal = Field(max_digits=10, decimal_places=2)
    moneda_pago: str = Field(default="MXN", max_length=3)
    
    # PayU
    payu_reference_code: Optional[str] = Field(default=None, max_length=100, unique=True)
    payu_transaction_id: Optional[str] = Field(default=None, max_length=100)
    payu_order_id: Optional[str] = Field(default=None, max_length=100)
    payu_estado: Optional[str] = Field(default=None, max_length=50)
    payu_response_json: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    fecha_pago: Optional[datetime] = None
    id_usuario_registro_pago: Optional[int] = Field(default=None, foreign_key="usuario.id_usuario")
    comprobante_pago_efectivo: Optional[str] = Field(default=None, max_length=100)
    
    # Control
    fecha_solicitud: datetime = Field(default_factory=datetime.now)
    fecha_emision: Optional[datetime] = None
    ip_solicitante: Optional[str] = Field(default=None, max_length=45)
    observaciones: Optional[str] = None
    motivo_rechazo: Optional[str] = Field(default=None, max_length=500)

class ConstanciaEmitida(SQLModel, table=True):
    __tablename__ = "constancia_emitida"
    id_constancia: Optional[int] = Field(default=None, primary_key=True)
    
    id_solicitud: int = Field(foreign_key="solicitud_constancia.id_solicitud", unique=True)
    folio: str = Field(max_length=50, unique=True, index=True)
    tipo_sacramento: str = Field(max_length=50)
    
    datos_constancia_json: str = Field(sa_column=Column(Text))
    url_pdf_final: str = Field(max_length=500)
    url_plantilla_usada: str = Field(max_length=500)
    
    # QR
    codigo_qr_contenido: str = Field(max_length=500)
    url_imagen_qr: Optional[str] = Field(default=None, max_length=500)
    qr_hash: str = Field(max_length=64)
    
    # Estado
    estado: str = Field(default="Vigente", max_length=50, index=True)
    motivo_cancelacion: Optional[str] = Field(default=None, max_length=500)
    fecha_cancelacion: Optional[datetime] = None
    id_usuario_cancelacion: Optional[int] = Field(default=None, foreign_key="usuario.id_usuario")
    id_constancia_reemplazo: Optional[int] = Field(default=None, foreign_key="constancia_emitida.id_constancia")
    
    # Control
    fecha_emision: datetime = Field(default_factory=datetime.now)
    id_usuario_emision: int = Field(foreign_key="usuario.id_usuario")
    
    # Estadísticas
    contador_descargas: int = Field(default=0)
    fecha_primera_descarga: Optional[datetime] = None
    fecha_ultima_descarga: Optional[datetime] = None
    contador_validaciones_qr: int = Field(default=0)
    fecha_primera_validacion: Optional[datetime] = None
    fecha_ultima_validacion: Optional[datetime] = None
    
    # Metadatos
    tamano_archivo_bytes: Optional[int] = None
    hash_pdf: Optional[str] = Field(default=None, max_length=64)

class HistorialTransaccionConstancia(SQLModel, table=True):
    __tablename__ = "historial_transaccion_constancia"
    id_historial: Optional[int] = Field(default=None, primary_key=True)
    
    id_solicitud: int = Field(foreign_key="solicitud_constancia.id_solicitud", index=True)
    fecha_evento: datetime = Field(default_factory=datetime.now, index=True)
    tipo_evento: str = Field(max_length=50, index=True)
    descripcion: str = Field(max_length=1000)
    
    id_usuario: Optional[int] = Field(default=None, foreign_key="usuario.id_usuario")
    nombre_usuario: Optional[str] = Field(default=None, max_length=200)
    datos_evento_json: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)
    resultado: str = Field(max_length=50)

class VerificacionConstancia(SQLModel, table=True):
    __tablename__ = "verificacion_constancia"
    id_verificacion: Optional[int] = Field(default=None, primary_key=True)
    
    folio: str = Field(max_length=50, index=True)
    fecha_verificacion: datetime = Field(default_factory=datetime.now, index=True)
    
    ip_verificador: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)
    pais: Optional[str] = Field(default=None, max_length=100)
    ciudad: Optional[str] = Field(default=None, max_length=100)
    latitud: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=8)
    longitud: Optional[Decimal] = Field(default=None, max_digits=11, decimal_places=8)
    
    resultado: str = Field(max_length=50)
    datos_mostrados_json: Optional[str] = Field(default=None, sa_column=Column(Text))

# ✅ NUEVOS MODELOS (estaban solo en models_constancias.py)

class PlantillaCorreoConstancia(SQLModel, table=True):
    __tablename__ = "plantilla_correo_constancia"
    id_plantilla: Optional[int] = Field(default=None, primary_key=True)
    
    nombre_plantilla: str = Field(max_length=100, unique=True)
    asunto: str = Field(max_length=200)
    cuerpo_html: str = Field(sa_column=Column(Text))
    variables_disponibles: str = Field(sa_column=Column(Text))
    
    activo: bool = Field(default=True)
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    fecha_modificacion: Optional[datetime] = None

class ConfiguracionCampoPlantilla(SQLModel, table=True):
    __tablename__ = "configuracion_campo_plantilla"
    id_config_campo: Optional[int] = Field(default=None, primary_key=True)
    
    tipo_sacramento: str = Field(max_length=50)
    nombre_campo: str = Field(max_length=100)
    
    pos_x: int
    pos_y: int
    
    fuente: str = Field(default="Times New Roman", max_length=100)
    tamano_fuente: int = Field(default=24)
    color_rgb: str = Field(default="0,0,0", max_length=20)
    alineacion: str = Field(default="center", max_length=20)
    ancho_maximo: Optional[int] = None
    
    activo: bool = Field(default=True)

# ====================================================================
# ✅ ORDEN DE SINCRONIZACIÓN COMPLETO Y CORRECTO
# ====================================================================

SYNC_ORDER_COMPLETE = [
    # Geografía
    Pais, Provincia, Arquidiocesis, Decanato, Parroquia, Comunidad, Capilla,
    
    # Personas
    Persona, Telefono, Direccion,
    
    # Catequesis
    CentroCatecismo, GrupoCatequesis, RolCatequista, RolCatequistaIntegrante, Catecumeno,
    
    # Clero
    Presbitero,
    
    # Sacramentos
    SacramentoBautizo, SacramentoConfirmacion, SacramentoEucaristia, SacramentoMatrimonio, RenovacionBautismal,
    
    # Grupos y educación
    GrupoParroquial, Rol, MembresiaGrupo, Curso, TemaCurso, Actividad, Horario, Salon, ReservacionSalon, Sesion,
    Inscripcion, RegistroAsistencia, ReunionGrupal, AsistenciaReunion,
    
    # Sistema
    Usuario,
    
    # Finanzas e inventario
    PerfilUsuario, UsuarioPerfil,
    PresupuestoAnual, CategoriaFinanciera, Donador, TransaccionFinanciera,
    Bodega, AreaParroquial, CategoriaInventario, BienInventario, MovimientoBien,
    
    # Actas
    TipoReunion, ActaReunion, AsistenteActa, HistorialActa,
    
    # Constancias
    ConfiguracionConstancia, SolicitudConstancia, ConstanciaEmitida,
    HistorialTransaccionConstancia, VerificacionConstancia,
    PlantillaCorreoConstancia, ConfiguracionCampoPlantilla
]