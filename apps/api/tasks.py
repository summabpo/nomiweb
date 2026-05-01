# Celery no está instalado en Nomiweb — envío síncrono.
# Si en el futuro se agrega Celery, reemplazar este archivo
# con la versión @shared_task.

def enviar_webhook_task(subscription_id, evento, modelo, objeto_id, datos_extra=None):
    from apps.api.webhook_service import enviar_webhook
    enviar_webhook(subscription_id, evento, modelo, objeto_id, datos_extra)

enviar_webhook_task.delay = enviar_webhook_task
