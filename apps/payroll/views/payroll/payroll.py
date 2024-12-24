from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Crearnomina , Tipodenomina ,Subcostos,Costos,Conceptosdenomina , Empresa , Anos , Nomina , Contratos
from apps.payroll.forms.PayrollForm import PayrollForm
from django.contrib import messages
from .common import generar_nombre_nomina , MES_CHOICES
from apps.payroll.forms.ConceptForm import ConceptForm
from datetime import timedelta


# @login_required
# @role_required('employee')
def payroll(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    form = PayrollForm()
    nominas = Crearnomina.objects.filter(estadonomina=True, id_empresa_id=idempresa).order_by('-idnomina')
    error = False

    if request.method == 'POST':
        form = PayrollForm(request.POST)
        if form.is_valid():
            try:
                # Obtener datos del formulario
                tiponomina_id = form.cleaned_data['tiponomina']

                # Buscar los objetos relacionados
                tiponomina = Tipodenomina.objects.get(idtiponomina=tiponomina_id)

                # Calcular mes y año acumulados a partir de fechainicial
                fechainicial = form.cleaned_data['fechainicial']
                fechafinal = form.cleaned_data['fechafinal']

                # Calcular días de nómina
                dias_nomina = (fechafinal - fechainicial).days + 1  # Incluir día inicial

                mes_numero = fechainicial.month  # Obtener el número del mes (1-12)
                mes_acumular = MES_CHOICES[mes_numero][0] if mes_numero else ''
                
                ano_acumular = Anos.objects.get(ano=fechainicial.year)  # Año de la fecha
                
                tipo_nomina_text = tiponomina.tipodenomina 

                empresa = Empresa.objects.get(idempresa=idempresa)

                # Crear instancia de Crearnomina
                Crearnomina.objects.create(
                    nombrenomina=generar_nombre_nomina(tipo_nomina_text, fechainicial),
                    fechainicial=fechainicial,
                    fechafinal=fechafinal,
                    fechapago=form.cleaned_data['fechapago'],
                    tiponomina=tiponomina,
                    mesacumular=mes_acumular,
                    anoacumular=ano_acumular,
                    estadonomina=True, 
                    diasnomina=dias_nomina,  # Usamos el cálculo aquí
                    id_empresa=empresa,
                )

                messages.success(request, "Nómina creada exitosamente.")
                return redirect('payroll:payroll')  # Redirigir a una vista de lista, por ejemplo
            except (Tipodenomina.DoesNotExist, Empresa.DoesNotExist):
                messages.error(request, "Hubo un problema al procesar la información.")

        else:
            error = True
            # Si el formulario no es válido, recopilamos todos los errores y los mostramos en un solo mensaje
            error_message = "Por favor, corrija los siguientes errores:"
            for field in form:
                for error in field.errors:
                    error_message += f"\n- {error}"

            messages.error(request, error_message)
    
    return render(request, './payroll/payroll.html', {'nominas': nominas, 'form': form, 'error': error})
   


def payrollview(request, id):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    empleados = Contratos.objects\
        .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede') \
        .order_by('idempleado__papellido') \
        .filter(estadocontrato=1, id_empresa=idempresa) \
        .values(
            'idempleado__docidentidad', 'idempleado__papellido', 'idempleado__pnombre',
            'idempleado__snombre', 'salario', 'idempleado__idempleado', 'idempleado__sapellido', 'idcontrato'
        )
    


    nombre = Crearnomina.objects.get(idnomina=id)
    # Inicializamos 'nomina' para cuando no se filtra
    nomina = Nomina.objects.filter(idnomina_id=id).order_by('idregistronom')
    form1 = ConceptForm(idempresa=idempresa)
    form2 = ConceptForm(idempresa=idempresa, form_id='form_custom_payroll_concept', dropdown_parent='#kt_modal_concept_used')
    error = False

    if request.method == 'GET':
        # Filtrar por user_id si se proporciona
        user_id = request.GET.get('user_id')  # O usar request.user.id si es el usuario logueado
        if user_id:
            nomina = Nomina.objects.filter(usuario_id=user_id,idnomina_id=id).order_by('idregistronom')  # Suponiendo que 'usuario_id' es el campo correcto
        else:
            # Si no se proporciona user_id, no filtrar
            nomina = Nomina.objects.filter(idnomina_id=id).order_by('idregistronom')

    if request.method == 'POST':
        # Procesar formulario 1 con submit_1
        if 'submit_full' in request.POST:
            form1 = ConceptForm(request.POST, idempresa=idempresa)
            if form1.is_valid():
                concepto = Conceptosdenomina.objects.get(idconcepto=form1.cleaned_data['idconcepto'])
                crear = Crearnomina.objects.get(idnomina=id)
                contratos = Contratos.objects.get(idcontrato=form1.cleaned_data['idcontrato'])
                costos = Costos.objects.get(idcosto=contratos.idcosto.idcosto)
                sub = Subcostos.objects.get(idsubcosto=contratos.idsubcosto.idsubcosto) if contratos.idsubcosto else None

                Nomina.objects.create(
                    valor=form1.cleaned_data['valor'],
                    cantidad=form1.cleaned_data['cantidad'],
                    idconcepto=concepto,
                    idnomina=crear,
                    estadonomina=crear.estadonomina,
                    idcontrato=contratos,
                    idcosto=costos,
                    idsubcosto=sub,
                    control=0,  # vacaciones o incapacidades o prestamos automatico
                )
                
                messages.success(request, "Concepto agregado exitosamente.")
                return redirect('payroll:payrollview')
            else:
                form1 = ConceptForm(idempresa=idempresa)

        # Procesar formulario 1 con submit_2
        elif 'submit_direct' in request.POST:
            form2 = ConceptForm(request.POST, idempresa=idempresa)
            print(request.POST)
            if form2.is_valid():
                
                pass
            else:
                form2 = ConceptForm(idempresa=idempresa)

    return render(request, './payroll/payrollviews.html', {
        'nomina': nomina,
        'nombre':nombre,
        'form1': form1,
        'form2': form2,
        'error': error,
        'empleados': empleados,
    })




