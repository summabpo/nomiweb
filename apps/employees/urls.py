from django.urls import path
from . import views
from apps.employees.views.certificaciones_laborales import vista_certificaciones
from apps.employees.views.comprobantes_nomina import ListaConceptosNomina, ListaNominas, genera_comprobante
from apps.employees.prueba import startemployees ,descargar_recibo
from apps.employees.views import index

urlpatterns = [
    path( 
        'emp/certificaciones_laborales',
        views.certificaciones_laborales.vista_certificaciones,
        name='certificaciones'
    ),
    path(
        'genera-certificaciones/<int:idcert>/',
        views.certificaciones_laborales.genera_certificaciones,
        name='genera-certificaciones'
    ),
    path(
        'emp/comprobantes',
        views.comprobantes_nomina.ListaNominas.as_view(),
        name='comprobantes_all'
    ),
    path(
        'recibo/',
        views.comprobantes_nomina.ListaConceptosNomina.as_view(),
        name='detalle_all'
    ),
    path(
        'genera-comprobante',
        views.comprobantes_nomina.genera_comprobante,
        name='genera-comprobante'
    ),
    path(
        'genera-comprobante/<int:idnomina>/<int:idcontrato>/',
        views.comprobantes_nomina.genera_comprobante,
        name='genera-comprobante'
    ),
    
    path(
        'employees/',
        index.index_employees,
        name='index_employees'
    ),
    
    path('descargar-recibo/', descargar_recibo, name='descargar_recibo')
]