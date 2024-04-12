from django.db import models
from django.contrib.auth.models import User


class Usuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    # ROLES = (
    #     ('administrador', 'Administrador'),
    #     ('gerente', 'Gerente'),
    #     ('miembro', 'Miembro'),
    # )
    rol = models.CharField(max_length=20)
    permisos = models.CharField(max_length=20)
