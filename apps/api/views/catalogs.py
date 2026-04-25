from rest_framework import viewsets, mixins
from apps.api.permissions import HasServiceAPIKey
from apps.api.pagination import NomiwebPagination
from apps.api.serializers.catalogs import (
    CiudadSerializer, BancoSerializer, TipodocumentoSerializer,
    EntidadSegSocialSerializer, TipocontratoSerializer,
    TipodenominaSerializer, TiposalarioSerializer,
    TiposdecotizantesSerializer, SubtipocotizantesSerializer,
    TipoavacausSerializer, CargosSerializer, CostosSerializer,
    SedesSerializer, CentrotrabajoSerializer,
)
from apps.common.models import (
    Ciudades, Bancos, Tipodocumento, Entidadessegsocial,
    Tipocontrato, Tipodenomina, Tiposalario,
    Tiposdecotizantes, Subtipocotizantes, Tipoavacaus,
    Cargos, Costos, Sedes, Centrotrabajo,
)


class ReadOnlyViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = [HasServiceAPIKey]
    pagination_class = NomiwebPagination


class CiudadesViewSet(ReadOnlyViewSet):
    serializer_class = CiudadSerializer

    def get_queryset(self):
        qs = Ciudades.objects.all()
        departamento = self.request.query_params.get('departamento')
        if departamento:
            qs = qs.filter(departamento__icontains=departamento)
        return qs.order_by('ciudad')


class BancosViewSet(ReadOnlyViewSet):
    serializer_class = BancoSerializer
    queryset = Bancos.objects.all().order_by('nombanco')


class TipodocumentoViewSet(ReadOnlyViewSet):
    serializer_class = TipodocumentoSerializer
    queryset = Tipodocumento.objects.all().order_by('documento')


class EntidadSegSocialViewSet(ReadOnlyViewSet):
    serializer_class = EntidadSegSocialSerializer

    def get_queryset(self):
        qs = Entidadessegsocial.objects.all()
        tipo = self.request.query_params.get('tipo')
        if tipo:
            qs = qs.filter(tipoentidad__iexact=tipo)
        return qs.order_by('entidad')


class TipocontratoViewSet(ReadOnlyViewSet):
    serializer_class = TipocontratoSerializer
    queryset = Tipocontrato.objects.all().order_by('tipocontrato')


class TipodenominaViewSet(ReadOnlyViewSet):
    serializer_class = TipodenominaSerializer
    queryset = Tipodenomina.objects.all().order_by('tipodenomina')


class TiposalarioViewSet(ReadOnlyViewSet):
    serializer_class = TiposalarioSerializer
    queryset = Tiposalario.objects.all().order_by('tiposalario')


class TiposdecotizantesViewSet(ReadOnlyViewSet):
    serializer_class = TiposdecotizantesSerializer
    queryset = Tiposdecotizantes.objects.all().order_by('tipocotizante')


class SubtipocotizantesViewSet(ReadOnlyViewSet):
    serializer_class = SubtipocotizantesSerializer
    queryset = Subtipocotizantes.objects.all().order_by('subtipocotizante')


class TipoavacausViewSet(ReadOnlyViewSet):
    serializer_class = TipoavacausSerializer
    queryset = Tipoavacaus.objects.all().order_by('nombrevacaus')


class CargosViewSet(ReadOnlyViewSet):
    serializer_class = CargosSerializer

    def get_queryset(self):
        qs = Cargos.objects.select_related('id_empresa', 'nombrenivel')
        empresa_id = self.request.query_params.get('empresa')
        if empresa_id:
            qs = qs.filter(id_empresa=empresa_id)
        return qs.order_by('nombrecargo')


class CostosViewSet(ReadOnlyViewSet):
    serializer_class = CostosSerializer

    def get_queryset(self):
        qs = Costos.objects.select_related('id_empresa')
        empresa_id = self.request.query_params.get('empresa')
        if empresa_id:
            qs = qs.filter(id_empresa=empresa_id)
        return qs.order_by('nomcosto')


class SedesViewSet(ReadOnlyViewSet):
    serializer_class = SedesSerializer

    def get_queryset(self):
        qs = Sedes.objects.select_related('id_empresa')
        empresa_id = self.request.query_params.get('empresa')
        if empresa_id:
            qs = qs.filter(id_empresa=empresa_id)
        return qs.order_by('nombresede')


class CentrotrabajoViewSet(ReadOnlyViewSet):
    serializer_class = CentrotrabajoSerializer

    def get_queryset(self):
        qs = Centrotrabajo.objects.select_related('id_empresa')
        empresa_id = self.request.query_params.get('empresa')
        if empresa_id:
            qs = qs.filter(id_empresa=empresa_id)
        return qs.order_by('nombrecentrotrabajo')
