from rest_framework import viewsets, mixins
from apps.api.permissions import HasServiceAPIKey
from apps.api.pagination import NomiwebPagination
from apps.api.serializers.empresa import EmpresaSerializer
from apps.common.models import Empresa


class EmpresaViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Solo lectura. HCM consume este endpoint para sync de tenants."""
    permission_classes = [HasServiceAPIKey]
    serializer_class = EmpresaSerializer
    pagination_class = NomiwebPagination

    def get_queryset(self):
        return Empresa.objects.select_related(
            'idciudad', 'arl', 'banco', 'pais',
        ).order_by('idempresa')
