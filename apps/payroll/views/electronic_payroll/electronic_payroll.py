import datetime
from django.shortcuts import render, redirect, get_object_or_404
import json
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import F, Q, Case, When, Value, CharField
from django.db.models.functions import Concat

from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required

# models
from apps.common.models import Anos, Nomina, Contratos, Contratosemp, NeDatosMensual, NeDetalleNominaElectronica, NeRespuestaDian, Ciudades, Paises, Empresa

# forms
from apps.payroll.forms.PayrollContainerForm import PayrollContainerForm


# create and view the electronic payroll container
@login_required
@role_required('accountant')
def electronic_payroll_container(request):
    #variables
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    empresa = get_object_or_404(Empresa, idempresa=idempresa)
    form_errors = False

    # container payroll
    container = NeDatosMensual.objects.filter(empresa=idempresa).order_by('-idnominaelectronica')

    # Formulario Vacantes
    if request.method == 'POST': 
        form = PayrollContainerForm(request.POST)
        if form.is_valid():
            # current date and time data
            fechageneracion = datetime.datetime.now().strftime('%Y-%m-%d')
            horageneracion = datetime.datetime.now().strftime('%H:%M:%S')
            fechaliquidacioninicio = form.cleaned_data['fechaliquidacioninicio']
            fechaliquidacionfin = form.cleaned_data['fechaliquidacionfin']
            prefijo = form.cleaned_data['prefijo']
            # consecutivo = form.cleaned_data['consecutivo']
            ciudad = Ciudades.objects.get(idciudad=form.cleaned_data['ciudadgeneracion'])
            ciudadgeneracion = ciudad.codciudad
            ciudaddepartamento = ciudad.coddepartamento
            departamentogeneracion = ciudad.coddepartamento
            periodonomina = form.cleaned_data['periodonomina']
            fechapago = form.cleaned_data['fechapago']
            mesacumular = form.cleaned_data['mesacumular']
            anoacumular = form.cleaned_data['anoacumular']

            #TODO
            paisgeneracion = 'CO'
            idioma = 'es'
            tipomoneda = 'COP'
            
            # Save the form data to the model
            NeDatosMensual.objects.create(
                fechaliquidacioninicio=fechaliquidacioninicio,
                fechaliquidacionfin=fechaliquidacionfin,
                fechageneracion=fechageneracion,
                prefijo=prefijo,
                consecutivo=None,
                paisgeneracion=paisgeneracion,
                departamentogeneracion=departamentogeneracion,
                ciudadgeneracion=ciudadgeneracion,
                idioma=idioma,
                horageneracion=horageneracion,
                periodonomina=periodonomina,
                tipomoneda=tipomoneda,
                fechapago=fechapago,
                ciudaddepartamento=ciudaddepartamento,
                mesacumular=mesacumular,
                anoacumular=anoacumular,
                empresa=empresa
            )

            messages.success(request, f'Se ha creado el contenedor para el  .')
            return redirect('payroll:nomina_electronica')
        else:
            form_errors = True
            messages.error(request, form.errors)
    else:
        form = PayrollContainerForm()

    context = {
        'container': container,
        'form': form,
        'form_errors': form_errors
    }
    return render(request, './payroll/electronic_payroll_container.html', context)

#create and view detail electronic payroll
@login_required
@role_required('accountant')
def electronic_payroll_detail(request, id):
    container = NeDatosMensual.objects.get(idnominaelectronica=id)
    #data view the detail of the electronic payroll
    detail = NeDetalleNominaElectronica.objects.filter(id_ne_datos_mensual=container.idnominaelectronica)

    context = {
        detail: detail,
    }

    return render(request, './payroll/electronic_payroll_detail.html', context)

#create and view detail electronic payroll
@login_required
@role_required('accountant')
def electronic_payroll_generate(request, pk):
    container = NeDatosMensual.objects.get(idnominaelectronica=pk)
    month = container.mesacumular
    year = container.anoacumular
    
    # Validate the year and get the id from the Anos model
    try:
        ano = Anos.objects.get(ano=year)
        ano_id = ano.idano
    except Anos.DoesNotExist:
        messages.error(request, 'El año especificado no existe en el sistema.')
        return redirect('payroll:nomina_electronica')
    
    empresa_id = container.empresa.idempresa



    #query the detail of the electronic payroll
    query_detail = Nomina.objects.select_related(
                        'idcontrato__idempleado',
                        'idnomina__anoacumular',
                    ).filter(
                        idcontrato__id_empresa=empresa_id,
                        idcontrato__estadocontrato=1,
                        idnomina__mesacumular=month,
                        idnomina__anoacumular=ano_id
                    ).values(
                            id = F('idcontrato'),
                            employee_name = Concat(
                                F('idcontrato__idempleado__papellido'),
                                Value(' '),
                                F('idcontrato__idempleado__sapellido'),
                                Value(' '),
                                F('idcontrato__idempleado__pnombre'),
                                Value(' '),
                                F('idcontrato__idempleado__snombre'),
                            ),
                            month = F('idnomina__mesacumular'),
                            year = F('idnomina__anoacumular__ano'),
                        employee_identification = F('idcontrato__idempleado__docidentidad')
                    ).distinct('idcontrato').order_by(
                        'idcontrato'
                    )
    
    # .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede')

    # Iterate over each field in query_detail
    for detail in query_detail:
        print(f"ID: {detail['id']}")
        print(f"Employee Name: {detail['employee_name']}")
        print(f"Month: {detail['month']}")
        print(f"Year: {detail['year']}")
        print(f"Employee Identification: {detail['employee_identification']}")

        query_payroll = Nomina.objects.select_related(
            'idcontrato',
            'idconcepto__grupo_dian'
        ).filter(
            idcontrato=detail['id'],
            idnomina__mesacumular=month,
            idnomina__anoacumular=ano_id
        ).values(
            concepto = F('idconcepto__nombreconcepto'),
            concepto_dian = F('idconcepto__grupo_dian__campo'),
            valor_anotado = F('valor'),
            anotado = F('cantidad'),
            control_id = F('control'),
            tipo_concepto = F('idconcepto__tipoconcepto'),
        )

        for payroll in query_payroll:
            # print(f"Concepto: {payroll['concepto']}")
            # print(f"Concepto DIAN: {payroll['concepto_dian']}")
            # print(f"Valor Anotado: {payroll['valor_anotado']}")
            # print(f"Cantidad Anotada: {payroll['anotado']}")
            # print(f"Control ID: {payroll['control_id']}")

            # validation of the concepts
            if payroll['concepto_dian'] == 'SueldoTrabajado':   
                print(f"Concepto: {payroll['concepto']}")
                print(f"Concepto DIAN: {payroll['concepto_dian']}")
                print(f"Valor Anotado: {payroll['valor_anotado']}")
                print(f"Cantidad Anotada: {payroll['anotado']}")
                print(f"Control ID: {payroll['control_id']}")
                print(f"Tipo de Concepto: {payroll['tipo_concepto']}")
        







    context = {
        'query_detail' : query_detail,
    }
    
    return render(request, './payroll/electronic_payroll_generate.html', context)


def electronic_payroll(request):

    data = {}
    
    canal = 2
    redondeo = 2
    DevengadosTotal = 2
    DeduccionesTotal = 2
    ComprobanteTotal = 2

    # Información del canal
    data["canal"] = canal

    # Información del periodo
    data["Periodo"] = {
        "FechaIngreso": "2024-10-02",
        "FechaRetiro": "", 
        "FechaLiquidacionInicio": "2024-11-01",
        "FechaLiquidacionFin": "2024-11-30",
        "TiempoLaborado": "59",
        "FechaGeneracion": "2024-12-09"
    }

    # Agregar la secuencia XML
    data["NumeroSecuenciaXML"] = {
        "CodigoTrabajador": "4138",
        "Prefijo": "BOG",
        "Consecutivo": "13428"
    }

    # Agregar el lugar de generación XML
    data["LugarGeneracionXML"] = {
        "Pais": "CO",
        "DepartamentoEstado": "11",
        "MunicipioCiudad": "11001",
        "Idioma": "es"
    }

    # Agregar información general
    data["InformacionGeneral"] = {
        "FechaGeneracion": "2024-12-09",
        "HoraGeneracion": "16:25:00",
        "PeriodoNomina": "5",
        "TipoMoneda": "COP"
    }

    # Agregar la información del empleador
    data["Empleador"] = {
        "RazonSocial": "LECTA LTDA",
        "NIT": "806003042",
        "DigitoVerificacion": "7",
        "Pais": "CO",
        "DepartamentoEstado": "11",
        "MunicipioCiudad": "11001",
        "Direccion": "Cra. 23 no 69-32"
    }

    # Agregar la información del trabajador
    data["Trabajador"] = {
        "TipoTrabajador": "01",
        "SubTipoTrabajador": "00",
        "AltoRiesgoPension": False,
        "TipoDocumento": "13",
        "NumeroDocumento": "1020787737",
        "CorreoElectronico": "alejoaponte13@hotmail.com",
        "NumeroMovil": "3239219378",
        "PrimerApellido": "APONTE",
        "SegundoApellido": "GONZALEZ",
        "PrimerNombre": "JAIRO",
        "OtrosNombres": "ALEJANDRO",
        "LugarTrabajoPais": "CO",
        "LugarTrabajoDepartamentoEstado": "11",
        "LugarTrabajoMunicipioCiudad": "11001",
        "LugarTrabajoDireccion": "CL 60 B SUR # 74 - 21\r\n",
        "SalarioIntegral": False,
        "TipoContrato": "3",
        "Sueldo": "1300000",
        "CodigoTrabajador": "4138"
    }

    #Devengados
    data["Devengados"] = {}

    # Salario Básico
    data["Devengados"]["Basico"] = {
        "DiasTrabajados": "3.375",
        "SueldoTrabajado": "1266773"
    }






    data["redondeo"] = redondeo
    data["DevengadosTotal"] = DevengadosTotal
    data["DeduccionesTotal"] = DeduccionesTotal
    data["ComprobanteTotal"] = ComprobanteTotal

    context = {
        'data': json.dumps(data)
    }

    return render(request, './payroll/electronic_payroll.html', context)