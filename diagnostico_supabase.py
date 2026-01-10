# diagnostico_supabase.py
"""
Script de diagnóstico para conexión a Supabase
Ejecutar: python diagnostico_supabase.py
"""

import os
import sys

print("🔍 DIAGNÓSTICO DE CONEXIÓN A SUPABASE")
print("=" * 60)
print()

# ====================================================================
# 1. VERIFICAR VARIABLES DE ENTORNO
# ====================================================================

print("📋 1. Verificando variables de entorno...")
print("-" * 60)

variables = {
    'SUPABASE_HOST': os.getenv('SUPABASE_HOST'),
    'SUPABASE_USER': os.getenv('SUPABASE_USER'),
    'SUPABASE_PASSWORD': os.getenv('SUPABASE_PASSWORD'),
    'SUPABASE_DB': os.getenv('SUPABASE_DB'),
    'SUPABASE_PORT': os.getenv('SUPABASE_PORT'),
    'DATABASE_URL': os.getenv('DATABASE_URL'),
    'SUPABASE_URL': os.getenv('SUPABASE_URL')
}

for var, valor in variables.items():
    if valor:
        # Ocultar password
        if 'PASSWORD' in var or 'URL' in var:
            mostrar = valor[:10] + "..." + valor[-5:] if len(valor) > 15 else "***"
            print(f"   ✅ {var}: {mostrar}")
        else:
            print(f"   ✅ {var}: {valor}")
    else:
        print(f"   ❌ {var}: No configurada")

print()

# ====================================================================
# 2. VERIFICAR DEPENDENCIAS
# ====================================================================

print("📦 2. Verificando dependencias instaladas...")
print("-" * 60)

dependencias = {
    'psycopg2': 'psycopg2-binary',
    'sqlmodel': 'sqlmodel',
    'streamlit': 'streamlit'
}

for modulo, paquete in dependencias.items():
    try:
        __import__(modulo)
        print(f"   ✅ {paquete}: Instalado")
    except ImportError:
        print(f"   ❌ {paquete}: NO instalado")
        print(f"      Instalar con: pip install {paquete}")

print()

# ====================================================================
# 3. VALIDAR FORMATO DE CREDENCIALES
# ====================================================================

print("🔍 3. Validando formato de credenciales...")
print("-" * 60)

host = variables['SUPABASE_HOST']
password = variables['SUPABASE_PASSWORD']
db_url = variables['DATABASE_URL']

if host:
    if 'supabase.com' in host:
        print(f"   ✅ Host tiene formato correcto: {host}")
    elif 'subabase.com' in host:
        print(f"   ⚠️  TYPO DETECTADO: 'subabase' debe ser 'supabase'")
        print(f"      Host correcto: {host.replace('subabase', 'supabase')}")
    else:
        print(f"   ⚠️  Host no parece ser de Supabase: {host}")

if password:
    if password.startswith('[') and password.endswith(']'):
        print(f"   ❌ Password tiene CORCHETES innecesarios")
        print(f"      Quita los corchetes: {password[1:-1]}")
    else:
        print(f"   ✅ Password sin corchetes")
    
    if '@' in password:
        print(f"   ℹ️  Password contiene '@' (puede causar problemas en URL)")
        print(f"      Recomendado: Usar variables separadas en vez de URL completa")

if db_url:
    if 'subabase.com' in db_url:
        print(f"   ⚠️  TYPO en DATABASE_URL: 'subabase' debe ser 'supabase'")
    if '?pgbouncer=true' in db_url:
        print(f"   ℹ️  Usando modo pooling (puerto 6543)")
        print(f"      Para desarrollo, usar puerto 5432 es más estable")

print()

# ====================================================================
# 4. PROBAR CONEXIÓN
# ====================================================================

print("🔌 4. Probando conexión a Supabase...")
print("-" * 60)

try:
    import psycopg2
    
    # Construir connection string
    if db_url and db_url.startswith('postgresql://'):
        # Usar DATABASE_URL
        conn_str = db_url.replace('postgresql://', '')
        if '?' in conn_str:
            conn_str = conn_str.split('?')[0]
        
        # Parse manual
        parts = conn_str.split('@')
        if len(parts) == 2:
            user_pass = parts[0].split(':')
            host_db = parts[1].split('/')
            
            if len(user_pass) == 2 and len(host_db) == 2:
                user = user_pass[0]
                password_raw = user_pass[1]
                host_port = host_db[0].split(':')
                database = host_db[1]
                
                if len(host_port) == 2:
                    host = host_port[0]
                    port = host_port[1]
                    
                    print(f"   📡 Intentando conectar a: {host}:{port}")
                    print(f"   👤 Usuario: {user}")
                    print(f"   🗄️  Base de datos: {database}")
                    
                    try:
                        conn = psycopg2.connect(
                            host=host,
                            port=port,
                            user=user,
                            password=password_raw,
                            database=database,
                            connect_timeout=10
                        )
                        
                        cursor = conn.cursor()
                        cursor.execute("SELECT version();")
                        version = cursor.fetchone()[0]
                        
                        print()
                        print(f"   ✅ ¡CONEXIÓN EXITOSA!")
                        print(f"   📌 PostgreSQL: {version[:50]}...")
                        
                        cursor.close()
                        conn.close()
                        
                    except psycopg2.OperationalError as e:
                        print(f"   ❌ Error de conexión: {e}")
                        print()
                        print("   💡 Posibles causas:")
                        print("      1. Password incorrecto (quita corchetes si tiene)")
                        print("      2. Host incorrecto (verifica typo: supabase vs subabase)")
                        print("      3. Puerto incorrecto (prueba 5432 en vez de 6543)")
                        print("      4. Firewall o problema de red")
                        
                    except Exception as e:
                        print(f"   ❌ Error inesperado: {e}")
    
    elif variables['SUPABASE_HOST'] and variables['SUPABASE_PASSWORD']:
        # Usar variables separadas
        host = variables['SUPABASE_HOST']
        user = variables['SUPABASE_USER'] or 'postgres'
        password = variables['SUPABASE_PASSWORD']
        database = variables['SUPABASE_DB'] or 'postgres'
        port = variables['SUPABASE_PORT'] or '5432'
        
        print(f"   📡 Intentando conectar a: {host}:{port}")
        print(f"   👤 Usuario: {user}")
        print(f"   🗄️  Base de datos: {database}")
        
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                connect_timeout=10
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            
            print()
            print(f"   ✅ ¡CONEXIÓN EXITOSA!")
            print(f"   📌 PostgreSQL: {version[:50]}...")
            
            cursor.close()
            conn.close()
            
        except psycopg2.OperationalError as e:
            print(f"   ❌ Error de conexión: {e}")
            print()
            print("   💡 Posibles causas:")
            print("      1. Password incorrecto")
            print("      2. Host incorrecto")
            print("      3. Puerto incorrecto")
            print("      4. Firewall o problema de red")
            
        except Exception as e:
            print(f"   ❌ Error inesperado: {e}")
    
    else:
        print("   ⚠️  No hay suficientes credenciales configuradas")
        print("   Configura DATABASE_URL o las variables individuales")

except ImportError:
    print("   ❌ psycopg2 no está instalado")
    print("   Instalar con: pip install psycopg2-binary")

print()

# ====================================================================
# 5. RECOMENDACIONES
# ====================================================================

print("💡 5. Recomendaciones")
print("=" * 60)

if not any(variables.values()):
    print("❌ NO HAY VARIABLES CONFIGURADAS")
    print()
    print("Configurar con PowerShell:")
    print('   $env:SUPABASE_HOST="aws-0-us-west-2.pooler.supabase.com"')
    print('   $env:SUPABASE_USER="postgres.emaktovavsuxvofltkbq"')
    print('   $env:SUPABASE_PASSWORD="asdl@colula70400"')
    print('   $env:SUPABASE_DB="postgres"')
    print('   $env:SUPABASE_PORT="5432"')
    print()
    print("O crear archivo .env con:")
    print("   SUPABASE_HOST=aws-0-us-west-2.pooler.supabase.com")
    print("   SUPABASE_USER=postgres.emaktovavsuxvofltkbq")
    print("   SUPABASE_PASSWORD=asdl@colula70400")
    print("   SUPABASE_DB=postgres")
    print("   SUPABASE_PORT=5432")

elif password and password.startswith('['):
    print("⚠️  ACCIÓN REQUERIDA: Quitar corchetes del password")
    print()
    print("   Password actual: [asdl@colula70400]")
    print("   Password correcto: asdl@colula70400")

elif db_url and 'subabase' in db_url:
    print("⚠️  ACCIÓN REQUERIDA: Corregir typo en URL")
    print()
    print("   Cambiar: subabase.com")
    print("   Por: supabase.com")

else:
    print("✅ Configuración parece correcta")
    print()
    print("Si aún no conecta:")
    print("   1. Verifica que el password sea exactamente el que creaste")
    print("   2. Intenta con puerto 5432 en vez de 6543")
    print("   3. Verifica tu conexión a Internet")
    print("   4. Revisa el dashboard de Supabase por errores")

print()
print("=" * 60)
print("Diagnóstico completado")
print("=" * 60)