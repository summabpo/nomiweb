from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Sum, DecimalField, F
from apps.components.filterform import FilterForm 
from apps.components.decorators import  role_required
from apps.companies.models import Incapacidades , Contratosemp ,Contratos,Entidadessegsocial ,Diagnosticosenfermedades,Nomina
from apps.companies.forms.disabilitiesForm  import DisabilitiesForm
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json

def maem(fecha_str):
    """
    Obtiene el nombre del mes anterior a partir de una fecha en formato 'YYYY-MM-DD'
    y el año actual (o anterior si es enero).
    
    Args:
        fecha_str (str): La fecha en formato 'YYYY-MM-DD'.
        
    Returns:
        tuple: Un tuple con el nombre del mes anterior en mayúsculas y el año correspondiente.
    """
    # Diccionario de meses
    meses = {
        1: "ENERO",
        2: "FEBRERO",
        3: "MARZO",
        4: "ABRIL",
        5: "MAYO",
        6: "JUNIO",
        7: "JULIO",
        8: "AGOSTO",
        9: "SEPTIEMBRE",
        10: "OCTUBRE",
        11: "NOVIEMBRE",
        12: "DICIEMBRE",
    }

    # Convertir la cadena a un objeto datetime
    initial_date = datetime.strptime(fecha_str, '%Y-%m-%d')

    # Calcular el mes anterior
    if initial_date.month == 1:
        previous_month = 12
        year = initial_date.year - 1
    else:
        previous_month = initial_date.month - 1
        year = initial_date.year

    # Obtener el mes anterior en mayúsculas
    return meses[previous_month], year
  
  

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
  ).order_by('-idincapacidad')[:10]
  
  
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
      
      
      
      contrato = Contratos.objects.get(idcontrato = contract)
      empleado = Contratosemp.objects.get(idempleado = contrato.idempleado.idempleado)
      entidad = Entidadessegsocial.objects.get(codigo = entity)
      dianostico = Diagnosticosenfermedades.objects.get(coddiagnostico = diagnosis_code)
      # Calcular el mes anterior
      mesanterior = maem(initial_date)
      mes_anterior, year = maem(initial_date)
      fecha1 = datetime.strptime(initial_date, "%Y-%m-%d")
      
      base_prestacion_social = Q(idconcepto__baseprestacionsocial=1)
      sueldo_basico = Q(idconcepto__sueldobasico=1)
      
      salario = Nomina.objects.filter(
          (base_prestacion_social),
          mesacumular=mesanterior,
          anoacumular=year,
          idcontrato=contract
      ).aggregate(total=Sum('valor'))['total']

      # Verificar si el resultado es None
      if salario is None:
          # Realizar la consulta para obtener el salario del contrato
          try:
              salario = Contratos.objects.get(idcontrato=contract).salario  
          except Contratos.DoesNotExist:
              salario = 0 
              
      fin_incap = fecha1 + timedelta(days=int(incapacity_days))
      new_incapacity = Incapacidades(
        empleado = f"{empleado.papellido} {empleado.sapellido} {empleado.snombre} {empleado.pnombre} - {empleado.snombre}" , 
        tipoentidad = entidad.tipoentidad, 
        entidad = entidad.entidad,
        coddiagnostico = dianostico,
        diagnostico =  dianostico.diagnostico,
        fechainicial = fecha1 ,
        dias = int (incapacity_days),
        idempleado= empleado,
        idcontrato = contrato,
        prorroga =  extension ,
        ibc = salario,
        finincap =  fin_incap,
      )
      new_incapacity.save()  
      errors = False
      messages.success(request, 'La Incapacidad ha sido añadido con éxito.')
      return redirect('companies:disabilities')
    else:
      print(form1.errors)
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
    if entidad.tipoentidad == 'EPS':
        if incapacidad.dias >= 100:
            origin = 'EPS2'
        else:
            origin = 'EPS1'
    else:
        origin = 'ARL'

    
    data ={ 
          'data': {
            'origin':origin,
            "contract": incapacidad.idcontrato.idcontrato,
            "entity": entidad.codigo ,
            "initial_date": incapacidad.fechainicial,
            "id":str(incapacidad.idincapacidad),
            "diagnosis_code":incapacidad.coddiagnostico.coddiagnostico,
            "incapacity_days":incapacidad.dias,
            "extension": incapacidad.prorroga,
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
    
    fecha1 = datetime.strptime(initial_date, "%Y-%m-%d")
    fin_incap = fecha1 + timedelta(days=int(incapacity_days))
    # contrato = Contratos.objects.get(idcontrato = contract)
    # empleado = Contratosemp.objects.get(idempleado = contrato.idempleado.idempleado)
    entidad = Entidadessegsocial.objects.get(codigo = entity)
    dianostico = Diagnosticosenfermedades.objects.get(coddiagnostico = diagnosis_code)
    
    print('-----------------')
    print(contract)
    print('-----------------')
    
    
    incapacidad_modificar = get_object_or_404(Incapacidades, pk=global_id)
    
    # incapacidad_modificar.idempleado = empleado
    # incapacidad_modificar.empleado = f"{empleado.papellido} {empleado.sapellido} {empleado.snombre} {empleado.pnombre} - {empleado.snombre} " ,
    incapacidad_modificar.tipoentidad = entidad.tipoentidad
    incapacidad_modificar.entidad = entidad.entidad
    incapacidad_modificar.coddiagnostico = dianostico
    incapacidad_modificar.diagnostico =  dianostico.diagnostico,
    incapacidad_modificar.fechainicial = datetime.strptime(initial_date, "%Y-%m-%d")
    incapacidad_modificar.dias = int (incapacity_days)
    # incapacidad_modificar.idcontrato = contrato
    incapacidad_modificar.prorroga =  extension
    incapacidad_modificar.ibc = previous_month_ibc
    incapacidad_modificar.finincap =  fin_incap
    
    incapacidad_modificar.save()
    
    messages.success(request, 'La Incapacidad ha sido Actualizada con éxito.')
    return redirect('companies:disabilities')
  # Si el método no es GET ni POST, retornamos un error
  return JsonResponse({'message': 'Método no permitido', 'status': 'error'}, status=405)

  

csrf_exempt
def get_entity(request):
  
  if request.method == 'GET':
    dato = request.GET.get('dato')
    dato_sin_numeros = ''.join([char for char in dato if not char.isdigit()])
    entidad = Entidadessegsocial.objects.filter( tipoentidad=dato_sin_numeros).order_by('codigo').values('codigo', 'entidad')

  # Convertir el queryset en una lista de diccionarios
  entidad_list = list(entidad)

  # Devolver la respuesta JSON
  return JsonResponse(entidad_list, safe=False) 

  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  