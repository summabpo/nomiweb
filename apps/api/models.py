from django.db import models
import uuid


class WebhookSubscription(models.Model):
    EVENTOS = [
        ('employee.created', 'Empleado creado'),
        ('employee.updated', 'Empleado actualizado'),
        ('contract.created', 'Contrato creado'),
        ('contract.updated', 'Contrato actualizado'),
        ('nomina.created', 'Nómina creada'),
        ('nomina.updated', 'Nómina actualizada'),
        ('vacacion.created', 'Vacación registrada'),
        ('liquidacion.created', 'Liquidación registrada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(
        max_length=100,
        help_text='Nombre identificador (ej: talent-hcm-dev)'
    )
    url_destino = models.URLField(
        help_text='URL de HCM que recibe el webhook. Ej: https://hcm.summa.co/api/v1/webhooks/receive/'
    )
    api_key_destino = models.CharField(
        max_length=200,
        help_text='API Key para autenticar el POST a HCM'
    )
    eventos = models.JSONField(
        default=list,
        help_text='Lista de eventos a notificar. Ej: ["employee.created", "contract.updated"]'
    )
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_webhook_subscription'
        verbose_name = 'Suscripción Webhook'
        verbose_name_plural = 'Suscripciones Webhook'

    def __str__(self):
        return f'{self.nombre} → {self.url_destino}'


class WebhookLog(models.Model):
    STATUS = [
        ('pending', 'Pendiente'),
        ('success', 'Enviado'),
        ('failed', 'Fallido'),
        ('retrying', 'Reintentando'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(
        WebhookSubscription,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    evento = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    objeto_id = models.CharField(max_length=50)
    payload = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    http_status = models.IntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    intentos = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'api_webhook_log'
        ordering = ['-created_at']
        verbose_name = 'Log Webhook'
        verbose_name_plural = 'Logs Webhook'
