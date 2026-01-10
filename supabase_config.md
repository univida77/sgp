# 🚀 Configuración de Supabase para Sistema Parroquial

## 📋 Paso 1: Crear Proyecto en Supabase

1. **Ir a Supabase**
   - Visita: https://supabase.com
   - Click en **"Start your project"**
   - Inicia sesión con GitHub (recomendado) o email

2. **Crear Nuevo Proyecto**
   - Click en **"New Project"**
   - Nombre: `sistema-parroquial` (o el que prefieras)
   - **Database Password**: Crea una contraseña SEGURA
     - ⚠️ **IMPORTANTE**: Guarda esta contraseña, la necesitarás después
   - Region: `South America (São Paulo)` (más cercano a México)
   - Click en **"Create new project"**
   - Espera 2-3 minutos mientras se crea el proyecto

---

## 🔑 Paso 2: Obtener Credenciales de Conexión

1. **En tu proyecto de Supabase**, ve a:
   - **Settings** (⚙️) → **Database** (en el menú lateral)

2. **Localizar "Connection string"**
   - Busca la sección **"Connection string"**
   - Selecciona la pestaña **"URI"**
   - Verás algo como:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
   ```

3. **Copiar las partes importantes:**
   - **HOST**: `db.xxxxxxxxxxxxx.supabase.co`
   - **PASSWORD**: El que creaste en el paso 1
   - **DATABASE**: `postgres` (normalmente no cambiar)
   - **USER**: `postgres` (normalmente no cambiar)
   - **PORT**: `5432` (normalmente no cambiar)

---

## ⚙️ Paso 3: Configurar la Aplicación

### Opción A: Variables de Entorno (Recomendado) 🌟

#### Windows PowerShell:
```powershell
# Configurar variables de entorno
$env:SUPABASE_HOST="db.xxxxxxxxxxxxx.supabase.co"  # ⬅️ TU HOST
$env:SUPABASE_PASSWORD="tu_password_aqui"          # ⬅️ TU PASSWORD
$env:SUPABASE_DB="postgres"
$env:SUPABASE_USER="postgres"
$env:SUPABASE_PORT="5432"

# Iniciar aplicación
streamlit run app.py
```

#### Windows CMD:
```cmd
set SUPABASE_HOST=db.xxxxxxxxxxxxx.supabase.co
set SUPABASE_PASSWORD=tu_password_aqui
set SUPABASE_DB=postgres
set SUPABASE_USER=postgres
set SUPABASE_PORT=5432

streamlit run app.py
```

#### Linux/Mac:
```bash
export SUPABASE_HOST="db.xxxxxxxxxxxxx.supabase.co"
export SUPABASE_PASSWORD="tu_password_aqui"
export SUPABASE_DB="postgres"
export SUPABASE_USER="postgres"
export SUPABASE_PORT="5432"

streamlit run app.py
```

### Opción B: URL Completa (Alternativa)

```powershell
# Solo configurar la URL completa
$env:SUPABASE_URL="postgresql://postgres:tu_password@db.xxxxx.supabase.co:5432/postgres"

streamlit run app.py
```

### Opción C: Archivo .env (Permanente) 🔒

1. **Crear archivo `.env`** en la raíz del proyecto:
   ```env
   SUPABASE_HOST=db.xxxxxxxxxxxxx.supabase.co
   SUPABASE_PASSWORD=tu_password_aqui
   SUPABASE_DB=postgres
   SUPABASE_USER=postgres
   SUPABASE_PORT=5432
   ```

2. **Instalar python-dotenv**:
   ```bash
   pip install python-dotenv
   ```

3. **Agregar al inicio de `app.py`**:
   ```python
   from dotenv import load_dotenv
   load_dotenv()  # Cargar variables de .env
   ```

4. **⚠️ Agregar `.env` al `.gitignore`**:
   ```
   # .gitignore
   .env
   *.pyc
   __pycache__/
   ```

---

## 📦 Paso 4: Instalar Dependencias

```bash
# Instalar driver de PostgreSQL
pip install psycopg2-binary

# O si usas requirements.txt
pip install -r requirements.txt
```

**Actualizar `requirements.txt`**:
```txt
streamlit==1.31.0
sqlmodel==0.0.14
psycopg2-binary==2.9.9
python-dotenv==1.0.0
```

---

## 🧪 Paso 5: Probar Conexión

1. **Iniciar aplicación**:
   ```bash
   streamlit run app.py
   ```

2. **En el Sidebar**:
   - Seleccionar **"Remoto (PostgreSQL)"** o **"Remoto (Supabase)"**
   - Deberías ver: **"✅ PostgreSQL Conectado"**

3. **Crear Tablas**:
   - Ve a la sección de **Sincronización**
   - Click en **"🔄 SINCRONIZAR"**
   - Las tablas se crearán automáticamente

---

## 🔒 Seguridad: Mejores Prácticas

### ✅ HACER:
- ✅ Usar variables de entorno
- ✅ Agregar `.env` al `.gitignore`
- ✅ Usar contraseñas seguras (16+ caracteres)
- ✅ Rotar contraseñas periódicamente

### ❌ NO HACER:
- ❌ Hardcodear contraseñas en el código
- ❌ Subir `.env` a GitHub
- ❌ Compartir credenciales por email/chat
- ❌ Usar contraseñas simples

---

## 🐛 Solución de Problemas

### Error: "could not connect to server"
```
✅ Verifica que el HOST sea correcto
✅ Verifica que tu IP esté permitida (Supabase permite todas por defecto)
✅ Revisa tu conexión a internet
```

### Error: "password authentication failed"
```
✅ Verifica el PASSWORD
✅ Asegúrate de no tener espacios al inicio/final
✅ Prueba resetear el password en Supabase Settings
```

### Error: "psycopg2 not found"
```bash
pip install psycopg2-binary
```

### La aplicación no encuentra las variables
```
✅ Cierra y reabre la terminal
✅ Verifica que ejecutes desde la misma terminal donde configuraste las variables
✅ Usa archivo .env con python-dotenv
```

---

## 📊 Verificar en Supabase

1. **Ver tus tablas**:
   - Ve a **Table Editor** en Supabase
   - Deberías ver todas las tablas creadas (persona, telefono, etc.)

2. **SQL Editor**:
   - Puedes ejecutar queries manualmente:
   ```sql
   SELECT * FROM persona LIMIT 10;
   ```

3. **Logs**:
   - Ve a **Logs** para ver actividad de la base de datos

---

## 💡 Consejos Adicionales

### Plan Gratuito de Supabase:
- ✅ 500 MB de almacenamiento
- ✅ 2 GB de transferencia/mes
- ✅ 50,000 usuarios activos/mes
- ✅ Backups automáticos (7 días)

### Cuando Migrar a Plan Pro:
- 📈 Más de 500 MB de datos
- 📈 Necesitas backups diarios
- 📈 Necesitas soporte prioritario

---

## 🎯 ¡Listo!

Ahora tu aplicación sincroniza con Supabase en la nube:
- 🌐 Accesible desde cualquier lugar
- ☁️ Backups automáticos
- 🔄 Sincronización bidireccional con SQLite local
- 🔒 Conexión segura SSL

**¿Necesitas ayuda?** Revisa la consola para mensajes de error detallados.
