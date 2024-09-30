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
from apps.components.humani import format_value


def loans(request):
  # Obtener los datos de la tabla Prestamos
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
      'estadoprestamo',
      'idprestamo',
  ).order_by('-idprestamo')

  # Aplicar format_value a los campos deseados
  prestamos_formateados = []
  for prestamo in prestamos:
    prestamo['valorprestamo'] = format_value(prestamo['valorprestamo'])
    prestamo['valorcuota'] = format_value(prestamo['valorcuota'])
    prestamo['saldoprestamo'] = format_value(prestamo['saldoprestamo'])
    prestamos_formateados.append(prestamo)

# Ahora `prestamos_formateados` contiene los datos con los valores formateados

    
  form1 = LoansForm()
  form2 = LoansForm(dropdown_parent='#kt_modal_2')
  
  
  errors = False
  if request.method == 'POST':
    form1 = LoansForm(request.POST)
    if form1.is_valid():
      # Procesar los datos del formulario aquí
      loan_amount = form1.cleaned_data['loan_amount']
      loan_date = form1.cleaned_data['loan_date']
      installment_value = form1.cleaned_data['installment_value']
      loan_status = form1.cleaned_data['loan_status']
      contract = form1.cleaned_data['contract']
      
      
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
                    'prestamos' :prestamos_formateados,  
                    'form1' :form1,
                    'form2' :form2,
                    'errors' : errors,
                  })
global_id = None 
    

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

  if request.method == 'POST':
    contract_id = request.POST.get('contract')
    loan_amount_str = request.POST.get('loan_amount')
    loan_date_str = request.POST.get('loan_date')
    loan_status_str = request.POST.get('loan_status')
    installment_value_str = request.POST.get('installment_value')
    
    loan_amount = float(loan_amount_str)
    installment_value = float(installment_value_str)
    
    if loan_amount <= 0 or installment_value <= 0:
        raise ValueError("El monto del préstamo y el valor de la cuota deben ser mayores a 0.")
    
    # Validar y convertir la fecha
    if isinstance(loan_date_str, str):
        loan_date = datetime.strptime(loan_date_str, "%Y-%m-%d").date()
    else:
        raise ValueError("La fecha del préstamo debe ser una cadena en formato YYYY-MM-DD.")
    if loan_status_str in ['on', None]:
      loan_status = True
    elif loan_status_str in ['off']:
      loan_status = False
    
    contrato = get_object_or_404(Contratos, idcontrato=contract_id)
    empleado = get_object_or_404(Contratosemp, idempleado=contrato.idempleado.idempleado)
    prestamo_modificar = get_object_or_404(Prestamos, pk=global_id)
    
    # Actualizar el préstamo
    prestamo_modificar.idcontrato = contrato
    prestamo_modificar.idempleado = empleado
    prestamo_modificar.valorprestamo = loan_amount
    prestamo_modificar.fechaprestamo = loan_date
    prestamo_modificar.cuotasprestamo = int(loan_amount / installment_value)
    prestamo_modificar.valorcuota = installment_value
    prestamo_modificar.saldoprestamo = loan_amount
    prestamo_modificar.estadoprestamo = not loan_status
    
    prestamo_modificar.save()
  
    messages.success(request, 'Se ha realizado la actualización del registro éxito.')
    return redirect('companies:loans')
  # Si el método no es GET ni POST, retornamos un error
  return JsonResponse({'message': 'Metodo no permitido', 'status': 'error'}, status=405)

    
    
    
    
    
    
    
    
    
    