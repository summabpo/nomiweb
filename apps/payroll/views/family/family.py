from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import NovFijos , Conceptosdenomina , Contratos ,Indicador
from apps.payroll.forms.FixedForm import FixidForm
from django.http import HttpResponse
from django.urls import reverse
from apps.payroll.forms.FamilyForm import FamilyForm , FamilyForm2
from django.contrib import messages



@login_required
@role_required('accountant')
def family_list(request):
    """
    Vista para listar todas las familias de conceptos (indicadores) registradas.

    Muestra una tabla con todas las familias creadas en el sistema, ordenadas por su identificador. 
    Está diseñada como parte de la gestión de conceptos de nómina y sirve como punto de entrada 
    para acceder a las funcionalidades de detalle, edición o eliminación de familias.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP GET para renderizar la lista.

    Returns
    -------
    HttpResponse
        Renderiza la plantilla 'payroll/family_list.html' con el contexto que incluye 
        todas las familias ordenadas por su ID.

    See Also
    --------
    Indicador : Modelo que representa agrupaciones o clasificaciones de conceptos de nómina.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    familys = Indicador.objects.filter(
    ).distinct().order_by('id')

    return render(request, './payroll/family_list.html', {'familys': familys})
   
   
   
@login_required
@role_required('accountant')
def family_create(request):
    """
    Vista para crear una nueva familia de conceptos mediante un formulario modal.

    Permite registrar una nueva familia (indicador) con nombre, descripción y conceptos asociados.
    Está diseñada para funcionar con Unpoly y formularios modales. Al finalizar, responde con
    cabeceras HTTP especiales que instruyen a Unpoly a cerrar el modal y actualizar la lista principal.

    Valida que los conceptos seleccionados existan y los asocia con la nueva familia. También 
    recibe el `idempresa` desde la sesión para filtrar el conjunto de datos en el formulario.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP GET para cargar el formulario vacío, o POST para procesar los datos enviados.

    Returns
    -------
    HttpResponse
        - Si el formulario es válido:
            Respuesta con cabeceras Unpoly para cerrar el modal y actualizar la vista principal.
        - Si hay errores:
            Renderiza el formulario nuevamente con los errores, sin cerrar el modal.

    See Also
    --------
    Indicador : Modelo de familia de conceptos.
    Conceptosdenomina : Modelo de conceptos asociados a la nómina.
    FamilyForm : Formulario para crear una nueva familia de conceptos.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    form = FamilyForm(idempresa = idempresa)
    if request.method == 'POST':
        form = FamilyForm(request.POST , idempresa=idempresa )
        if form.is_valid():
            indicador = Indicador.objects.create(
                nombre = form.cleaned_data['name'] ,
                descripcion = form.cleaned_data['descrip']
            )
            
            concepts = form.cleaned_data['idconcepto']
            for data in concepts : 
                concept = Conceptosdenomina.objects.get(idconcepto = data )
                concept.indicador.add(indicador)
                
            response = HttpResponse()
            response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
            response['X-Up-icon'] = 'success'  # URL para recargar la página principal   
            response['X-Up-message'] = 'Familia guardada exitosamente'    
            response['X-Up-Location'] = reverse('payroll:family_list')           
            return response
        else:
            # En caso de que el formulario no sea válido, mostrar los errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    print(request, f"Error en {field}: {error}")    
    
    return render(request, './payroll/partials/family_create.html',{'form': form})




@login_required
@role_required('accountant')
def family_detail(request,id):
    """
    Vista para visualizar los detalles de una familia específica.

    Muestra la información principal de la familia (nombre, descripción) y los conceptos asociados a ella,
    filtrados por la empresa activa del usuario. Esta vista está diseñada para ser utilizada en un modal.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP GET para obtener y renderizar los detalles.
    id : int
        Identificador único de la familia (indicador) a consultar.

    Returns
    -------
    HttpResponse
        Renderiza la plantilla 'payroll/partials/family_detail.html' con la información de la familia.

    See Also
    --------
    Indicador : Modelo de la familia de conceptos.
    Conceptosdenomina : Conceptos asociados a una familia específica.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    family = Indicador.objects.get(id = id)
    conceptos = Conceptosdenomina.objects.filter(indicador=family ,id_empresa = idempresa )
    data = {
        'name': family.nombre,
        'descrip': family.descripcion,
        'concepts': conceptos,  # Lista de conceptos relacionados
    }
    return render(request, './payroll/partials/family_detail.html',{'data': data})
   


@login_required
@role_required('accountant')
def family_edit(request,id):
    """
    Vista para editar una familia de conceptos existente mediante un formulario modal.

    Permite modificar la descripción de la familia y actualizar la lista de conceptos asociados.
    La vista compara los conceptos actuales con los enviados en el formulario para eliminar 
    las asociaciones que ya no apliquen y agregar nuevas.

    Utiliza un formulario personalizado que incluye datos precargados y validados según la empresa activa. 
    Al guardar, responde con cabeceras Unpoly para cerrar el modal y actualizar la vista principal.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP GET para cargar el formulario con los datos actuales, o POST para aplicar los cambios.
    id : int
        Identificador único de la familia a editar.

    Returns
    -------
    HttpResponse
        - Si el formulario es válido:
            Cierra el modal y actualiza la lista principal con mensajes de éxito.
        - Si hay errores:
            Renderiza el formulario nuevamente para su corrección.

    See Also
    --------
    Indicador : Modelo de agrupación o familia de conceptos.
    Conceptosdenomina : Modelo que representa los conceptos que pueden ser asociados a una familia.
    FamilyForm2 : Formulario de edición para familias de conceptos.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    family = Indicador.objects.get(id = id)
    conceptos = Conceptosdenomina.objects.filter(indicador=family ,id_empresa = idempresa )
    data = {
        'name': family.nombre,
        'descrip': family.descripcion,
        'idconcepto': [i.idconcepto for i in conceptos] ,  # Lista de conceptos relacionados
    }
    
    form = FamilyForm2(idempresa = idempresa , initial = data)
    if request.method == 'POST':
        form = FamilyForm2(request.POST,idempresa = idempresa)
        if form.is_valid():
            
            descrip = form.cleaned_data['descrip']
            
            if family.descripcion != descrip:
                family.descripcion = descrip 
            
            family.save()
            
            concepts_ids_post = set(form.cleaned_data['idconcepto'])  # IDs del formulario (POST)
            concepts_current = Conceptosdenomina.objects.filter(indicador=family, id_empresa=idempresa)

            # 1. Eliminar conceptos que ya no están seleccionados
            for concept in concepts_current:
                if concept.idconcepto not in concepts_ids_post:
                    concept.indicador.remove(family)

            # 2. Agregar los nuevos conceptos seleccionados (o mantener los existentes)
            for concept_id in concepts_ids_post:
                concept = Conceptosdenomina.objects.get(idconcepto=concept_id)
                concept.indicador.add(family)
                
            
            response = HttpResponse()
            response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
            response['X-Up-icon'] = 'success'  # URL para recargar la página principal   
            response['X-Up-message'] = 'Familia actualizada exitosamente'    
            response['X-Up-Location'] = reverse('payroll:family_list')           
            return response
        
    return render(request, './payroll/partials/family_edit.html',{'form': form})



@login_required
@role_required('accountant')
def family_delete(request, id):
    """
    Vista para eliminar una familia de conceptos de nómina (indicador) mediante confirmación modal.

    Permite desvincular todos los conceptos asociados a una familia específica y eliminarla del sistema. 
    Está protegida por una verificación POST para asegurar que la eliminación sea intencional y 
    está limitada a usuarios con el rol de contador.

    Antes de eliminar la familia, remueve la relación con todos los conceptos que la referencian dentro
    de la empresa del usuario autenticado, garantizando integridad de datos.

    Esta vista es compatible con flujos de trabajo modales y presenta una advertencia visual tras la eliminación.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP GET para mostrar la confirmación de eliminación o POST para ejecutar la acción.
    id : int
        Identificador de la familia (indicador) a eliminar.

    Returns
    -------
    HttpResponse
        - Si es GET: Renderiza el modal de confirmación.
        - Si es POST: Elimina la familia, muestra un mensaje de advertencia y redirige a la lista principal.

    See Also
    --------
    Indicador : Modelo de familia de conceptos.
    Conceptosdenomina : Modelo que puede estar relacionado con una o más familias.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    family = Indicador.objects.get(id=id)

    if request.method == 'POST':
        
        conceptos_asociados = Conceptosdenomina.objects.filter(indicador=family, id_empresa=idempresa)
        for concepto in conceptos_asociados:
            concepto.indicador.remove(family)
            
        family.delete()

        messages.warning(request, 'Familia eliminada correctamente')
        return redirect('payroll:family_list')

    return render(request, './payroll/partials/family_delete.html', {'family': family})


