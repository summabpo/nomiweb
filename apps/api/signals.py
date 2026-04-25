import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.common.models import (
    Contratosemp, Contratos, Crearnomina, Vacaciones, Liquidacion,
)
from apps.api.webhook_service import disparar_webhooks

logger = logging.getLogger('api.webhooks')


@receiver(post_save, sender=Contratosemp)
def empleado_signal(sender, instance, created, **kwargs):
    try:
        evento = 'employee.created' if created else 'employee.updated'
        disparar_webhooks(
            evento=evento,
            modelo='empleado',
            objeto_id=instance.idempleado,
            datos_extra={'empresa_id': instance.id_empresa_id},
        )
    except Exception as e:
        logger.error('Signal empleado error: %s', e)


@receiver(post_save, sender=Contratos)
def contrato_signal(sender, instance, created, **kwargs):
    try:
        evento = 'contract.created' if created else 'contract.updated'
        disparar_webhooks(
            evento=evento,
            modelo='contrato',
            objeto_id=instance.idcontrato,
            datos_extra={
                'empleado_id': instance.idempleado_id,
                'empresa_id': instance.id_empresa_id,
            },
        )
    except Exception as e:
        logger.error('Signal contrato error: %s', e)


@receiver(post_save, sender=Crearnomina)
def nomina_signal(sender, instance, created, **kwargs):
    try:
        evento = 'nomina.created' if created else 'nomina.updated'
        disparar_webhooks(
            evento=evento,
            modelo='nomina',
            objeto_id=instance.idnomina,
            datos_extra={
                'empresa_id': instance.id_empresa_id,
                'estado': instance.estadonomina,
            },
        )
    except Exception as e:
        logger.error('Signal nomina error: %s', e)


@receiver(post_save, sender=Vacaciones)
def vacacion_signal(sender, instance, created, **kwargs):
    if not created:
        return
    try:
        disparar_webhooks(
            evento='vacacion.created',
            modelo='vacacion',
            objeto_id=instance.idvacaciones,
            datos_extra={'contrato_id': instance.idcontrato_id},
        )
    except Exception as e:
        logger.error('Signal vacacion error: %s', e)


@receiver(post_save, sender=Liquidacion)
def liquidacion_signal(sender, instance, created, **kwargs):
    if not created:
        return
    try:
        disparar_webhooks(
            evento='liquidacion.created',
            modelo='liquidacion',
            objeto_id=instance.idliquidacion,
            datos_extra={'contrato_id': instance.idcontrato_id},
        )
    except Exception as e:
        logger.error('Signal liquidacion error: %s', e)
