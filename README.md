# 🛐 Sistema de Gestión Parroquial

Sistema completo de gestión para iglesias católicas desarrollado con **Python**, **Streamlit** y **SQLModel**.

## 📋 Características Principales

### ✨ Módulos Principales
- **👥 Gestión de Personas**: Registro completo con relaciones familiares (padres, abuelos)
- **✝️ Sacramentos**: Bautizo, Confirmación, Eucaristía, Matrimonio, Renovación Bautismal
- **📚 Catecumenado**: Gestión de catecúmenos y preparación sacramental
- **🌍 Jerarquía Geográfica**: Arquidiócesis → Decanato → Parroquia → Comunidad
- **🙏 Presbíteros**: Registro y asignación de sacerdotes
- **👥 Grupos**: Grupos de catequesis y grupos parroquiales
- **👤 Usuarios**: Sistema de usuarios con autenticación

### 🆕 Módulos Avanzados
- **🏫 Salones**: Gestión de espacios físicos con calendario de uso
- **📖 Cursos**: Plantillas de cursos reutilizables con temas/sesiones
- **🎯 Actividades**: Implementación concreta de cursos o eventos
- **📅 Sesiones**: Clases específicas con manejo de excepciones
- **📝 Asistencia**: Registro individual y grupal de asistencia
- **📋 Inscripciones**: Control de participantes en actividades

## 🚀 Instalación

### 1. Requisitos Previos
- Python 3.9 o superior
- MySQL Server 8.0+ (para base de datos remota)
- Git (opcional)

### 2. Clonar el Repositorio
```bash
git clone <url-del-repositorio>
cd sistema-parroquial
```

### 3. Crear Entorno Virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 5. Configurar Base de Datos Remota

#### Opción A: Usar archivo .env
```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
# DB_HOST=localhost
# DB_USER=root
# DB_PASSWORD=tu_password
# DB_NAME=sql3805544
```

#### Opción B: Variables de entorno del sistema
```bash
# Windows
set DB_HOST=localhost
set DB_USER=root
set DB_PASSWORD=tu_password
set DB_NAME=sql3805544

# Linux/Mac
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=tu_password
export DB_NAME=sql3805544
```

### 6. Inicializar Base de Datos

#### Crear Base de Datos en MySQL
```sql
-- Conectarse a MySQL
mysql -u root -p

-- Crear la base de datos
CREATE DATABASE sql3805544 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Salir de MySQL
EXIT;
```

#### Crear Tablas Automáticamente
El sistema creará todas las tablas automáticamente al iniciar, pero puedes forzar la creación:

1. Ejecutar la aplicación: `streamlit run app.py`
2. En el sidebar, seleccionar **"Remoto (MySQL)"**
3. Hacer clic en **"🗂️ Crear Tablas"**

## 🎮 Uso

### Iniciar la Aplicación
```bash
streamlit run app.py
```

La aplicación se abrirá en tu navegador en `http://localhost:8501`

### Primer Uso

#### 1. Configuración de Base de Datos
En el **sidebar izquierdo**:
- Seleccionar **"Remoto (MySQL)"** para usar la base de datos remota
- O **"Local (SQLite)"** para pruebas locales

#### 2. Verificar Conexión
- Hacer clic en **"🔍 Verificar Tablas"** para ver el estado de las tablas
- Si hay problemas, usar **"🗂️ Crear Tablas"** para crearlas

#### 3. Crear Datos Iniciales

**Orden recomendado:**

1. **Jerarquía Geográfica**
   - Ir a "🌍 Gestión de Jerarquía Geográfica"
   - Crear: Arquidiócesis → Decanato → Parroquia → Comunidad → Centro de Catecismo

2. **Personas**
   - Ir a "👥 Gestión de Personas"
   - Registrar personas (catequistas, catecúmenos, etc.)

3. **Presbíteros**
   - Ir a "🙏 Gestión de Presbíteros"
   - Asignar sacerdotes

4. **Grupos**
   - Crear grupos de catequesis o parroquiales

5. **Salones y Cursos**
   - Crear salones disponibles
   - Crear plantillas de cursos

6. **Actividades**
   - Crear actividades (implementación de cursos)
   - Asignar horarios
   - Inscribir participantes

## 📊 Sincronización Local ↔️ Remota

El sistema permite trabajar con dos bases de datos simultáneamente:

### Base de Datos Local (SQLite)
- **Ubicación**: `parroquia.db` en la carpeta del proyecto
- **Uso**: Desarrollo, pruebas, trabajo offline
- **Ventajas**: Rápida, no requiere servidor

### Base de Datos Remota (MySQL)
- **Ubicación**: Servidor MySQL configurado
- **Uso**: Producción, trabajo en equipo
- **Ventajas**: Multiusuario, backups automáticos

### Cómo Sincronizar
1. En el sidebar, asegúrate de estar conectado a **"Remoto (MySQL)"**
2. Hacer clic en **"🔄 SINCRONIZAR TODO"**
3. Opcionalmente, marcar **"⚠️ Forzar recreación completa"** si hay errores de estructura

⚠️ **IMPORTANTE**: La sincronización toma como fuente de verdad la base de datos REMOTA y sobrescribe la LOCAL.

## 🔧 Solución de Problemas

### Error: "No se puede conectar a MySQL"
```bash
# Verificar que MySQL esté corriendo
# Windows
net start MySQL80

# Linux
sudo systemctl start mysql

# Mac
brew services start mysql
```

### Error: "Tablas no existen"
1. Ir a **"Remoto (MySQL)"** en el sidebar
2. Clic en **"🗂️ Crear Tablas"**
3. Si el error persiste, marcar **"⚠️ Forzar recreación completa"** y sincronizar

### Error: "Duplicate entry" al crear registros
- Esto indica que ya existe un registro con los mismos datos únicos (ej: CURP duplicado)
- Verifica que no estés intentando crear un registro duplicado

### La aplicación no inicia
```bash
# Verificar que todas las dependencias estén instaladas
pip install -r requirements.txt

# Verificar la versión de Python
python --version  # Debe ser 3.9+
```

## 📁 Estructura del Proyecto

```
sistema-parroquial/
│
├── app.py                          # Aplicación principal
├── models.py                       # Modelos de base de datos
├── database_local.py               # Gestión SQLite
├── database_remote.py              # Gestión MySQL
├── utils.py                        # Funciones auxiliares
│
├── crud_personas.py                # CRUD Personas
├── crud_sacramentos.py             # CRUD Sacramentos
├── crud_catecumenos.py             # CRUD Catecúmenos
├── crud_geografia.py               # CRUD Jerarquía
├── crud_presbiteros.py             # CRUD Presbíteros
├── crud_cursos_catequesis.py       # CRUD Grupos Catequesis
├── crud_grupo_parroquial.py        # CRUD Grupos Parroquiales
├── crud_usuarios.py                # CRUD Usuarios
│
├── crud_salones.py                 # CRUD Salones
├── crud_cursos.py                  # CRUD Cursos
├── crud_actividades.py             # CRUD Actividades
├── crud_sesiones.py                # CRUD Sesiones
├── crud_asistencia.py              # CRUD Asistencia
│
├── requirements.txt                # Dependencias
├── .env.example                    # Ejemplo de configuración
├── .env                            # Configuración (no versionado)
├── README.md                       # Este archivo
└── parroquia.db                    # Base de datos SQLite (auto-generada)
```

## 🔐 Seguridad

### Contraseñas
- Las contraseñas se almacenan con hash SHA-256
- Requisitos mínimos: 8 caracteres, mayúsculas, minúsculas y números

### Base de Datos
- Las credenciales se almacenan en variables de entorno
- Nunca versionar el archivo `.env`
- Usar usuarios con permisos limitados en producción

## 🤝 Contribuir

1. Fork el proyecto
2. Crear una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.

## 👨‍💻 Autor

Sistema desarrollado para la gestión integral de parroquias católicas.

## 📞 Soporte

Para reportar errores o solicitar funcionalidades:
- Crear un Issue en el repositorio
- Contactar al administrador del sistema

---

**Versión**: 3.0 - Sistema Completo  
**Fecha**: Diciembre 2024  
**Stack**: Python + Streamlit + SQLModel + MySQL + SQLite