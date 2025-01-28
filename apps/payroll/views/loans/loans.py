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
        print('AQUI VOY POR AQUI')
        if form.is_valid():
            print('y POR AQUI')
            print(form.cleaned_data['loan_date'])
            print(form.cleaned_data['contract'])
            print(form.cleaned_data['loan_amount'])
            print(form.cleaned_data['installment_value'])
            Prestamos.objects.create(
                idcontrato=Contratos.objects.get(idcontrato=form.cleaned_data['contract']),
                valorprestamo=form.cleaned_data['loan_amount'],
                fechaprestamo=form.cleaned_data['loan_date'],
                cuotasprestamo=form.cleaned_data['installments_number'],
                valorcuota=form.cleaned_data['installment_value'],
                estadoprestamo = 1
            )

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

# view detail electronic payroll container
@login_required
@role_required('accountant', 'company')
def detail_employee_loans(request, pk=None):
    employee_info = Contratos.objects.select_related('idempleado').get(idcontrato=pk)
    full_name = f"{employee_info.idempleado.pnombre} {employee_info.idempleado.snombre} {employee_info.idempleado.papellido} {employee_info.idempleado.sapellido}"
    document_id = employee_info.idempleado.docidentidad
    # position = employee_info.idempleado.cargo
    loans_detail = Prestamos.objects.filter(idcontrato=pk).order_by('-idprestamo')
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

    payroll_loans = Nomina.objects.select_related(
        'idnomina'
    ).values(
        'idnomina__idnomina',
        'idnomina__fechapago',
        'valor',
    ).filter(
        idconcepto = 35, control=pk
    ).order_by('idnomina__fechapago')
    
    loans_data = payroll_loans.values(
        'idnomina__idnomina',
        'idnomina__fechapago',
        'valor',
    )

    return JsonResponse(list(loans_data), safe=False)