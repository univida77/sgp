# components/validadores.py - Validaciones Centralizadas
"""
Validaciones reutilizables para todo el sistema
"""

import re
from typing import Tuple
from datetime import date

# ====================================================================
# VALIDACIÓN DE CURP
# ====================================================================

def validar_curp(curp: str) -> Tuple[bool, str]:
    """
    Valida formato de CURP mexicano
    
    Returns:
        Tuple[bool, str]: (es_valido, mensaje_error)
    """
    if not curp:
        return False, "El CURP no puede estar vacío"
    
    curp_limpio = curp.strip().upper()
    
    if len(curp_limpio) != 18:
        return False, f"El CURP debe tener 18 caracteres (tiene {len(curp_limpio)})"
    
    if not curp_limpio.isalnum():
        return False, "El CURP solo debe contener letras y números"
    
    # Validación de estructura básica
    patron = r'^[A-Z]{4}[0-9]{6}[HM][A-Z]{5}[0-9A-Z][0-9]$'
    if not re.match(patron, curp_limpio):
        return False, "El formato del CURP no es válido"
    
    return True, curp_limpio


# ====================================================================
# VALIDACIÓN DE TELÉFONO
# ====================================================================

def validar_telefono(numero: str) -> Tuple[bool, str]:
    """
    Valida y limpia número telefónico mexicano
    
    Returns:
        Tuple[bool, str]: (es_valido, numero_limpio_o_error)
    """
    if not numero:
        return False, "El número telefónico no puede estar vacío"
    
    # Remover espacios, guiones, paréntesis
    numero_limpio = re.sub(r'[\s\-()]', '', numero)
    
    # Verificar que solo contenga dígitos y opcionalmente +
    if not re.match(r'^\+?\d+$', numero_limpio):
        return False, "El número solo debe contener dígitos, espacios, guiones o +"
    
    # Remover código de país si existe
    if numero_limpio.startswith('+52'):
        numero_limpio = numero_limpio[3:]
    elif numero_limpio.startswith('52') and len(numero_limpio) > 10:
        numero_limpio = numero_limpio[2:]
    
    # Validar longitud (10 dígitos para México)
    if len(numero_limpio) != 10:
        return False, f"Debe tener 10 dígitos (tiene {len(numero_limpio)})"
    
    return True, numero_limpio


def formatear_telefono(numero: str) -> str:
    """
    Formatea número telefónico: 5512345678 -> (55) 1234-5678
    
    Args:
        numero: Número de 10 dígitos
    
    Returns:
        str: Número formateado
    """
    if len(numero) == 10:
        return f"({numero[:2]}) {numero[2:6]}-{numero[6:]}"
    return numero


# ====================================================================
# VALIDACIÓN DE CÓDIGO POSTAL
# ====================================================================

def validar_codigo_postal(cp: str) -> Tuple[bool, str]:
    """
    Valida código postal mexicano (5 dígitos)
    
    Returns:
        Tuple[bool, str]: (es_valido, cp_limpio_o_error)
    """
    if not cp:
        return False, "El código postal no puede estar vacío"
    
    cp_limpio = cp.strip()
    
    if not cp_limpio.isdigit():
        return False, "El código postal solo debe contener dígitos"
    
    if len(cp_limpio) != 5:
        return False, f"Debe tener 5 dígitos (tiene {len(cp_limpio)})"
    
    return True, cp_limpio


# ====================================================================
# VALIDACIÓN DE EMAIL
# ====================================================================

def validar_email(email: str) -> Tuple[bool, str]:
    """
    Valida formato de email
    
    Returns:
        Tuple[bool, str]: (es_valido, mensaje_error)
    """
    if not email:
        return False, "El email no puede estar vacío"
    
    email_limpio = email.strip().lower()
    
    # Validación básica de formato
    patron = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if not re.match(patron, email_limpio):
        return False, "El formato del email no es válido"
    
    return True, email_limpio


# ====================================================================
# VALIDACIÓN DE MONTOS
# ====================================================================

def validar_monto(monto: float, minimo: float = 0.01, maximo: float = 999999999.99) -> Tuple[bool, str]:
    """
    Valida que el monto esté en rango válido
    
    Returns:
        Tuple[bool, str]: (es_valido, mensaje_error)
    """
    if monto < minimo:
        return False, f"El monto debe ser mayor o igual a {minimo}"
    
    if monto > maximo:
        return False, f"El monto debe ser menor o igual a {maximo}"
    
    return True, ""


# ====================================================================
# VALIDACIÓN DE FECHAS
# ====================================================================

def validar_fecha_pasada(fecha: date) -> Tuple[bool, str]:
    """
    Valida que la fecha no sea futura
    
    Returns:
        Tuple[bool, str]: (es_valido, mensaje_error)
    """
    if fecha > date.today():
        return False, "La fecha no puede ser futura"
    
    return True, ""


def validar_rango_fechas(fecha_inicio: date, fecha_fin: date) -> Tuple[bool, str]:
    """
    Valida que el rango de fechas sea correcto
    
    Returns:
        Tuple[bool, str]: (es_valido, mensaje_error)
    """
    if fecha_fin < fecha_inicio:
        return False, "La fecha de fin no puede ser anterior a la fecha de inicio"
    
    return True, ""


# ====================================================================
# VALIDACIÓN DE CAMPOS REQUERIDOS
# ====================================================================

def validar_campos_requeridos(campos: dict) -> Tuple[bool, list]:
    """
    Valida múltiples campos requeridos
    
    Args:
        campos: Dict con {nombre_campo: valor}
    
    Returns:
        Tuple[bool, list]: (todos_validos, lista_campos_faltantes)
    """
    campos_faltantes = []
    
    for nombre, valor in campos.items():
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            campos_faltantes.append(nombre)
    
    return len(campos_faltantes) == 0, campos_faltantes


# ====================================================================
# VALIDACIÓN DE AUTO-REFERENCIA
# ====================================================================

def validar_no_auto_referencia(
    id_entidad: int,
    id_padre: int = None,
    id_madre: int = None
) -> Tuple[bool, str]:
    """
    Valida que una entidad no se referencie a sí misma
    Útil para relaciones familiares
    
    Returns:
        Tuple[bool, str]: (es_valido, mensaje_error)
    """
    if id_padre and id_padre == id_entidad:
        return False, "Una persona no puede ser su propio padre"
    
    if id_madre and id_madre == id_entidad:
        return False, "Una persona no puede ser su propia madre"
    
    return True, ""


# ====================================================================
# VALIDACIÓN DE CONTRASEÑA
# ====================================================================

def validar_password(password: str) -> Tuple[bool, str]:
    """
    Valida requisitos mínimos de contraseña
    
    Returns:
        Tuple[bool, str]: (es_valido, mensaje_error)
    """
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    
    if not any(c.isupper() for c in password):
        return False, "La contraseña debe contener al menos una mayúscula"
    
    if not any(c.islower() for c in password):
        return False, "La contraseña debe contener al menos una minúscula"
    
    if not any(c.isdigit() for c in password):
        return False, "La contraseña debe contener al menos un número"
    
    return True, ""


# ====================================================================
# VALIDACIÓN DE CÓDIGO DE BIEN
# ====================================================================

def validar_codigo_bien(codigo: str) -> Tuple[bool, str]:
    """
    Valida formato de código de bien de inventario
    
    Returns:
        Tuple[bool, str]: (es_valido, mensaje_error)
    """
    if not codigo:
        return False, "El código no puede estar vacío"
    
    codigo_limpio = codigo.strip().upper()
    
    # Formato esperado: INV-000001
    patron = r'^[A-Z]{3}-\d{6}$'
    if not re.match(patron, codigo_limpio):
        return False, "El código debe tener formato XXX-000000"
    
    return True, codigo_limpio


# ====================================================================
# SANITIZACIÓN DE TEXTO
# ====================================================================

def sanitizar_texto(texto: str, max_length: int = None) -> str:
    """
    Limpia y sanitiza texto de entrada
    
    Args:
        texto: Texto a sanitizar
        max_length: Longitud máxima opcional
    
    Returns:
        str: Texto sanitizado
    """
    if not texto:
        return ""
    
    # Remover espacios extra
    texto_limpio = ' '.join(texto.split())
    
    # Truncar si es necesario
    if max_length and len(texto_limpio) > max_length:
        texto_limpio = texto_limpio[:max_length]
    
    return texto_limpio.strip()


# ====================================================================
# VALIDACIÓN DE DUPLICADOS
# ====================================================================

def validar_no_duplicado(
    db_engine,
    modelo,
    campo: str,
    valor: str,
    id_excluir: int = None
) -> Tuple[bool, str]:
    """
    Valida que no exista un valor duplicado en la base de datos
    
    Args:
        db_engine: Engine de la base de datos
        modelo: Modelo SQLModel a verificar
        campo: Nombre del campo a verificar
        valor: Valor a buscar
        id_excluir: ID a excluir de la búsqueda (para actualizaciones)
    
    Returns:
        Tuple[bool, str]: (no_existe_duplicado, mensaje_error)
    """
    from sqlmodel import Session, select
    
    with Session(db_engine) as session:
        statement = select(modelo).where(getattr(modelo, campo) == valor)
        
        resultado = session.exec(statement).first()
        
        if resultado:
            # Si estamos actualizando, excluir el registro actual
            if id_excluir:
                pk_field = list(modelo.__table__.primary_key.columns)[0].name
                if getattr(resultado, pk_field) == id_excluir:
                    return True, ""
            
            return False, f"Ya existe un registro con ese {campo}"
    
    return True, ""


# ====================================================================
# VALIDACIÓN DE HORARIOS
# ====================================================================

def validar_horario(hora_inicio, hora_fin) -> Tuple[bool, str]:
    """
    Valida que el horario sea correcto (fin después de inicio)
    
    Returns:
        Tuple[bool, str]: (es_valido, mensaje_error)
    """
    if hora_fin <= hora_inicio:
        return False, "La hora de fin debe ser posterior a la hora de inicio"
    
    return True, ""


# ====================================================================
# MENSAJES DE ERROR ESTANDARIZADOS
# ====================================================================

class MensajesError:
    """Mensajes de error estandarizados"""
    
    CAMPO_REQUERIDO = "Este campo es obligatorio"
    FORMATO_INVALIDO = "El formato ingresado no es válido"
    VALOR_DUPLICADO = "Ya existe un registro con este valor"
    FECHA_INVALIDA = "La fecha ingresada no es válida"
    MONTO_INVALIDO = "El monto ingresado no es válido"
    RANGO_INVALIDO = "El rango de valores no es válido"
    LONGITUD_INVALIDA = "La longitud del valor no es válida"
