from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.components.filterform import FilterForm 
from apps.components.decorators import  role_required
from apps.companies.models import Prestamos,Contratosemp,Contratos 
from apps.companies.forms.loansForm import LoansForm
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


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
      'saldoprestamo',
      'idprestamo',
      )
    
    form1 = LoansForm()
    form2 = LoansForm(dropdown_parent='#kt_modal_2')
    
    
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
          saldoprestamo = loan_amount,
          cuotaspagadas = 0,
          estadoprestamo = not(loan_status),
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
                      'form1' :form1,
                      'form2' :form2,
                      'errors' : errors,
                    })
    
    

@csrf_exempt    
def edit_loans(request):
  global global_id
  
  if request.method == 'GET':
    dato = request.GET.get('dato')
    
    prestamo =  get_object_or_404(Prestamos, pk=dato)
    global_id = prestamo.idprestamo
    data ={ 
          'data': {
            "id":str(prestamo.idprestamo),
            "contract": prestamo.idcontrato.idcontrato,
            "loan_amount": prestamo.valorprestamo ,
            "loan_date": prestamo.fechaprestamo,
            "installment_value":prestamo.valorcuota,
            "loan_status":prestamo.estadoprestamo,

          },
          'status': 'success',
        }
    return JsonResponse(data)

  elif request.method == 'POST':
      data = json.loads(request.body.decode('utf-8'))
      
      
      contract = request.POST.get('contract')
      loan_amount = request.POST.get('loan_amount')
      loan_date = request.POST.get('loan_date')
      loan_status = request.POST.get('loan_status')
      installment_value = request.POST.get('installment_value')
      
      contrato = Contratos.objects.get(idcontrato = contract)
      empleado = Contratosemp.objects.get(idempleado = contrato.idempleado.idempleado)
      
      
      prestamo_modificar = get_object_or_404(Prestamos, pk= global_id )
      
      prestamo_modificar.idcontrato = contrato 
      prestamo_modificar.idempleado = empleado 
      prestamo_modificar.valorprestamo = loan_amount 
      prestamo_modificar.fechaprestamo = datetime.strptime(loan_date, "%Y-%m-%d"),
      prestamo_modificar.cuotasprestamo = int(loan_amount/installment_value)
      prestamo_modificar.valorcuota = installment_value 
      prestamo_modificar.saldoprestamo = loan_amount 
      prestamo_modificar.estadoprestamo = not(loan_status),
      
      prestamo_modificar.save()
      
      response_data = {
          'status': 'success'
      }
      
      return JsonResponse(response_data)
  
  # Si el método no es GET ni POST, retornamos un error
  return JsonResponse({'message': 'Método no permitido', 'status': 'error'}, status=405)

    
    
    
    
    
    
    
    
    
    