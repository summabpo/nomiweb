from rest_framework.routers import DefaultRouter
from apps.api.views.empresa import EmpresaViewSet
from apps.api.views.empleado import ContratosempViewSet
from apps.api.views.contrato import ContratosViewSet
from apps.api.views.nomina import (
    CrearnominaViewSet, VacacionesViewSet, LiquidacionViewSet,
)
from apps.api.views.catalogs import (
    CiudadesViewSet, BancosViewSet, TipodocumentoViewSet,
    EntidadSegSocialViewSet, TipocontratoViewSet, TipodenominaViewSet,
    TiposalarioViewSet, TiposdecotizantesViewSet, SubtipocotizantesViewSet,
    TipoavacausViewSet, CargosViewSet, CostosViewSet, SedesViewSet,
    CentrotrabajoViewSet,
)

router = DefaultRouter()
router.register(r'empresas', EmpresaViewSet, basename='empresa')
router.register(r'empleados', ContratosempViewSet, basename='empleado')
router.register(r'contratos', ContratosViewSet, basename='contrato')
router.register(r'nominas', CrearnominaViewSet, basename='nomina')
router.register(r'vacaciones', VacacionesViewSet, basename='vacaciones')
router.register(r'liquidaciones', LiquidacionViewSet, basename='liquidacion')
router.register(r'ciudades', CiudadesViewSet, basename='ciudad')
router.register(r'bancos', BancosViewSet, basename='banco')
router.register(r'tipos-documento', TipodocumentoViewSet, basename='tipodoc')
router.register(r'entidades-seg-social', EntidadSegSocialViewSet, basename='segsocial')
router.register(r'tipos-contrato', TipocontratoViewSet, basename='tipocontrato')
router.register(r'tipos-nomina', TipodenominaViewSet, basename='tiponomina')
router.register(r'tipos-salario', TiposalarioViewSet, basename='tiposalario')
router.register(r'tipos-cotizante', TiposdecotizantesViewSet, basename='tipocotizante')
router.register(r'subtipos-cotizante', SubtipocotizantesViewSet, basename='subtipocotizante')
router.register(r'tipos-vacacion', TipoavacausViewSet, basename='tipovacacion')
router.register(r'cargos', CargosViewSet, basename='cargo')
router.register(r'costos', CostosViewSet, basename='costo')
router.register(r'sedes', SedesViewSet, basename='sede')
router.register(r'centros-trabajo', CentrotrabajoViewSet, basename='centrotrabajo')

urlpatterns = router.urls
