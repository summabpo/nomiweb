from django.db import models
from django.contrib.auth.models import User

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
    
    class Meta:
        managed = False
        db_table = 'login_usuario'
        
    
    
class Empresa(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    db_name = models.CharField(max_length=100)
    
    class Meta:
        managed = False
        db_table = 'login_empresa'
        
    def __str__(self):
        return f"{self.name}"
