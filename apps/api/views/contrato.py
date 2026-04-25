from rest_framework import viewsets, mixins
from apps.api.permissions import HasServiceAPIKey
from apps.api.pagination import NomiwebPagination
from apps.api.serializers.contrato import ContratosSerializer
from apps.common.models import Contratos


class ContratosViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    """Lectura y escritura. HCM puede crear/actualizar contratos."""
    permission_classes = [HasServiceAPIKey]
    serializer_class = ContratosSerializer
    pagination_class = NomiwebPagination
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_queryset(self):
        qs = Contratos.objects.select_related(
            'idempleado',
            'cargo',
            'tipocontrato',
            'tiponomina',
            'bancocuenta',
            'centrotrabajo',
            'ciudadcontratacion',
            'tiposalario',
            'tipocotizante',
            'subtipocotizante',
            'codeps',
            'codafp',
            'codccf',
            'fondocesantias',
            'idcosto',
            'idsubcosto',
            'idsede',
            'id_empresa',
        )
        empleado_id = self.request.query_params.get('empleado')
        if empleado_id:
            qs = qs.filter(idempleado=empleado_id)
        empresa_id = self.request.query_params.get('empresa')
        if empresa_id:
            qs = qs.filter(id_empresa=empresa_id)
        return qs.order_by('idcontrato')
