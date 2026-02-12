#!/usr/bin/env python
"""Debug para ver cómo Django descubre comandos"""
import os
import sys
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nomiweb.settings')

import django
django.setup()

from django.conf import settings

print("=" * 70)
print("DEBUG: Descubrimiento de comandos de Django")
print("=" * 70)

# Verificar INSTALLED_APPS
print("\n[1] Verificando INSTALLED_APPS...")
if 'apps.pila' in settings.INSTALLED_APPS:
    print("  ✓ 'apps.pila' está en INSTALLED_APPS")
else:
    print("  ✗ 'apps.pila' NO está en INSTALLED_APPS")
    print(f"  Apps instaladas relacionadas con 'pila':")
    for app in settings.INSTALLED_APPS:
        if 'pila' in app.lower():
            print(f"    - {app}")

# Intentar el método de discovery de Django
print("\n[2] Intentando descubrir comandos manualmente...")
try:
    from django.core.management import find_commands
    import importlib
    
    # Simular cómo Django busca comandos
    app_module = importlib.import_module('apps.pila')
    app_path = app_module.__path__[0]
    command_dir = os.path.join(app_path, 'management', 'commands')
    
    print(f"  Ruta del comando: {command_dir}")
    print(f"  Existe el directorio: {os.path.exists(command_dir)}")
    
    if os.path.exists(command_dir):
        commands = find_commands(command_dir)
        print(f"  Comandos encontrados: {commands}")
        
        if 'probar_pila_payload' in commands:
            print("  ✓ 'probar_pila_payload' encontrado en el directorio")
        else:
            print("  ✗ 'probar_pila_payload' NO encontrado")
            print(f"    Archivos en el directorio: {os.listdir(command_dir)}")
            
except Exception as e:
    print(f"  ✗ Error: {e}")
    traceback.print_exc()

# Intentar importar el comando como Django lo haría
print("\n[3] Intentando importar el comando como Django...")
try:
    from django.utils.module_loading import import_string
    command_path = 'apps.pila.management.commands.probar_pila_payload.Command'
    command_class = import_string(command_path)
    print(f"  ✓ Comando importado: {command_class}")
    print(f"  ✓ Help: {command_class.help}")
except Exception as e:
    print(f"  ✗ Error al importar: {e}")
    traceback.print_exc()

# Verificar si Django lo registra
print("\n[4] Verificando registro de comandos...")
try:
    from django.core.management import get_commands, load_command_class
    
    # Intentar cargar el comando directamente
    try:
        cmd = load_command_class('apps.pila', 'probar_pila_payload')
        print(f"  ✓ Comando cargado con load_command_class: {cmd}")
    except Exception as e:
        print(f"  ✗ Error con load_command_class: {e}")
        traceback.print_exc()
    
    # Verificar comandos registrados
    all_commands = get_commands()
    if 'probar_pila_payload' in all_commands:
        print(f"  ✓ 'probar_pila_payload' está registrado")
    else:
        print("  ✗ 'probar_pila_payload' NO está registrado")
        
except Exception as e:
    print(f"  ✗ Error: {e}")
    traceback.print_exc()

print("\n" + "=" * 70)
