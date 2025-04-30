from django.shortcuts import render,redirect
from apps.administrator.forms.companiesForm import CompaniesForm
from apps.common.models import  Empresa, Ciudades, Paises, Entidadessegsocial, Bancos
from django.http import JsonResponse


def createcompanies_admin(request):
    
    """
    Renderiza el formulario de creación de nuevas empresas para el panel de administración.

    Este view se encarga de cargar el formulario para registrar nuevas empresas y mostrar
    una lista de las empresas ya existentes ordenadas de manera descendente por ID.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP enviado por el navegador del usuario.

    Returns
    -------
    HttpResponse
        Página HTML renderizada que contiene el formulario de creación de empresas
        y la lista de empresas existentes.

    See Also
    --------
    CompaniesForm : Formulario utilizado para registrar una nueva empresa.
    Empresa : Modelo que representa una empresa dentro del sistema.

    Notes
    -----
    - Este view solo renderiza el formulario y los datos existentes; no procesa envíos POST.
    - Para la creación efectiva de empresas, se requiere un view complementario que maneje los POST.
    - El formulario está disponible en la plantilla 'admin/companies.html'.
    """
    
    
    form = CompaniesForm()
    empresas = Empresa.objects.all().order_by('-idempresa')
    return render(request, './admin/companies.html',{
        'form': form ,
        'empresas':empresas
        
        })
    
    
def addcompanies_admin(request):
    
    """
    Procesa el formulario de creación de una nueva empresa en el panel administrativo.

    Este view maneja solicitudes POST con datos del formulario para registrar una nueva empresa.
    Si la solicitud no es POST, se renderiza el modal con el formulario vacío.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP, que puede ser GET o POST.

    Returns
    -------
    JsonResponse
        Si el formulario es enviado por POST y es válido, retorna un JSON indicando éxito.

    HttpResponse
        Si la solicitud es GET o el formulario no es válido, renderiza el formulario HTML en
        la plantilla `admin/partials/companiesModal.html`.

    See Also
    --------
    CompaniesForm : Formulario para la creación de empresas.
    Empresa : Modelo principal que representa una empresa registrada.
    Ciudades, Paises, Entidadessegsocial, Bancos : Modelos auxiliares relacionados con la empresa.

    Notes
    -----
    - Este view extrae múltiples campos del formulario, incluyendo campos relacionales (como ciudad, país, banco, ARL).
    - Algunos campos numéricos o booleanos se transforman a texto y se truncan a los dos primeros caracteres.
    - Se carga el formulario con `request.FILES` para permitir el envío de archivos como el logo empresarial.
    - Si el formulario no es válido, los errores se imprimen en consola pero no se devuelven en la respuesta JSON.
    - Este view está diseñado para funcionar junto con un modal (partial) del panel administrativo.

    Examples
    --------
    - POST: Registro de una nueva empresa con los campos completos.
    - GET: Apertura de un modal con el formulario de creación de empresas.
    """
    
    if request.method == 'POST':
        form = CompaniesForm(request.POST, request.FILES)
        if form.is_valid():
            vstccf = form.cleaned_data.get('vstccf', '')
            vstsenaicbf = form.cleaned_data.get('vstsenaicbf', '')
            ige100 = form.cleaned_data.get('ige100', '')
            ajustarnovedad = form.cleaned_data.get('ajustarnovedad', '')
            
                        
            empresa = Empresa(
                nit=form.cleaned_data['nit'],
                nombreempresa=form.cleaned_data['nombreempresa'],
                dv=form.cleaned_data['dv'],
                tipodoc=form.cleaned_data['tipodoc'],
                replegal=form.cleaned_data['replegal'],
                direccionempresa=form.cleaned_data['direccionempresa'],
                telefono=form.cleaned_data['telefono'],
                email=form.cleaned_data['email'],
                codciudad=Ciudades.objects.get(idciudad=form.cleaned_data['codciudad']),
                pais=Paises.objects.get(idpais=form.cleaned_data['pais']),
                arl=Entidadessegsocial.objects.get(identidad=form.cleaned_data['arl']),
                contactonomina=form.cleaned_data['contactonomina'],
                emailnomina=form.cleaned_data['emailnomina'],
                contactorrhh=form.cleaned_data['contactorrhh'],
                emailrrhh=form.cleaned_data['emailrrhh'],
                contactocontab=form.cleaned_data['contactocontab'],
                emailcontab=form.cleaned_data['emailcontab'],
                cargocertificaciones=form.cleaned_data['cargocertificaciones'],
                firmacertificaciones=form.cleaned_data['firmacertificaciones'],
                website=form.cleaned_data['website'],
                logo=form.cleaned_data['logo'],
                metodoextras=form.cleaned_data['metodoextras'],
                realizarparafiscales=form.cleaned_data['realizarparafiscales'],
                vstccf=str(vstccf)[:2] if vstccf else '',
                vstsenaicbf=str(vstsenaicbf)[:2] if vstsenaicbf else '',
                ige100=str(ige100)[:2] if ige100 else '',
                slntarifapension=form.cleaned_data['slntarifapension'],
                banco=Bancos.objects.get(idbanco=form.cleaned_data['banco']) if form.cleaned_data['banco'] else None,
                numcuenta=form.cleaned_data['numcuenta'],
                tipocuenta=form.cleaned_data['tipocuenta'],
                codigosuc=form.cleaned_data['codigosuc'],
                nombresuc=form.cleaned_data['nombresuc'],
                claseaportante=form.cleaned_data['claseaportante'],
                tipoaportante=form.cleaned_data['tipoaportante'],
                ajustarnovedad=str(ajustarnovedad)[:2] if ajustarnovedad else '',	
            )
            empresa.save()
            return JsonResponse({'status': 'success', 'message': 'Empresa creada exitosamente'})
        else:
            # En caso de que el formulario no sea válido, mostrar los errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    print(request, f"Error en {field}: {error}")
    else:
        form = CompaniesForm()
    return render(request, './admin/partials/companiesModal.html',{
        'form': form
        })