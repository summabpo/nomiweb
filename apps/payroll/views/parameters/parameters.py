from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Bancos ,Festivos , Entidadessegsocial,Conceptosfijos , Salariominimoanual

from apps.payroll.forms.PayrollForm import PayrollForm
from django.contrib import messages
from .forms import BanksForm ,HolidaysForm , EntitiesForm ,FixedForm , AnnualForm



@login_required
@role_required('accountant')
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
@role_required('accountant')
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
@role_required('accountant')
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
                # Crear instancia de Crearnomina
                Festivos.objects.create(
                    fecha=form.cleaned_data['fecha'],
                    descripcion=form.cleaned_data['descripcion']
                )

                messages.success(request, "Nómina creada exitosamente.")
                return redirect('payroll:payroll')  # Redirigir a una vista de lista, por ejemplo
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
@role_required('accountant')
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
@role_required('accountant')
def annual(request):
    wages = Salariominimoanual.objects.all().order_by('idano')
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

