from django.urls import path
from . import views
from apps.employees.views.certificaciones_laborales import vista_certificaciones
from apps.employees.views.vacation_history import VacationList
from apps.employees.views.vacation_list import VacationListAll
from .views.vacation_request import vacation_request_function
from apps.employees.views.comprobantes_nomina import ListaConceptosNomina, ListaNominas, genera_comprobante
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

    path(
        'vacation_history',
        views.vacation_history.VacationList.as_view(),
        name='vacation_list'
    ),

    path(
        'vacation_request/',
        views.vacation_request.vacation_request_function,
        name='form_vac',
    ),
    
    path('vacation_list/', 
         VacationListAll.as_view(), 
         name='vacation_list_all'),
]