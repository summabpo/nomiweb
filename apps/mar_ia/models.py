from django.db import models
from django.conf import settings


class MarIaConsulta(models.Model):
    """
    Modelo para guardar todas las consultas y respuestas de MAR-IA
    Permite análisis de qué consultan los empleados
    """
    idconsulta = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mar_ia_consultas'
    )
    pregunta = models.TextField(max_length=500)
    respuesta = models.TextField()
    tokens_usados = models.IntegerField(default=0, null=True, blank=True)
    tipo_respuesta = models.CharField(
        max_length=20,
        choices=[
            ('directa', 'Respuesta Directa (sin IA)'),
            ('ia', 'Respuesta con IA'),
            ('error', 'Error'),
        ],
        default='ia'
    )
    error_tipo = models.CharField(max_length=50, null=True, blank=True)
    fecha_consulta = models.DateTimeField(auto_now_add=True)
    idcontrato = models.IntegerField(null=True, blank=True)  # Para análisis por contrato
    
    class Meta:
        managed = False  # Para que Django no gestione la tabla (ya existe en BD)
        db_table = 'mar_ia_consultas'
        verbose_name = 'Consulta MAR-IA'
        verbose_name_plural = 'Consultas MAR-IA'
        ordering = ['-fecha_consulta']
        indexes = [
            models.Index(fields=['user', '-fecha_consulta']),
            models.Index(fields=['tipo_respuesta', '-fecha_consulta']),
            models.Index(fields=['-fecha_consulta']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.pregunta[:50]}... ({self.fecha_consulta})"
