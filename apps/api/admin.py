from django.contrib import admin
from apps.api.models import WebhookSubscription, WebhookLog


@admin.register(WebhookSubscription)
class WebhookSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'url_destino', 'activo', 'eventos_display', 'created_at']
    list_filter = ['activo']
    search_fields = ['nombre', 'url_destino']
    readonly_fields = ['id', 'created_at', 'updated_at']

    def eventos_display(self, obj):
        return ', '.join(obj.eventos) if obj.eventos else '—'
    eventos_display.short_description = 'Eventos'


@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    list_display = [
        'created_at', 'evento', 'modelo',
        'objeto_id', 'status', 'http_status', 'intentos',
    ]
    list_filter = ['status', 'evento', 'modelo']
    search_fields = ['objeto_id', 'evento']
    readonly_fields = [
        'id', 'subscription', 'evento', 'modelo', 'objeto_id',
        'payload', 'status', 'http_status', 'response_body',
        'intentos', 'created_at', 'sent_at',
    ]
    ordering = ['-created_at']

    def has_add_permission(self, request):
        return False
