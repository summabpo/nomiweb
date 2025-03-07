from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Crearnomina , Tipodenomina ,Subcostos,Costos,Conceptosdenomina , Empresa , Anos , Nomina , Contratos
from apps.payroll.forms.PayrollForm import PayrollForm
from apps.payroll.forms.updateForm import UpdateForm
from django.contrib import messages
from .common import generar_nombre_nomina , MES_CHOICES
from apps.payroll.forms.ConceptForm import ConceptForm
from datetime import timedelta
from django.http import JsonResponse
from django.views import View
from apps.components.humani import format_value
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
import random
from django.http import HttpResponse
from decimal import Decimal
from django.views.decorators.http import require_GET

@login_required
@role_required('accountant')
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
    
    
    
    


@login_required
@role_required('accountant')
def payrollview(request, id):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']


    empleados = Nomina.objects \
        .select_related('idcontrato') \
        .filter(idnomina=id) \
        .values(
            'idcontrato__idempleado__docidentidad', 'idcontrato__idempleado__papellido',
            'idcontrato__idempleado__pnombre', 'idcontrato__idempleado__snombre',
            'idcontrato__salario', 'idcontrato__idempleado__idempleado', 
            'idcontrato__idempleado__sapellido', 'idcontrato'
        ) \
        .order_by('idcontrato__idempleado__papellido') \
        .distinct()

    nombre = Crearnomina.objects.get(idnomina=id)
    # Inicializamos 'nomina' para cuando no se filtra
    nomina = Nomina.objects.filter(idnomina_id=id).order_by('idregistronom')
    
    return render(request, './payroll/payrollviews.html', {
        'nomina': nomina,
        'nombre':nombre,
        'empleados': empleados,
        'id': id
    })

# @login_required
# @role_required('accountant')
# def payroll_modal(request,id,idnomina):
#     usuario = request.session.get('usuario', {})
#     idempresa = usuario['idempresa']
#     ingreso = 0  # Inicializamos la variable ingreso
#     egreso = 0   # Inicializamos la variable egreso
#     conceptos_data = []
    
    
#     contrato = Contratos.objects.select_related('idempleado').get(idcontrato=id)


#     conceptos = Nomina.objects.filter(
#         idnomina__idnomina=idnomina,
#         idcontrato__idcontrato=id
#     ).select_related('idcontrato').order_by('idconcepto__codigo')
    
    
    
    
    
#     data = {}
#     data['valor'] = random.randint(1, 100)
#     return render(request, './payroll/partials/payrollmodal2.html',data)



@login_required
@role_required('accountant')
def payroll_modal(request,id,idnomina):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    ingreso = 0  # Inicializamos la variable ingreso
    egreso = 0   # Inicializamos la variable egreso
    conceptos_data = []
    
    contrato = Contratos.objects.select_related('idempleado').get(idcontrato=id)


    conceptos = Nomina.objects.filter(
        idnomina__idnomina=idnomina,
        idcontrato__idcontrato=id
    ).select_related('idcontrato').order_by('idconcepto__codigo')
    
    
    # Verificar si hay conceptos encontrados
    if not conceptos.exists():
        return JsonResponse({"error": "No se encontraron conceptos para este empleado y nómina"}, status=404)

    
    # Optimizar consulta del contrato
    contrato = Contratos.objects.select_related('idempleado').get(idcontrato=id)

    # Estructurar los datos para la respuesta
    for concepto in conceptos:
        # Crear el diccionario con los datos del concepto
        concepto_info = {
            'idn': concepto.idregistronom,
            "id": concepto.idconcepto.idconcepto,
            "amount": concepto.cantidad,
            "value": concepto.valor,
        }
        
        # Agregar el concepto al arreglo
        conceptos_data.append(concepto_info)
        
        # Revisar si el valor es mayor que 0 (ingreso) o negativo (egreso)
        if concepto.valor > 0:
            ingreso += concepto.valor  # Agregar a ingreso si es positivo
        elif concepto.valor < 0:
            egreso += concepto.valor 

    
    # Construir el nombre completo
    empleado = contrato.idempleado
    nombre_completo = " ".join(filter(None, [empleado.papellido, empleado.sapellido, empleado.pnombre, empleado.snombre]))

    total = ingreso + egreso
        
    data = {
        "idnomina":idnomina,
        "idempleado" :id,
        "nombre": nombre_completo,
        "cargo": contrato.cargo,
        "salario": f"${format_value(contrato.salario)}",
        "ingresos": f"${format_value(ingreso)}",
        "egresos": f"${format_value(egreso)}",
        "total": f"${format_value(total)}",
        "idnomina": idnomina,
        "id":id , 
        "conceptos": conceptos_data,
        "conceptors": [(item.idconcepto, f"{item.codigo} - {item.nombreconcepto}") for item in Conceptosdenomina.objects.filter(id_empresa_id=idempresa).order_by('codigo') ]
        
    }
    
    return render(request, './payroll/partials/payrollmodal2.html',{'data': data})




@login_required
@role_required('accountant')
def payroll_create(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    conceptos_data = []
    if request.method == 'POST':
        # Procesar los datos del formulario
        mi_select = request.POST.get('concept')
        cantidad = request.POST.get('cantidad')
        valor = request.POST.get('valor')
        idnomina = request.POST.get('idnomina')
        id = request.POST.get('idempleado')

        Nomina.objects.create(
            idconcepto_id=mi_select,
            cantidad=cantidad,
            valor=int(valor.replace(',', '')),
            idcontrato_id=id,
            idnomina_id=idnomina,
        )
        
        
        conceptos = Nomina.objects.filter(
                idnomina__idnomina=idnomina,
                idcontrato__idcontrato=id
            ).select_related('idcontrato').order_by('idconcepto__codigo')
            
        
        for concepto in conceptos:
            # Crear el diccionario con los datos del concepto
            concepto_info = {
                'idn': concepto.idregistronom,
                "id": concepto.idconcepto.idconcepto,
                "amount": concepto.cantidad,
                "value": concepto.valor,
            }
            
            # Agregar el concepto al arreglo
            conceptos_data.append(concepto_info)
        
    data = {    
        "conceptos": conceptos_data,
        "value": True,
        "conceptors": [(item.idconcepto, f"{item.codigo} - {item.nombreconcepto}") for item in Conceptosdenomina.objects.filter(id_empresa_id=idempresa).order_by('codigo') ]
    }
    return render(request, './payroll/partials/concepts_list.html', {'data': data})




def payroll_edit(request):
    if request.method == 'POST':
        data = request.POST
        idn = data.get('idn')
        amount = data.get('amount').replace(',', '.')  # Reemplazamos la coma por un punto
        value = data.get('value')
        concept = data.get('concept')
        try:
            value_decimal = Decimal(value)
            # Obtener el concepto por ID
            concepto_obj = Nomina.objects.get(idregistronom=idn)
            
            concepto_obj.idconcepto_id = concept  # Asigna el ID del concepto (no el objeto completo)
            concepto_obj.cantidad = amount
            concepto_obj.valor = value_decimal
            concepto_obj.save()
        except Nomina.DoesNotExist: 
            return JsonResponse(f"No se encontró el concepto con ID {idn}.")
            
        return JsonResponse({'mensaje': 'Concepto actualizado correctamente'})
    print(request.method)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required
@role_required('accountant')
def payroll_delete(request, idn):
    concepto = get_object_or_404(Conceptosdenomina, idn=idn)
    concepto.delete()
    return HttpResponse(status=204)  # Respuesta sin contenido (eliminación exitosa)



@require_GET
def payroll_value(request):
    print('Solicitud recibida:', request.GET)
    print('llege')
    cantidad = int(request.GET.get('cantidad', 0))
    sueldo = 1400000  # Sueldo base
    valor = cantidad * sueldo
    # Devuelve un fragmento de HTML con el valor calculado
    return HttpResponse(f"<input type='number' id='valor' name='valor' class='form-control mb-2 mb-md-0' value='{valor}' readonly />")






@login_required
@role_required('accountant')
def payroll_general(request,idnomina):
    
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    contratos_empleados = Contratos.objects\
        .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede') \
        .filter(estadocontrato=1,id_empresa_id =  idempresa) \
        .values('idempleado__docidentidad', 'idempleado__papellido', 'idempleado__pnombre',
                'idempleado__snombre', 'cargo__nombrecargo', 'idcontrato')
    
    dato = {
        'contratos_empleados': contratos_empleados,
        'idnomina': idnomina
    }
        
    return render(request, './payroll/partials/payroll_general.html',{'dato': dato})


@login_required
@role_required('accountant')
def payroll_general_data(request,idnomina):
    ingreso = 0  # Inicializamos la variable ingreso
    egreso = 0   # Inicializamos la variable egreso
    conceptos_data = []
    variable = False
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    if request.method == 'POST':
        idcontrato = request.POST.get('contrato_empleado')
        variable = True
        
        conceptos = Nomina.objects.filter(
            idnomina__idnomina=idnomina,
            idcontrato__idcontrato=idcontrato
        ).select_related('idcontrato').order_by('idconcepto__codigo')
            
        # Estructurar los datos para la respuesta
        for concepto in conceptos:
            # Crear el diccionario con los datos del concepto
            concepto_info = {
                'idn': concepto.idregistronom,
                "id": concepto.idconcepto.idconcepto,
                "amount": concepto.cantidad,
                "value": concepto.valor,
            }
            
            # Agregar el concepto al arreglo
            conceptos_data.append(concepto_info)
            
            # Revisar si el valor es mayor que 0 (ingreso) o negativo (egreso)
            if concepto.valor > 0:
                ingreso += concepto.valor  # Agregar a ingreso si es positivo
            elif concepto.valor < 0:
                egreso += concepto.valor 
        
        # Optimizar consulta del contrato
        contrato = Contratos.objects.select_related('idempleado').get(idcontrato=idcontrato)
        
    
    total = ingreso + egreso
    
    
    data = {
        'true': variable,
        "salario": f"${format_value(contrato.salario)}",
        "ingresos": f"${format_value(ingreso)}",
        "egresos": f"${format_value(egreso)}",
        "total": f"${format_value(total)}",
        "idnomina": idnomina,
        "id":idcontrato, 
        "conceptos": conceptos_data,
        "conceptors": [(item.idconcepto, f"{item.codigo} - {item.nombreconcepto}") for item in Conceptosdenomina.objects.filter(id_empresa_id=idempresa).order_by('codigo') ]
    }
    
    return render(request, './payroll/partials/payroll_general_data.html',{'data': data})
    



@login_required
@role_required('accountant')
def payroll_concept_info(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        idconcepto = data.get('idconcepto')
        concepto = Conceptosdenomina.objects.get(idconcepto=idconcepto)
        return JsonResponse({
            'codigo': concepto.codigo,
            'nombreconcepto': concepto.nombreconcepto,
            'tipoconcepto': concepto.tipoconcepto,
        })
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required
@role_required('accountant')
def payroll_calculate(request,id):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    if request.method == 'POST':
        print(id)
        idcontrato = id         
        try:
            cantidad = int(request.POST.get('cantidad', 0))
            print('------------')
            print(cantidad)
            print('------------')
            resultado = cantidad * 2  # Por ejemplo, multiplicar por 2
            return HttpResponse(resultado)  # Solo devolvemos el número, nada de HTML
        except ValueError:
            return HttpResponse("")
    return HttpResponse("")



