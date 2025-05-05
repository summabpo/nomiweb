
from django.shortcuts import render, redirect, get_object_or_404
from apps.common.models  import Cargos,Empresa,Nivelesestructura , Contabgrupos
from apps.companies.forms.accountinggroupForm import accountinggroupForm
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse



@login_required
@role_required('company','accountant')
def accountinggroup(request): 
    """
    Muestra los grupos contables asociados a una empresa y el formulario para agregar nuevos grupos.

    Filtra los registros de grupos contables (`Contabgrupos`) de acuerdo con la empresa del usuario
    autenticado y los ordena por ID de grupo ascendente. También se renderiza el formulario vacío para 
    crear nuevos grupos contables.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP con la sesión del usuario autenticado.

    Returns
    -------
    HttpResponse
        Respuesta que renderiza la plantilla `'companies/accountinggroup.html'` con los grupos contables
        y el formulario para agregar nuevos grupos.

    See Also
    --------
    Contabgrupos : Modelo de grupos contables asociados a una empresa.
    accountinggroupForm : Formulario utilizado para crear nuevos grupos contables.
    role_required : Decorador personalizado que restringe el acceso según el rol.
    login_required : Decorador de Django que exige autenticación del usuario.

    Notes
    -----
    El usuario debe estar autenticado y tener el rol `'company'` o `'accountant'` para acceder a esta vista.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    groups = Contabgrupos.objects.filter(id_empresa__idempresa = idempresa ).order_by('idgrupo')
    form = accountinggroupForm()
    return render(request, './companies/accountinggroup.html',
                    {
                        'groups':groups,
                        'form':form,
                    })
    
    
@login_required
@role_required('company','accountant')
def accountinggroup_modal(request): 
    """
    Permite crear un nuevo grupo contable para una empresa.

    Recibe datos a través de una solicitud POST, valida el formulario para crear un nuevo grupo contable
    y lo guarda en la base de datos. En caso de éxito, devuelve una respuesta JSON con el estado y mensaje.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que contiene los datos del formulario para crear un grupo contable.

    Returns
    -------
    JsonResponse
        Respuesta en formato JSON indicando el estado de la creación del grupo contable.
        
    HttpResponse
        Si la solicitud no es de tipo POST, renderiza el formulario de creación del grupo contable.

    See Also
    --------
    accountinggroupForm : Formulario utilizado para crear nuevos grupos contables.
    Contabgrupos : Modelo que representa los grupos contables asociados a una empresa.
    role_required : Decorador personalizado que restringe el acceso según el rol.
    login_required : Decorador de Django que exige autenticación del usuario.

    Notes
    -----
    El usuario debe estar autenticado y tener el rol `'company'` o `'accountant'` para acceder a esta vista.
    """
    
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    if request.method == 'POST':
        form = accountinggroupForm(request.POST)
        if form.is_valid():
            empresa = Empresa.objects.get(idempresa= idempresa )
            
            nuevogrupo = Contabgrupos(
                    grupo=form.cleaned_data['grupo'] ,
                    grupocontable =form.cleaned_data['grupocontable'] ,
                    id_empresa = empresa
                )
            nuevogrupo.save()
            return JsonResponse({'status': 'success', 'message': 'Grupo creado exitosamente'})
        else:
            # En caso de que el formulario no sea válido, mostrar los errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    print(request, f"Error en {field}: {error}")
                    
    else:
        form = accountinggroupForm()             
    
    return render(request, './companies/partials/accountinggroupModal.html',
                    {
                        'form':form,
                    })
    