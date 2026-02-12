#!/usr/bin/env python
"""Verificar INSTALLED_APPS"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nomiweb.settings')

import django
django.setup()

from django.conf import settings

print("INSTALLED_APPS:")
for app in settings.INSTALLED_APPS:
    if 'pila' in app.lower():
        print(f"  ✓ {app}")

if 'apps.pila' in settings.INSTALLED_APPS:
    print("\n✓ 'apps.pila' está en INSTALLED_APPS")
else:
    print("\n✗ 'apps.pila' NO está en INSTALLED_APPS")
    print("\nTodas las apps instaladas:")
    for app in settings.INSTALLED_APPS:
        print(f"  - {app}")
