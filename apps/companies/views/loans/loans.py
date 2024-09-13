from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.components.filterform import FilterForm 
from apps.components.decorators import  role_required
from apps.companies.models import Prestamos,Contratosemp,Contratos 
from apps.companies.forms.loansForm import LoansForm
from datetime import datetime


def loans(request):
    prestamos = Prestamos.objects.values(
      'idcontrato__idcontrato',
      'idempleado__docidentidad',
      'idempleado__pnombre',
      'idempleado__snombre',
      'idempleado__papellido',
      'idempleado__sapellido',
      'fechaprestamo',
      'valorprestamo',
      'valorcuota',
      )
    
    form = LoansForm()
    
    
    errors = False
    if request.method == 'POST':
      form = LoansForm(request.POST)
      if form.is_valid():
        # Procesar los datos del formulario aquí
        loan_amount = form.cleaned_data['loan_amount']
        loan_date = form.cleaned_data['loan_date']
        installment_value = form.cleaned_data['installment_value']
        loan_status = form.cleaned_data['loan_status']
        contract = form.cleaned_data['contract']
        
        contrato = Contratos.objects.get(idcontrato = contract)
        empleado = Contratosemp.objects.get(idempleado = contrato.idempleado.idempleado)
        
        nuevo_prestamo = Prestamos(
          idempleado= empleado,
          idcontrato = contrato,
          valorprestamo = loan_amount,
          fechaprestamo = datetime.strptime(loan_date, "%Y-%m-%d"),
          valorcuota = installment_value ,
          cuotasprestamo = int(loan_amount/installment_value),
        )
        nuevo_prestamo.save()
        errors = False
        messages.success(request, 'La Incapacidad ha sido añadido con éxito.')
        return redirect('companies:loans')
      else:
        errors = True
    
    
    return render (request, './companies/loans.html',
                    {
                      'prestamos' :prestamos,  
                      'form' :form,
                      'errors' : errors,
                    })