import logging
import requests as req
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.api.permissions import HasServiceAPIKey
from apps.api.models import WebhookSubscription
from apps.api.serializers.webhooks import WebhookSubscriptionSerializer

logger = logging.getLogger('api.webhooks')


class WebhookSubscriptionViewSet(viewsets.ModelViewSet):
    """HCM usa este endpoint para registrar/actualizar su suscripción de webhooks."""
    permission_classes = [HasServiceAPIKey]
    serializer_class = WebhookSubscriptionSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        return WebhookSubscription.objects.all()

    @action(detail=False, methods=['post'], url_path='test')
    def test_webhook(self, request):
        """Prueba de conectividad: envía evento de prueba a la URL indicada."""
        url_destino = request.data.get('url_destino')
        api_key = request.data.get('api_key_destino', '')

        if not url_destino:
            return Response(
                {'error': 'url_destino requerida'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from django.utils import timezone
            response = req.post(
                url_destino,
                json={
                    'evento': 'webhook.test',
                    'modelo': 'test',
                    'objeto_id': '0',
                    'timestamp': timezone.now().isoformat(),
                    'mensaje': 'Prueba de conectividad Nomiweb → HCM',
                },
                headers={
                    'Content-Type': 'application/json',
                    'X-Nomiweb-Event': 'webhook.test',
                    'X-Nomiweb-Signature': api_key,
                },
                timeout=5,
            )
            return Response({
                'status': 'ok',
                'http_status': response.status_code,
                'response': response.text[:200],
            })
        except Exception as e:
            logger.warning('Test webhook failed: %s', e)
            return Response(
                {'status': 'error', 'error': str(e)},
                status=status.HTTP_200_OK,
            )
