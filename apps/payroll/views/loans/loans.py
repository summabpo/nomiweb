import datetime
from django.shortcuts import redirect, render
import requests

from django.http import JsonResponse
from django.contrib import messages
from django.db.models import F, Q, Case, When, Value, CharField, Sum, Count

#models
from apps.common.models import Prestamos, Contratos, Nomina

#forms
from apps.payroll.forms.LoansForm import LoansForm

#
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required

# view employee loans
@login_required
@role_required('accountant', 'company')
def employee_loans(request):
    """
    Vista que permite a usuarios con rol 'accountant' o 'company' gestionar préstamos de empleados.

    Muestra un formulario para registrar nuevos préstamos y una lista agrupada por contrato que 
    resume cuántos préstamos tiene cada empleado. La vista valida y guarda los datos del formulario
    cuando se realiza un POST.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que puede incluir datos de formulario vía POST.

    Returns
    -------
    HttpResponse
        Renderiza la plantilla 'payroll/employee_loans.html' con el formulario y la lista de préstamos.

    See Also
    --------
    LoansForm : Formulario para registrar préstamos.
    Prestamos : Modelo que representa los préstamos de los empleados.
    Contratos : Relación entre empleados y la empresa.
    """

    #variables
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    form_errors = False

    if request.method == 'POST':
        form = LoansForm(request.POST, id_empresa=idempresa)
        if form.is_valid():
            Prestamos.objects.create(
                idcontrato=Contratos.objects.get(idcontrato=form.cleaned_data['contract']),
                valorprestamo=form.cleaned_data['loan_amount'],
                fechaprestamo=form.cleaned_data['loan_date'],
                cuotasprestamo=form.cleaned_data['installments_number'],
                valorcuota=form.cleaned_data['installment_value'],
                estadoprestamo=1
            )
            messages.success(request, 'Préstamo creado exitosamente')
            return redirect('payroll:loans_list')
        else:
            form_errors = True
            messages.error(request, 'Error al crear el préstamo')
    else:
        form = LoansForm(id_empresa=idempresa)

    # Agrupación por contrato con conteo de préstamos
    loans_list = Prestamos.objects.select_related(
        'idcontrato__idempleado'
    ).filter(
        idcontrato__id_empresa=idempresa, 
        estadoprestamo=1
    ).values(
        contract_id=F('idcontrato__idcontrato'),
        employee_document=F('idcontrato__idempleado__docidentidad'),
        employee_first_name=F('idcontrato__idempleado__pnombre'),
        employee_second_name=F('idcontrato__idempleado__snombre'),
        employee_first_last_name=F('idcontrato__idempleado__papellido'),
        employee_second_last_name=F('idcontrato__idempleado__sapellido'),
    ).annotate(
        loan_count=Count('idprestamo')
    ).order_by('-idprestamo')

    # Construcción del nombre completo limpio (sin "no data" ni None)
    for loan in loans_list:
        name_parts = [
            loan.get("employee_first_name"),
            loan.get("employee_second_name"),
            loan.get("employee_first_last_name"),
            loan.get("employee_second_last_name")
        ]
        # eliminar None, espacios vacíos y texto "no data"
        loan["full_name"] = " ".join([
            part.strip() for part in name_parts
            if part and part.strip().lower() != "no data"
        ])

    context = {
        'loans_list': loans_list,
        'form': form,
        'form_errors': form_errors,
    }

    return render(request, 'payroll/employee_loans.html', context)

# view loans detail employee
@login_required
@role_required('accountant', 'company', 'employee')
def detail_employee_loans(request, pk=None):
    """
    Vista que muestra el historial detallado de préstamos de un empleado específico.

    Se adapta dinámicamente según el rol del usuario autenticado: si es un empleado, se filtra 
    automáticamente el contrato más reciente. Para otros roles, se usa el contrato directamente 
    identificado por 'pk'.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP estándar.
    pk : int, optional
        Identificador del contrato o del empleado, dependiendo del rol del usuario.

    Returns
    -------
    HttpResponse
        Renderiza la plantilla 'payroll/detail_employee_loans.html' con información del empleado
        y sus préstamos detallados.

    See Also
    --------
    Prestamos : Modelo de préstamos asociados al contrato.
    Contratos : Modelo para obtener los datos del empleado asociado al préstamo.
    """
    # Verificar si el usuario tiene el rol de 'employee'
    usuario = request.session.get('usuario', {})
    rol = usuario['rol']

    if rol == 'employee':
        employee_info = Contratos.objects.select_related('idempleado').filter(idempleado=pk).latest('-idcontrato')
    else:
        employee_info = Contratos.objects.select_related('idempleado').get(idcontrato=pk)

    contrato_id = employee_info.idcontrato

    # Construcción del nombre completo sin "no data", None o vacíos
    name_parts = [
        employee_info.idempleado.pnombre,
        employee_info.idempleado.snombre,
        employee_info.idempleado.papellido,
        employee_info.idempleado.sapellido
    ]
    full_name = " ".join([
        part.strip() for part in name_parts
        if part and part.strip().lower() != "no data"
    ])

    # Documento limpio: si dice "no data", se deja vacío
    doc_id = employee_info.idempleado.docidentidad
    document_id = "" if not doc_id or str(doc_id).strip().lower() == "no data" else doc_id

    # position = employee_info.idempleado.cargo
    loans_detail = Prestamos.objects.filter(idcontrato=contrato_id).order_by('-idprestamo')

    context = {
        'employee_info': {
            'full_name': full_name,
            'document_id': document_id,
            # 'position': position,
        },
        'loans_detail': loans_detail
    }
    return render(request, 'payroll/detail_employee_loans.html', context)





def api_detail_payroll_loan(request, pk=None):
    """
    API que devuelve en formato JSON el detalle de pagos y deducciones de un préstamo específico.

    Esta vista calcula el saldo restante de un préstamo, restando las deducciones de nómina 
    asociadas al mismo. La información se devuelve en orden cronológico con fechas de pago, 
    valor deducido y saldo restante.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP estándar.
    pk : int, optional
        ID del préstamo a consultar.

    Returns
    -------
    JsonResponse
        Un objeto JSON que incluye el saldo inicial y una lista de deducciones con fechas y saldos.

    Raises
    ------
    Http404
        Si no se encuentra el préstamo con el ID dado.

    Example Response
    ----------------
    {
        "saldo_inicial": "$2,000,000",
        "detalles": [
            {
                "nomina_id": 45,
                "fecha_pago": "15/03/2024",
                "valor_deduccion": "$200,000",
                "saldo_restante": "$1,800,000"
            },
            ...
        ]
    }

    See Also
    --------
    Prestamos : Modelo que representa préstamos.
    Nomina : Modelo que representa movimientos de nómina (deducciones).
    """
    # Obtener el préstamo y su saldo inicial
    try:
        prestamo = Prestamos.objects.get(idprestamo=pk)
        saldo_inicial = prestamo.valorprestamo
    except Prestamos.DoesNotExist:
        return JsonResponse({"error": "Préstamo no encontrado"}, status=404)

    # Obtener deducciones de nómina relacionadas al préstamo
    deducciones = Nomina.objects.filter(
        idconcepto__codigo = 50,  # Asegúrate que este es el id correcto para "deducción de préstamo"
        control=pk
    ).order_by('idnomina__fechapago')  # Orden ascendente para cálculo progresivo
    
    # Preparar datos y calcular saldos
    detalles = []
    saldo_actual = saldo_inicial

    for deduccion in deducciones:
        monto_deduccion = abs(deduccion.valor)  # Asume que 'valor' es negativo
        saldo_actual -= monto_deduccion

        detalles.append({
            "nomina_id": deduccion.idnomina.idnomina,
            "fecha_pago": deduccion.idnomina.fechapago.strftime("%d/%m/%Y"),
            "valor_deduccion": f"${monto_deduccion:,.0f}",
            "saldo_restante": f"${saldo_actual:,.0f}",
        })

    return JsonResponse({
        "saldo_inicial": f"${saldo_inicial:,.0f}",
        "detalles": detalles,
    }, safe=False)