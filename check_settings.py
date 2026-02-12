#!/usr/bin/env python
"""Verificar qué settings se está usando"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nomiweb.settings')

try:
    from django.conf import settings
    print(f"Settings module: {settings.SETTINGS_ENV}")
    print(f"INSTALLED_APPS tiene 'apps.pila': {'apps.pila' in settings.INSTALLED_APPS}")
    print(f"Total de apps: {len(settings.INSTALLED_APPS)}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
