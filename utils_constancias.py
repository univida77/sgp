# utils_constancias.py
"""
Utilidades para generación de constancias
Sistema Parroquial v4.0 - Optimizado

DEPENDENCIAS:
pip install qrcode[pil] pillow reportlab
"""

import qrcode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import hashlib
from datetime import datetime
from decimal import Decimal
import json
from typing import Dict, Tuple, Optional
import os

# ====================================================================
# GENERACIÓN DE CÓDIGO QR
# ====================================================================

def generar_qr_code(contenido: str, tamano: int = 150) -> Tuple[Image.Image, str]:
    """
    Genera código QR con el contenido especificado
    
    Returns:
        Tuple[Image, str]: (Imagen PIL del QR, Hash SHA-256 del contenido)
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    
    qr.add_data(contenido)
    qr.make(fit=True)
    
    img_qr = qr.make_image(fill_color="black", back_color="white")
    img_qr = img_qr.resize((tamano, tamano), Image.Resampling.LANCZOS)
    
    hash_qr = hashlib.sha256(contenido.encode()).hexdigest()
    
    return img_qr, hash_qr


def qr_a_base64(img_qr: Image.Image) -> str:
    """Convierte imagen QR a string base64"""
    import base64
    
    buffer = BytesIO()
    img_qr.save(buffer, format="PNG")
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return img_base64


# ====================================================================
# GENERACIÓN DE FOLIO
# ====================================================================

def generar_folio_constancia(tipo_sacramento: str, numero: int, anio: int = None) -> str:
    """
    Genera folio único para constancia
    Ejemplo: CONST-BAU-2025-000123
    """
    if anio is None:
        anio = datetime.now().year
    
    prefijos = {
        "Bautizo": "BAU",
        "Confirmación": "CON",
        "Eucaristía": "EUC",
        "Matrimonio": "MAT"
    }
    
    prefijo = prefijos.get(tipo_sacramento, "SAC")
    folio = f"CONST-{prefijo}-{anio}-{numero:06d}"
    
    return folio


# ====================================================================
# FORMATEO DE DATOS
# ====================================================================

def formatear_datos_para_constancia(datos_sacramento: Dict) -> Dict:
    """Formatea datos del sacramento para la constancia"""
    datos_formateados = {}
    
    # Nombre completo
    if 'nombre_completo' in datos_sacramento:
        datos_formateados['nombre_completo'] = datos_sacramento['nombre_completo'].upper()
    
    # Fechas
    if 'fecha_sacramento' in datos_sacramento:
        fecha = datos_sacramento['fecha_sacramento']
        if hasattr(fecha, 'strftime'):
            datos_formateados['fecha_sacramento'] = fecha.strftime('%d de %B de %Y')
        else:
            datos_formateados['fecha_sacramento'] = str(fecha)
    
    # Nombres de padres
    for campo in ['nombre_padre', 'nombre_madre', 'padrino', 'madrina']:
        if campo in datos_sacramento and datos_sacramento[campo]:
            datos_formateados[campo] = datos_sacramento[campo].title()
    
    # Lugar
    if 'lugar' in datos_sacramento:
        datos_formateados['lugar'] = datos_sacramento['lugar']
    
    # Datos del libro
    if 'libro' in datos_sacramento:
        datos_formateados['libro'] = f"Libro {datos_sacramento['libro']}"
    if 'folio' in datos_sacramento:
        datos_formateados['folio_libro'] = f"Folio {datos_sacramento['folio']}"
    if 'partida' in datos_sacramento:
        datos_formateados['partida'] = f"Partida {datos_sacramento['partida']}"
    
    return datos_formateados


# ====================================================================
# CONFIGURACIÓN DE CAMPOS POR SACRAMENTO
# ====================================================================

def obtener_configuracion_campos(tipo_sacramento: str) -> Dict:
    """Obtiene configuración de campos según tipo de sacramento"""
    
    if tipo_sacramento == "Confirmación":
        return {
            'qr': {'x': 50, 'y': 950},
            'campos': {
                'nombre_completo': {'x': 400, 'y': 450, 'fuente': 'normal', 'color': (139, 0, 0)},
                'fecha_sacramento': {'x': 400, 'y': 530, 'fuente': 'normal', 'color': (0, 0, 0)},
                'lugar': {'x': 400, 'y': 600, 'fuente': 'pequena', 'color': (0, 0, 0)},
                'nombre_padre': {'x': 500, 'y': 680, 'fuente': 'pequena', 'color': (0, 0, 0)},
                'nombre_madre': {'x': 500, 'y': 720, 'fuente': 'pequena', 'color': (0, 0, 0)},
                'padrino': {'x': 500, 'y': 760, 'fuente': 'pequena', 'color': (0, 0, 0)},
            }
        }
    
    elif tipo_sacramento == "Bautizo":
        return {
            'qr': {'x': 50, 'y': 950},
            'campos': {
                'nombre_completo': {'x': 400, 'y': 450, 'fuente': 'normal'},
                'fecha_sacramento': {'x': 400, 'y': 520, 'fuente': 'normal'},
                'lugar': {'x': 400, 'y': 590, 'fuente': 'normal'},
                'nombre_padre': {'x': 500, 'y': 660, 'fuente': 'pequena'},
                'nombre_madre': {'x': 500, 'y': 710, 'fuente': 'pequena'},
                'padrino': {'x': 500, 'y': 760, 'fuente': 'pequena'},
                'madrina': {'x': 500, 'y': 810, 'fuente': 'pequena'},
            }
        }
    
    # Default
    return {'qr': {'x': 50, 'y': 950}, 'campos': {}}


# ====================================================================
# CÁLCULO DE HASH
# ====================================================================

def calcular_hash_pdf(ruta_pdf: str) -> str:
    """Calcula hash SHA-256 de un archivo PDF"""
    sha256_hash = hashlib.sha256()
    
    try:
        with open(ruta_pdf, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"Error al calcular hash: {e}")
        return ""


# ====================================================================
# UTILIDADES JSON
# ====================================================================

def preparar_datos_para_json(datos: Dict) -> str:
    """Prepara datos para guardar en JSON"""
    return json.dumps(datos, default=str, ensure_ascii=False, indent=2)


def convertir_decimal_a_float(obj):
    """Convierte objetos Decimal a float para JSON"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Tipo {type(obj)} no serializable")