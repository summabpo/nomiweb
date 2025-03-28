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
    #variables
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    form_errors = False
    

    if request.method == 'POST':
        form = LoansForm(request.POST, id_empresa=idempresa)
        if form.is_valid():
            
            print(form.cleaned_data)
            
            # Prestamos.objects.create(
            #     idcontrato=Contratos.objects.get(idcontrato=form.cleaned_data['contract']),
            #     valorprestamo=form.cleaned_data['loan_amount'],
            #     fechaprestamo=form.cleaned_data['loan_date'],
            #     cuotasprestamo=form.cleaned_data['installments_number'],
            #     valorcuota=form.cleaned_data['installment_value'],
            #     estadoprestamo = 1
            # )

            messages.success(request, 'Prestamo creado exitosamente')
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
        idcontrato__id_empresa=idempresa  # Filtrar por la empresa relacionada
    ).values(
        contract_id=F('idcontrato__idcontrato'),
        employee_document=F('idcontrato__idempleado__docidentidad'),
        employee_first_name=F('idcontrato__idempleado__pnombre'),
        employee_second_name=F('idcontrato__idempleado__snombre'),
        employee_first_last_name=F('idcontrato__idempleado__papellido'),
        employee_second_last_name=F('idcontrato__idempleado__sapellido'),
    ).annotate(
        loan_count=Count('idprestamo')
    ).order_by('idcontrato__idempleado__papellido')

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

    # Verificar si el usuario tiene el rol de 'employee'
    usuario = request.session.get('usuario', {})
    rol = usuario['rol']
    
    if rol == 'employee':
        employee_info = Contratos.objects.select_related('idempleado').filter(idempleado=pk).latest('-idcontrato')
    else:
        employee_info = Contratos.objects.select_related('idempleado').get(idcontrato=pk)
    
    contrato_id = employee_info.idcontrato
    
    
    full_name = f"{employee_info.idempleado.pnombre} {employee_info.idempleado.snombre} {employee_info.idempleado.papellido} {employee_info.idempleado.sapellido}"
    document_id = employee_info.idempleado.docidentidad
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

from django.http import JsonResponse

def api_detail_payroll_loan(request, pk=None):

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