from django.urls import path
from . import views
from apps.employees.views import certificaciones_laborales
from apps.employees.views.vacation_history import VacationList
from apps.employees.views.vacation_request import vacation_request_function, vacation_detail_modal
from apps.employees.views.comprobantes_nomina import ListaConceptosNomina, ListaNominas, genera_comprobante ,listaNomina 
from apps.employees.views import index
from apps.employees.views.viewdian import viewdian
from apps.employees.views import edituser
from apps.employees.views import comprobantes_nomina
from apps.employees.views import newpassword


urlpatterns = [
    path('Certificate/labor',certificaciones_laborales.vista_certificaciones,name='certificaciones' ),
    path('Certificate/labor/download/<int:idcert>/', certificaciones_laborales.certificatedownload, name='certificatedownload' ),
    path('Certificate/labor/download/create/', certificaciones_laborales.generateworkcertificate,name='generateworkcertificate' ),
    # path(
    #     'genera-certificaciones/<int:idcert>/',
    #     views.certificaciones_laborales.genera_certificaciones,
    #     name='genera-certificaciones'
    # ),
    path(
        'vouchers/payroll/',
        views.comprobantes_nomina.listaNomina,
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
    
    path('vacation/modal/<int:pk>/',
        views.vacation_request.vacation_detail_modal,
        name='vacation_detail_modal'),
    
    path('Certificate/DIAN/',viewdian.viewdian,name='viewdian'),
    path('Certificate/DIAN/download/<str:idingret>',viewdian.viewdian_empleado,name='viewdiandownload'),
    
    path('user', edituser.user_employees, name='user' ),
    path('edit/user', edituser.edit_user_employees, name='edituser' ),
    path('Certificate/payroll/<str:idnomina>/<str:idcontrato>', comprobantes_nomina.generatepayrollcertificate, name='generatepayrollcertificate' ),
    path('user/new/password', newpassword.newpassword_employees, name='newpassword' ),
    
]