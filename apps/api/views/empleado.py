from rest_framework import viewsets, mixins
from apps.api.permissions import HasServiceAPIKey
from apps.api.pagination import NomiwebPagination
from apps.api.serializers.empleado import ContratosempSerializer
from apps.common.models import Contratosemp


class ContratosempViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    """Lectura y escritura. HCM puede crear/actualizar empleados."""
    permission_classes = [HasServiceAPIKey]
    serializer_class = ContratosempSerializer
    pagination_class = NomiwebPagination
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_queryset(self):
        qs = Contratosemp.objects.select_related(
            'tipodocident',
            'ciudadnacimiento',
            'ciudadresidencia',
            'ciudadexpedicion',
            'paisnacimiento',
            'paisresidencia',
            'id_empresa',
        )
        empresa_id = self.request.query_params.get('empresa')
        if empresa_id:
            qs = qs.filter(id_empresa=empresa_id)
        return qs.order_by('idempleado')
