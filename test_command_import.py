#!/usr/bin/env python
"""Test para verificar si el comando se puede importar"""
import os
import sys
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nomiweb.settings')

try:
    import django
    django.setup()
    print("Django configurado correctamente")
    
    # Intentar importar el comando directamente
    print("\nIntentando importar el comando...")
    from apps.pila.management.commands.probar_pila_payload import Command
    print("✓ Comando importado correctamente!")
    print(f"  Help: {Command.help}")
    
    # Verificar si Django lo detecta
    print("\nVerificando si Django lo detecta...")
    from django.core.management import get_commands
    commands = get_commands()
    if 'probar_pila_payload' in commands:
        print("✓ Comando detectado por Django!")
    else:
        print("✗ Comando NO detectado por Django")
        print(f"  Comandos disponibles: {sorted(commands.keys())}")
        
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    print("\nTraceback completo:")
    traceback.print_exc()
