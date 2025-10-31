from django.shortcuts import render, redirect, get_object_or_404
from apps.components.decorators import  role_required
from apps.common.models  import Tipodenomina , Vacaciones ,Contratos, Anos,Crearnomina ,Nomina , Conceptosdenomina
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse
from apps.payroll.views.payroll.payroll_automatic_systems import calcular_vacaciones
from django.utils import timezone
from datetime import date
from django.http import JsonResponse


@login_required
@role_required('company', 'accountant')
def vacation_send_nomina(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    ahora = timezone.localtime(timezone.now())
    hoy = date.today()

    if request.method == 'POST':
        nueva_nomina = Crearnomina.objects.create(
            nombrenomina=f"Nomina Aut. Vacas - {ahora.strftime('%Y-%m-%d %H:%M:%S')}",
            fechainicial=hoy,
            fechafinal=hoy,
            fechapago=ahora.date(),
            tiponomina=Tipodenomina.objects.get(tipodenomina='Vacaciones'),
            mesacumular=ahora.month,
            anoacumular=Anos.objects.get(ano=ahora.year),
            estadonomina=True,
            diasnomina=1,
            id_empresa_id=idempresa,
        )

        # 🔹 Retornar un fragmento HTML/JS que cierre el modal y emita evento
        return HttpResponse(
            "<script>"
            "up.emit('nomina:created');"  # Dispara evento
            "up.dismiss();"               # Cierra el modal secundario
            "</script>"
        )

    return render(request, './companies/partials/vacation_send_nomina.html')


# @login_required
# @role_required('company', 'accountant')
# def vacation_send_nomina(request, id):
#     usuario = request.session.get('usuario', {})
#     idempresa = usuario['idempresa']

#     # 🚀 1️⃣ Si el método es GET: renderizamos el formulario (abrir modal)
#     if request.method == 'GET':
#         return render(request, 'companies/partials/vacation_send_nomina.html', {
#             'idempresa': idempresa,
#             'idvacation': id,
#         })

#     # 🚀 2️⃣ Si el método es POST: procesamos la creación y devolvemos headers Unpoly
#     if request.method == 'POST':
#         ahora = timezone.localtime(timezone.now())
#         hoy = date.today()
#         # Crea la nómina automática
#         nueva_nomina = Crearnomina.objects.create(
#             nombrenomina=f"Nomina Aut. Vacas - {ahora.strftime('%Y-%m-%d %H:%M:%S')}",
#             fechainicial=hoy,
#             fechafinal=hoy,
#             fechapago=ahora.date(),
#             tiponomina=Tipodenomina.objects.get(tipodenomina='Vacaciones'),
#             mesacumular=ahora.month,
#             anoacumular=Anos.objects.get(ano=ahora.year),
#             estadonomina=True,
#             diasnomina=1,
#             id_empresa_id=idempresa,
#         )

#         # ✅ IMPORTANTE:
#         # Unpoly no necesita JSON aquí. Necesita solo un 200 con headers personalizados
#         # para cerrar el modal y redirigir (sin causar el error de JSON inválido).
#         return HttpResponse(
#             '',  # <- cuerpo vacío, sin JSON
#             headers={
#                 'X-Up-Location': reverse('vacation_resumen', args=[id]),
#                 'X-Up-Message': 'Nómina creada correctamente.',
#                 'X-Up-Icon': 'success',
#             }
#         )

#     # 🚫 Si llega otro método (poco probable)
#     return HttpResponse(status=405)


















