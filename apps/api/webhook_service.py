import logging
import requests
from django.utils import timezone

logger = logging.getLogger('api.webhooks')


def build_payload(evento, modelo, objeto_id, datos_extra=None):
    payload = {
        'evento': evento,
        'modelo': modelo,
        'objeto_id': str(objeto_id),
        'timestamp': timezone.now().isoformat(),
        'nomiweb_url': 'https://jes.nomiweb.com.co',
    }
    if datos_extra:
        payload.update(datos_extra)
    return payload


def enviar_webhook(subscription_id, evento, modelo, objeto_id, datos_extra=None):
    from apps.api.models import WebhookSubscription, WebhookLog

    try:
        subscription = WebhookSubscription.objects.get(id=subscription_id, activo=True)
    except WebhookSubscription.DoesNotExist:
        return

    payload = build_payload(evento, modelo, objeto_id, datos_extra)
    log = WebhookLog.objects.create(
        subscription=subscription,
        evento=evento,
        modelo=modelo,
        objeto_id=str(objeto_id),
        payload=payload,
        status='pending',
    )

    try:
        response = requests.post(
            subscription.url_destino,
            json=payload,
            headers={
                'Content-Type': 'application/json',
                'X-Nomiweb-Event': evento,
                'X-Nomiweb-Signature': subscription.api_key_destino,
            },
            timeout=10,
        )
        log.http_status = response.status_code
        log.response_body = response.text[:500]
        log.intentos += 1
        log.sent_at = timezone.now()

        if response.status_code < 400:
            log.status = 'success'
            logger.info(
                'Webhook enviado: %s %s#%s → %s [%s]',
                evento, modelo, objeto_id,
                subscription.url_destino, response.status_code,
            )
        else:
            log.status = 'failed'
            logger.warning(
                'Webhook fallido: %s %s#%s → HTTP %s',
                evento, modelo, objeto_id, response.status_code,
            )

    except requests.exceptions.Timeout:
        log.status = 'failed'
        log.response_body = 'Timeout after 10s'
        log.intentos += 1
        logger.error('Webhook timeout: %s → %s', evento, subscription.url_destino)

    except requests.exceptions.ConnectionError as e:
        log.status = 'failed'
        log.response_body = str(e)[:500]
        log.intentos += 1
        logger.error('Webhook connection error: %s', e)

    finally:
        log.save()


def disparar_webhooks(evento, modelo, objeto_id, datos_extra=None):
    """
    Punto de entrada. Silencioso si no hay suscripciones activas —
    sin queries extras si no hay webhooks configurados.
    """
    from apps.api.models import WebhookSubscription

    try:
        subscriptions = WebhookSubscription.objects.filter(
            activo=True,
            eventos__contains=evento,
        )
        if not subscriptions.exists():
            return

        for subscription in subscriptions:
            try:
                enviar_webhook(
                    str(subscription.id), evento,
                    modelo, objeto_id, datos_extra,
                )
            except Exception as e:
                # Nunca interrumpir el save original del modelo
                logger.error('Error al enviar webhook %s: %s', evento, e)

    except Exception as e:
        logger.error('Error en disparar_webhooks %s: %s', evento, e)
