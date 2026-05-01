from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from apps.api.permissions import HasServiceAPIKey
from apps.api.pagination import NomiwebPagination
from apps.api.serializers.nomina import (
    CrearnominaSerializer, VacacionesSerializer, LiquidacionSerializer,
)
from apps.common.models import Crearnomina, Vacaciones, Liquidacion


class CrearnominaViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Lista nóminas por empresa. HCM muestra listado con botones de descarga PDF."""
    permission_classes = [HasServiceAPIKey]
    serializer_class = CrearnominaSerializer
    pagination_class = NomiwebPagination

    def get_queryset(self):
        qs = Crearnomina.objects.select_related(
            'tiponomina', 'anoacumular', 'id_empresa',
        ).order_by('-fechainicial')

        empresa_id = self.request.query_params.get('empresa')
        if empresa_id:
            qs = qs.filter(id_empresa=empresa_id)

        estado = self.request.query_params.get('estado')
        if estado is not None:
            qs = qs.filter(estadonomina=(estado.lower() == 'true'))

        anio = self.request.query_params.get('anio')
        if anio:
            qs = qs.filter(fechainicial__year=anio)

        return qs

    @action(detail=True, methods=['get'], url_path='comprobantes-pdf')
    def comprobantes_pdf(self, request, pk=None):
        """
        Devuelve la URL interna de Nomiweb para descargar el PDF masivo de comprobantes.
        HCM usa Estrategia B: redirect a la URL interna (requiere sesión activa en Nomiweb).
        Para Estrategia A (proxy server-side) se debe agregar idcontrato como query param.
        """
        nomina = self.get_object()
        return Response({
            'nomina_id': nomina.idnomina,
            'nombre': nomina.nombrenomina,
            'pdf_url': f'/companies/payroll/sheet/download/{nomina.idnomina}/0/0',
            'pdf_url_por_contrato': f'/companies/payroll/sheet/download/{nomina.idnomina}/{{idcontrato}}/0',
            'message': (
                'Usar pdf_url_por_contrato reemplazando {idcontrato} para un empleado específico. '
                'Requiere sesión activa en Nomiweb (Estrategia B).'
            ),
        })

    @action(detail=True, methods=['get'], url_path='resumen-pdf')
    def resumen_pdf(self, request, pk=None):
        """
        Devuelve la URL interna de Nomiweb para descargar el PDF de resumen de nómina.
        URL: /companies/payroll/summary/download/{idnomina}/0
        """
        nomina = self.get_object()
        return Response({
            'nomina_id': nomina.idnomina,
            'nombre': nomina.nombrenomina,
            'pdf_url': f'/companies/payroll/summary/download/{nomina.idnomina}/0',
            'message': (
                'Usar pdf_url para descargar el resumen de nómina. '
                'Requiere sesión activa en Nomiweb (Estrategia B).'
            ),
        })


class VacacionesViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Lista vacaciones por contrato o por empleado."""
    permission_classes = [HasServiceAPIKey]
    serializer_class = VacacionesSerializer
    pagination_class = NomiwebPagination

    def get_queryset(self):
        qs = Vacaciones.objects.select_related(
            'idcontrato', 'idcontrato__idempleado', 'tipovac',
        ).order_by('-fechainicialvac')

        contrato_id = self.request.query_params.get('contrato')
        if contrato_id:
            qs = qs.filter(idcontrato=contrato_id)

        empleado_id = self.request.query_params.get('empleado')
        if empleado_id:
            qs = qs.filter(idcontrato__idempleado=empleado_id)

        return qs


class LiquidacionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Lista liquidaciones por contrato o por empleado. Solo lectura."""
    permission_classes = [HasServiceAPIKey]
    serializer_class = LiquidacionSerializer
    pagination_class = NomiwebPagination

    def get_queryset(self):
        qs = Liquidacion.objects.select_related(
            'idcontrato', 'idcontrato__idempleado',
        ).order_by('-fechafincontrato')

        contrato_id = self.request.query_params.get('contrato')
        if contrato_id:
            qs = qs.filter(idcontrato=contrato_id)

        empleado_id = self.request.query_params.get('empleado')
        if empleado_id:
            qs = qs.filter(idcontrato__idempleado=empleado_id)

        estado = self.request.query_params.get('estado')
        if estado:
            qs = qs.filter(estadoliquidacion=estado)

        return qs
