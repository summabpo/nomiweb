from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Crearnomina , Tipodenomina , Empresa , Anos , Nomina , Contratos
from apps.payroll.forms.PayrollForm import PayrollForm
from django.contrib import messages
from .common import generar_nombre_nomina , MES_CHOICES
from apps.payroll.forms.ConceptForm import ConceptForm

# @login_required
# @role_required('employee')
def payroll(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    form = PayrollForm()
    nominas = Crearnomina.objects.filter(estadonomina = True , id_empresa_id = idempresa ).order_by('-idnomina')
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
                
                
                mes_numero = fechainicial.month  # Obtener el número del mes (1-12)
                mes_acumular = MES_CHOICES[mes_numero][0] if mes_numero else ''
                
                ano_acumular = Anos.objects.get(ano = fechainicial.year )   # Año de la fecha
                
                tipo_nomina_text = tiponomina.tipodenomina 

                empresa = Empresa.objects.get(idempresa = idempresa)
                print(empresa)
                #Crear instancia de Crearnomina
                Crearnomina.objects.create(
                    nombrenomina = generar_nombre_nomina(tipo_nomina_text, fechainicial),
                    fechainicial=fechainicial,
                    fechafinal=form.cleaned_data['fechafinal'],
                    fechapago=form.cleaned_data['fechapago'],
                    tiponomina=tiponomina,
                    mesacumular=mes_acumular,
                    anoacumular=ano_acumular,
                    estadonomina = True , 
                    diasnomina=form.cleaned_data['diasnomina'],
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
    
    return render(request, './payroll/payroll.html',{'nominas':nominas , 'form':form ,'error': error })
    
    


def payrollview(request , id ):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    empleados = Contratos.objects\
        .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede') \
        .order_by('idempleado__papellido') \
        .filter(estadocontrato = 1 , id_empresa = idempresa) \
        .values(
            'idempleado__docidentidad', 'idempleado__papellido', 'idempleado__pnombre',
            'idempleado__snombre','salario','idempleado__idempleado','idempleado__sapellido', 'idcontrato'
            
        )
    

    nomina = Nomina.objects.filter(idnomina_id = id ).order_by('idregistronom')
    form1 = ConceptForm(idempresa=idempresa)
    form2 = ConceptForm(idempresa=idempresa,dropdown_parent='#kt_modal_concept_used')
    error = False


    if request.method == 'POST':
        form = ConceptForm(request.POST,idempresa=idempresa)
        if form.is_valid():
            try:

                Crearnomina.objects.create(
                    
                )

                messages.success(request, "Concepto agreagado exitosamente.")
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
    

    return render(request, './payroll/payrollviews.html',{'nomina':nomina , 'form1':form1 ,'form2':form2 ,'error': error ,'empleados':empleados})




