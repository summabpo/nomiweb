from django.shortcuts import render 
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import NovFijos , Conceptosdenomina , Contratos
from apps.payroll.forms.FixedForm import FixidForm
from django.http import HttpResponse
from django.urls import reverse

@login_required
@role_required('accountant')
def fixed(request):
    """
    Muestra las novedades fijas asociadas a los contratos de una empresa.

    Filtra las novedades fijas (`NovFijos`) correspondientes a la empresa del usuario 
    autenticado y las ordena por ID descendente para su visualización.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP con la sesión del usuario autenticado.

    Returns
    -------
    HttpResponse
        Respuesta que renderiza la plantilla `'./payroll/fixedconcepts.html'` con 
        el contexto de las novedades fijas.

    See Also
    --------
    NovFijos : Modelo de novedades fijas asociadas a contratos.
    role_required : Decorador personalizado que restringe el acceso según el rol.
    login_required : Decorador de Django que exige autenticación del usuario.

    Notes
    -----
    El usuario debe tener el rol `'accountant'` para acceder a esta vista.
    """
    
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    novfijos = NovFijos.objects.filter(idcontrato__id_empresa = idempresa , estado_novfija=True ).order_by('-idnovfija')


    
    return render(request, './payroll/fixedconcepts.html',{'novfijos': novfijos})
    

@login_required
@role_required('accountant')
def fixed_modal(request):
    """
    Muestra y procesa el formulario modal para registrar una novedad fija.

    Si la solicitud es GET, renderiza el formulario vacío. Si es POST y los datos 
    son válidos, crea una nueva instancia de `NovFijos` y devuelve una respuesta 
    HTTP personalizada con encabezados compatibles con Unpoly para cerrar el modal 
    y actualizar la vista principal.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que puede contener datos POST del formulario.

    Returns
    -------
    HttpResponse
        Respuesta que renderiza la plantilla `'./payroll/partials/fixedconceptsmodal.html'`
        con el formulario si es una solicitud GET o si el formulario no es válido.

    HttpResponse
        Respuesta con encabezados Unpoly para cerrar el modal y mostrar un mensaje de éxito 
        si el formulario es válido y se crea la novedad.

    See Also
    --------
    FixidForm : Formulario para registrar una novedad fija.
    NovFijos : Modelo que representa novedades fijas en contratos.
    Conceptosdenomina : Modelo de conceptos de nómina relacionados.
    Contratos : Modelo de contratos vinculados a empleados.

    Notes
    -----
    Esta vista está diseñada para funcionar con Unpoly, utilizando encabezados como 
    `'X-Up-Accept-Layer'`, `'X-Up-message'` y `'X-Up-Location'` para controlar el comportamiento 
    del modal en el frontend.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    form = FixidForm(idempresa=idempresa)
    
    if request.method == 'POST':
        form = FixidForm(request.POST , idempresa=idempresa )
        if form.is_valid():
            
            # Aquí obtienes los datos del formulario limpio
            idcontrato = form.cleaned_data['idcontrato']
            valor = form.cleaned_data['valor']
            descrip = form.cleaned_data['descrip']
            idconcepto = form.cleaned_data['idconcepto']
            estado = form.cleaned_data['estado']
            fecha = form.cleaned_data['fecha']

            concepto = Conceptosdenomina.objects.get(idconcepto = idconcepto  )
            contrato = Contratos.objects.get(idcontrato = idcontrato)

            NovFijos.objects.create(
                idconcepto = concepto ,  
                valor = valor , 
                idcontrato = contrato ,   #fk principal 
                estado_novfija = estado,
                descripcion = descrip ,
                fechafinnovedad = fecha ,

            )

            response = HttpResponse()
            response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
            response['X-Up-icon'] = 'success'  # URL para recargar la página principal   
            response['X-Up-message'] = 'La Novedad fue registrada correctamente'    
            response['X-Up-Location'] = reverse('payroll:fixedconcepts')           
            return response
    
    return render(request, './payroll/partials/fixedconceptsmodal.html' ,{'form':form})



@login_required
@role_required('accountant')
def fixed_modal_edit(request,id):
    """
    Muestra y procesa el formulario modal para registrar una novedad fija.

    Si la solicitud es GET, renderiza el formulario vacío. Si es POST y los datos 
    son válidos, crea una nueva instancia de `NovFijos` y devuelve una respuesta 
    HTTP personalizada con encabezados compatibles con Unpoly para cerrar el modal 
    y actualizar la vista principal.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que puede contener datos POST del formulario.

    Returns
    -------
    HttpResponse
        Respuesta que renderiza la plantilla `'./payroll/partials/fixedconceptsmodal.html'`
        con el formulario si es una solicitud GET o si el formulario no es válido.

    HttpResponse
        Respuesta con encabezados Unpoly para cerrar el modal y mostrar un mensaje de éxito 
        si el formulario es válido y se crea la novedad.

    See Also
    --------
    FixidForm : Formulario para registrar una novedad fija.
    NovFijos : Modelo que representa novedades fijas en contratos.
    Conceptosdenomina : Modelo de conceptos de nómina relacionados.
    Contratos : Modelo de contratos vinculados a empleados.

    Notes
    -----
    Esta vista está diseñada para funcionar con Unpoly, utilizando encabezados como 
    `'X-Up-Accept-Layer'`, `'X-Up-message'` y `'X-Up-Location'` para controlar el comportamiento 
    del modal en el frontend.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    novfija = NovFijos.objects.get(idcontrato__id_empresa = idempresa , estado_novfija=True ,idnovfija =  id  )


    
    data = {
        'idconcepto': novfija.idconcepto.idconcepto,
        'valor': novfija.valor ,
        'idcontrato': novfija.idcontrato.idcontrato ,
        'estado': novfija.estado_novfija ,
        'fecha': novfija.fechafinnovedad ,
        'descrip': novfija.descripcion ,
        
    }
    
    
    form = FixidForm(idempresa=idempresa ,edit = True , initial = data)
    
    if request.method == 'POST':
        form = FixidForm(request.POST , idempresa=idempresa , edit = True)
        if form.is_valid():
            
            # Aquí obtienes los datos del formulario limpio
            idcontrato = form.cleaned_data['idcontrato']
            valor = form.cleaned_data['valor']
            descrip = form.cleaned_data['descrip']
            idconcepto = form.cleaned_data['idconcepto']
            estado = form.cleaned_data['estado']
            fecha = form.cleaned_data['fecha']

            concepto = Conceptosdenomina.objects.get(idconcepto = idconcepto  )
            contrato = Contratos.objects.get(idcontrato = idcontrato)

            NovFijos.objects.create(
                idconcepto = concepto ,  
                valor = valor , 
                idcontrato = contrato ,   #fk principal 
                estado_novfija = estado,
                descripcion = descrip ,
                fechafinnovedad = fecha ,

            )

            response = HttpResponse()
            response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
            response['X-Up-icon'] = 'success'  # URL para recargar la página principal   
            response['X-Up-message'] = 'La Novedad fue registrada correctamente'    
            response['X-Up-Location'] = reverse('payroll:fixedconcepts')           
            return response
    
    return render(request, './payroll/partials/fixedconceptsmodal_edit.html' ,{'form':form})






