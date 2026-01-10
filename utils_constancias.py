# utils_constancias.py
"""
Utilidades para generación de constancias
Sistema Parroquial v4.0

INSTALACIÓN:
1. Guardar como: utils_constancias.py
2. Colocar en la raíz del proyecto
3. Importar en crud_constancias.py:
   from utils_constancias import generar_pdf_constancia, generar_qr_code

DEPENDENCIAS:
pip install qrcode[pil] pillow reportlab PyPDF2
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

# Para PDF
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️ reportlab no está instalado. Instalar con: pip install reportlab")


# ====================================================================
# GENERACIÓN DE CÓDIGO QR
# ====================================================================

def generar_qr_code(contenido: str, tamano: int = 150) -> Tuple[Image.Image, str]:
    """
    Genera código QR con el contenido especificado
    
    Args:
        contenido: URL o texto a codificar en el QR
        tamano: Tamaño en píxeles del QR
    
    Returns:
        Tuple[Image, str]: (Imagen PIL del QR, Hash SHA-256 del contenido)
    """
    # Generar QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Alta corrección de errores
        box_size=10,
        border=4,
    )
    
    qr.add_data(contenido)
    qr.make(fit=True)
    
    # Crear imagen
    img_qr = qr.make_image(fill_color="black", back_color="white")
    
    # Redimensionar
    img_qr = img_qr.resize((tamano, tamano), Image.Resampling.LANCZOS)
    
    # Generar hash del contenido
    hash_qr = hashlib.sha256(contenido.encode()).hexdigest()
    
    return img_qr, hash_qr


def guardar_qr_como_png(img_qr: Image.Image, ruta_destino: str) -> bool:
    """
    Guarda imagen QR como archivo PNG
    
    Args:
        img_qr: Imagen PIL del QR
        ruta_destino: Ruta donde guardar el archivo
    
    Returns:
        bool: True si se guardó exitosamente
    """
    try:
        # Crear directorio si no existe
        directorio = os.path.dirname(ruta_destino)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio)
        
        img_qr.save(ruta_destino, "PNG")
        return True
    except Exception as e:
        print(f"Error al guardar QR: {e}")
        return False


def qr_a_base64(img_qr: Image.Image) -> str:
    """
    Convierte imagen QR a string base64
    
    Args:
        img_qr: Imagen PIL del QR
    
    Returns:
        str: Imagen codificada en base64
    """
    import base64
    
    buffer = BytesIO()
    img_qr.save(buffer, format="PNG")
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return img_base64


# ====================================================================
# GENERACIÓN DE PDF CON PLANTILLA
# ====================================================================

def generar_pdf_constancia(
    plantilla_png_path: str,
    datos_constancia: Dict,
    folio: str,
    qr_image: Image.Image,
    configuracion_campos: Dict,
    output_path: str
) -> Tuple[bool, Optional[str]]:
    """
    Genera PDF de constancia insertando datos en plantilla PNG
    
    Args:
        plantilla_png_path: Ruta a la plantilla PNG
        datos_constancia: Diccionario con datos del sacramento
        folio: Folio único de la constancia
        qr_image: Imagen PIL del código QR
        configuracion_campos: Configuración de posiciones de campos
        output_path: Ruta donde guardar el PDF
    
    Returns:
        Tuple[bool, str]: (Éxito, Ruta del archivo o mensaje de error)
    """
    if not REPORTLAB_AVAILABLE:
        return False, "reportlab no está instalado"
    
    try:
        # Cargar plantilla PNG
        if not os.path.exists(plantilla_png_path):
            return False, f"Plantilla no encontrada: {plantilla_png_path}"
        
        plantilla = Image.open(plantilla_png_path)
        ancho, alto = plantilla.size
        
        # Crear copia de plantilla para trabajar
        img_final = plantilla.copy()
        draw = ImageDraw.Draw(img_final)
        
        # Configuración de fuente
        try:
            fuente_path = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
            if not os.path.exists(fuente_path):
                # Fallback para Windows
                fuente_path = "C:\\Windows\\Fonts\\times.ttf"
            
            fuente_normal = ImageFont.truetype(fuente_path, 24)
            fuente_pequena = ImageFont.truetype(fuente_path, 18)
        except:
            fuente_normal = ImageFont.load_default()
            fuente_pequena = ImageFont.load_default()
        
        # Insertar datos según configuración
        insertar_datos_en_plantilla(
            draw, datos_constancia, configuracion_campos, 
            fuente_normal, fuente_pequena
        )
        
        # Insertar QR en la posición configurada
        qr_pos = configuracion_campos.get('qr', {'x': 800, 'y': 1000})
        img_final.paste(qr_image, (qr_pos['x'], qr_pos['y']))
        
        # Guardar como imagen temporal
        temp_image_path = output_path.replace('.pdf', '_temp.png')
        img_final.save(temp_image_path, 'PNG', dpi=(300, 300))
        
        # Crear PDF
        c = canvas.Canvas(output_path, pagesize=letter)
        
        # Calcular dimensiones para ajustar al tamaño carta
        page_width, page_height = letter
        img_width, img_height = img_final.size
        
        # Escalar manteniendo proporción
        scale = min(page_width / img_width, page_height / img_height)
        new_width = img_width * scale
        new_height = img_height * scale
        
        # Centrar imagen
        x = (page_width - new_width) / 2
        y = (page_height - new_height) / 2
        
        c.drawImage(
            temp_image_path,
            x, y,
            width=new_width,
            height=new_height,
            preserveAspectRatio=True
        )
        
        c.save()
        
        # Limpiar archivo temporal
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        
        return True, output_path
        
    except Exception as e:
        return False, f"Error al generar PDF: {str(e)}"


def insertar_datos_en_plantilla(
    draw: ImageDraw.Draw,
    datos: Dict,
    configuracion: Dict,
    fuente_normal: ImageFont.FreeTypeFont,
    fuente_pequena: ImageFont.FreeTypeFont
):
    """
    Inserta datos de texto en la plantilla
    
    Args:
        draw: Objeto ImageDraw para dibujar texto
        datos: Diccionario con los datos a insertar
        configuracion: Configuración de posiciones
        fuente_normal: Fuente para texto normal
        fuente_pequena: Fuente para texto pequeño
    """
    # Ejemplo de configuración básica si no viene especificada
    if not configuracion or 'campos' not in configuracion:
        configuracion = {
            'campos': {
                'nombre_completo': {'x': 400, 'y': 450, 'fuente': 'normal'},
                'fecha_sacramento': {'x': 400, 'y': 520, 'fuente': 'normal'},
                'lugar': {'x': 400, 'y': 590, 'fuente': 'normal'},
                'nombre_padre': {'x': 400, 'y': 660, 'fuente': 'pequena'},
                'nombre_madre': {'x': 400, 'y': 710, 'fuente': 'pequena'},
                'padrino': {'x': 400, 'y': 760, 'fuente': 'pequena'},
                'madrina': {'x': 400, 'y': 810, 'fuente': 'pequena'},
            }
        }
    
    # Insertar cada campo
    for campo, config in configuracion['campos'].items():
        if campo in datos and datos[campo]:
            valor = str(datos[campo])
            
            # Formatear fechas
            if 'fecha' in campo and hasattr(datos[campo], 'strftime'):
                valor = datos[campo].strftime('%d de %B de %Y')
            
            # Seleccionar fuente
            fuente = fuente_normal if config.get('fuente') == 'normal' else fuente_pequena
            
            # Dibujar texto
            x = config.get('x', 0)
            y = config.get('y', 0)
            color = config.get('color', (0, 0, 0))  # Negro por defecto
            
            draw.text((x, y), valor, font=fuente, fill=color)


# ====================================================================
# VALIDACIÓN DE PLANTILLAS
# ====================================================================

def validar_plantilla_png(ruta_plantilla: str) -> Tuple[bool, str]:
    """
    Valida que la plantilla PNG sea correcta
    
    Args:
        ruta_plantilla: Ruta a la plantilla
    
    Returns:
        Tuple[bool, str]: (Es válida, Mensaje)
    """
    if not os.path.exists(ruta_plantilla):
        return False, "El archivo no existe"
    
    try:
        img = Image.open(ruta_plantilla)
        
        # Verificar formato
        if img.format != 'PNG':
            return False, f"El archivo debe ser PNG, no {img.format}"
        
        # Verificar dimensiones mínimas
        ancho, alto = img.size
        if ancho < 800 or alto < 1000:
            return False, f"Dimensiones mínimas: 800x1000px. Actual: {ancho}x{alto}px"
        
        # Verificar modo de color
        if img.mode not in ['RGB', 'RGBA']:
            return False, f"Modo de color debe ser RGB o RGBA, no {img.mode}"
        
        return True, f"Plantilla válida: {ancho}x{alto}px, {img.mode}"
        
    except Exception as e:
        return False, f"Error al validar: {str(e)}"


# ====================================================================
# GENERACIÓN DE FOLIO
# ====================================================================

def generar_folio_constancia(tipo_sacramento: str, numero: int, anio: int = None) -> str:
    """
    Genera folio único para constancia
    
    Args:
        tipo_sacramento: Tipo de sacramento
        numero: Número consecutivo
        anio: Año (por defecto el actual)
    
    Returns:
        str: Folio generado (ej: CONST-BAU-2025-000123)
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
    """
    Formatea datos del sacramento para la constancia
    
    Args:
        datos_sacramento: Datos crudos del sacramento
    
    Returns:
        Dict: Datos formateados y listos para insertar
    """
    datos_formateados = {}
    
    # Formatear nombre completo
    if 'nombre_completo' in datos_sacramento:
        datos_formateados['nombre_completo'] = datos_sacramento['nombre_completo'].upper()
    
    # Formatear fechas
    if 'fecha_sacramento' in datos_sacramento:
        fecha = datos_sacramento['fecha_sacramento']
        if hasattr(fecha, 'strftime'):
            datos_formateados['fecha_sacramento'] = fecha.strftime('%d de %B de %Y')
        else:
            datos_formateados['fecha_sacramento'] = str(fecha)
    
    # Formatear nombres de padres
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
    """
    Obtiene configuración de campos según tipo de sacramento
    
    Args:
        tipo_sacramento: Tipo de sacramento
    
    Returns:
        Dict: Configuración de posiciones de campos
    """
    # Configuración basada en la imagen de ejemplo de Confirmación
    # Estas coordenadas deben ajustarse según cada plantilla real
    
    if tipo_sacramento == "Confirmación":
        return {
            'qr': {'x': 50, 'y': 950},  # Esquina inferior izquierda
            'campos': {
                'nombre_completo': {
                    'x': 400,
                    'y': 450,
                    'fuente': 'normal',
                    'color': (139, 0, 0),  # Color vino/marrón
                    'alineacion': 'center'
                },
                'fecha_sacramento': {
                    'x': 400,
                    'y': 530,
                    'fuente': 'normal',
                    'color': (0, 0, 0),
                    'alineacion': 'center'
                },
                'lugar': {
                    'x': 400,
                    'y': 600,
                    'fuente': 'pequena',
                    'color': (0, 0, 0),
                    'alineacion': 'center'
                },
                'nombre_padre': {
                    'x': 500,
                    'y': 680,
                    'fuente': 'pequena',
                    'color': (0, 0, 0),
                    'alineacion': 'left'
                },
                'nombre_madre': {
                    'x': 500,
                    'y': 720,
                    'fuente': 'pequena',
                    'color': (0, 0, 0),
                    'alineacion': 'left'
                },
                'padrino': {
                    'x': 500,
                    'y': 760,
                    'fuente': 'pequena',
                    'color': (0, 0, 0),
                    'alineacion': 'left'
                },
                'libro': {
                    'x': 100,
                    'y': 1000,
                    'fuente': 'pequena',
                    'color': (0, 0, 0),
                    'alineacion': 'left'
                },
                'folio_libro': {
                    'x': 100,
                    'y': 1030,
                    'fuente': 'pequena',
                    'color': (0, 0, 0),
                    'alineacion': 'left'
                },
                'partida': {
                    'x': 100,
                    'y': 1060,
                    'fuente': 'pequena',
                    'color': (0, 0, 0),
                    'alineacion': 'left'
                }
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
    
    # Configuración por defecto
    return {
        'qr': {'x': 50, 'y': 950},
        'campos': {}
    }


# ====================================================================
# UTILIDADES DE CONVERSIÓN
# ====================================================================

def convertir_decimal_a_float(obj):
    """Convierte objetos Decimal a float para JSON"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Tipo {type(obj)} no serializable")


def preparar_datos_para_json(datos: Dict) -> str:
    """
    Prepara datos para guardar en JSON
    
    Args:
        datos: Diccionario con datos
    
    Returns:
        str: JSON string
    """
    return json.dumps(datos, default=str, ensure_ascii=False, indent=2)


# ====================================================================
# CÁLCULO DE HASH
# ====================================================================

def calcular_hash_pdf(ruta_pdf: str) -> str:
    """
    Calcula hash SHA-256 de un archivo PDF
    
    Args:
        ruta_pdf: Ruta al archivo PDF
    
    Returns:
        str: Hash hexadecimal
    """
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
# EJEMPLO DE USO
# ====================================================================

if __name__ == "__main__":
    print("=== Utilidades de Constancias ===")
    print()
    
    # Ejemplo 1: Generar QR
    print("1. Generando código QR...")
    url_verificacion = "https://parroquia-tlacolula.com/verificar/CONST-BAU-2025-000001"
    img_qr, hash_qr = generar_qr_code(url_verificacion, tamano=150)
    print(f"   QR generado. Hash: {hash_qr[:16]}...")
    
    # Ejemplo 2: Generar folio
    print()
    print("2. Generando folio...")
    folio = generar_folio_constancia("Confirmación", 123, 2025)
    print(f"   Folio: {folio}")
    
    # Ejemplo 3: Validar plantilla
    print()
    print("3. Validar plantilla...")
    # valido, msg = validar_plantilla_png("plantilla_confirmacion.png")
    # print(f"   {msg}")
    
    print()
    print("✅ Utilidades listas para usar")
