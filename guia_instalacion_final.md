# 🚀 Guía de Instalación Completa
## Sistema Parroquial v4.0 - Arquitectura Modular

---

## 📋 Tabla de Contenido

1. [Requisitos Previos](#requisitos-previos)
2. [Descarga de Archivos](#descarga-de-archivos)
3. [Instalación Paso a Paso](#instalación-paso-a-paso)
4. [Configuración](#configuración)
5. [Primer Uso](#primer-uso)
6. [Troubleshooting](#troubleshooting)

---

## 🔧 Requisitos Previos

### Software Necesario

- **Python 3.9+** ([Descargar](https://www.python.org/downloads/))
- **pip** (gestor de paquetes de Python)
- **MySQL** (opcional, para base de datos remota)
- **Git** (opcional, para control de versiones)

### Verificar Instalación

```bash
python --version
pip --version
```

---

## 📥 Descarga de Archivos

### Opción A: Descargar Archivos Individuales

Descarga todos los archivos `.py` y `.md` generados y organízalos según la estructura:

```
proyecto_parroquial/
├── app.py
├── models.py
├── utils.py
├── sync_manager.py
├── database/
│   ├── __init__.py
│   ├── local.py
│   └── remote.py
├── components/
│   ├── __init__.py
│   ├── selectores.py
│   └── validadores.py
├── modules/
│   ├── __init__.py
│   ├── personas/
│   ├── geografia/
│   ├── sacramentos/
│   ├── grupos/
│   ├── clero/
│   ├── educacion/
│   ├── espacios/
│   ├── asistencia/
│   ├── finanzas/
│   ├── inventario/
│   ├── actas/
│   ├── constancias/
│   └── sistema/
└── scripts/
    └── init_sistema_completo.py
```

### Opción B: Usar Git (si tienes repositorio)

```bash
git clone <url-del-repositorio>
cd proyecto_parroquial
```

---

## 🛠️ Instalación Paso a Paso

### Paso 1: Crear Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual

# En Windows:
venv\Scripts\activate

# En Linux/Mac:
source venv/bin/activate
```

### Paso 2: Instalar Dependencias

```bash
# Instalar paquetes necesarios
pip install streamlit sqlmodel mysql-connector-python qrcode[pil] pillow reportlab PyPDF2
```

**Lista completa de dependencias:**
- `streamlit` - Framework web
- `sqlmodel` - ORM para bases de datos
- `mysql-connector-python` - Conector MySQL
- `qrcode[pil]` - Generación de códigos QR
- `pillow` - Procesamiento de imágenes
- `reportlab` - Generación de PDFs
- `PyPDF2` - Manipulación de PDFs

### Paso 3: Crear Estructura de Carpetas

```bash
# Crear todas las carpetas necesarias
mkdir -p database components modules scripts templates data

# Crear subcarpetas de modules
mkdir -p modules/personas modules/geografia modules/sacramentos
mkdir -p modules/grupos modules/clero modules/educacion
mkdir -p modules/espacios modules/asistencia modules/finanzas
mkdir -p modules/inventario modules/actas modules/constancias modules/sistema

# Crear subcarpetas de data
mkdir -p data/constancias data/qr_codes data/reportes
```

### Paso 4: Crear Archivos `__init__.py`

```bash
# Ejecutar script para crear todos los __init__.py

# En Linux/Mac:
for dir in database components modules modules/{personas,geografia,sacramentos,grupos,clero,educacion,espacios,asistencia,finanzas,inventario,actas,constancias,sistema}; do
    touch $dir/__init__.py
done

# En Windows PowerShell:
$dirs = @("database", "components", "modules", "modules/personas", "modules/geografia", "modules/sacramentos", "modules/grupos", "modules/clero", "modules/educacion", "modules/espacios", "modules/asistencia", "modules/finanzas", "modules/inventario", "modules/actas", "modules/constancias", "modules/sistema")
foreach ($dir in $dirs) {
    New-Item -Path "$dir/__init__.py" -ItemType File -Force
}
```

### Paso 5: Copiar Archivos Descargados

Copia todos los archivos `.py` descargados a sus ubicaciones correspondientes según la estructura de carpetas.

### Paso 6: Ejecutar Script de Inicialización

```bash
python scripts/init_sistema_completo.py
```

Selecciona la opción según tu caso:
- **1** = Solo LOCAL (SQLite) - Recomendado para empezar
- **2** = Solo REMOTA (MySQL) - Si ya tienes MySQL configurado
- **3** = Ambas - Para usar ambas bases de datos

El script creará:
- ✅ Configuración inicial
- ✅ Geografía eclesiástica básica (México, Oaxaca, Parroquia)
- ✅ Áreas parroquiales (6 áreas)
- ✅ Bodegas (B-1 a B-6)
- ✅ Perfiles de usuario con permisos (6 perfiles)
- ✅ Tipos de reunión (6 tipos)
- ✅ Categorías de inventario (10 categorías)
- ✅ Configuración de constancias

---

## ⚙️ Configuración

### Configurar Base de Datos Local (SQLite)

**No requiere configuración adicional.** SQLite se crea automáticamente en la primera ejecución.

Archivo creado: `parroquial.db`

### Configurar Base de Datos Remota (MySQL) - Opcional

Edita `database/remote.py` con tus credenciales:

```python
DB_CONFIG = {
    "host": "tu-servidor.com",
    "port": 3306,
    "user": "tu_usuario",
    "password": "tu_contraseña",
    "database": "parroquial_db"
}
```

### Configurar Constancias

Accede al sistema y ve a:
```
📜 Constancias → ⚙️ Configuración
```

Configura:
1. **Costos** (base + IVA)
2. **URLs de plantillas PNG** (subir plantillas)
3. **PayU** (si usarás pago en línea)

---

## 🎉 Primer Uso

### Iniciar el Sistema

```bash
streamlit run app.py
```

El sistema se abrirá en tu navegador en: `http://localhost:8501`

### Primer Inicio de Sesión

Por ahora el sistema no tiene autenticación activa. Próximamente se implementará.

### Crear Primer Usuario

Ve a:
```
⚙️ Sistema → 👤 Usuarios
```

Crea tu primer usuario administrador.

### Verificar Instalación

1. **Verificar Base de Datos:**
   - Sidebar: Verifica que aparezca "✅ SQLite Conectado"

2. **Verificar Módulos:**
   - Navega por cada módulo del menú
   - Verifica que no haya errores

3. **Verificar Estadísticas:**
   - Ve a "🏠 Inicio"
   - Deben aparecer estadísticas (aunque en 0)

---

## 🐛 Troubleshooting

### Problema: "ModuleNotFoundError"

**Causa:** Falta un módulo de Python

**Solución:**
```bash
pip install <nombre-del-modulo>
```

### Problema: "No module named 'database'"

**Causa:** Faltan archivos `__init__.py` o estructura incorrecta

**Solución:**
```bash
# Verificar que existan los __init__.py
ls database/__init__.py
ls components/__init__.py
ls modules/__init__.py

# Si no existen, crearlos:
touch database/__init__.py components/__init__.py modules/__init__.py
```

### Problema: "Import Error en models.py"

**Causa:** El archivo models.py está incompleto

**Solución:**
- Verifica que `models.py` tenga todo el contenido
- Debe terminar con `SYNC_ORDER_COMPLETE = [...]`

### Problema: "Error al conectar MySQL"

**Causa:** Credenciales incorrectas o servidor no disponible

**Solución:**
1. Verifica credenciales en `database/remote.py`
2. Verifica que MySQL esté corriendo
3. Verifica que la base de datos exista:
```sql
CREATE DATABASE IF NOT EXISTS parroquial_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Problema: "ImportError: cannot import name 'crud_personas'"

**Causa:** Archivo CRUD no está en la ubicación correcta

**Solución:**
```bash
# Verificar ubicación
ls modules/personas/crud_personas.py

# Verificar __init__.py
cat modules/personas/__init__.py
```

### Problema: Sistema lento

**Causa:** Demasiados datos en caché

**Solución:**
1. Reiniciar Streamlit: `Ctrl+C` y volver a ejecutar
2. Limpiar caché: En el menú de Streamlit → "Clear cache"

---

## 📚 Recursos Adicionales

### Documentación

- [README_CONSTANCIAS.md](README_CONSTANCIAS.md) - Módulo de constancias
- [ESTRUCTURA_FINAL.txt](ESTRUCTURA_FINAL.txt) - Estructura completa

### Soporte

**Parroquia de Santa María de la Asunción**  
📞 951 56 200 19  
📍 Av. 2 de abril No. 22, Tlacolula, Oaxaca

---

## ✅ Checklist de Verificación

Marca cada elemento al completarlo:

### Instalación Básica
- [ ] Python 3.9+ instalado
- [ ] Entorno virtual creado
- [ ] Dependencias instaladas
- [ ] Estructura de carpetas creada
- [ ] Archivos `__init__.py` creados
- [ ] Archivos `.py` copiados

### Configuración
- [ ] Script de inicialización ejecutado
- [ ] Base de datos creada
- [ ] Datos iniciales cargados

### Verificación
- [ ] Sistema inicia sin errores
- [ ] Todos los módulos accesibles
- [ ] Estadísticas visibles en inicio
- [ ] Base de datos conectada

### Opcional
- [ ] MySQL configurado
- [ ] Plantillas PNG subidas
- [ ] PayU configurado
- [ ] Usuarios creados

---

## 🎊 ¡Listo!

El sistema está completamente instalado y listo para usar.

### Próximos Pasos

1. **Registrar datos básicos:**
   - Crear personas
   - Registrar grupos parroquiales
   - Configurar centros de catecismo

2. **Configurar módulos administrativos:**
   - Subir plantillas de constancias
   - Configurar categorías financieras
   - Registrar bienes en inventario

3. **Capacitar usuarios:**
   - Crear cuentas de usuario
   - Asignar perfiles y permisos
   - Explicar flujos de trabajo

---

**Sistema Parroquial v4.0**  
*Desarrollado con ❤️ para la gestión pastoral y administrativa*

✨ **¡Que Dios bendiga este proyecto!** ✨
