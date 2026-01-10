#!/usr/bin/env python3
"""
cleanup.py - Script de Limpieza del Proyecto
Sistema Parroquial v4.0

Uso: python cleanup.py
"""

import os
import shutil
from pathlib import Path

def limpiar_pycache():
    """Elimina directorios __pycache__"""
    contador = 0
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            path = os.path.join(root, '__pycache__')
            shutil.rmtree(path)
            print(f"✅ Eliminado: {path}")
            contador += 1
    return contador

def limpiar_archivos_pyc():
    """Elimina archivos .pyc"""
    contador = 0
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                path = os.path.join(root, file)
                os.remove(path)
                print(f"✅ Eliminado: {path}")
                contador += 1
    return contador

def verificar_init_vacios():
    """Verifica archivos __init__.py vacíos"""
    vacios = []
    for root, dirs, files in os.walk('.'):
        if '__init__.py' in files:
            path = os.path.join(root, '__init__.py')
            if os.path.getsize(path) == 0:
                vacios.append(path)
    return vacios

def main():
    print("=" * 60)
    print("🧹 LIMPIEZA DEL PROYECTO")
    print("=" * 60)
    print()
    
    # Limpiar __pycache__
    print("1. Limpiando directorios __pycache__...")
    pycache = limpiar_pycache()
    print(f"   Total eliminados: {pycache}")
    print()
    
    # Limpiar .pyc
    print("2. Limpiando archivos .pyc...")
    pyc = limpiar_archivos_pyc()
    print(f"   Total eliminados: {pyc}")
    print()
    
    # Verificar __init__.py vacíos
    print("3. Verificando archivos __init__.py vacíos...")
    vacios = verificar_init_vacios()
    if vacios:
        print(f"   ⚠️ Encontrados {len(vacios)} archivos __init__.py vacíos:")
        for v in vacios:
            print(f"      - {v}")
        print()
        print("   💡 En Python 3.3+ estos archivos son opcionales.")
        print("   💡 Puedes eliminarlos manualmente si no los necesitas.")
    else:
        print("   ✅ No se encontraron archivos __init__.py vacíos")
    print()
    
    print("=" * 60)
    print("✅ LIMPIEZA COMPLETADA")
    print("=" * 60)

if __name__ == "__main__":
    main()