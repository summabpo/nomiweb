import datetime
from django.shortcuts import render, redirect, get_object_or_404
import json
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import F, Q, Case, When, Value, CharField, Sum
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
    fechaliquidacioninicio = container.fechaliquidacioninicio
    fechaliquidacionfin = container.fechaliquidacionfin
    prefijo = container.prefijo
    periodonomina = container.periodonomina
    tipomoneda = container.tipomoneda
    idioma = container.idioma
    fechapago = container.fechapago
    ciudadgeneracion = container.ciudadgeneracion
    paisgeneracion = container.paisgeneracion
    departamentogeneracion = container.departamentogeneracion

    
    # Validate the year and get the id from the Anos model
    try:
        ano = Anos.objects.get(ano=year)
        ano_id = ano.idano
    except Anos.DoesNotExist:
        messages.error(request, 'El año especificado no existe en el sistema.')
        return redirect('payroll:nomina_electronica')
    
    empresa_id = container.empresa.idempresa



    # Query the contracts of the electronic payroll that correspond to the month and year
    query_detail = Nomina.objects.select_related(
                        'idcontrato__idempleado',
                        'idnomina__anoacumular',
                    ).filter(
                        idcontrato__id_empresa=empresa_id,
                        # idcontrato__estadocontrato=1,
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
                            entry_date = F('idcontrato__fechainiciocontrato'),
                            month = F('idnomina__mesacumular'),
                            year = F('idnomina__anoacumular__ano'),
                            employee_identification = F('idcontrato__idempleado__docidentidad')
                    ).distinct('idcontrato').order_by(
                        'idcontrato'
                    )

    #query the detail of the electronic payroll
    query_detail_all = Nomina.objects.select_related(
                            'idcontrato',
                            'idconcepto__grupo_dian'
                        ).filter(
                            idnomina__mesacumular=month,
                            idnomina__anoacumular=ano_id
                        ).values(
                            contrato_id = F('idcontrato__idcontrato'),
                            concepto = F('idconcepto__nombreconcepto'),
                            concepto_dian = F('idconcepto__grupo_dian__campo'),
                            valor_anotado = F('valor'),
                            cantidad_anotado = F('cantidad'),
                            control_id = F('control'),
                            tipo_concepto = F('idconcepto__tipoconcepto'),
                        )               

    # Iterate over each field in query_detail
    for detail in query_detail:

        #query the detail of the electronic payroll for id contract
        detail_contract = electronic_payroll_generate_detail(query_detail_all, detail['id'])
        
        # iterate over contract details for each concept
        for item in detail_contract:
            print(f"MOONDAAAA: {item['concepto']}")

            
        print(f"ID: {detail['id']}")
        print(f"Employee Name: {detail['employee_name']}")
        print(f"Month: {detail['month']}")
        print(f"Year: {detail['year']}")
        print(f"Employee Identification: {detail['employee_identification']}")
        print(f"Employee Entry Date: {detail['entry_date']}")

        #building the json data payroll
        data = {}
        data["canal"] = 2
        data["Periodo"] = {
            "FechaIngreso": detail['entry_date'].isoformat() if isinstance(detail['entry_date'], datetime.date) else detail['entry_date'],
            "FechaRetiro": "", 
            "FechaLiquidacionInicio": "2024-11-01",
            "FechaLiquidacionFin": "2024-11-30",
            "TiempoLaborado": "59",
            "FechaGeneracion": "2024-12-09"
        }

        print(json.dumps(data))
        print('-------------------------')


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
            # CODSueldoTrabajado
            if payroll['concepto_dian'] == 'SueldoTrabajado':   
                print(f"Concepto: {payroll['concepto']}")
                print(f"Concepto DIAN: {payroll['concepto_dian']}")
                print(f"Valor Anotado: {payroll['valor_anotado']}")
                print(f"Cantidad Anotada: {payroll['anotado']}")
                print(f"Control ID: {payroll['control_id']}")
                print(f"Tipo de Concepto: {payroll['tipo_concepto']}")
            
        query_payroll = Nomina.objects.select_related(
                'idcontrato',
                'idconcepto__grupo_dian'
            ).filter(
                idcontrato=detail['id'],
                idnomina__mesacumular=month,
                idnomina__anoacumular=ano_id
            ).values(
                grupo_dian=F('idconcepto__grupo_dian__campo')  # Agrupamos por este campo
            ).annotate(
                total_valor=Sum('valor'),          # Sumatoria del campo 'valor'
                total_cantidad=Sum('cantidad'),   # Sumatoria del campo 'cantidad'
                concepto=F('idconcepto__nombreconcepto'),  # Puedes incluir campos adicionales según necesidad
                tipo_concepto=F('idconcepto__tipoconcepto')  # Agregar más datos si son útiles
            )
        
        for payroll in query_payroll:
            # validation of the concepts grouped by DIAN
            # CODSueldoTrabajado
            if payroll['grupo_dian'] == 'SueldoTrabajado':   
                print(f"Concepto: {payroll['concepto']}")
                print(f"Concepto DIAN: {payroll['grupo_dian']}")
                print(f"Valor Anotado: {payroll['total_valor']}")
                print(f"Cantidad Anotada: {payroll['total_cantidad']}")
                print(f"Tipo de Concepto: {payroll['tipo_concepto']}")

    context = {
        'query_detail' : query_detail,
    }
    
    return render(request, './payroll/electronic_payroll_generate.html', context)


#json data
def electronic_payroll_generate_json(data):

    return JsonResponse(data)

#query the detail of the electronic payroll
def electronic_payroll_generate_detail(query_detail_all, contrato_id):
    filtered_data = [item for item in query_detail_all if item['contrato_id'] == contrato_id]
    # Ahora filtered_data contiene solo los registros con el ID filtrado
    print(filtered_data)
    return filtered_data

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

#     {
#     "canal": 2,
#     "Periodo": {
#         "FechaIngreso": "2024-08-01",
#         "FechaRetiro": "",
#         "FechaLiquidacionInicio": "2024-11-01",
#         "FechaLiquidacionFin": "2024-11-30",
#         "TiempoLaborado": "120",
#         "FechaGeneracion": "2024-12-09"
#     },
#     "NumeroSecuenciaXML": {
#         "CodigoTrabajador": "2535",
#         "Prefijo": "CAR",
#         "Consecutivo": "2819"
#     },
#     "LugarGeneracionXML": {
#         "Pais": "CO",
#         "DepartamentoEstado": "13",
#         "MunicipioCiudad": "13001",
#         "Idioma": "es"
#     },
#     "InformacionGeneral": {
#         "TipoXML": "",
#         "FechaGeneracion": "2024-12-09",
#         "HoraGeneracion": "15:45:00",
#         "PeriodoNomina": "5",
#         "TipoMoneda": "COP"
#     },
#     "Empleador": {
#         "RazonSocial": "CARIBBEAN SUPPORT AND FLIGHT SERVICES SAS",
#         "NIT": "806013964",
#         "DigitoVerificacion": "5",
#         "Pais": "CO",
#         "DepartamentoEstado": "13",
#         "MunicipioCiudad": "13001",
#         "Direccion": "CRA 2 #67-143 OF 101"
#     },
#     "Trabajador": {
#         "TipoTrabajador": "01",
#         "SubTipoTrabajador": "00",
#         "AltoRiesgoPension": "false",
#         "TipoDocumento": "13",
#         "NumeroDocumento": "1041771148",
#         "CorreoElectronico": "edgarjunior1041@gmail.com",
#         "NumeroMovil": "300 3081264",
#         "PrimerApellido": "FRANCO",
#         "SegundoApellido": "PERTUZ",
#         "PrimerNombre": "EDGARDO",
#         "OtrosNombres": "ANTONIO",
#         "LugarTrabajoPais": "CO",
#         "LugarTrabajoDepartamentoEstado": "08",
#         "LugarTrabajoMunicipioCiudad": "08001",
#         "LugarTrabajoDireccion": "KRA 17B #21 C26. BARANOA, ATL\u00c1NTICO",
#         "SalarioIntegral": "false",
#         "TipoContrato": "2",
#         "Sueldo": "1300000",
#         "CodigoTrabajador": "2535"
#     },
#     "Pago": {
#         "Forma": "1",
#         "Metodo": "30",
#         "Banco": "",
#         "TipoCuenta": "ahorros",
#         "NumeroCuenta": ""
#     },
#     "FechasPagos": [
#         {
#             "FechaPago": "2024-11-30"
#         }
#     ],
#     "Devengados": {
#         "Basico": {
#             "DiasTrabajados": "3.75",
#             "SueldoTrabajado": "1300000"
#         },
#         "Transporte": [
#             {
#                 "AuxilioTransporte": "162000"
#             }
#         ],
#         "HoraRecargoDiurnoDominicalFestivo": [
#             {
#                 "HoraInicio": "",
#                 "HoraFin": "",
#                 "Cantidad": "24.0",
#                 "Porcentaje": "1.75",
#                 "Pago": "232340"
#             }
#         ]
#     },
#     "Deducciones": {
#         "Salud": {
#             "Porcentaje": "4",
#             "Deduccion": "61294"
#         },
#         "FondoPension": {
#             "Porcentaje": "4",
#             "Deduccion": "61294"
#         }
#     },
#     "Redondeo": "",
#     "DevengadosTotal": "1694340",
#     "DeduccionesTotal": "122588",
#     "ComprobanteTotal": "1571752"
# }




    data["redondeo"] = redondeo
    data["DevengadosTotal"] = DevengadosTotal
    data["DeduccionesTotal"] = DeduccionesTotal
    data["ComprobanteTotal"] = ComprobanteTotal

    context = {
        'data': json.dumps(data)
    }

    return render(request, './payroll/electronic_payroll.html', context)