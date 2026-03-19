from django.shortcuts import render,redirect
from apps.administrator.forms.companiesForm import CompaniesForm
from apps.common.models import  Empresa, Ciudades, Paises, Entidadessegsocial, Bancos , Conceptosdenomina ,Familia
from django.http import JsonResponse
from django.http import HttpResponse
from django.urls import reverse

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

            metodoextras = "SI" if form.cleaned_data.get('metodoextras') else "NO"
            realizarparafiscales = "SI" if form.cleaned_data.get('realizarparafiscales') else "NO"
            vstccf = "SI" if form.cleaned_data.get('vstccf') else "NO"
            vstsenaicbf = "SI" if form.cleaned_data.get('vstsenaicbf') else "NO"
            ige100 = "SI" if form.cleaned_data.get('ige100') else "NO"
            slntarifapension = "SI" if form.cleaned_data.get('slntarifapension') else "NO"

            empresa_exonerada = "SI" if form.cleaned_data.get('empresa_exonerada') else "NO"

            empresa = Empresa(
                nit=form.cleaned_data['nit'],
                nombreempresa=form.cleaned_data['nombreempresa'],
                dv=form.cleaned_data['dv'],
                tipodoc=form.cleaned_data['tipodoc'],

                # NUEVOS CAMPOS
                tipo_persona=form.cleaned_data.get('tipo_persona'),
                naturaleza_juridica=form.cleaned_data.get('naturaleza_juridica'),

                replegal=form.cleaned_data['replegal'],

                tipo_identificacion_rep_legal=form.cleaned_data.get('tipo_identificacion_rep_legal'),
                numero_identificacion_rep_legal=form.cleaned_data.get('numero_identificacion_rep_legal'),
                papellido_rep_legal=form.cleaned_data.get('papellido_rep_legal'),
                sapellido_rep_legal=form.cleaned_data.get('sapellido_rep_legal'),
                pnombre_rep_legal=form.cleaned_data.get('pnombre_rep_legal'),
                snombre_rep_legal=form.cleaned_data.get('snombre_rep_legal'),

                direccionempresa=form.cleaned_data['direccionempresa'],
                telefono=form.cleaned_data['telefono'],
                email=form.cleaned_data['email'],

                idciudad=Ciudades.objects.get(idciudad=form.cleaned_data['codciudad']),
                pais=Paises.objects.get(idpais=form.cleaned_data['pais']),
                arl=Entidadessegsocial.objects.get(identidad=form.cleaned_data['arl']),

                contactonomina=form.cleaned_data['contactonomina'],
                emailnomina=form.cleaned_data['emailnomina'],
                contactorrhh=form.cleaned_data['contactorrhh'],
                emailrrhh=form.cleaned_data['emailrrhh'],

                contactocontab=form.cleaned_data['contactocontab'],
                emailcontab=form.cleaned_data['emailcontab'],

                cargocertificaciones=form.cleaned_data['cargocertificaciones'],
                firmacertificaciones=form.cleaned_data.get('firmacertificaciones') or "",

                website=form.cleaned_data['website'],
                logo=form.cleaned_data['logo'],

                metodoextras=metodoextras,
                realizarparafiscales=realizarparafiscales,
                vstccf=vstccf,
                vstsenaicbf=vstsenaicbf,
                ige100=ige100,
                slntarifapension=slntarifapension,

                empresa_exonerada=empresa_exonerada,

                banco=Bancos.objects.get(idbanco=form.cleaned_data['banco']) if form.cleaned_data['banco'] else None,
                numcuenta=form.cleaned_data['numcuenta'],
                tipocuenta=form.cleaned_data['tipocuenta'],

                codigosuc=form.cleaned_data['codigosuc'],
                nombresuc=form.cleaned_data['nombresuc'],

                # NUEVOS CAMPOS PILA
                tipo_presentacion_planilla=form.cleaned_data.get('tipo_presentacion_planilla'),
                codigo_sucursal=form.cleaned_data.get('codigo_sucursal'),
                nombre_sucursal=form.cleaned_data.get('nombre_sucursal'),

                claseaportante=form.cleaned_data['claseaportante'],
                tipoaportante=form.cleaned_data.get('tipoaportante') or None,

                ajustarnovedad=str(ajustarnovedad)[:2] if ajustarnovedad else '',
            )

            empresa.save()

            data1 = proceso_conceptos(empresa.idempresa)
            data2 = proceso_indicadores(empresa.idempresa)

            if data1 or data2:
                mensaje = f"Hubo problemas al guardar la empresa: {data1} {data2}".strip()
                icono = 'error'
            else:
                mensaje = "Empresa guardada exitosamente"
                icono = 'success'

            response = HttpResponse()
            response['X-Up-Accept-Layer'] = 'true'
            response['X-Up-icon'] = icono
            response['X-Up-message'] = mensaje
            response['X-Up-Location'] = reverse('admin:companies')

            return response
            
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
    


def proceso_conceptos(id):
    try:
        data = Conceptosdenomina.objects.filter(id_empresa_id=1)

        # Si no hay conceptos base en la empresa 1
        if not data.exists():
            return "Error: No hay conceptos base en la empresa 1 para copiar."

        nuevos = []

        for concepto in data:
            nuevos.append(
                Conceptosdenomina(
                    nombreconcepto=concepto.nombreconcepto,
                    multiplicadorconcepto=concepto.multiplicadorconcepto,
                    tipoconcepto=concepto.tipoconcepto,
                    formula=concepto.formula,
                    grupo_dian=concepto.grupo_dian,
                    id_empresa_id=id,
                    codigo=concepto.codigo
                )
            )

        # Inserta TODO de una vez
        Conceptosdenomina.objects.bulk_create(nuevos)

        return ""  # éxito, sin mensaje

    except Exception as e:
        # Para debug / logs
        print("ERROR EN GENERACIÓN DE CONCEPTOS:", str(e))

        return "Error en la generación de conceptos para la empresa."
    
    

def proceso_indicadores(id_empresa_destino):
    try:
        # 1. Conceptos base (empresa 1)
        base_conceptos = Conceptosdenomina.objects.filter(id_empresa_id=1)

        if not base_conceptos.exists():
            return "Error: No hay conceptos base en la empresa 1 para copiar indicadores."

        # 2. Conceptos clonados en la empresa destino
        nuevos_conceptos = Conceptosdenomina.objects.filter(id_empresa_id=id_empresa_destino)

        # Crear mapa por codigo (clave única que ambos comparten)
        mapa_nuevos = {c.codigo: c for c in nuevos_conceptos}

        # 3. Recorrer los conceptos base y replicar sus indicadores
        for concepto_base in base_conceptos:
            indicadores = concepto_base.indicador.all()  # indicadores M2M

            if not indicadores:
                continue

            # Buscar el concepto nuevo correspondiente
            concepto_nuevo = mapa_nuevos.get(concepto_base.codigo)

            if not concepto_nuevo:
                print(f"No se encontró concepto nuevo para código {concepto_base.codigo}")
                continue

            # Asignar M2M
            concepto_nuevo.indicador.set(indicadores)

        return ""

    except Exception as e:
        print("ERROR en proceso_indicadores:", str(e))
        return "Error al generar los indicadores de los conceptos."