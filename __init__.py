# ====================================================================
# database/__init__.py
# ====================================================================
"""
Módulo de acceso a base de datos
"""
from . import local
from . import remote

__all__ = ['local', 'remote']


# ====================================================================
# components/__init__.py
# ====================================================================
"""
Componentes reutilizables del sistema
"""
from . import selectores
from . import validadores

__all__ = ['selectores', 'validadores']


# ====================================================================
# modules/__init__.py
# ====================================================================
"""
Módulos CRUD del sistema
"""

__all__ = [
    'personas',
    'geografia',
    'sacramentos',
    'grupos',
    'clero',
    'educacion',
    'espacios',
    'asistencia',
    'finanzas',
    'inventario',
    'actas',
    'constancias',
    'sistema'
]


# ====================================================================
# modules/personas/__init__.py
# ====================================================================
"""
Módulo de gestión de personas
"""
from . import crud_personas
from . import crud_contacto
from . import crud_catecumenos

__all__ = ['crud_personas', 'crud_contacto', 'crud_catecumenos']


# ====================================================================
# modules/geografia/__init__.py
# ====================================================================
"""
Módulo de geografía eclesiástica
"""
from . import crud_geografia

__all__ = ['crud_geografia']


# ====================================================================
# modules/sacramentos/__init__.py
# ====================================================================
"""
Módulo de sacramentos
"""
from . import crud_sacramentos

__all__ = ['crud_sacramentos']


# ====================================================================
# modules/grupos/__init__.py
# ====================================================================
"""
Módulo de grupos parroquiales y catequesis
"""
from . import crud_cursos_catequesis
from . import crud_grupo_parroquial

__all__ = ['crud_cursos_catequesis', 'crud_grupo_parroquial']


# ====================================================================
# modules/clero/__init__.py
# ====================================================================
"""
Módulo de clero
"""
from . import crud_presbiteros

__all__ = ['crud_presbiteros']


# ====================================================================
# modules/educacion/__init__.py
# ====================================================================
"""
Módulo de educación pastoral
"""
from . import crud_cursos
from . import crud_actividades
from . import crud_sesiones

__all__ = ['crud_cursos', 'crud_actividades', 'crud_sesiones']


# ====================================================================
# modules/espacios/__init__.py
# ====================================================================
"""
Módulo de espacios físicos
"""
from . import crud_salones

__all__ = ['crud_salones']


# ====================================================================
# modules/asistencia/__init__.py
# ====================================================================
"""
Módulo de control de asistencia
"""
from . import crud_asistencia

__all__ = ['crud_asistencia']


# ====================================================================
# modules/finanzas/__init__.py
# ====================================================================
"""
Módulo de gestión financiera
"""
from . import crud_finanzas

__all__ = ['crud_finanzas']


# ====================================================================
# modules/inventario/__init__.py
# ====================================================================
"""
Módulo de inventario de bienes
"""
from . import crud_inventario

__all__ = ['crud_inventario']


# ====================================================================
# modules/actas/__init__.py
# ====================================================================
"""
Módulo de archivo de actas
"""
from . import crud_actas

__all__ = ['crud_actas']


# ====================================================================
# modules/constancias/__init__.py
# ====================================================================
"""
Módulo de constancias sacramentales
"""
from . import crud_constancias
from . import utils_constancias

__all__ = ['crud_constancias', 'utils_constancias']


# ====================================================================
# modules/sistema/__init__.py
# ====================================================================
"""
Módulo de sistema y usuarios
"""
from . import crud_usuarios

__all__ = ['crud_usuarios']


# ====================================================================
# INSTRUCCIONES DE USO
# ====================================================================
"""
CÓMO CREAR LOS ARCHIVOS __init__.py:

1. Crear archivo vacío en cada carpeta:
   touch database/__init__.py
   touch components/__init__.py
   touch modules/__init__.py
   touch modules/personas/__init__.py
   touch modules/geografia/__init__.py
   touch modules/sacramentos/__init__.py
   touch modules/grupos/__init__.py
   touch modules/clero/__init__.py
   touch modules/educacion/__init__.py
   touch modules/espacios/__init__.py
   touch modules/asistencia/__init__.py
   touch modules/finanzas/__init__.py
   touch modules/inventario/__init__.py
   touch modules/actas/__init__.py
   touch modules/constancias/__init__.py
   touch modules/sistema/__init__.py

2. Opcionalmente, copiar el contenido correspondiente de arriba
   a cada archivo para mejor documentación

3. Los archivos __init__.py pueden estar vacíos y funcionarán igual

SCRIPT RÁPIDO (Linux/Mac):
---------------------------
for dir in database components modules modules/{personas,geografia,sacramentos,grupos,clero,educacion,espacios,asistencia,finanzas,inventario,actas,constancias,sistema}; do
    touch $dir/__init__.py
done

SCRIPT RÁPIDO (Windows PowerShell):
------------------------------------
$dirs = @("database", "components", "modules", "modules/personas", "modules/geografia", "modules/sacramentos", "modules/grupos", "modules/clero", "modules/educacion", "modules/espacios", "modules/asistencia", "modules/finanzas", "modules/inventario", "modules/actas", "modules/constancias", "modules/sistema")
foreach ($dir in $dirs) {
    New-Item -Path "$dir/__init__.py" -ItemType File -Force
}
"""
