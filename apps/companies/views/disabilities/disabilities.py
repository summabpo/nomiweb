from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Sum, DecimalField, F
from apps.components.filterform import FilterForm 
from apps.components.decorators import  role_required
from apps.common.models  import Incapacidades , Contratosemp , NominaComprobantes ,Contratos,Entidadessegsocial ,Diagnosticosenfermedades,Nomina
from apps.companies.forms.disabilitiesForm  import DisabilitiesForm , DisabilitiesEditForm
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
from django.http import JsonResponse
from django.urls import reverse
from django.http import HttpResponse


def generate_random_filename(extension="pdf"):
    """Genera un nombre aleatorio de 80 caracteres con la extensión adecuada."""
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=80))
    return f"{random_string}.{extension}"
  
  
  
  
@login_required
@role_required('company','accountant')
def disabilities(request):
  """
    Genera un nombre de archivo aleatorio con una extensión especificada.

    Esta función genera un nombre de archivo único utilizando una cadena aleatoria de 80 caracteres 
    combinados con letras y números. Se puede especificar la extensión del archivo (por defecto es 
    "pdf"). El nombre generado puede ser usado para guardar archivos de manera segura y única.

    Parameters
    ----------
    extension : str, opcional
        La extensión del archivo a generar (por defecto "pdf").

    Returns
    -------
    str
        Devuelve un nombre de archivo aleatorio con la extensión especificada.

    Notes
    -----
    El nombre del archivo generado es aleatorio y tiene 80 caracteres, lo que lo hace único y adecuado
    para evitar conflictos de nombres de archivo.

    Example
    --------
    >>> generate_random_filename("pdf")
    'A3fG6kjB7hF29xCzL1yP0mQsA1aPdf6A9Pq5Ym3s.txt'
    """

  
  usuario = request.session.get('usuario', {})
  idempresa = usuario['idempresa']
  
  incapacidades = Incapacidades.objects.filter(idcontrato__id_empresa = idempresa ).values(
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
      'idcontrato__id_empresa_id'
  ).order_by('-idincapacidad')

  # Reemplazar None por cadena vacía en los campos especificados
  for inc in incapacidades:
      for campo in [
          'idcontrato__idempleado__pnombre',
          'idcontrato__idempleado__snombre',
          'idcontrato__idempleado__papellido',
          'idcontrato__idempleado__sapellido'
      ]:
          if inc[campo] is None:
              inc[campo] = ""
  
  return render (request, './companies/disabilities.html', {'incapacidades' :incapacidades})



@login_required
@role_required('company','accountant')
def disabilities_modal(request):
  """
    Vista para registrar una incapacidad en el sistema.

    Esta vista permite registrar una incapacidad de un empleado en el sistema, asociando los detalles 
    como el contrato, origen, entidad de salud, fecha de inicio, días de incapacidad y diagnóstico.
    Además, guarda el archivo PDF asociado con el certificado de incapacidad si se proporciona.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que contiene los datos del formulario de incapacidad a registrar.
        - El formulario debe incluir detalles como el contrato, origen, entidad de salud, fecha inicial, 
        días de incapacidad, código diagnóstico y un archivo PDF opcional.

    Returns
    -------
    HttpResponse
        Devuelve una respuesta HTTP que indica el estado del proceso de registro de la incapacidad.

    See Also
    --------
    generate_random_filename : Función para generar un nombre de archivo aleatorio para el PDF.
    DisabilitiesForm : Formulario para la creación de incapacidades.
    Incapacidades : Modelo que representa las incapacidades registradas en el sistema.

    Notes
    -----
    El usuario debe estar autenticado y tener el rol de 'accountant' en la empresa para acceder a esta vista.
    """

  usuario = request.session.get('usuario', {})
  idempresa = usuario['idempresa']
  form = DisabilitiesForm(idempresa = idempresa)
  
  if request.method == 'POST':
    form = DisabilitiesForm(request.POST, request.FILES ,idempresa = idempresa)
    if form.is_valid():
      #Obtener datos del formulario
      contract = form.cleaned_data['contract']
      origin = form.cleaned_data['origin']
      entity = form.cleaned_data['entity']
      initial_date = form.cleaned_data['initial_date']
      incapacity_days = form.cleaned_data['incapacity_days']
      diagnosis_code = form.cleaned_data['diagnosis_code']
      extension = form.cleaned_data['extension'] #Convierte a string y usa '0' como valor predeterminado
      prorroga = extension == '1'  #Devuelve True si extension es '1'
      pdf_file = form.cleaned_data['pdf_file']
            
      entidad = Entidadessegsocial.objects.get(codigo = entity)
      dianostico = Diagnosticosenfermedades.objects.get(coddiagnostico = diagnosis_code)
      
      #* Funcion de guardado de pdf 
      new_filename = ''
      
      if pdf_file :
        # Generar un nuevo nombre aleatorio
        new_filename = generate_random_filename("pdf")
        pdf_folder = os.path.join(settings.MEDIA_ROOT, 'pdfs')
        # ✅ Crear la carpeta si no existe
        os.makedirs(pdf_folder, exist_ok=True)
        # Guardar el archivo con el nuevo nombre
        pdf_path = os.path.join(pdf_folder, new_filename)
        with open(pdf_path, 'wb+') as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)
              
              
      ibc = NominaComprobantes.objects.filter(idcontrato_id=contract).order_by('-idhistorico').first()

      # Guardar en la base de datos
      Incapacidades.objects.create(
        entidad = entidad , #enlace segsocial
        coddiagnostico = dianostico ,
        fechainicial = initial_date ,
        dias = incapacity_days,
        imagenincapacidad = new_filename if new_filename else "" ,  #cambiar tipo enlace 
        certificadoincapacidad = pdf_file if pdf_file else "", 
        idcontrato_id  = contract ,  
        prorroga = prorroga ,
        ibc =  ibc.salario ,
        origenincap = origin , 
      )
      
      response = HttpResponse()
      response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
      response['X-Up-icon'] = 'success'  # URL para recargar la página principal   
      response['X-Up-message'] = 'La Incapacidad fue registrada correctamente'    
      response['X-Up-Location'] = reverse('companies:disabilities')           
      return response
        
  return render (request, './companies/partials/create_disabilities_modal.html',{'form' :form,})



@login_required
@role_required('company','accountant')
def disabilities_modal_edit(request , id ):
  """
    Vista para editar una incapacidad existente en el sistema.

    Esta vista permite editar los detalles de una incapacidad ya registrada, como el origen, entidad de 
    salud, fecha de inicio, días de incapacidad y diagnóstico. Si se proporciona un nuevo archivo PDF, 
    este se guarda como un archivo nuevo con un nombre aleatorio.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que contiene los datos del formulario para editar la incapacidad.
        - El formulario debe incluir detalles como el origen, entidad de salud, fecha inicial, días de incapacidad,
        código diagnóstico y un archivo PDF opcional.
    id : int
        Identificador de la incapacidad a editar.

    Returns
    -------
    HttpResponse
        Devuelve una respuesta HTTP que indica el estado del proceso de edición de la incapacidad.

    See Also
    --------
    generate_random_filename : Función para generar un nombre de archivo aleatorio para el PDF.
    DisabilitiesEditForm : Formulario para editar las incapacidades.
    Incapacidades : Modelo que representa las incapacidades registradas en el sistema.

    Notes
    -----
    El usuario debe estar autenticado y tener el rol de 'accountant' en la empresa para acceder a esta vista.
    """

  usuario = request.session.get('usuario', {})
  idempresa = usuario['idempresa']
  
  incapacidad = Incapacidades.objects.get(pk = id)
  
  
  data = {
    'contract' :incapacidad.idcontrato.idcontrato , 
    'origin' :incapacidad.origenincap ,  
    'entity' :incapacidad.entidad.codigo ,  
    'initial_date' :incapacidad.fechainicial ,  
    'incapacity_days' :incapacidad.dias ,  
    'diagnosis_code' :incapacidad.coddiagnostico ,  
    'extension' : '1' if incapacidad.prorroga  else '0',  
    'id':incapacidad.idincapacidad 
  }
  
  
  
  form = DisabilitiesEditForm(idempresa = idempresa ,initial= data ,id=id)
  
  if request.method == 'POST':
    form = DisabilitiesEditForm(request.POST, request.FILES ,idempresa = idempresa,id=id)
    if form.is_valid():
      #Obtener datos del formulario
      origin = form.cleaned_data['origin']
      entity = form.cleaned_data['entity']
      initial_date = form.cleaned_data['initial_date']
      incapacity_days = form.cleaned_data['incapacity_days']
      diagnosis_code = form.cleaned_data['diagnosis_code']
      extension = form.cleaned_data['extension'] #Convierte a string y usa '0' como valor predeterminado
      prorroga = extension == '1'  #Devuelve True si extension es '1'
      pdf_file = form.cleaned_data['pdf_file']
            
      entidad = Entidadessegsocial.objects.get(codigo = entity)
      dianostico = Diagnosticosenfermedades.objects.get(coddiagnostico = diagnosis_code)
      
      #* Funcion de guardado de pdf 
      new_filename = ''
      
      if pdf_file :
        # Generar un nuevo nombre aleatorio
        new_filename = generate_random_filename("pdf")
        pdf_folder = os.path.join(settings.MEDIA_ROOT, 'pdfs')
        # ✅ Crear la carpeta si no existe
        os.makedirs(pdf_folder, exist_ok=True)
        # Guardar el archivo con el nuevo nombre
        pdf_path = os.path.join(pdf_folder, new_filename)
        with open(pdf_path, 'wb+') as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)
              
              
  

      # Guardar en la base de datos
      
      if incapacidad.entidad != entidad:
        incapacidad.entidad = entidad  # enlace segsocial

      if incapacidad.coddiagnostico != dianostico:
        incapacidad.coddiagnostico = dianostico

      if incapacidad.fechainicial != initial_date:
        incapacidad.fechainicial = initial_date

      if incapacidad.dias != incapacity_days:
        incapacidad.dias = incapacity_days

      if incapacidad.prorroga != prorroga:
        incapacidad.prorroga = prorroga

      if incapacidad.origenincap != origin:
        incapacidad.origenincap = origin

      incapacidad.save()
      
      response = HttpResponse()
      response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
      response['X-Up-icon'] = 'success'  # URL para recargar la página principal   
      response['X-Up-message'] = 'La incapacidad fue actualizada correctamente.'    
      response['X-Up-Location'] = reverse('companies:disabilities')           
      return response
  
  return render (request, './companies/partials/create_disabilities_modal_edit.html',{'form' :form, 'data':data})



@login_required
@role_required('company','accountant')
def disabilities_modal_detail(request , id ):
  """
  Vista para editar los detalles de una incapacidad mediante una solicitud AJAX.

  Esta vista permite editar una incapacidad existente a través de una solicitud GET o POST. Los datos editados
  incluyen el contrato, origen, entidad de salud, fecha de inicio, días de incapacidad, diagnóstico y fecha de 
  finalización de la incapacidad. Esta vista es utilizada en combinación con un sistema AJAX para la actualización 
  dinámica de la incapacidad.

  Parameters
  ----------
  request : HttpRequest
      Objeto de solicitud HTTP que contiene los datos para la modificación de la incapacidad.
      - En GET, contiene el identificador de la incapacidad a editar.
      - En POST, contiene los nuevos datos de la incapacidad a modificar.

  Returns
  -------
  JsonResponse
      Devuelve una respuesta JSON con los datos modificados y el estado de la operación.

  See Also
  --------
  Incapacidades : Modelo que representa las incapacidades registradas en el sistema.

  Notes
  -----
  La vista acepta tanto solicitudes GET como POST. La solicitud POST se utiliza para actualizar los detalles
  de una incapacidad existente.
  """

  incapacidad = get_object_or_404(Incapacidades, pk=id)
  
  return render (request, './companies/partials/create_disabilities_modal_detail.html',{'incapacidad':incapacidad}) 
  



global_id = None 

@csrf_exempt
def edit_disabilities(request):
  """
  Vista para editar los detalles de una incapacidad mediante una solicitud AJAX.

  Esta vista permite editar una incapacidad existente a través de una solicitud GET o POST. Los datos editados
  incluyen el contrato, origen, entidad de salud, fecha de inicio, días de incapacidad, diagnóstico y fecha de 
  finalización de la incapacidad. Esta vista es utilizada en combinación con un sistema AJAX para la actualización 
  dinámica de la incapacidad.

  Parameters
  ----------
  request : HttpRequest
      Objeto de solicitud HTTP que contiene los datos para la modificación de la incapacidad.
      - En GET, contiene el identificador de la incapacidad a editar.
      - En POST, contiene los nuevos datos de la incapacidad a modificar.

  Returns
  -------
  JsonResponse
      Devuelve una respuesta JSON con los datos modificados y el estado de la operación.

  See Also
  --------
  Incapacidades : Modelo que representa las incapacidades registradas en el sistema.

  Notes
  -----
  La vista acepta tanto solicitudes GET como POST. La solicitud POST se utiliza para actualizar los detalles
  de una incapacidad existente.
  """

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
  """
    Vista para obtener las entidades de salud disponibles basadas en un tipo de entidad.

    Esta vista permite obtener una lista de entidades de salud basadas en el tipo de entidad (EPS o ARL). 
    Dependiendo del tipo de entidad proporcionado, se devuelve una lista filtrada de entidades que pueden ser seleccionadas 
    para asociar a una incapacidad. 

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que contiene los datos de tipo de entidad y contrato.
        - 'dato' es el tipo de entidad (EPS o ARL).
        - 'id' es el identificador del contrato.

    Returns
    -------
    JsonResponse
        Devuelve una respuesta JSON con las entidades de salud disponibles para el tipo de entidad dado.

    See Also
    --------
    Contratos : Modelo que representa los contratos de los empleados.
    Entidadessegsocial : Modelo que representa las entidades de salud disponibles.

    Notes
    -----
    El usuario debe estar autenticado para acceder a esta vista.
    """

  entidad_select = ''
  if request.method == 'GET':
    dato = request.GET.get('dato')
    id = request.GET.get('id')
    
    
    
    dato_sin_numeros = ''.join([char for char in dato if not char.isdigit()])
    
    
    if dato_sin_numeros.upper() == "EPS":
      # Filtrar tanto ARL como EPS
      entidad_select = Contratos.objects.get(idcontrato = id ).codeps.codigo
      entidad = Entidadessegsocial.objects.filter(tipoentidad__in=['ARL', 'EPS']).order_by('codigo').values('codigo', 'entidad')
    else:

      entidad_select = Contratos.objects.get(idcontrato = id ).id_empresa.arl.codigo
      # Filtrar por tipoentidad específico
      entidad = Entidadessegsocial.objects.filter(tipoentidad=dato_sin_numeros).order_by('codigo').values('codigo', 'entidad')
          
    entidad_list = list(entidad)

    data = {
      'entidad_list' : entidad_list,
      'entidad_select' : entidad_select 
    }
    # Devolver la respuesta JSON
    return JsonResponse(data ,safe=False)


  
  
  
  
  
  
  
  
  
  
  
  
  