from django.urls import path
from . import views
from apps.employees.views import (
    certificaciones_laborales,
    vacation_history,
    vacation_request,
    comprobantes_nomina,
    index,
    edituser,
    newpassword
)
from apps.employees.views.viewdian import viewdian

urlpatterns = [
    # Certificaciones Laborales
    path('Certificate/labor', certificaciones_laborales.vista_certificaciones, name='certificaciones'),
    path('Certificate/labor/download/<int:idcert>/', certificaciones_laborales.certificatedownload, name='certificatedownload'),
    path('Certificate/labor/download/create/', certificaciones_laborales.generateworkcertificate, name='generateworkcertificate'),

    # Comprobantes de Nómina
    path('vouchers/payroll/', comprobantes_nomina.listaNomina, name='comprobantes_all'),
    path('recibo/', comprobantes_nomina.ListaConceptosNomina.as_view(), name='detalle_all'),
    path('genera/comprobante/', comprobantes_nomina.genera_comprobante, name='genera-comprobante'),
    path('genera/comprobante/<int:idnomina>/<int:idcontrato>/', comprobantes_nomina.genera_comprobante, name='genera-comprobante_detail'),

    # Empleados
    path('employees/', index.index_employees, name='index_employees'),

    # Vacaciones
    path('vacation/history/', vacation_history.vacationHistori, name='vacation_list'),
    path('vacation/request/', vacation_request.vacation_request_function, name='form_vac'),

    # DIAN
    path('Certificate/DIAN/', viewdian.viewdian, name='viewdian'),
    path('Certificate/DIAN/download/<str:idingret>/', viewdian.viewdian_empleado, name='viewdiandownload'),

    # Usuario
    path('user/', edituser.user_employees, name='user'),
    path('edit/user/', edituser.edit_user_employees, name='edituser'),

    # Generación de Certificados de Nómina
    path('Certificate/payroll/<str:idnomina>/<str:idcontrato>/', comprobantes_nomina.generatepayrollcertificate, name='generatepayrollcertificate'),

    # Cambiar Contraseña
    path('user/new/password/', newpassword.newpassword_employees, name='newpassword'),

    # AJAX
    path('ajax/my_get_view/', vacation_request.my_get_view, name='my_get_view'),
]
