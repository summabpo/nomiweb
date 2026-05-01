from rest_framework import serializers
from apps.api.models import WebhookSubscription


class WebhookSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookSubscription
        fields = [
            'id', 'nombre', 'url_destino', 'api_key_destino',
            'eventos', 'activo', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'api_key_destino': {'write_only': True},
        }
