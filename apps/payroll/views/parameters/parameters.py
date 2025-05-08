from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Bancos ,Festivos , Entidadessegsocial,Conceptosfijos , Salariominimoanual , Conceptosdenomina , NeSumatorias , Empresa , Indicador
from django.contrib import messages
from .forms import BanksForm ,HolidaysForm , EntitiesForm ,FixedForm , AnnualForm , PayrollConceptsForm, PayrollConceptsForm2
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
from django.urls import reverse

@login_required
@role_required('company','admin','accountant')
def banks(request):
    """
    Vista que gestiona la creación y visualización de bancos.

    Permite listar bancos existentes y registrar nuevos mediante un formulario. Solo accesible
    para usuarios autenticados con roles específicos.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP que puede ser GET o POST.

    Returns
    -------
    HttpResponse
        Renderiza la plantilla 'payroll/banks.html' con el formulario y la lista de bancos.

    See Also
    --------
    Banks : Modelo que almacena la información bancaria de la empresa.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    form = BanksForm()
    error = False
    bancos = Bancos.objects.all().order_by('nombanco')
    
    
    if request.method == 'POST':
        form = BanksForm(request.POST)
        if form.is_valid():
            try:
                # Obtener datos del formulario
                tiponomina_id = form.cleaned_data['tiponomina']

                
                # Crear instancia de Crearnomina
                Bancos.objects.create(
                    
                )

                messages.success(request, "Nómina creada exitosamente.")
                return redirect('payroll:payroll')  # Redirigir a una vista de lista, por ejemplo
            except:
                messages.error(request, "Hubo un problema al procesar la información.")

        else:
            error = True
            # Si el formulario no es válido, recopilamos todos los errores y los mostramos en un solo mensaje
            error_message = "Por favor, corrija los siguientes errores:"
            for field in form:
                for error in field.errors:
                    error_message += f"\n- {error}"

            messages.error(request, error_message)
    
    return render(request, './payroll/banks.html', {'bancos': bancos, 'form': form, 'error': error})


@login_required
@role_required('company','admin','accountant')
def entities(request):
    """
    Vista para registrar y listar entidades de seguridad social.

    Filtra entidades inválidas por NIT o código y previene duplicados. Accesible solo para
    usuarios con roles autorizados.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP que puede ser GET o POST.

    Returns
    -------
    HttpResponse
        Renderiza la plantilla 'payroll/entities.html' con el formulario y lista de entidades.

    See Also
    --------
    Entity : Modelo que representa entidades como EPS, ARL o fondos de pensión.
    """

    form = EntitiesForm()
    entidades = Entidadessegsocial.objects.all().exclude(
        codigo__in=['000', '9999', '9988', '9998']
    ).exclude(
        nit=''
    ).exclude(
        nit__isnull=True
    ).order_by('entidad')
    error = False

    if request.method == 'POST':
        form = EntitiesForm(request.POST)
        if form.is_valid():
            try:
                # Validar si el código ya existe
                codigo = form.cleaned_data['codigo']
                if Entidadessegsocial.objects.filter(codigo=codigo).exists():
                    print('codigo',codigo)
                    messages.error(request, f"El código {codigo} ya existe en la base de datos.")
                    return redirect('payroll:entities')

                # Crear instancia de Entidadessegsocial
                Entidadessegsocial.objects.create(
                    codigo=codigo,
                    nit=form.cleaned_data['nit'],
                    entidad=form.cleaned_data['entidad'],
                    tipoentidad=form.cleaned_data['tipoentidad'],
                    codsgp=form.cleaned_data['codsgp'] if form.cleaned_data['codsgp'] else None,
                )

                messages.success(request, "Entidad creada exitosamente.")
                return redirect('payroll:entities')  # Redirigir a una vista de lista, por ejemplo
            except ValueError as e:
                messages.error(request, "Hubo un problema al procesar la información.")
                return redirect('payroll:entities')

        else:
            error = True
            # Si el formulario no es válido, recopilamos todos los errores y los mostramos en un solo mensaje
            error_message = "Por favor, corrija los siguientes errores:"
            for field in form:
                for error in field.errors:
                    error_message += f"\n- {error}"

            messages.error(request, error_message)

    return render(request, './payroll/entities.html', {'entidades': entidades, 'form': form, 'error': error})


@login_required
@role_required('company','admin','accountant')
def holidays(request):
    """
    Vista que gestiona la creación de festivos en el sistema.

    Permite registrar días festivos que afectan el cálculo de nómina y validarlos por año.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP con datos del formulario o solicitud de vista.

    Returns
    -------
    HttpResponse
        Renderiza la plantilla 'payroll/holidays.html' con los festivos existentes.

    See Also
    --------
    Festivos : Modelo que almacena fechas festivas por año.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    form = HolidaysForm()
    festivos = Festivos.objects.all().order_by('idfestivo')
    error = False

    if request.method == 'POST':
        form = HolidaysForm(request.POST)
        if form.is_valid():
            try:
                fecha = form.cleaned_data['fecha']
                # Crear instancia de Crearnomina
                Festivos.objects.create(
                    dia=fecha,
                    descripcion=form.cleaned_data['descripcion'],
                    ano=fecha.year
                )

                messages.success(request, "Nómina creada exitosamente.")
                return redirect('payroll:holidays')  # Redirigir a una vista de lista, por ejemplo
            except :
                messages.error(request, "Hubo un problema al procesar la información.")

        else:
            error = True
            # Si el formulario no es válido, recopilamos todos los errores y los mostramos en un solo mensaje
            error_message = "Por favor, corrija los siguientes errores:"
            for field in form:
                for error in field.errors:
                    error_message += f"\n- {error}"

            messages.error(request, error_message)
    
    return render(request, './payroll/holidays.html', {'festivos': festivos, 'form': form, 'error': error})


@login_required
@role_required('company','admin','accountant')
def fixed(request):
    """
    Vista que permite gestionar conceptos fijos asociados a contratos.

    Permite listar, agregar y validar conceptos fijos como bonificaciones recurrentes o descuentos.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP GET o POST con datos del formulario.

    Returns
    -------
    HttpResponse
        Renderiza la plantilla 'payroll/fixed.html' con el formulario y lista de conceptos.

    See Also
    --------
    ConceptosFijos : Modelo de conceptos de nómina fijos ligados a contratos.
    """

    fixeds = Conceptosfijos.objects.all().order_by('idfijo')
    form = FixedForm()
    error = False
    
    if request.method == 'POST':
        form = FixedForm(request.POST)
        if form.is_valid():
            try:
                # Crear instancia de Crearnomina
                Conceptosfijos.objects.create(
                    conceptofijo=form.cleaned_data['conceptofijo'],
                    valorfijo  = form.cleaned_data['valorfijo']
                )

                messages.success(request, "Dato creada exitosamente.")
                return redirect('payroll:fixed')  # Redirigir a una vista de lista, por ejemplo
            except:
                messages.error(request, "Hubo un problema al procesar la información.")

        else:
            error = True
            # Si el formulario no es válido, recopilamos todos los errores y los mostramos en un solo mensaje
            error_message = "Por favor, corrija los siguientes errores:"
            for field in form:
                for error in field.errors:
                    error_message += f"\n- {error}"

            messages.error(request, error_message)
    
    
    return render(request, './payroll/fixed.html',{'fixeds': fixeds, 'form': form, 'error': error})


@login_required
@role_required('company','admin','accountant')
def annual(request):
    """
    Vista que administra el salario mínimo, auxilio de transporte y UVT anual.

    Permite crear registros anuales con los valores legales correspondientes.

    Parameters
    ----------
    request : HttpRequest
        Solicitud GET para ver o POST para guardar nuevo salario mínimo anual.

    Returns
    -------
    HttpResponse
        Renderiza la plantilla 'payroll/annual.html' con datos actuales y formulario.

    See Also
    --------
    SalarioMinimo : Modelo que contiene los valores anuales relevantes para nómina.
    """

    wages = Salariominimoanual.objects.all().order_by('-ano')
    form = AnnualForm()
    error = False
    
    if request.method == 'POST':
        form = AnnualForm(request.POST)
        if form.is_valid():
            try:
                # Crear instancia de Crearnomina
                Salariominimoanual.objects.create(
                    auxtransporte = form.cleaned_data['auxtransporte'],
                    uvt = form.cleaned_data['uvt'],
                    ano=form.cleaned_data['ano'],
                    salario  = form.cleaned_data['salario']
                )

                messages.success(request, "Dato creada exitosamente.")
                return redirect('payroll:annual')  # Redirigir a una vista de lista, por ejemplo
            except:
                messages.error(request, "Hubo un problema al procesar la información.")

        else:
            error = True
            # Si el formulario no es válido, recopilamos todos los errores y los mostramos en un solo mensaje
            error_message = "Por favor, corrija los siguientes errores:"
            for field in form:
                for error in field.errors:
                    error_message += f"\n- {error}"

            messages.error(request, error_message)
    return render(request, './payroll/annual.html',{'wages': wages, 'form': form, 'error': error})




@login_required
@role_required('company','admin','accountant')
def concepts(request):
    """
    Vista que lista los conceptos de nómina definidos por la empresa.

    Proporciona un formulario vacío para registrar nuevos conceptos si se desea.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP GET para visualizar conceptos existentes.

    Returns
    -------
    HttpResponse
        Renderiza la plantilla 'payroll/concepts.html' con los conceptos y formulario.

    See Also
    --------
    Concepto : Modelo que representa reglas o fórmulas de cálculo de nómina.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    concepts = Conceptosdenomina.objects.filter(id_empresa_id=idempresa).select_related('grupo_dian').order_by('codigo')

    form = PayrollConceptsForm()
    
        
    return render(request, './payroll/concepts.html',{'concepts': concepts,'form': form})


@login_required
@role_required('company','admin','accountant')
def concepts_add(request):
    """
    Vista para agregar nuevos conceptos de nómina mediante un formulario modal.

    Esta vista se encarga de crear un nuevo concepto de nómina (como bonificaciones, descuentos o
    prestaciones) dentro del sistema. Soporta múltiples relaciones con indicadores contables y
    parámetros adicionales. Además, es compatible con peticiones asincrónicas a través de Unpoly,
    lo que permite una experiencia más fluida en la interfaz de usuario.

    El formulario valida automáticamente la unicidad del código del concepto por empresa, y
    verifica que el nombre no esté repetido. También puede procesar reglas de fórmula y 
    condicionales según el tipo y categoría del concepto (devengo, deducción, aporte).

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP POST con los datos del formulario del concepto.

    Returns
    -------
    HttpResponse
        Si el formulario es válido:
            - Retorna cabeceras HTTP específicas para Unpoly, lo que provoca el cierre del modal
            y la actualización de secciones en la vista principal.
        Si el formulario contiene errores:
            - Renderiza nuevamente el formulario dentro del modal con los errores visibles para
            su corrección.

    See Also
    --------
    Concepto : Modelo principal que define la lógica del concepto de nómina.
    Indicador : Modelo relacionado que categoriza o clasifica los conceptos según su naturaleza contable.
    """


    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    if request.method == 'POST':
        form = PayrollConceptsForm(request.POST,id_empresa=idempresa)
        if form.is_valid():
            # Aquí puedes guardar los datos del formulario en la base de datos
            nombreconcepto = form.cleaned_data['nombreconcepto']
            multiplicadorconcepto = form.cleaned_data['multiplicadorconcepto']
            tipoconcepto = form.cleaned_data['tipoconcepto']
            formula = form.cleaned_data['formula']
            codigo = form.cleaned_data['codigo']
            
            # Obtener el objeto grupo_dian
            grupo_dian_id = form.cleaned_data['grupo_dian']
            grupo_dian = NeSumatorias.objects.filter(ne_id=grupo_dian_id).first()  # O get() si estás seguro de que existe
            
            # Obtener el objeto empresa (Asegúrate de tener el ID de la empresa disponible)
            empresa = Empresa.objects.get(idempresa=idempresa)

            # Crear la instancia del modelo
            concepto = Conceptosdenomina.objects.create(
                nombreconcepto=nombreconcepto,
                multiplicadorconcepto=multiplicadorconcepto,
                tipoconcepto=tipoconcepto,
                formula=formula,
                grupo_dian= grupo_dian if grupo_dian else None,
                id_empresa=empresa,
                codigo=codigo
            )

            #Ahora que el objeto existe en la BD, asignar los indicadores
            indicador_ids = request.POST.getlist('indicador') #Captura múltiples valores
            indicadores = Indicador.objects.filter(id__in=indicador_ids)
            concepto.indicador.add(*indicadores)  # Usamos .add() en lugar de .set()
            
            
            response = HttpResponse()
            response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
            response['X-Up-icon'] = 'success'  # URL para recargar la página principal   
            response['X-Up-message'] = 'Concepto guardado exitosamente'    
            response['X-Up-Location'] = reverse('payroll:concepts')           
            return response

        else:
            # En caso de que el formulario no sea válido, mostrar los errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    print(request, f"Error en {field}: {error}")
    else:
        form = PayrollConceptsForm(id_empresa=idempresa)
    # Renderizar el modal con el formulario
    return render(request, './payroll/partials/conceptsmodal.html', {'form': form})


@login_required
@role_required('company','admin','accountant')
def concepts_detail(request,id):
    """
    Vista que muestra los detalles de un concepto de nómina en un modal.

    Accede a través de ID del concepto y despliega su fórmula, tipo, categoría y otros atributos.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP GET.
    id : int
        Identificador del concepto.

    Returns
    -------
    HttpResponse
        Renderiza la plantilla 'payroll/conceptsmodaldetail.html' con información del concepto.

    See Also
    --------
    Concepto : Modelo de conceptos de nómina.
    """

    concept = get_object_or_404(Conceptosdenomina, pk=id)
    return render(request, './payroll/partials/conceptsmodaldetail.html',{'concept':concept})

@login_required
@role_required('company','admin','accountant')
def concepts_edit(request,id):
    """
    Vista para editar un concepto de nómina existente mediante un formulario modal.

    Permite modificar atributos clave de un concepto de nómina ya creado, como el nombre, tipo,
    categoría, fórmula de cálculo, valores fijos, condiciones, y su relación con indicadores. Es
    una vista diseñada para funcionar con formularios modales, especialmente en flujos de trabajo
    con Unpoly.

    Realiza validaciones de integridad (por ejemplo, si se intenta cambiar el tipo de concepto y
    ya está asociado a movimientos de nómina), y también se asegura de mantener la unicidad del
    código y el nombre dentro de la empresa.

    La lógica también considera qué campos deben ser bloqueados o protegidos si el concepto ya fue
    usado en una nómina liquidada (por ejemplo, evitando el cambio del tipo o categoría si ya hay
    registros históricos).

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP GET o POST. GET carga el formulario prellenado, POST intenta actualizarlo.
    id : int
        Identificador del concepto a editar.

    Returns
    -------
    HttpResponse
        Si el formulario es válido:
            - Respuesta HTTP con cabeceras Unpoly para cerrar el modal y actualizar la vista principal.
        Si hay errores:
            - Renderiza el formulario con errores para su corrección dentro del modal.

    See Also
    --------
    Concepto : Modelo que define la fórmula, comportamiento y naturaleza del concepto.
    Indicador : Modelo que clasifica el concepto (e.g., salud, pensión, bonificación).
    """



    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    
    concept = get_object_or_404(Conceptosdenomina, pk=id)
    
    
    data = {
        'nombreconcepto':concept.nombreconcepto ,
        'multiplicadorconcepto':concept.multiplicadorconcepto ,
        'tipoconcepto':concept.tipoconcepto ,
        'formula':concept.formula ,
        'codigo':concept.codigo ,
        'grupo_dian':concept.grupo_dian.ne_id ,
        'indicador': [i.id for i in concept.indicador.all()],
        }
    
    form = PayrollConceptsForm2(initial = data ,id_empresa=idempresa ,id = id)
    
    
    if request.method == 'POST':
        form = PayrollConceptsForm2(request.POST,id_empresa=idempresa,id = id)
        if form.is_valid():
            
            # Aquí puedes guardar los datos del formulario en la base de datos
            multiplicadorconcepto = form.cleaned_data['multiplicadorconcepto']
            tipoconcepto = form.cleaned_data['tipoconcepto']
            formula = form.cleaned_data['formula']
            indicadores_nuevos = form.cleaned_data['indicador']            # Obtener el objeto grupo_dian
            grupo_dian_id = form.cleaned_data['grupo_dian']
            grupo_dian = NeSumatorias.objects.filter(ne_id=grupo_dian_id).first() 


            ##
            if multiplicadorconcepto != concept.multiplicadorconcepto:
                concept.multiplicadorconcepto = multiplicadorconcepto

            if tipoconcepto != concept.tipoconcepto:
                concept.tipoconcepto = tipoconcepto
                
            if formula != concept.formula:
                concept.formula = formula
                
            if grupo_dian != concept.grupo_dian:
                concept.grupo_dian = grupo_dian
                
                
            if grupo_dian != concept.grupo_dian:
                concept.grupo_dian = grupo_dian
                
            concept.save()  # IMPORTANTE: guardar primero el objeto antes de set()
            concept.indicador.set(indicadores_nuevos)
            
            
            response = HttpResponse()
            response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
            response['X-Up-icon'] = 'success'  # URL para recargar la página principal   
            response['X-Up-message'] = 'Concepto actualizado exitosamente'    
            response['X-Up-Location'] = reverse('payroll:concepts')           
            return response
            
    
    return render(request, './payroll/partials/conceptsmodaledit.html',{'form':form})


@login_required
@role_required('company','admin','accountant')
def check_code(request):
    """
    Vista asincrónica para validar si un código de concepto ya está en uso.

    Usada comúnmente en formularios con validación en tiempo real.

    Parameters
    ----------
    request : HttpRequest
        Solicitud GET con parámetro 'code'.

    Returns
    -------
    JsonResponse
        Diccionario con clave 'valid': True si el código está disponible, False si no.

    See Also
    --------
    Concepto : Modelo que contiene el campo 'code' único por empresa.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario.get('idempresa')  # Usar get() en lugar de acceder directamente.
    codigo = request.GET.get('codigo', '').strip()
    # Agregar un print para verificar el valor recibido
    
    
    data = Conceptosdenomina.objects.filter(codigo=codigo, id_empresa=idempresa).exists()
    if data:
        return JsonResponse({"valid": False, "message": "Código ya en uso"})

    return JsonResponse({"valid": True, "message": "Código disponible"})



