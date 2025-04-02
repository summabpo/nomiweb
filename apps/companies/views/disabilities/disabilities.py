from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Sum, DecimalField, F
from apps.components.filterform import FilterForm 
from apps.components.decorators import  role_required
from apps.common.models  import Incapacidades , Contratosemp ,Contratos,Entidadessegsocial ,Diagnosticosenfermedades,Nomina
from apps.companies.forms.disabilitiesForm  import DisabilitiesForm
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
import os
import random
import string
from django.core.files.storage import default_storage
from django.conf import settings



def generate_random_filename(extension="jpg"):
    """Genera un nombre aleatorio de 100 caracteres con la extensión adecuada."""
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=80))
    return f"{random_string}.{extension}"
  

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
  
  
@login_required
@role_required('company','accountant')
def disabilities(request):
  
  usuario = request.session.get('usuario', {})
  idempresa = usuario['idempresa']
  
  incapacidades = Incapacidades.objects.values(
      'idcontrato__idcontrato',
      'idcontrato__idempleado__docidentidad',
      'idcontrato__idempleado__pnombre',
      'idcontrato__idempleado__snombre',
      'idcontrato__idempleado__papellido',
      'idcontrato__idempleado__sapellido',
      'entidad__entidad',
      'coddiagnostico__coddiagnostico',
      'coddiagnostico__diagnostico',
      'prorroga',
      'fechainicial',
      'dias',
      'idincapacidad',
      'imagenincapacidad',
      
  ).order_by('-idincapacidad')
  
  
  
  return render (request, './companies/disabilities.html', {'incapacidades' :incapacidades})

  


@login_required
@role_required('company','accountant')
def disabilities_modal(request):
  usuario = request.session.get('usuario', {})
  idempresa = usuario['idempresa']
  
  form = DisabilitiesForm(idempresa = idempresa)
  
  if request.method == 'POST':
  # Obtener datos del formulario
    contract = request.POST.get('contract')
    origin = request.POST.get('origin')
    entity = request.POST.get('entity')
    initial_date = request.POST.get('initial_date')
    incapacity_days = request.POST.get('incapacity_days')
    diagnosis_code = request.POST.get('diagnosis_code')
    extension = str(request.POST.get('extension', '0'))  # Convierte a string y usa '0' como valor predeterminado
    prorroga = extension == '1'  # Devuelve True si extension es '1'

    entidad = Entidadessegsocial.objects.get(codigo = entity)
    dianostico = Diagnosticosenfermedades.objects.get(coddiagnostico = diagnosis_code)
    
    # Obtener la imagen
    imagen = request.FILES.get('image')
    if imagen:
      # Obtener la extensión del archivo
      ext = imagen.name.split('.')[-1]

      # Generar un nombre aleatorio con la misma extensión
      filename = generate_random_filename(ext)

      # Guardar en MEDIA_ROOT en la subcarpeta 'incapacities/'
      file_path = os.path.join(settings.MEDIA_ROOT, 'incapacities', filename)
      os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Asegurar que la carpeta existe
      
      with open(file_path, 'wb+') as destination:
          for chunk in imagen.chunks():
              destination.write(chunk)

      print(f"Imagen guardada en: {file_path}")
      
      
    # Guardar en la base de datos
    Incapacidades.objects.create(
      entidad = entidad ,#enlace segsocial
      coddiagnostico = dianostico ,
      fechainicial = initial_date ,
      dias = incapacity_days,
      imagenincapacidad = filename if filename else "" ,  # cambiar tipo enlace 
      idcontrato_id  = contract ,  
      prorroga = prorroga ,
      ibc =  0 ,
      origenincap = origin , 
    )
        
    #messages.success(request, 'La Incapacidad ha sido añadido con éxito.')
    return redirect('companies:disabilities')
  
  return render (request, './companies/partials/create_disabilities_modal.html',{'form' :form,})



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

  

@csrf_exempt
def get_entity(request):
  if request.method == 'GET':
    dato = request.GET.get('dato')
    dato_sin_numeros = ''.join([char for char in dato if not char.isdigit()])

    if dato_sin_numeros.upper() == "TDO":
      # Filtrar tanto ARL como EPS
      entidad = Entidadessegsocial.objects.filter(tipoentidad__in=['ARL', 'EPS']).order_by('codigo').values('codigo', 'entidad')
    else:
      # Filtrar por tipoentidad específico
      entidad = Entidadessegsocial.objects.filter(tipoentidad=dato_sin_numeros).order_by('codigo').values('codigo', 'entidad')
    entidad_list = list(entidad)

    # Devolver la respuesta JSON
    return JsonResponse(entidad_list, safe=False)


  
  
  
  
  
  
  
  
  
  
  
  
  