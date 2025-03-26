from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Bancos ,Festivos , Entidadessegsocial,Conceptosfijos , Salariominimoanual , Conceptosdenomina , NeSumatorias , Empresa , Indicador
from django.contrib import messages
from .forms import BanksForm ,HolidaysForm , EntitiesForm ,FixedForm , AnnualForm , PayrollConceptsForm
from django.http import HttpResponse
from django.http import JsonResponse

@login_required
@role_required('company','admin')
def banks(request):
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
@role_required('company','admin')
def entities(request):

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
@role_required('company','admin')
def holidays(request):
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
@role_required('company','admin')
def fixed(request):
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
@role_required('company','admin')
def annual(request):
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
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    concepts = Conceptosdenomina.objects.filter(id_empresa_id=idempresa).select_related('grupo_dian').order_by('codigo')

    form = PayrollConceptsForm()
    
        
    return render(request, './payroll/concepts.html',{'concepts': concepts,'form': form})


@login_required
@role_required('company','admin','accountant')
def concepts_add(request):
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
            
            #return JsonResponse({'status': 'success', 'message': 'Concepto guardado exitosamente'})
            messages.success(request, "Concepto guardado exitosamente")
            return redirect('apartment:apartment_home')
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
def check_code(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario.get('idempresa')  # Usar get() en lugar de acceder directamente.
    codigo = request.GET.get('codigo', '').strip()
    print('codigo recibido:', codigo)  # Agregar un print para verificar el valor recibido
    
    
    data = Conceptosdenomina.objects.filter(codigo=codigo, id_empresa=idempresa).exists()
    print('data:',data)
    if data:
        print('Código ya en uso:',data)
        return JsonResponse({"valid": False, "message": "Código ya en uso"})

    print('Código disponible:', codigo)
    return JsonResponse({"valid": True, "message": "Código disponible"})
