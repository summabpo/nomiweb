from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import threading
import time


class Usuario(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    ROLES = (
        ('administrator', 'Administrator'),
        ('employee', 'Employee'),
        ('accountant', 'Accountant'),
        ('entrepreneur', 'Entrepreneur'),
    )
    
    role = models.CharField(max_length=20, choices=ROLES)
    company = models.ForeignKey('Empresa', on_delete=models.CASCADE )
    permission = models.CharField(max_length=100)
    id_empleado = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'login_usuario'
        
    @staticmethod
    def filter_by_username(username):
        return Usuario.objects.get(user__username=username)
        
    
    
class Empresa(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    db_name = models.CharField(max_length=100)
    
    class Meta:
        managed = False
        db_table = 'login_empresa'
        
    def __str__(self):
        return f"{self.db_name}"
    
class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token_temporal = models.CharField(max_length=100)
    tiempo_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)
    
    class Meta:
        managed = False
        db_table = 'token'

@receiver(post_save, sender=Token)
def eliminar_objeto_despues_dos_horas(sender, instance, **kwargs):
    def eliminar():
        time.sleep(1200)
        instance.estado = False
        instance.save()

    threading.Thread(target=eliminar).start()
    