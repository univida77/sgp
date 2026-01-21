# models.py - Sistema Parroquial v4.0
"""
CAMBIO ARQUITECTÓNICO: Persona → Feligres
Todos los modelos actualizados para usar 'Feligres' como entidad base
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import date, datetime, time
from decimal import Decimal

# ====================================================================
# MODELO BASE: FELIGRES (antes Persona)
# ====================================================================

class Feligres(SQLModel, table=True):
    """
    Feligres: Miembro de la comunidad parroquial
    (Reemplaza el modelo 'Persona')
    """
    __tablename__ = "feligres"
    
    id_feligres: Optional[int] = Field(default=None, primary_key=True)
    
    # Datos personales
    nombres: str = Field(max_length=100)
    apellido_paterno: str = Field(max_length=100)
    apellido_materno: Optional[str] = Field(default=None, max_length=100)
    curp: Optional[str] = Field(default=None, max_length=18, unique=True, index=True)
    
    # Estado canónico
    estado_canonico: str = Field(default="soltero", max_length=50)
    
    # Relaciones familiares (auto-referencia)
    id_padre: Optional[int] = Field(default=None, foreign_key="feligres.id_feligres")
    id_madre: Optional[int] = Field(default=None, foreign_key="feligres.id_feligres")
    
    # Control de sincronización
    id_local: Optional[int] = Field(default=None, index=True)
    id_remoto: Optional[int] = Field(default=None, index=True)
    sincronizado: bool = Field(default=False)
    fecha_sync: Optional[datetime] = Field(default=None)
    
    # Método auxiliar
    def nombre_completo(self) -> str:
        """Retorna nombre completo del feligrés"""
        partes = [self.nombres, self.apellido_paterno]
        if self.apellido_materno:
            partes.append(self.apellido_materno)
        return " ".join(partes)


# ====================================================================
# CONTACTO
# ====================================================================

class Telefono(SQLModel, table=True):
    """Teléfonos de feligreses"""
    __tablename__ = "telefono"
    
    id_telefono: Optional[int] = Field(default=None, primary_key=True)
    id_feligres: int = Field(foreign_key="feligres.id_feligres")
    
    numero_telefono: str = Field(max_length=20)
    tipo: str = Field(default="Móvil", max_length=20)
    tiene_whatsapp: bool = Field(default=False)
    etiqueta: Optional[str] = Field(default=None, max_length=50)
    extension: Optional[str] = Field(default=None, max_length=10)
    principal: bool = Field(default=False)
    observaciones: Optional[str] = Field(default=None)
    activo: bool = Field(default=True)
    
    # Sincronización
    id_local: Optional[int] = Field(default=None)
    id_remoto: Optional[int] = Field(default=None)
    sincronizado: bool = Field(default=False)
    fecha_sync: Optional[datetime] = Field(default=None)


class Direccion(SQLModel, table=True):
    """Direcciones de feligreses"""
    __tablename__ = "direccion"
    
    id_direccion: Optional[int] = Field(default=None, primary_key=True)
    id_feligres: int = Field(foreign_key="feligres.id_feligres")
    
    calle: str = Field(max_length=200)
    numero_exterior: str = Field(max_length=20)
    numero_interior: Optional[str] = Field(default=None, max_length=20)
    colonia: Optional[str] = Field(default=None, max_length=100)
    comunidad: Optional[str] = Field(default=None, max_length=100)
    municipio: str = Field(max_length=100)
    distrito: Optional[str] = Field(default=None, max_length=100)
    estado: Optional[str] = Field(default=None, max_length=100)
    pais: str = Field(default="México", max_length=100)
    codigo_postal: str = Field(max_length=5)
    referencias: Optional[str] = Field(default=None)
    tipo_direccion: str = Field(default="Casa", max_length=50)
    principal: bool = Field(default=False)
    observaciones: Optional[str] = Field(default=None)
    activo: bool = Field(default=True)
    
    # Sincronización
    id_local: Optional[int] = Field(default=None)
    id_remoto: Optional[int] = Field(default=None)
    sincronizado: bool = Field(default=False)
    fecha_sync: Optional[datetime] = Field(default=None)


# ====================================================================
# CATEQUESIS
# ====================================================================

class Catecumeno(SQLModel, table=True):
    """Feligreses en preparación sacramental"""
    __tablename__ = "catecumeno"
    
    id_catecumeno: Optional[int] = Field(default=None, primary_key=True)
    id_feligres: int = Field(foreign_key="feligres.id_feligres")
    
    sacramento_preparacion: str = Field(max_length=100)
    fecha_inicio: date
    fecha_fin: Optional[date] = Field(default=None)
    id_grupo_catequesis: Optional[int] = Field(default=None, foreign_key="grupo_catequesis.id_grupo")
    id_centro_catecismo: Optional[int] = Field(default=None, foreign_key="centro_catecismo.id_centro")
    estado: str = Field(default="activo", max_length=50)
    nivel: Optional[str] = Field(default=None, max_length=100)
    generacion: Optional[str] = Field(default=None, max_length=50)
    observaciones: Optional[str] = Field(default=None)
    
    # Sincronización
    id_local: Optional[int] = Field(default=None)
    id_remoto: Optional[int] = Field(default=None)
    sincronizado: bool = Field(default=False)
    fecha_sync: Optional[datetime] = Field(default=None)


# ====================================================================
# CLERO
# ====================================================================

class Presbitero(SQLModel, table=True):
    """Sacerdotes (feligreses ordenados)"""
    __tablename__ = "presbitero"
    
    id_presbitero: Optional[int] = Field(default=None, primary_key=True)
    id_feligres: int = Field(foreign_key="feligres.id_feligres", unique=True)
    
    fecha_ordenacion: date
    diocesis: Optional[str] = Field(default=None, max_length=200)
    cargo: str = Field(max_length=100)
    
    # Sincronización
    id_local: Optional[int] = Field(default=None)
    id_remoto: Optional[int] = Field(default=None)
    sincronizado: bool = Field(default=False)
    fecha_sync: Optional[datetime] = Field(default=None)


# ====================================================================
# SACRAMENTOS
# ====================================================================

class SacramentoBautizo(SQLModel, table=True):
    """Registro de bautizos"""
    __tablename__ = "sacramento_bautizo"
    
    id_bautizo: Optional[int] = Field(default=None, primary_key=True)
    id_bautizado: int = Field(foreign_key="feligres.id_feligres")
    
    fecha_celebracion: date
    id_comunidad: int = Field(foreign_key="comunidad.id_comunidad")
    id_ministro: Optional[int] = Field(default=None, foreign_key="presbitero.id_presbitero")
    id_padrino: Optional[int] = Field(default=None, foreign_key="feligres.id_feligres")
    id_madrina: Optional[int] = Field(default=None, foreign_key="feligres.id_feligres")
    
    libro: Optional[str] = Field(default=None, max_length=10)
    folio: Optional[str] = Field(default=None, max_length=10)
    partida: Optional[str] = Field(default=None, max_length=10)
    url_certificado: Optional[str] = Field(default=None, max_length=500)
    
    # Sincronización
    id_local: Optional[int] = Field(default=None)
    id_remoto: Optional[int] = Field(default=None)
    sincronizado: bool = Field(default=False)
    fecha_sync: Optional[datetime] = Field(default=None)


class SacramentoConfirmacion(SQLModel, table=True):
    """Registro de confirmaciones"""
    __tablename__ = "sacramento_confirmacion"
    
    id_confirmacion: Optional[int] = Field(default=None, primary_key=True)
    id_confirmado: int = Field(foreign_key="feligres.id_feligres")
    
    fecha_celebracion: date
    id_comunidad: int = Field(foreign_key="comunidad.id_comunidad")
    id_ministro: Optional[int] = Field(default=None, foreign_key="presbitero.id_presbitero")
    id_padrino: Optional[int] = Field(default=None, foreign_key="feligres.id_feligres")
    id_madrina: Optional[int] = Field(default=None, foreign_key="feligres.id_feligres")
    
    libro: Optional[str] = Field(default=None, max_length=10)
    folio: Optional[str] = Field(default=None, max_length=10)
    partida: Optional[str] = Field(default=None, max_length=10)
    url_certificado: Optional[str] = Field(default=None, max_length=500)
    
    # Sincronización
    id_local: Optional[int] = Field(default=None)
    id_remoto: Optional[int] = Field(default=None)
    sincronizado: bool = Field(default=False)
    fecha_sync: Optional[datetime] = Field(default=None)


class SacramentoEucaristia(SQLModel, table=True):
    """Registro de primera comunión"""
    __tablename__ = "sacramento_eucaristia"
    
    id_eucaristia: Optional[int] = Field(default=None, primary_key=True)
    id_comulgado: int = Field(foreign_key="feligres.id_feligres")
    
    fecha_celebracion: date
    id_comunidad: int = Field(foreign_key="comunidad.id_comunidad")
    id_ministro: Optional[int] = Field(default=None, foreign_key="presbitero.id_presbitero")
    id_padrino: Optional[int] = Field(default=None, foreign_key="feligres.id_feligres")
    id_madrina: Optional[int] = Field(default=None, foreign_key="feligres.id_feligres")
    
    libro: Optional[str] = Field(default=None, max_length=10)
    folio: Optional[str] = Field(default=None, max_length=10)
    partida: Optional[str] = Field(default=None, max_length=10)
    url_certificado: Optional[str] = Field(default=None, max_length=500)
    
    # Sincronización
    id_local: Optional[int] = Field(default=None)
    id_remoto: Optional[int] = Field(default=None)
    sincronizado: bool = Field(default=False)
    fecha_sync: Optional[datetime] = Field(default=None)


class SacramentoMatrimonio(SQLModel, table=True):
    """Registro de matrimonios"""
    __tablename__ = "sacramento_matrimonio"
    
    id_matrimonio: Optional[int] = Field(default=None, primary_key=True)
    id_ConyugeVaron: int = Field(foreign_key="feligres.id_feligres")
    id_ConyugeMujer: int = Field(foreign_key="feligres.id_feligres")
    
    fecha_celebracion: date
    id_comunidad: int = Field(foreign_key="comunidad.id_comunidad")
    id_ministro: Optional[int] = Field(default=None, foreign_key="presbitero.id_presbitero")
    id_padrino: Optional[int] = Field(default=None, foreign_key="feligres.id_feligres")
    id_madrina: Optional[int] = Field(default=None, foreign_key="feligres.id_feligres")
    
    libro: Optional[str] = Field(default=None, max_length=10)
    folio: Optional[str] = Field(default=None, max_length=10)
    partida: Optional[str] = Field(default=None, max_length=10)
    url_certificado: Optional[str] = Field(default=None, max_length=500)
    
    # Sincronización
    id_local: Optional[int] = Field(default=None)
    id_remoto: Optional[int] = Field(default=None)
    sincronizado: bool = Field(default=False)
    fecha_sync: Optional[datetime] = Field(default=None)


class RenovacionBautismal(SQLModel, table=True):
    """Registro de renovaciones bautismales"""
    __tablename__ = "renovacion_bautismal"
    
    id_registro: Optional[int] = Field(default=None, primary_key=True)
    id_feligres: int = Field(foreign_key="feligres.id_feligres")
    
    fecha_celebracion: date
    id_comunidad: int = Field(foreign_key="comunidad.id_comunidad")
    id_ministro: Optional[int] = Field(default=None, foreign_key="presbitero.id_presbitero")
    id_padrino: Optional[int] = Field(default=None, foreign_key="feligres.id_feligres")
    id_madrina: Optional[int] = Field(default=None, foreign_key="feligres.id_feligres")
    
    libro: Optional[str] = Field(default=None, max_length=10)
    folio: Optional[str] = Field(default=None, max_length=10)
    partida: Optional[str] = Field(default=None, max_length=10)
    url_certificado: Optional[str] = Field(default=None, max_length=500)
    
    # Sincronización
    id_local: Optional[int] = Field(default=None)
    id_remoto: Optional[int] = Field(default=None)
    sincronizado: bool = Field(default=False)
    fecha_sync: Optional[datetime] = Field(default=None)


# ====================================================================
# SISTEMA
# ====================================================================

class Usuario(SQLModel, table=True):
    """Usuarios del sistema (feligreses con acceso)"""
    __tablename__ = "usuario"
    
    id_usuario: Optional[int] = Field(default=None, primary_key=True)
    id_feligres: int = Field(foreign_key="feligres.id_feligres", unique=True)
    
    username: str = Field(max_length=50, unique=True, index=True)
    email: str = Field(max_length=100, unique=True)
    password_hash: str = Field(max_length=255)
    activo: bool = Field(default=True)
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    
    # Sincronización
    id_local: Optional[int] = Field(default=None)
    id_remoto: Optional[int] = Field(default=None)
    sincronizado: bool = Field(default=False)
    fecha_sync: Optional[datetime] = Field(default=None)


# ====================================================================
# NOTA: Los demás modelos (Geografía, Grupos, Educación, etc.) 
# permanecen igual ya que solo referencian a Feligres, no necesitan
# cambios internos más allá del foreign_key
# ====================================================================

# Por brevedad, incluyo solo los esenciales aquí
# El resto de modelos están en el archivo completo

# ORDEN DE SINCRONIZACIÓN ACTUALIZADO
SYNC_ORDER_COMPLETE = [
    # Geografía (sin cambios)
    # ...
    
    # ⚠️ CAMBIO: Feligres es ahora la tabla base
    Feligres,  # ANTES: Persona
    Telefono,
    Direccion,
    
    # Catequesis
    Catecumeno,
    
    # Clero
    Presbitero,
    
    # Sacramentos
    SacramentoBautizo,
    SacramentoConfirmacion,
    SacramentoEucaristia,
    SacramentoMatrimonio,
    RenovacionBautismal,
    
    # Sistema
    Usuario,
    
    # ... resto de modelos
]