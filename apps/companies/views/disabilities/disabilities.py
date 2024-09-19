from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.components.filterform import FilterForm 
from apps.components.decorators import  role_required
from apps.companies.models import Incapacidades , Contratosemp ,Contratos,Entidadessegsocial ,Diagnosticosenfermedades
from apps.companies.forms.disabilitiesForm  import DisabilitiesForm
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json



def disabilities(request):
  errors = False
  incapacidades = Incapacidades.objects.values(
      'idcontrato__idcontrato',
      'idempleado__docidentidad',
      'idempleado__pnombre',
      'idempleado__snombre',
      'idempleado__papellido',
      'idempleado__sapellido',
      'entidad',
      'coddiagnostico__coddiagnostico',
      'diagnostico',
      'prorroga',
      'fechainicial',
      'dias',
      'idincapacidad'
  ).order_by('-idincapacidad')
  
  
  form1 = DisabilitiesForm()
  form2 = DisabilitiesForm(dropdown_parent='#kt_modal_2')
  
  if request.method == 'POST':
    form1 = DisabilitiesForm(request.POST)
    if form1.is_valid():
      # Procesa los datos del formulario
      contract = form1.cleaned_data['contract']
      entity = form1.cleaned_data['entity']
      origin = form1.cleaned_data['origin']
      initial_date = form1.cleaned_data['initial_date']
      incapacity_days = form1.cleaned_data['incapacity_days']
      diagnosis_code = form1.cleaned_data['diagnosis_code']
      extension = form1.cleaned_data['extension']
      end_date = form1.cleaned_data['end_date']
      previous_month_ibc = form1.cleaned_data['previous_month_ibc']
      
      
      contrato = Contratos.objects.get(idcontrato = contract)
      empleado = Contratosemp.objects.get(idempleado = contrato.idempleado.idempleado)
      entidad = Entidadessegsocial.objects.get(codigo = entity)
      dianostico = Diagnosticosenfermedades.objects.get(coddiagnostico = diagnosis_code)
      
      
      new_incapacity = Incapacidades(
        empleado = f"{empleado.papellido} {empleado.sapellido} {empleado.snombre} {empleado.pnombre} - {empleado.snombre}" , 
        tipoentidad = entidad.tipoentidad, 
        entidad = entidad.entidad,
        coddiagnostico = dianostico,
        diagnostico =  dianostico.diagnostico,
        fechainicial = datetime.strptime(initial_date, "%Y-%m-%d"),
        dias = int (incapacity_days),
        idempleado= empleado,
        idcontrato = contrato,
        prorroga =  extension ,
        ibc = previous_month_ibc,
        finincap =  datetime.strptime(end_date, "%Y-%m-%d"),
      )
      new_incapacity.save()  
      errors = False
      messages.success(request, 'La Incapacidad ha sido añadido con éxito.')
      return redirect('companies:disabilities')
    else:
      errors = True
    

  return render (request, './companies/disabilities.html',
                  {
                    'incapacidades' :incapacidades,  
                    'form1' :form1,
                    'form2' :form2,
                    'errors':errors,
                  })
  
  
global_id = None 

@csrf_exempt
def edit_disabilities(request):
  global global_id
  
  if request.method == 'GET':
    dato = request.GET.get('dato')

    incapacidad =  get_object_or_404(Incapacidades, pk=dato)
    entidad = Entidadessegsocial.objects.get(entidad = incapacidad.entidad , tipoentidad = incapacidad.tipoentidad )
    global_id = incapacidad.idincapacidad
    data ={ 
          'data': {
            
            "contract": incapacidad.idcontrato.idcontrato,
            "entity": entidad.codigo ,
            "initial_date": incapacidad.fechainicial,
            "id":str(incapacidad.idincapacidad),
            "diagnosis_code":incapacidad.coddiagnostico.coddiagnostico,
            "incapacity_days":incapacidad.dias,
            "extension": incapacidad.prorroga,
            "previous_month_ibc":incapacidad.ibc,
            "end_date": incapacidad.finincap ,
          },
          'status': 'success',
        }
    return JsonResponse(data)

  elif request.method == 'POST':
    
    
    contract = request.POST.get('contract')
    entity = request.POST.get('entity')
    origin = request.POST.get('origin')
    initial_date = request.POST.get('initial_date')
    incapacity_days = request.POST.get('incapacity_days')
    diagnosis_code = request.POST.get('diagnosis_code')
    extension = request.POST.get('extension')
    end_date = request.POST.get('end_date')
    previous_month_ibc = request.POST.get('previous_month_ibc')
    
        
    contrato = Contratos.objects.get(idcontrato = contract)
    empleado = Contratosemp.objects.get(idempleado = contrato.idempleado.idempleado)
    entidad = Entidadessegsocial.objects.get(codigo = entity)
    dianostico = Diagnosticosenfermedades.objects.get(coddiagnostico = diagnosis_code)
    
    
    incapacidad_modificar = get_object_or_404(Incapacidades, pk=global_id)
    
    incapacidad_modificar.idempleado = empleado
    incapacidad_modificar.empleado = f"{empleado.papellido} {empleado.sapellido} {empleado.snombre} {empleado.pnombre} - {empleado.snombre} P" ,
    incapacidad_modificar.tipoentidad = entidad.tipoentidad
    incapacidad_modificar.entidad = entidad.entidad
    incapacidad_modificar.coddiagnostico = dianostico
    incapacidad_modificar.diagnostico =  dianostico.diagnostico,
    incapacidad_modificar.fechainicial = datetime.strptime(initial_date, "%Y-%m-%d")
    incapacidad_modificar.dias = int (incapacity_days)
    incapacidad_modificar.idcontrato = contrato
    incapacidad_modificar.prorroga =  extension
    incapacidad_modificar.ibc = previous_month_ibc
    incapacidad_modificar.finincap =  datetime.strptime(end_date, "%Y-%m-%d")
    
    incapacidad_modificar.save()
    
    messages.success(request, 'La Incapacidad ha sido Actualizada con éxito.')
    return redirect('companies:disabilities')
  # Si el método no es GET ni POST, retornamos un error
  return JsonResponse({'message': 'Método no permitido', 'status': 'error'}, status=405)

  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  