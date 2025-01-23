import datetime
from django.shortcuts import render, redirect, get_object_or_404
import json
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import F, Q, Case, When, Value, CharField, Sum, Count
from django.db.models.functions import Concat
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
import requests


from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required

# models
from apps.common.models import Anos, Nomina, Contratos, Contratosemp, NeDatosMensual, NeDetalleNominaElectronica, NeRespuestaDian, Ciudades, Paises, Empresa, Conceptosfijos, Vacaciones, Incapacidades

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
    container = (
        NeDatosMensual.objects.filter(empresa=idempresa)
        .annotate(
            generado=Count('nedetallenominaelectronica', filter=Q(nedetallenominaelectronica__estado=1)),
            exitoso=Count('nedetallenominaelectronica', filter=Q(nedetallenominaelectronica__estado=2)),
            error=Count('nedetallenominaelectronica', filter=Q(nedetallenominaelectronica__estado=3)),
            eliminado=Count('nedetallenominaelectronica', filter=Q(nedetallenominaelectronica__estado=4)),
            reemplazado=Count('nedetallenominaelectronica', filter=Q(nedetallenominaelectronica__estado=5)),
            anulado=Count('nedetallenominaelectronica', filter=Q(nedetallenominaelectronica__estado=6)),
            total=Count('nedetallenominaelectronica'),
        )
        .order_by('-idnominaelectronica')
    )
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


# view detail electronic payroll container
@login_required
@role_required('accountant')
def electronic_payroll_detail(request, pk=None):
    detail_payroll = NeDetalleNominaElectronica.objects.select_related(
        'id_contrato__idempleado',
        'id_contrato__cargo',
    ).filter(id_ne_datos_mensual=pk).annotate(
        contract_id = F('id_contrato'),
        employee_name=Concat(
            F('id_contrato__idempleado__pnombre'), Value(' '),
            F('id_contrato__idempleado__snombre'), Value(' '),
            F('id_contrato__idempleado__papellido'), Value(' '),
            F('id_contrato__idempleado__sapellido')
        ),
        employee_document=F('id_contrato__idempleado__docidentidad'), 
        employee_position = F('id_contrato__cargo__nombrecargo'),
    )

    context =  {
        'container_id' : pk,
        'detail_payroll': detail_payroll
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
    fechageneracion = container.fechageneracion
    horageneracion = container.horageneracion
    prefijo = container.prefijo
    periodonomina = container.periodonomina
    tipomoneda = container.tipomoneda
    idioma = container.idioma
    fechapago = container.fechapago
    ciudadgeneracion = container.ciudadgeneracion
    paisgeneracion = container.paisgeneracion
    departamentogeneracion = container.departamentogeneracion

    #metho validate enterprise
    company = Empresa.objects.get(idempresa=container.empresa.idempresa)

    #concepts static payroll
    ces_percentage = Conceptosfijos.objects.get(idfijo=8).valorfijo
    eps_percentage = Conceptosfijos.objects.get(idfijo=10).valorfijo
    pension_percentage = Conceptosfijos.objects.get(idfijo=12).valorfijo
    fsp_percentage = Conceptosfijos.objects.get(idfijo=14).valorfijo
    
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
                            first_name = F('idcontrato__idempleado__pnombre'),
                            second_name = F('idcontrato__idempleado__snombre'),
                            first_lastname = F('idcontrato__idempleado__papellido'),
                            second_lastname = F('idcontrato__idempleado__sapellido'),
                            entry_date = F('idcontrato__fechainiciocontrato'),
                            exit_date = F('idcontrato__fechafincontrato'),
                            contributing_type = F('idcontrato__tipocotizante__tipocotizante'),
                            subcontributing_type = F('idcontrato__subtipocotizante__subtipocotizante'),
                            pension_risk = F('idcontrato__riesgo_pension'),
                            month = F('idnomina__mesacumular'),
                            year = F('idnomina__anoacumular__ano'),
                            employee_identification = F('idcontrato__idempleado__docidentidad'),
                            document_type = F('idcontrato__idempleado__tipodocident__cod_dian'),
                            employee_email = F('idcontrato__idempleado__email'),
                            employee_phone = F('idcontrato__idempleado__telefonoempleado'),
                            employee_address = F('idcontrato__idempleado__direccionempleado'),
                            salary_type = Case(
                                When(idcontrato__tiposalario__idtiposalario=2, then=Value(True)),
                                default=Value(False),
                                output_field=CharField()
                            ),
                            salary = F('idcontrato__salario'),
                            type_of_contract = F('idcontrato__tipocontrato__cod_dian'),
                            employee_bank   = F('idcontrato__bancocuenta__nombanco'),
                            employee_type_bank   = F('idcontrato__tipocuentanomina'),
                            employee_account = F('idcontrato__cuentanomina'),

                            ).distinct('idcontrato').order_by(
                                'idcontrato'
                            )

    #query the detail of the electronic payroll
    query_detail_all = Nomina.objects.select_related(
                            'idcontrato',
                            'idconcepto__grupo_dian'
                        ).filter(
                            idnomina__mesacumular=month,
                            idnomina__anoacumular=ano_id,
                            idcontrato__id_empresa=empresa_id,
                        ).values(
                            contrato_id = F('idcontrato__idcontrato'),
                            concepto = F('idconcepto__nombreconcepto'),
                            concepto_dian = F('idconcepto__grupo_dian__campo'),
                            valor_anotado = F('valor'),
                            cantidad_anotado = F('cantidad'),
                            control_id = F('control'),
                            tipo_concepto = F('idconcepto__tipoconcepto'),
                            mulitplicador_concepto = F('idconcepto__multiplicadorconcepto'),
                        )               

    # Iterate over each field in query_detail
    for detail in query_detail:
        #building the json data payroll
        data = {}
        data["canal"] = 2
        data["Periodo"] = {
            "FechaIngreso": format_date(detail['entry_date']),
            "FechaRetiro": format_date(detail['exit_date']), 
            "FechaLiquidacionInicio": format_date(fechaliquidacioninicio),
            "FechaLiquidacionFin": format_date(fechaliquidacionfin),
            "TiempoLaborado": format_date(calculate_worked_days(detail['entry_date'], detail['exit_date'], fechaliquidacionfin)),
            "FechaGeneracion": format_date(fechageneracion)
        }

        # Agregar la secuencia XML
        data["NumeroSecuenciaXML"] = {
            "CodigoTrabajador": detail['id'],
            "Prefijo": prefijo,
            "Consecutivo": "13428"
        }

        # Agregar el lugar de generación XML
        data["LugarGeneracionXML"] = {
            "Pais": paisgeneracion,
            "DepartamentoEstado": ciudadgeneracion,
            "MunicipioCiudad": f"{ciudadgeneracion}{departamentogeneracion}",
            "Idioma": idioma
        }

        # Agregar información general
        data["InformacionGeneral"] = {
            "TipoXML": "",
            "FechaGeneracion": fechageneracion,
            "HoraGeneracion": horageneracion,
            "PeriodoNomina": periodonomina,
            "TipoMoneda": tipomoneda
        }

        # Agregar la información del empleador
        data["Empleador"] = {
            "RazonSocial": company.nombreempresa,
            "NIT": company.nit,
            "DigitoVerificacion": company.dv,
            "Pais": paisgeneracion,
            "DepartamentoEstado": ciudadgeneracion,
            "MunicipioCiudad": f"{ciudadgeneracion}{departamentogeneracion}",
            "Direccion": company.direccionempresa
        }

        # Agregar la información del trabajador
        data["Trabajador"] = {
            "TipoTrabajador": detail['contributing_type'],
            "SubTipoTrabajador":detail['subcontributing_type'],
            "AltoRiesgoPension": detail['pension_risk'],
            "TipoDocumento": detail['document_type'],
            "NumeroDocumento": detail['employee_identification'],
            "CorreoElectronico": detail['employee_email'],
            "NumeroMovil": detail['employee_phone'],
            "PrimerApellido": detail['first_lastname'],
            "SegundoApellido": detail['second_lastname'],
            "PrimerNombre": detail['first_name'],
            "OtrosNombres": detail['second_name'],
            "LugarTrabajoPais": paisgeneracion,
            "LugarTrabajoDepartamentoEstado": ciudadgeneracion,
            "LugarTrabajoMunicipioCiudad": f"{ciudadgeneracion}{departamentogeneracion}",
            "LugarTrabajoDireccion": detail['employee_address'],
            "SalarioIntegral": detail['salary_type'],
            "TipoContrato": detail['type_of_contract'],
            "Sueldo": detail['salary'],
            "CodigoTrabajador": detail['id']
        }

        # Add payment information
        data["Pago"] = {
            "Forma": "1",
            "Metodo": "30",
            "Banco": detail['employee_bank'],
            "TipoCuenta": detail['employee_type_bank'],
            "NumeroCuenta": detail['employee_account']
        }

        # Add payment dates
        data["FechasPagos"] = [
            {
                "FechaPago": format_date(fechapago)
            }
        ]

        #detail of the electronic payroll devengados
        data["Devengados"] = {}

        #detail of the electronic payroll deducciones
        data["Deducciones"] = {}

        #query the detail of the electronic payroll for id contract
        detail_contract = electronic_payroll_generate_detail(query_detail_all, detail['id'])

        # iterate over contract details for each concept
        for item in detail_contract:
            #validate the concepts is deduccion
            if item['tipo_concepto'] == 2:
                item['valor_anotado'] = abs(item['valor_anotado'])
            
            print(f"Concepto: {item['concepto_dian']}")
            
            #validation of the concepts

            #DEVENGADOS
            # CODSueldoTrabajado
            if item['concepto_dian'] == 'SueldoTrabajado':
                if "Basico" not in data["Devengados"]:
                    data["Devengados"]["Basico"] = {
                        "DiasTrabajados": 0,
                        "SueldoTrabajado": 0
                    }
                data["Devengados"]["Basico"]["DiasTrabajados"] += item['cantidad_anotado']
                data["Devengados"]["Basico"]["SueldoTrabajado"] += item['valor_anotado']
            
            # CODAuxilioTransporte
            if item['concepto_dian'] == 'AuxilioTransporte':
                if "Transporte" not in data["Devengados"]:
                    data["Devengados"]["Transporte"] = {
                        "AuxilioTransporte": 0
                    }
                data["Devengados"]["Transporte"]["AuxilioTransporte"] += item['valor_anotado']

            # CODViaticoManuAlojNS
            if item['concepto_dian'] == 'ViaticoManuAlojNS':
                if "Transporte" not in data["Devengados"]:
                    data["Devengados"]["Transporte"] = {
                        "ViaticoManuAlojNS": 0
                    }
                data["Devengados"]["Transporte"]["ViaticoManuAlojNS"] += item['valor_anotado']
                
            # CODViaticoManuAlojS
            if item['concepto_dian'] == 'ViaticoManuAlojS':
                if "Transporte" not in data["Devengados"]:
                    data["Devengados"]["Transporte"] = {
                        "ViaticoManuAlojS": 0
                    }
                data["Devengados"]["Transporte"]["ViaticoManuAlojS"] += item['valor_anotado']

            # HoraExtraDiurna, HoraExtraDiurnaDominicalFestivo HoraExtraNocturna, RecargoNocturno, HoraExtraDiurnaDominicalFestiva, HoraRecargoDiurnoDominicalFestivo, HoraExtraNocturnaDominicalFestiva, HoraRecargoNocturnoDominicalFestivo
            if item['concepto_dian'] in [
                'HoraExtraDiurna', 'HoraExtraDiurnaDominicalFestivo', 'HoraExtraNocturna', 'RecargoNocturno',
                'HoraExtraDiurnaDominicalFestiva', 'HoraRecargoDiurnoDominicalFestivo', 'HoraExtraNocturnaDominicalFestiva',
                'HoraRecargoNocturnoDominicalFestivo'
            ]:
                # Sub array Transporte
                array_sub = {
                    "HoraInicio": "",  # YYYY-MM-DD HH:MM:SS
                    "HoraFin": "",
                    "Cantidad": str(item['cantidad_anotado']),
                    "Porcentaje": str(item['mulitplicador_concepto']),  # Example percentage, replace with actual value if needed
                    "Pago": str(item['valor_anotado'])
                }

                if item['concepto_dian'] not in data["Devengados"]:
                    data["Devengados"][item['concepto_dian']] = []

                data["Devengados"][item['concepto_dian']].append(array_sub)

            # VacacionesComunes
            if item['concepto_dian'] == 'VacacionesComunes':

                vacation_detail = Vacaciones.objects.filter(idvacaciones=item['control_id']).values('fechainicialvac', 'ultimodiavac', 'diascalendario', 'pagovac')

                if "Vacaciones" not in data["Devengados"]:
                    data["Devengados"]["Vacaciones"] = {
                        "VacacionesComunes": []
                    }
                data["Devengados"]["Vacaciones"]["VacacionesComunes"].append({
                    "FechaInicio": format_date(vacation_detail[0]['fechainicialvac']),
                    "FechaFin": format_date(vacation_detail[0]['ultimodiavac']),
                    "Cantidad": item['cantidad_anotado'],
                    "Pago": item['valor_anotado']
                })

            # VacacionesCompensadas
            if item['concepto_dian'] == 'VacacionesCompensadas':
                if "Vacaciones" not in data["Devengados"]:
                    data["Devengados"]["Vacaciones"] = {
                        "VacacionesCompensadas": []
                    }
                data["Devengados"]["Vacaciones"]["VacacionesCompensadas"].append({
                    "Cantidad": item['cantidad_anotado'],
                    "Pago": item['valor_anotado']
                })

            # Primas
            if item['concepto_dian'] == 'Primas':
                if "Primas" not in data["Devengados"]:
                    data["Devengados"]["Primas"] = {
                        "Cantidad": 0,
                        "Pago": 0,
                        "PagoNS": 0
                    }
                data["Devengados"]["Primas"]["Cantidad"] += item['cantidad_anotado']
                data["Devengados"]["Primas"]["Pago"] += item['valor_anotado']
                data["Devengados"]["Primas"]["PagoNS"] += item['valor_anotado'] if item['tipo_concepto'] == 'NS' else 0

            # Cesantias
            if item['concepto_dian'] == 'Cesantias':
                if "Cesantias" not in data["Devengados"]:
                    data["Devengados"]["Cesantias"] = {
                        "Pago": 0,
                        "Porcentaje": ces_percentage,
                        "PagoInter  eses": 0
                    }
                data["Devengados"]["Cesantias"]["Pago"] += item['valor_anotado']

            # Intereses sobre Cesantias
            if item['concepto_dian'] == 'Intereses':
                if "Cesantias" not in data["Devengados"]:
                    data["Devengados"]["Cesantias"] = {
                        "Pago": 0,
                        "Porcentaje": ces_percentage,
                        "PagoIntereses": 0
                    }
                data["Devengados"]["Cesantias"]["PagoIntereses"] += item['valor_anotado']

            # Incapacidad
            if item['concepto_dian'] == 'Incapacidad':

                disability_detail = Incapacidades.objects.filter(idincapacidad=item['control_id']).values('fechainicial', 'dias', 'origenincap')

                if not disability_detail.exists():
                    origenincap = ''
                    fechainicial = ''
                    dias = ''
                    fechafinal = ''
                else:
                    # Calculate the end date based on the start date and the number of days
                    origenincap = disability_detail[0]['origenincap']
                    fechainicial = disability_detail[0]['fechainicial']
                    dias = disability_detail[0]['dias']
                    fechafinal = fechainicial + datetime.timedelta(days=dias)

                if "Incapacidad" not in data["Devengados"]:
                    data["Devengados"]["Incapacidad"] = []
                data["Devengados"]["Incapacidad"].append({
                    "FechaInicio": format_date(fechainicial),
                    "FechaFin": format_date(fechafinal),
                    "Cantidad": dias,
                    "Tipo": origenincap,
                    "Pago": item['valor_anotado']
                })

            # LicenciaMP
            if item['concepto_dian'] == 'LicenciaMP':
                if "LicenciaMP" not in data["Devengados"]:
                    data["Devengados"]["LicenciaMP"] = []
                data["Devengados"]["LicenciaMP"].append({
                    "FechaInicio": '',
                    "FechaFin": '',
                    "Cantidad": item['cantidad_anotado'],
                    "Pago": item['valor_anotado']
                })

            # LicenciaR
            if item['concepto_dian'] == 'LicenciaR':
                if "LicenciaR" not in data["Devengados"]:
                    data["Devengados"]["LicenciaR"] = []
                data["Devengados"]["LicenciaR"].append({
                    "FechaInicio": '',
                    "FechaFin": '',
                    "Cantidad": item['cantidad_anotado'],
                    "Pago": item['valor_anotado']
                })

            # LicenciaNR
            if item['concepto_dian'] == 'LicenciaNR':
                if "LicenciaNR" not in data["Devengados"]:
                    data["Devengados"]["LicenciaNR"] = []
                data["Devengados"]["LicenciaNR"].append({
                    "FechaInicio": format_date(item['fechainicial']),
                    "FechaFin": format_date(item['fechafinal']),
                    "Cantidad": item['cantidad_anotado'],
                    "Pago": item['valor_anotado']
                })

            # BonificacionS
            if item['concepto_dian'] == 'BonificacionS':
                if "Bonificacion" not in data["Devengados"]:
                    data["Devengados"]["Bonificacion"] = {
                        "BonificacionS": 0,
                        "BonificacionNS": 0
                    }
                data["Devengados"]["Bonificacion"]["BonificacionS"] += item['valor_anotado']

            # BonificacionNS
            if item['concepto_dian'] == 'BonificacionNS':
                if "Bonificacion" not in data["Devengados"]:
                    data["Devengados"]["Bonificacion"] = {
                        "BonificacionS": 0,
                        "BonificacionNS": 0
                    }
                data["Devengados"]["Bonificacion"]["BonificacionNS"] += item['valor_anotado']

            # AuxilioS
            if item['concepto_dian'] == 'AuxilioS':
                if "Auxilio" not in data["Devengados"]:
                    data["Devengados"]["Auxilio"] = {
                        "AuxilioS": 0,
                        "AuxilioNS": 0
                    }
                data["Devengados"]["Auxilio"]["AuxilioS"] += item['valor_anotado']

            # AuxilioNS
            if item['concepto_dian'] == 'AuxilioNS':
                if "Auxilio" not in data["Devengados"]:
                    data["Devengados"]["Auxilio"] = {   
                        "AuxilioS": 0,
                        "AuxilioNS": 0
                    }
                data["Devengados"]["Auxilio"]["AuxilioNS"] += item['valor_anotado']

            # HuelgaLegal
            if item['concepto_dian'] == 'HuelgaLegal':
                if "HuelgaLegal" not in data["Devengados"]:
                    data["Devengados"]["HuelgaLegal"] = []
                data["Devengados"]["HuelgaLegal"].append({
                    "FechaInicio": format_date(item['fechainicial']),
                    "FechaFin": format_date(item['fechafinal']),
                    "Cantidad": item['cantidad_anotado']
                })

            # OtroConcepto
            if item['concepto_dian'] == 'OtroConcepto':
                if "OtroConcepto" not in data["Devengados"]:
                    data["Devengados"]["OtroConcepto"] = []
                data["Devengados"]["OtroConcepto"].append({
                    "DescripcionConcepto": item['concepto'],
                    "ConceptoS": item['valor_anotado'] if item['tipo_concepto'] == 'S' else 0,
                    "ConceptoNS": item['valor_anotado'] if item['tipo_concepto'] == 'NS' else 0
                })

            # Compensacion
            if item['concepto_dian'] == 'Compensacion':
                if "Compensacion" not in data["Devengados"]:
                    data["Devengados"]["Compensacion"] = []
                data["Devengados"]["Compensacion"].append({
                    "CompensacionO": item['valor_anotado'] if item['tipo_concepto'] == 'O' else 0,
                    "CompensacionE": item['valor_anotado'] if item['tipo_concepto'] == 'E' else 0
                })

            # BonoEPCTV
            if item['concepto_dian'] == 'BonoEPCTV':
                if "BonoEPCTV" not in data["Devengados"]:
                    data["Devengados"]["BonoEPCTV"] = []
                data["Devengados"]["BonoEPCTV"].append({
                    "PagoS": item['valor_anotado'] if item['tipo_concepto'] == 'S' else 0,
                    "PagoNS": item['valor_anotado'] if item['tipo_concepto'] == 'NS' else 0,
                    "PagoAlimentacionS": item['valor_anotado'] if item['tipo_concepto'] == 'AlimentacionS' else 0,
                    "PagoAlimentacionNS": item['valor_anotado'] if item['tipo_concepto'] == 'AlimentacionNS' else 0
                })

            # Comisiones
            if item['concepto_dian'] == 'Comisiones':
                if "Comisiones" not in data["Devengados"]:
                    data["Devengados"]["Comisiones"] = []
                data["Devengados"]["Comisiones"].append({
                    "Comision": item['valor_anotado']
                })

            # PagosTerceros
            if item['concepto_dian'] == 'PagosTerceros':
                if "PagosTerceros" not in data["Devengados"]:
                    data["Devengados"]["PagosTerceros"] = []
                data["Devengados"]["PagosTerceros"].append({
                    "PagosTercero": item['valor_anotado']
                })

            # Anticipos
            if item['concepto_dian'] == 'Anticipos':
                if "Anticipos" not in data["Devengados"]:
                    data["Devengados"]["Anticipos"] = []
                data["Devengados"]["Anticipos"].append({
                    "Anticipo": item['valor_anotado']
                })



            #DEDUCCIONES
            # CODSalud
            if item['concepto_dian'] == 'Salud':
                if "Salud" not in data["Deducciones"]:
                    data["Deducciones"]["Salud"] = {
                        "Porcentaje": eps_percentage,
                        "Deduccion": 0
                    }
                data["Deducciones"]["Salud"]["Deduccion"] += item['valor_anotado']
            
            # CODFondoPension
            if item['concepto_dian'] == 'FondoPension':
                if "FondoPension" not in data["Deducciones"]:
                    data["Deducciones"]["FondoPension"] = {
                        "Porcentaje": pension_percentage,
                        "Deduccion": 0
                    }
                data["Deducciones"]["FondoPension"]["Deduccion"] += item['valor_anotado']
            
            # CODFondoSP
            if item['concepto_dian'] == 'FondoSP':
                if "FondoSP" not in data["Deducciones"]:
                    data["Deducciones"]["FondoSP"] = {
                        "Porcentaje": fsp_percentage,
                        "DeduccionSP": 0,
                        "PorcentajeSub": 0,
                        "DeduccionSub": 0
                    }
                data["Deducciones"]["FondoSP"]["DeduccionSP"] += item['valor_anotado']

            # CODSindicatos
            if item['concepto_dian'] == 'Sindicatos':
                if "Sindicatos" not in data["Deducciones"]:
                    data["Deducciones"]["Sindicatos"] = {
                        "Deduccion": 0
                    }
                data["Deducciones"]["Sindicatos"]["Deduccion"] += item['valor_anotado']

            # CODSanciones
            if item['concepto_dian'] == 'Sanciones':
                if "Sanciones" not in data["Deducciones"]:
                    data["Deducciones"]["Sanciones"] = {
                        "Deduccion": 0
                    }
                data["Deducciones"]["Sanciones"]["Deduccion"] += item['valor_anotado']

            # CODLibranzas
            if item['concepto_dian'] == 'Libranzas':
                if "Libranzas" not in data["Deducciones"]:
                    data["Deducciones"]["Libranzas"] = {
                        "Deduccion": 0
                    }
                data["Deducciones"]["Libranzas"]["Deduccion"] += item['valor_anotado']

            # CODOtrasDeducciones
            if item['concepto_dian'] == 'OtrasDeducciones':
                if "OtrasDeducciones" not in data["Deducciones"]:
                    data["Deducciones"]["OtrasDeducciones"] = {
                        "Deduccion": 0
                    }
                data["Deducciones"]["OtrasDeducciones"]["Deduccion"] += item['valor_anotado']

            # CODAnticipos
            if item['concepto_dian'] == 'Anticipos':
                if "Anticipos" not in data["Deducciones"]:
                    data["Deducciones"]["Anticipos"] = {
                        "Deduccion": 0
                    }
                data["Deducciones"]["Anticipos"]["Deduccion"] += item['valor_anotado']

            # CODPensionVoluntaria
            if item['concepto_dian'] == 'PensionVoluntaria':
                if "PensionVoluntaria" not in data["Deducciones"]:
                    data["Deducciones"]["PensionVoluntaria"] = {
                        "Deduccion": 0
                    }
                data["Deducciones"]["PensionVoluntaria"]["Deduccion"] += item['valor_anotado']

            # CODRetencionFuente
            if item['concepto_dian'] == 'RetencionFuente':
                if "RetencionFuente" not in data["Deducciones"]:
                    data["Deducciones"]["RetencionFuente"] = {
                        "Deduccion": 0
                    }
                data["Deducciones"]["RetencionFuente"]["Deduccion"] += item['valor_anotado']

            # CODAFC
            if item['concepto_dian'] == 'AFC':
                if "AFC" not in data["Deducciones"]:
                    data["Deducciones"]["AFC"] = {
                        "Deduccion": 0
                    }
                data["Deducciones"]["AFC"]["Deduccion"] += item['valor_anotado']

            # CODCooperativa
            if item['concepto_dian'] == 'Cooperativa':
                if "Cooperativa" not in data["Deducciones"]:
                    data["Deducciones"]["Cooperativa"] = {
                        "Deduccion": 0
                    }
                data["Deducciones"]["Cooperativa"]["Deduccion"] += item['valor_anotado']

            # CODEmbargoFiscal
            if item['concepto_dian'] == 'EmbargoFiscal':
                if "EmbargoFiscal" not in data["Deducciones"]:
                    data["Deducciones"]["EmbargoFiscal"] = {
                        "Deduccion": 0
                    }
                data["Deducciones"]["EmbargoFiscal"]["Deduccion"] += item['valor_anotado']

            # CODPlanComplementarios
            if item['concepto_dian'] == 'PlanComplementarios':
                if "PlanComplementarios" not in data["Deducciones"]:
                    data["Deducciones"]["PlanComplementarios"] = {
                        "Deduccion": 0
                    }
                data["Deducciones"]["PlanComplementarios"]["Deduccion"] += item['valor_anotado']

            # CODEducacion
            if item['concepto_dian'] == 'Educacion':
                if "Educacion" not in data["Deducciones"]:
                    data["Deducciones"]["Educacion"] = {
                        "Deduccion": 0
                    }
                data["Deducciones"]["Educacion"]["Deduccion"] += item['valor_anotado']

            # CODReintegro
            if item['concepto_dian'] == 'Reintegro':
                if "Reintegro" not in data["Deducciones"]:
                    data["Deducciones"]["Reintegro"] = {
                        "Deduccion": 0
                    }
                data["Deducciones"]["Reintegro"]["Deduccion"] += item['valor_anotado']

            # CODDeuda
            if item['concepto_dian'] == 'Deuda':
                if "Deuda" not in data["Deducciones"]:
                    data["Deducciones"]["Deuda"] = {
                        "Deduccion": 0
                    }
                data["Deducciones"]["Deuda"]["Deduccion"] += item['valor_anotado']

            if item['concepto_dian'] == 'PensionVoluntaria':
                if "PensionVoluntaria" not in data["Deducciones"]:
                    data["Deducciones"]["PensionVoluntaria"] = {
                        "Deduccion": 0
                    }
                data["Deducciones"]["PensionVoluntaria"]["Deduccion"] += item['valor_anotado']

            
            # CODPensionVoluntaria
            if item['concepto_dian'] == 'PensionVoluntaria':
                if "PensionVoluntaria" not in data["Deducciones"]:
                    data["Deducciones"]["PensionVoluntaria"] = {
                        "Deduccion": 0
                    }
                data["Deducciones"]["PensionVoluntaria"]["Deduccion"] += item['valor_anotado']

            # CODRetencionFuente
            if item['concepto_dian'] == 'RetencionFuente':
                if "RetencionFuente" not in data["Deducciones"]:
                    data["Deducciones"]["RetencionFuente"] = {
                        "Deduccion": 0
                    }
                data["Deducciones"]["RetencionFuente"]["Deduccion"] += item['valor_anotado']

            # CODAFC
            if item['concepto_dian'] == 'AFC':
                if "AFC" not in data["Deducciones"]:
                    data["Deducciones"]["AFC"] = {
                        "Deduccion": 0
                    }
                data["Deducciones"]["AFC"]["Deduccion"] += item['valor_anotado']

            # CODCooperativa
            if item['concepto_dian'] == 'Cooperativa':
                if "Cooperativa" not in data["Deducciones"]:
                    data["Deducciones"]["Cooperativa"] = {
                        "Deduccion": 0
                    }
                data["Deducciones"]["Cooperativa"]["Deduccion"] += item['valor_anotado']

            # CODEmbargoFiscal
            if item['concepto_dian'] == 'EmbargoFiscal':
                if "EmbargoFiscal" not in data["Deducciones"]:
                    data["Deducciones"]["EmbargoFiscal"] = {
                        "Deduccion": 0
                    }
                data["Deducciones"]["EmbargoFiscal"]["Deduccion"] += item['valor_anotado']

            # CODPlanComplementarios
            if item['concepto_dian'] == 'PlanComplementarios':
                if "PlanComplementarios" not in data["Deducciones"]:
                    data["Deducciones"]["PlanComplementarios"] = {
                        "Deduccion": 0
                    }
                data["Deducciones"]["PlanComplementarios"]["Deduccion"] += item['valor_anotado']

            # CODEducacion
            if item['concepto_dian'] == 'Educacion':
                if "Educacion" not in data["Deducciones"]:
                    data["Deducciones"]["Educacion"] = {
                        "Deduccion": 0
                    }
                data["Deducciones"]["Educacion"]["Deduccion"] += item['valor_anotado']

            # CODReintegro
            if item['concepto_dian'] == 'Reintegro':
                if "Reintegro" not in data["Deducciones"]:
                    data["Deducciones"]["Reintegro"] = {
                        "Deduccion": 0
                    }
                data["Deducciones"]["Reintegro"]["Deduccion"] += item['valor_anotado']

            # CODDeuda
            if item['concepto_dian'] == 'Deuda':
                if "Deuda" not in data["Deducciones"]:
                    data["Deducciones"]["Deuda"] = {
                        "Deduccion": 0
                    }
                data["Deducciones"]["Deuda"]["Deduccion"] += item['valor_anotado']
            


        print(f"ID: {detail['id']}")
        print(f"Employee Name: {detail['employee_name']}")
        print(f"Month: {detail['month']}")
        print(f"Year: {detail['year']}")
        print(f"Employee Identification: {detail['employee_identification']}")
        print(f"Employee Entry Date: {detail['entry_date']}")

        

        # Convertir los datos a JSON con el serializador personalizado
        json_data = json.dumps(data, cls=DjangoJSONEncoder, indent=4)
        print(json_data)
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


# method format date
def format_date(value):
    """
    Convierte un valor a una cadena ISO 8601 si es una fecha válida.
    Si no es una fecha o es None, devuelve una cadena vacía.
    """
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    return '' if value is None else str(value)

#method to calculate the worked days
def calculate_worked_days(start_date, end_date=None, liquidation_end_date=None):
    """
    Calculates the number of worked days based on the provided dates.
    - If end_date exists, it calculates from start_date to end_date.
    - If end_date does not exist, it calculates from start_date to liquidation_end_date.
    :param start_date: Start date (required).
    :param end_date: End date (optional).
    :param liquidation_end_date: Liquidation end date (optional).
    :return: Number of worked days.
    """
    if not start_date:
        raise ValueError("The start date is required.")
    
    # Convert dates to datetime objects if they are strings
    if isinstance(start_date, str):
        start_date = datetime.datetime.fromisoformat(start_date)
    if end_date and isinstance(end_date, str):
        end_date = datetime.datetime.fromisoformat(end_date)
    if liquidation_end_date and isinstance(liquidation_end_date, str):
        liquidation_end_date = datetime.datetime.fromisoformat(liquidation_end_date)
    
    # Determine the final date for the calculation
    final_date = end_date or liquidation_end_date
    if not final_date:
        raise ValueError("An end date or a liquidation end date is required.")
    
    # Calculate the difference in days
    worked_days = (final_date - start_date).days
    return worked_days


#method to get the company data
def get_company_data(container):
    """Retrieve and format company data."""
    company = Empresa.objects.filter(idempresa=container.empresa.idempresa).values_list(
        'nombreempresa', 'nit', 'dv', 'direccionempresa'
    ).first()
    
    return {
        "RazonSocial": company[0],
        "NIT": company[1],
        "DigitoVerificacion": company[2],
        "Pais": container.paisgeneracion,
        "DepartamentoEstado": container.ciudadgeneracion,
        "MunicipioCiudad": f"{container.ciudadgeneracion}{container.departamentogeneracion}",
        "Direccion": company[3]
    }


#method to get the employee data
def get_employee_details(container, month, ano_id):
    """Query and retrieve employee details for payroll."""
    return Nomina.objects.select_related('idcontrato__idempleado').filter(
        idcontrato__id_empresa=container.empresa.idempresa,
        idnomina__mesacumular=month,
        idnomina__anoacumular=ano_id
    ).values(
        id=F('idcontrato'),
        employee_name=Concat(
            F('idcontrato__idempleado__papellido'), Value(' '), F('idcontrato__idempleado__sapellido'),
            Value(' '), F('idcontrato__idempleado__pnombre'), Value(' '), F('idcontrato__idempleado__snombre')
        ),
        first_name=F('idcontrato__idempleado__pnombre'),
        second_name=F('idcontrato__idempleado__snombre'),
        first_lastname=F('idcontrato__idempleado__papellido'),
        second_lastname=F('idcontrato__idempleado__sapellido'),
        entry_date=F('idcontrato__fechainiciocontrato'),
        exit_date=F('idcontrato__fechafincontrato'),
        contributing_type=F('idcontrato__tipocotizante__tipocotizante'),
        subcontributing_type=F('idcontrato__subtipocotizante__subtipocotizante'),
        pension_risk=F('idcontrato__riesgo_pension'),
        month=F('idnomina__mesacumular'),
        year=F('idnomina__anoacumular__ano'),
        employee_identification=F('idcontrato__idempleado__docidentidad'),
        document_type=F('idcontrato__idempleado__tipodocident__cod_dian'),
        employee_email=F('idcontrato__idempleado__email'),
        employee_phone=F('idcontrato__idempleado__telefonoempleado'),
        employee_address=F('idcontrato__idempleado__direccionempleado'),
        salary_type=Case(
            When(idcontrato__tiposalario__idtiposalario=2, then=Value(True)),
            default=Value(False),
            output_field=CharField()
        ),
        salary=F('idcontrato__salario'),
        type_of_contract=F('idcontrato__tipocontrato__cod_dian'),
        employee_bank=F('idcontrato__bancocuenta__nombanco'),
        employee_type_bank=F('idcontrato__tipocuentanomina'),
        employee_account=F('idcontrato__cuentanomina')
    ).distinct('idcontrato').order_by('idcontrato')


#method to get the payroll data
def get_concept_details(month, ano_id):
    """Query and retrieve concept details for payroll."""
    return Nomina.objects.select_related('idcontrato', 'idconcepto__grupo_dian').filter(
        idnomina__mesacumular=month,
        idnomina__anoacumular=ano_id
    ).values(
        contrato_id=F('idcontrato__idcontrato'),
        concepto=F('idconcepto__nombreconcepto'),
        concepto_dian=F('idconcepto__grupo_dian__campo'),
        valor_anotado=F('valor'),
        cantidad_anotado=F('cantidad'),
        control_id=F('control'),
        tipo_concepto=F('idconcepto__tipoconcepto'),
        mulitplicador_concepto=F('idconcepto__multiplicadorconcepto')
    )


def classify_concepts(concept_details):

    #concepts static payroll
    ces_percentage = int(Conceptosfijos.objects.get(idfijo=8).valorfijo)
    eps_percentage = int(Conceptosfijos.objects.get(idfijo=10).valorfijo)
    pension_percentage = int(Conceptosfijos.objects.get(idfijo=12).valorfijo)
    fsp_percentage = int(Conceptosfijos.objects.get(idfijo=14).valorfijo)

    """Classify concepts into earnings (Devengados) and deductions (Deducciones)."""
    devengados = {}
    deducciones = {}

    devengadosSum = 0
    deduccionesSum = 0

    for concept in concept_details:

        #validate concept type is 2 and the value is negative
        if concept['tipo_concepto'] == 2 and concept['valor_anotado'] < 0:
            concept['valor_anotado'] = abs(concept['valor_anotado'])
        
        if concept['concepto_dian'] == 'SueldoTrabajado':
            if "Basico" not in devengados:
                devengados["Basico"] = {
                    "DiasTrabajados": 0,
                    "SueldoTrabajado": 0
                }
            devengados["Basico"]["DiasTrabajados"] += concept['cantidad_anotado']
            devengados["Basico"]["SueldoTrabajado"] += concept['valor_anotado']

            devengadosSum += concept['valor_anotado']

        # CODAuxilioTransporte
        if concept['concepto_dian'] == 'AuxilioTransporte':
            if "Transporte" not in devengados:
                devengados["Transporte"] = {
                    "AuxilioTransporte": 0
                }
            devengados["Transporte"]["AuxilioTransporte"] += concept['valor_anotado']
            devengadosSum += concept['valor_anotado']

        # CODViaticoManuAlojNS
        if concept['concepto_dian'] == 'ViaticoManuAlojNS':
            if "Transporte" not in devengados:
                devengados["Transporte"] = {
                    "ViaticoManuAlojNS": 0
                }
            devengados["Transporte"]["ViaticoManuAlojNS"] += concept['valor_anotado']
            devengadosSum += concept['valor_anotado']

        # CODViaticoManuAlojS
        if concept['concepto_dian'] == 'ViaticoManuAlojS':
            if "Transporte" not in devengados:
                devengados["Transporte"] = {
                    "ViaticoManuAlojS": 0
                }
            devengados["Transporte"]["ViaticoManuAlojS"] += concept['valor_anotado']
            devengadosSum += concept['valor_anotado']

        # HoraExtraDiurna, HoraExtraDiurnaDominicalFestivo HoraExtraNocturna, RecargoNocturno, HoraExtraDiurnaDominicalFestiva, HoraRecargoDiurnoDominicalFestivo, HoraExtraNocturnaDominicalFestiva, HoraRecargoNocturnoDominicalFestivo
        if concept['concepto_dian'] in [
            'HoraExtraDiurna', 'HoraExtraDiurnaDominicalFestivo', 'HoraExtraNocturna', 'RecargoNocturno',
            'HoraExtraDiurnaDominicalFestiva', 'HoraRecargoDiurnoDominicalFestivo', 'HoraExtraNocturnaDominicalFestiva',
            'HoraRecargoNocturnoDominicalFestivo'
        ]:
            array_sub = {
                "HoraInicio": "",  # YYYY-MM-DD HH:MM:SS
                "HoraFin": "",
                "Cantidad": concept['cantidad_anotado'],
                "Porcentaje": concept['mulitplicador_concepto'],
                "Pago": concept['valor_anotado']
            }

            if concept['concepto_dian'] not in devengados:
                devengados[concept['concepto_dian']] = {
                    "Cantidad": 0,
                    "Pago": 0,
                    "Detalles": []
                }

            devengados[concept['concepto_dian']]["Cantidad"] += concept['cantidad_anotado']
            devengados[concept['concepto_dian']]["Pago"] += concept['valor_anotado']
            devengados[concept['concepto_dian']]["Detalles"].append(array_sub)
            devengadosSum += concept['valor_anotado']

        # VacacionesComunes
        if concept['concepto_dian'] == 'VacacionesComunes':
            vacation_detail = Vacaciones.objects.filter(idvacaciones=concept['control_id']).values('fechainicialvac', 'ultimodiavac', 'diascalendario', 'pagovac')
            if "Vacaciones" not in devengados:
                devengados["Vacaciones"] = {
                    "VacacionesComunes": []
                }
            devengados["Vacaciones"]["VacacionesComunes"].append({
                "FechaInicio": format_date(vacation_detail[0]['fechainicialvac']),
                "FechaFin": format_date(vacation_detail[0]['ultimodiavac']),
                "Cantidad": concept['cantidad_anotado'],
                "Pago": concept['valor_anotado']
            })
            devengadosSum += concept['valor_anotado']

        # VacacionesCompensadas
        if concept['concepto_dian'] == 'VacacionesCompensadas':
            if "Vacaciones" not in devengados:
                devengados["Vacaciones"] = {}  # Inicializar "Vacaciones" como un diccionario

            # Asegurarse de que "VacacionesCompensadas" existe dentro de "Vacaciones"
            if "VacacionesCompensadas" not in devengados["Vacaciones"]:
                devengados["Vacaciones"]["VacacionesCompensadas"] = []  # Inicializar como lista

            # Agregar los datos al array "VacacionesCompensadas"
            devengados["Vacaciones"]["VacacionesCompensadas"].append({
                "Cantidad": concept['cantidad_anotado'],
                "Pago": concept['valor_anotado']
            })

            # Sumar el valor al total de devengados
            devengadosSum += concept['valor_anotado']

        # Primas
        if concept['concepto_dian'] == 'Primas':
            if "Primas" not in devengados:
                devengados["Primas"] = {
                    "Cantidad": 0,
                    "Pago": 0,
                    "PagoNS": 0
                }
            devengados["Primas"]["Cantidad"] += concept['cantidad_anotado']
            devengados["Primas"]["Pago"] += concept['valor_anotado']
            devengados["Primas"]["PagoNS"] += concept['valor_anotado'] if concept['tipo_concepto'] == 'NS' else 0
            devengadosSum += concept['valor_anotado']

        # Cesantias
        if concept['concepto_dian'] == 'Cesantias':
            if "Cesantias" not in devengados:
                devengados["Cesantias"] = {
                    "Pago": 0,
                    "Porcentaje": ces_percentage,
                    "PagoIntereses": 0
                }
            devengados["Cesantias"]["Pago"] += concept['valor_anotado']
            devengadosSum += concept['valor_anotado']

        # Intereses sobre Cesantias
        if concept['concepto_dian'] == 'Intereses':
            if "Cesantias" not in devengados:
                devengados["Cesantias"] = {
                    "Pago": 0,
                    "Porcentaje": ces_percentage,
                    "PagoIntereses": 0
                }
            devengados["Cesantias"]["PagoIntereses"] += concept['valor_anotado']
            devengadosSum += concept['valor_anotado']

        # Incapacidad
        if concept['concepto_dian'] == 'Incapacidad':
            disability_detail = Incapacidades.objects.filter(idincapacidad=concept['control_id']).values('fechainicial', 'dias', 'origenincap')
            if not disability_detail.exists():
                origenincap = ''
                fechainicial = ''
                dias = ''
                fechafinal = ''
            else:
                origenincap = disability_detail[0]['origenincap']
                fechainicial = disability_detail[0]['fechainicial']
                dias = disability_detail[0]['dias']
                fechafinal = fechainicial + datetime.timedelta(days=dias)
            if "Incapacidad" not in devengados:
                devengados["Incapacidad"] = []
            devengados["Incapacidad"].append({
                "FechaInicio": format_date(fechainicial),
                "FechaFin": format_date(fechafinal),
                "Cantidad": dias,
                "Tipo": origenincap,
                "Pago": concept['valor_anotado']
            })
            devengadosSum += concept['valor_anotado']

        # LicenciaMP
        if concept['concepto_dian'] == 'LicenciaMP':
            if "LicenciaMP" not in devengados:
                devengados["LicenciaMP"] = []
            devengados["LicenciaMP"].append({
                "FechaInicio": '',
                "FechaFin": '',
                "Cantidad": concept['cantidad_anotado'],
                "Pago": concept['valor_anotado']
            })
            devengadosSum += concept['valor_anotado']

        # LicenciaR
        if concept['concepto_dian'] == 'LicenciaR':
            if "LicenciaR" not in devengados:
                devengados["LicenciaR"] = []
            devengados["LicenciaR"].append({
                "FechaInicio": '',
                "FechaFin": '',
                "Cantidad": concept['cantidad_anotado'],
                "Pago": concept['valor_anotado']
            })
            devengadosSum += concept['valor_anotado']

        # LicenciaNR
        if concept['concepto_dian'] == 'LicenciaNR':
            if "LicenciaNR" not in devengados:
                devengados["LicenciaNR"] = []
            devengados["LicenciaNR"].append({
                "FechaInicio": format_date(concept['fechainicial']),
                "FechaFin": format_date(concept['fechafinal']),
                "Cantidad": concept['cantidad_anotado'],
                "Pago": concept['valor_anotado']
            })
            devengadosSum += concept['valor_anotado']

        # BonificacionS
        if concept['concepto_dian'] == 'BonificacionS':
            if "Bonificacion" not in devengados:
                devengados["Bonificacion"] = {
                    "BonificacionS": 0,
                    "BonificacionNS": 0
                }
            devengados["Bonificacion"]["BonificacionS"] += concept['valor_anotado']
            devengadosSum += concept['valor_anotado']

        # BonificacionNS
        if concept['concepto_dian'] == 'BonificacionNS':
            if "Bonificacion" not in devengados:
                devengados["Bonificacion"] = {
                    "BonificacionS": 0,
                    "BonificacionNS": 0
                }
            devengados["Bonificacion"]["BonificacionNS"] += concept['valor_anotado']
            devengadosSum += concept['valor_anotado']

        # AuxilioS
        if concept['concepto_dian'] == 'AuxilioS':
            if "Auxilio" not in devengados:
                devengados["Auxilio"] = {
                    "AuxilioS": 0,
                    "AuxilioNS": 0
                }
            devengados["Auxilio"]["AuxilioS"] += concept['valor_anotado']
            devengadosSum += concept['valor_anotado']

        # AuxilioNS
        if concept['concepto_dian'] == 'AuxilioNS':
            if "Auxilio" not in devengados:
                devengados["Auxilio"] = {
                    "AuxilioS": 0,
                    "AuxilioNS": 0
                }
            devengados["Auxilio"]["AuxilioNS"] += concept['valor_anotado']
            devengadosSum += concept['valor_anotado']

        # HuelgaLegal
        if concept['concepto_dian'] == 'HuelgaLegal':
            if "HuelgaLegal" not in devengados:
                devengados["HuelgaLegal"] = []
            devengados["HuelgaLegal"].append({
                "FechaInicio": format_date(concept['fechainicial']),
                "FechaFin": format_date(concept['fechafinal']),
                "Cantidad": concept['cantidad_anotado']
            })
            devengadosSum += concept['valor_anotado']

        # OtroConcepto
        if concept['concepto_dian'] == 'OtroConcepto':
            if "OtroConcepto" not in devengados:
                devengados["OtroConcepto"] = []
            devengados["OtroConcepto"].append({
                "DescripcionConcepto": concept['concepto'],
                "ConceptoS": concept['valor_anotado'] if concept['tipo_concepto'] == 'S' else 0,
                "ConceptoNS": concept['valor_anotado'] if concept['tipo_concepto'] == 'NS' else 0
            })
            devengadosSum += concept['valor_anotado']

        # Compensacion
        if concept['concepto_dian'] == 'Compensacion':
            if "Compensacion" not in devengados:
                devengados["Compensacion"] = []
            devengados["Compensacion"].append({
                "CompensacionO": concept['valor_anotado'] if concept['tipo_concepto'] == 'O' else 0,
                "CompensacionE": concept['valor_anotado'] if concept['tipo_concepto'] == 'E' else 0
            })
            devengadosSum += concept['valor_anotado']

        # BonoEPCTV
        if concept['concepto_dian'] == 'BonoEPCTV':
            if "BonoEPCTV" not in devengados:
                devengados["BonoEPCTV"] = []
            devengados["BonoEPCTV"].append({
                "PagoS": concept['valor_anotado'] if concept['tipo_concepto'] == 'S' else 0,
                "PagoNS": concept['valor_anotado'] if concept['tipo_concepto'] == 'NS' else 0,
                "PagoAlimentacionS": concept['valor_anotado'] if concept['tipo_concepto'] == 'AlimentacionS' else 0,
                "PagoAlimentacionNS": concept['valor_anotado'] if concept['tipo_concepto'] == 'AlimentacionNS' else 0
            })
            devengadosSum += concept['valor_anotado']

        # Comisiones
        if concept['concepto_dian'] == 'Comisiones':
            if "Comisiones" not in devengados:
                devengados["Comisiones"] = []
            devengados["Comisiones"].append({
                "Comision": concept['valor_anotado']
            })
            devengadosSum += concept['valor_anotado']

        # PagosTerceros
        if concept['concepto_dian'] == 'PagosTerceros':
            if "PagosTerceros" not in devengados:
                devengados["PagosTerceros"] = []
            devengados["PagosTerceros"].append({
                "PagosTercero": concept['valor_anotado']
            })
            devengadosSum += concept['valor_anotado']

        # Anticipos
        if concept['concepto_dian'] == 'Anticipos':
            if "Anticipos" not in devengados:
                devengados["Anticipos"] = []
            devengados["Anticipos"].append({
                "Anticipo": concept['valor_anotado']
            })
            devengadosSum += concept['valor_anotado']

        # Deductions
        # CODSalud
        if concept['concepto_dian'] == 'Salud':
            if "Salud" not in deducciones:
                deducciones["Salud"] = {
                    "Porcentaje": eps_percentage,
                    "Deduccion": 0
                }
            deducciones["Salud"]["Deduccion"] += concept['valor_anotado']
            deduccionesSum += concept['valor_anotado']

        # CODFondoPension
        if concept['concepto_dian'] == 'FondoPension':
            if "FondoPension" not in deducciones:
                deducciones["FondoPension"] = {
                    "Porcentaje": pension_percentage,
                    "Deduccion": 0
                }
            deducciones["FondoPension"]["Deduccion"] += concept['valor_anotado']
            deduccionesSum += concept['valor_anotado']

        # CODFondoSP
        if concept['concepto_dian'] == 'FondoSP':
            if "FondoSP" not in deducciones:
                deducciones["FondoSP"] = {
                    "Porcentaje": fsp_percentage,
                    "DeduccionSP": 0,
                    "PorcentajeSub": 0,
                    "DeduccionSub": 0
                }
            deducciones["FondoSP"]["DeduccionSP"] += concept['valor_anotado']
            deduccionesSum += concept['valor_anotado']

        # CODSindicatos
        if concept['concepto_dian'] == 'Sindicatos':
            if "Sindicatos" not in deducciones:
                deducciones["Sindicatos"] = {
                    "Deduccion": 0
                }
            deducciones["Sindicatos"]["Deduccion"] += concept['valor_anotado']
            deduccionesSum += concept['valor_anotado']

        # CODSanciones
        if concept['concepto_dian'] == 'Sanciones':
            if "Sanciones" not in deducciones:
                deducciones["Sanciones"] = {
                    "Deduccion": 0
                }
            deducciones["Sanciones"]["Deduccion"] += concept['valor_anotado']
            deduccionesSum += concept['valor_anotado']

        # CODLibranzas
        if concept['concepto_dian'] == 'Libranzas':
            if "Libranzas" not in deducciones:
                deducciones["Libranzas"] = {
                    "Deduccion": 0
                }
            deducciones["Libranzas"]["Deduccion"] += concept['valor_anotado']
            deduccionesSum += concept['valor_anotado']

        # CODOtrasDeducciones
        if concept['concepto_dian'] == 'OtrasDeducciones':
            if "OtrasDeducciones" not in deducciones:
                deducciones["OtrasDeducciones"] = {
                    "OtraDeduccion": 0
                }
            deducciones["OtrasDeducciones"]["Deduccion"] += concept['valor_anotado']
            deduccionesSum += concept['valor_anotado']

        # CODAnticipos
        if concept['concepto_dian'] == 'Anticipos':
            if "Anticipos" not in deducciones:
                deducciones["Anticipos"] = {
                    "Anticipo": 0
                }
            deducciones["Anticipos"]["Deduccion"] += concept['valor_anotado']
            deduccionesSum += concept['valor_anotado']

        # CODPensionVoluntaria
        if concept['concepto_dian'] == 'PensionVoluntaria':
            if "PensionVoluntaria" not in deducciones:
                deducciones["PensionVoluntaria"] = 0
            deducciones["PensionVoluntaria"] += concept['valor_anotado']
            deduccionesSum += concept['valor_anotado']

        # CODRetencionFuente
        if concept['concepto_dian'] == 'RetencionFuente':
            if "RetencionFuente" not in deducciones:
                deducciones["RetencionFuente"] = 0
            
            deducciones["RetencionFuente"] += concept['valor_anotado']
            deduccionesSum += concept['valor_anotado']

        # CODAFC
        if concept['concepto_dian'] == 'AFC':
            if "AFC" not in deducciones:
                deducciones["AFC"] = 0

            deducciones["AFC"] += concept['valor_anotado']
            deduccionesSum += concept['valor_anotado']

        # CODCooperativa
        if concept['concepto_dian'] == 'Cooperativa':
            if "Cooperativa" not in deducciones:
                deducciones["Cooperativa"] = 0
            deducciones["Cooperativa"] += concept['valor_anotado']
            deduccionesSum += concept['valor_anotado']

        # CODEmbargoFiscal
        if concept['concepto_dian'] == 'EmbargoFiscal':
            if "EmbargoFiscal" not in deducciones:
                deducciones["EmbargoFiscal"] = 0
            deducciones["EmbargoFiscal"] += concept['valor_anotado']
            deduccionesSum += concept['valor_anotado']

        # CODPlanComplementarios
        if concept['concepto_dian'] == 'PlanComplementarios':
            if "PlanComplementarios" not in deducciones:
                deducciones["PlanComplementarios"] = 0

            deducciones["PlanComplementarios"] += concept['valor_anotado']
            deduccionesSum += concept['valor_anotado']

        # CODEducacion
        if concept['concepto_dian'] == 'Educacion':
            if "Educacion" not in deducciones:
                deducciones["Educacion"] = 0

            deducciones["Educacion"] += concept['valor_anotado']
            deduccionesSum += concept['valor_anotado']

        # CODReintegro
        if concept['concepto_dian'] == 'Reintegro':
            if "Reintegro" not in deducciones:
                deducciones["Reintegro"] = 0
            deducciones["Reintegro"] += concept['valor_anotado']
            deduccionesSum += concept['valor_anotado']

        # CODDeuda
        if concept['concepto_dian'] == 'Deuda':
            if "Deuda" not in deducciones:
                deducciones["Deuda"] = 0
            deducciones["Deuda"] += concept['valor_anotado']
            deduccionesSum += concept['valor_anotado']
        # if concept['tipo_concepto'] == 1:  # Earnings
        #     if concept['concepto_dian'] not in devengados:
        #         devengados[concept['concepto_dian']] = {
        #             "Cantidad": 0,
        #             "Valor": 0
        #         }
        #     devengados[concept['concepto_dian']]["Cantidad"] += concept['cantidad_anotado']
        #     devengados[concept['concepto_dian']]["Valor"] += concept['valor_anotado']
        # elif concept['tipo_concepto'] == 2:  # Deductions
        #     if concept['concepto_dian'] not in deducciones:
        #         deducciones[concept['concepto_dian']] = {
        #             "Cantidad": 0,
        #             "Valor": 0
        #         }
        #     deducciones[concept['concepto_dian']]["Cantidad"] += concept['cantidad_anotado']
        #     deducciones[concept['concepto_dian']]["Valor"] += abs(concept['valor_anotado'])

    return devengados, deducciones, devengadosSum, deduccionesSum

#method to generate json body principal
def generate_employee_json(detail, container, company_data, concept_details, generated_id):
    """Generate JSON data for an individual employee."""
    devengados, deducciones, devengadosSum, deduccionesSum = classify_concepts(concept_details)
    ComprobanteTotal = devengadosSum - deduccionesSum
    data = {
        "canal": 2,
        "Periodo": {
            "FechaIngreso": format_date(detail['entry_date']),
            "FechaRetiro": format_date(detail['exit_date']),
            "FechaLiquidacionInicio": format_date(container.fechaliquidacioninicio),
            "FechaLiquidacionFin": format_date(container.fechaliquidacionfin),
            "TiempoLaborado": str(calculate_worked_days(detail['entry_date'], detail['exit_date'], container.fechaliquidacionfin)),
            "FechaGeneracion": format_date(container.fechageneracion)
        },
        "NumeroSecuenciaXML": {
            "CodigoTrabajador": str(detail['id']),
            "Prefijo": container.prefijo,
            "Consecutivo": generated_id
        },
        "LugarGeneracionXML": {
            "Pais": container.paisgeneracion,
            "DepartamentoEstado": container.ciudadgeneracion,
            "MunicipioCiudad": f"{container.ciudadgeneracion}{container.departamentogeneracion}",
            "Idioma": container.idioma
        },
        "InformacionGeneral": {
            "TipoXML": "",
            "FechaGeneracion": container.fechageneracion,
            "HoraGeneracion": container.horageneracion,
            "PeriodoNomina": container.periodonomina,
            "TipoMoneda": container.tipomoneda
        },
        "Empleador": company_data,
        "Trabajador": {
            "TipoTrabajador": detail['contributing_type'],
            "SubTipoTrabajador": str('00'),
            "AltoRiesgoPension": str(detail['pension_risk']),
            "TipoDocumento": str(detail['document_type']),
            "NumeroDocumento": detail['employee_identification'],
            "CorreoElectronico": detail['employee_email'],
            "NumeroMovil": detail['employee_phone'],
            "PrimerApellido": detail['first_lastname'],
            "SegundoApellido": detail['second_lastname'],
            "PrimerNombre": detail['first_name'],
            "OtrosNombres": detail['second_name'],
            "LugarTrabajoPais": container.paisgeneracion,
            "LugarTrabajoDepartamentoEstado": container.ciudadgeneracion,
            "LugarTrabajoMunicipioCiudad": f"{container.ciudadgeneracion}{container.departamentogeneracion}",
            "LugarTrabajoDireccion": detail['employee_address'],
            "SalarioIntegral": "true" if detail['salary_type'] else "false",
            "TipoContrato": str(detail['type_of_contract']),
            "Sueldo": detail['salary'],
            "CodigoTrabajador": str(detail['id'])
        },
        "Pago": {
            "Forma": "1",
            "Metodo": "30",
            "Banco": detail['employee_bank'],
            "TipoCuenta": detail['employee_type_bank'],
            "NumeroCuenta": detail['employee_account']
        },
        "FechasPagos": [
            {"FechaPago": format_date(container.fechapago)}
        ],
        "Devengados": devengados,
        "Deducciones": deducciones,

        "Redondeo": "",
        "DevengadosTotal": devengadosSum,
        "DeduccionesTotal": deduccionesSum,
        "ComprobanteTotal": ComprobanteTotal
    }
    return data

@login_required
@role_required('accountant')
#method to generate the employee json
def electronic_payroll_generate_refactor(request, pk=None):
    """Main function to generate payroll JSON for one or all employees."""
    container = NeDatosMensual.objects.get(idnominaelectronica=pk)
    month, year = container.mesacumular, container.anoacumular

    try:
        ano_id = Anos.objects.get(ano=year).idano
    except Anos.DoesNotExist:
        messages.error(request, 'El año especificado no existe en el sistema.')
        return redirect('payroll:nomina_electronica')

    company_data = get_company_data(container)
    employee_details = get_employee_details(container, month, ano_id)
    concept_details = get_concept_details(month, ano_id)

    json_results = []
    for detail in employee_details:

        contrato_instance = Contratos.objects.get(idcontrato=detail['id'])

        # Create NeDetalleNominaElectronica object
        datail_payroll = NeDetalleNominaElectronica.objects.create(
            id_ne_datos_mensual=container,
            id_contrato=contrato_instance,
            fecha_creacion = datetime.datetime.now(),
            estado=1,  # Assuming 1 is the default state
            tipo_registro=1,  # Assuming 1 is the default type
            observaciones=""
        )

        # Get the generated ID
        generated_id = datail_payroll.id_detalle_nomina_electronica
        print(f"Generated ID: {generated_id}")

        employee_concepts = [concept for concept in concept_details if concept['contrato_id'] == detail['id']]
        employee_json = generate_employee_json(detail, container, company_data, employee_concepts, generated_id)

        # Update the JSON field in the NeDetalleNominaElectronica object
        formatted_json = json.dumps(employee_json, cls=DjangoJSONEncoder, indent=4, ensure_ascii=False)
        datail_payroll.json_nomina = formatted_json
        datail_payroll.save()

        json_results.append(employee_json)

    messages.success(request, 'Nómina Generada Exitosamente.')
    return redirect('payroll:detalle_nomina_electronica',  pk=pk)  # Cambia a la vista deseada después de guardar


#method to get the employee data individual
def get_employee_details_individual(contract_id):
    """Query and retrieve employee details for payroll."""
    return Nomina.objects.select_related('idcontrato__idempleado').filter(
        idcontrato=contract_id
    ).values(
        id=F('idcontrato'),
        employee_name=Concat(
            F('idcontrato__idempleado__papellido'), Value(' '), F('idcontrato__idempleado__sapellido'),
            Value(' '), F('idcontrato__idempleado__pnombre'), Value(' '), F('idcontrato__idempleado__snombre')
        ),
        first_name=F('idcontrato__idempleado__pnombre'),
        second_name=F('idcontrato__idempleado__snombre'),
        first_lastname=F('idcontrato__idempleado__papellido'),
        second_lastname=F('idcontrato__idempleado__sapellido'),
        entry_date=F('idcontrato__fechainiciocontrato'),
        exit_date=F('idcontrato__fechafincontrato'),
        contributing_type=F('idcontrato__tipocotizante__tipocotizante'),
        subcontributing_type=F('idcontrato__subtipocotizante__subtipocotizante'),
        pension_risk=F('idcontrato__riesgo_pension'),
        employee_identification=F('idcontrato__idempleado__docidentidad'),
        document_type=F('idcontrato__idempleado__tipodocident__cod_dian'),
        employee_email=F('idcontrato__idempleado__email'),
        employee_phone=F('idcontrato__idempleado__telefonoempleado'),
        employee_address=F('idcontrato__idempleado__direccionempleado'),
        salary_type=Case(
            When(idcontrato__tiposalario__idtiposalario=2, then=Value(True)),
            default=Value(False),
            output_field=CharField()
        ),
        salary=F('idcontrato__salario'),
        type_of_contract=F('idcontrato__tipocontrato__cod_dian'),
        employee_bank=F('idcontrato__bancocuenta__nombanco'),
        employee_type_bank=F('idcontrato__tipocuentanomina'),
        employee_account=F('idcontrato__cuentanomina')
    )

#method to get the payroll data for the employee contract
def get_concept_details_individual(month, ano_id, idcontrato):
    """Query and retrieve concept details for payroll."""
    return Nomina.objects.select_related('idcontrato', 'idconcepto__grupo_dian').filter(
        idnomina__mesacumular=month,
        idnomina__anoacumular=ano_id,
        idnomina__idcontrato=idcontrato
    ).values(
        contrato_id=F('idcontrato__idcontrato'),
        concepto=F('idconcepto__nombreconcepto'),
        concepto_dian=F('idconcepto__grupo_dian__campo'),
        valor_anotado=F('valor'),
        cantidad_anotado=F('cantidad'),
        control_id=F('control'),
        tipo_concepto=F('idconcepto__tipoconcepto'),
        mulitplicador_concepto=F('idconcepto__multiplicadorconcepto')
    )

def electronic_payroll_regenerate(request, pk=None):
    detail_payroll = NeDetalleNominaElectronica.objects.get(id_detalle_nomina_electronica=pk)
    container = detail_payroll.id_ne_datos_mensual
    month, year = container.mesacumular, container.anoacumular

    try:
        ano_id = Anos.objects.get(ano=year).idano
    except Anos.DoesNotExist:
        messages.error(request, 'El año especificado no existe en el sistema.')
        return redirect('payroll:nomina_electronica')

    company_data = get_company_data(container)
    employee_details = get_employee_details_individual(detail_payroll.id_contrato)
    concept_details = get_concept_details_individual(month, ano_id, detail_payroll.id_contrato)

    # Generate JSON for the individual employee
    for detail in employee_details:
        employee_concepts = [concept for concept in concept_details if concept['contrato_id'] == detail['id']]
        employee_json = generate_employee_json(detail, container, company_data, employee_concepts, detail_payroll.id_detalle_nomina_electronica)

        # Update the JSON field in the NeDetalleNominaElectronica object
        formatted_json = json.dumps(employee_json, cls=DjangoJSONEncoder, indent=4, ensure_ascii=False)
        detail_payroll.fecha_modificacion = datetime.datetime.now()
        detail_payroll.json_nomina = formatted_json
        detail_payroll.estado = 1
        detail_payroll.save()

        # Optionally, you can print or log the generated JSON
        print(formatted_json)

    messages.success(request, 'Nómina Generada Exitosamente.')
    return redirect('payroll:detalle_nomina_electronica', pk=container.idnominaelectronica)

#method to generate token
def electronic_payroll_token(empresa):
    url = f"https://alfauat.dominadigital.com.co/api/GenerarTokenJWT/{empresa.nit}-{empresa.dv}"
    payload = ""
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload)
    
    response_data = response.json()
    code_response = response_data.get("codigo")
    token = response_data.get("token")
    print(response.text)
    return code_response, token

#method to send json a provider
def electronic_payroll_send(pk=None, json_data=None):
    try:
        empresa = Empresa.objects.get(idempresa=pk)
        code_response, token = electronic_payroll_token(empresa)

        payload = json.dumps(json_data) if not isinstance(json_data, str) else json_data
        
        url = f"https://alfauat.dominadigital.com.co/api/ReceptorNominaJson/{empresa.nit}-{empresa.dv}"
        headers = {
            'Authorization': token,
            'Version-Document': '2',
            'Content-Type': 'application/json',
        }

        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Lanza una excepción si el status code no es 200
        return response.text  # Devuelve el cuerpo de la respuesta como texto
    except Empresa.DoesNotExist:
        raise ValueError("Empresa no encontrada.")
    except Exception as e:
        raise ValueError(f"Error al enviar nómina electrónica: {str(e)}")

#method to send the payroll and register detail electronic payroll
def electronic_payroll_validate_send(request, pk=None):
    details = NeDetalleNominaElectronica.objects.get(id_detalle_nomina_electronica=pk)
    JsonResponse = electronic_payroll_send(details.id_ne_datos_mensual.empresa.idempresa, details.json_nomina)
    JsonResponse = json.loads(JsonResponse)
    print(JsonResponse)
    estado_codigo = JsonResponse.get("estado", {}).get("codigo")
    
    # Pretty print the JSON response
    json_end = json.dumps(JsonResponse, indent=4, ensure_ascii=False)
    
    if estado_codigo == 'EXITOSO':
        NeRespuestaDian.objects.create(
            id_ne_detalle_nomina_electronica=details,
            fecha_transaccion = datetime.datetime.now(),
            json_respuesta = json_end,
            codigo_respuesta= estado_codigo,
        )
        details.estado = 2
        messages.success(request, 'Registro Enviado Exitosamente.')
    elif estado_codigo == 'ERROR' or estado_codigo == 'ERRORDIAN':
        NeRespuestaDian.objects.create(
            id_ne_detalle_nomina_electronica=details,
            fecha_transaccion = datetime.datetime.now(),
            json_respuesta = json_end,
            codigo_respuesta= estado_codigo,
        )
        details.estado = 3
        messages.error(request, 'Registro con Error, por favor validar.')
    
    details.save()

    return redirect('payroll:detalle_nomina_electronica',  pk=details.id_ne_datos_mensual.idnominaelectronica)  # Cambia a la vista deseada después de guardar 


def electronic_payroll_validate_masive_send(request, pk=None):
    details_payroll = NeDetalleNominaElectronica.objects.filter(id_ne_datos_mensual=pk, estado=1)
    for detail in details_payroll:
        JsonResponse = electronic_payroll_send(detail.id_ne_datos_mensual.empresa.idempresa, detail.json_nomina)
        JsonResponse = json.loads(JsonResponse)
        print(JsonResponse)
        estado_codigo = JsonResponse.get("estado", {}).get("codigo")
        
        # Pretty print the JSON response
        json_end = json.dumps(JsonResponse, indent=4, ensure_ascii=False)
        
        if estado_codigo == 'EXITOSO':
            NeRespuestaDian.objects.create(
                id_ne_detalle_nomina_electronica=detail,
                fecha_transaccion = datetime.datetime.now(),
                json_respuesta = json_end,
                codigo_respuesta= estado_codigo,
            )
            detail.estado = 2
            
        elif estado_codigo == 'ERROR' or estado_codigo == 'ERRORDIAN':
            NeRespuestaDian.objects.create(
                id_ne_detalle_nomina_electronica=detail,
                fecha_transaccion = datetime.datetime.now(),
                json_respuesta = json_end,
                codigo_respuesta= estado_codigo,
            )
            detail.estado = 3
            
        
        detail.save()

    return redirect('payroll:detalle_nomina_electronica',  pk=pk)  # Cambia a la vista deseada después de guardar 


def electronic_payroll_detail_view(request, pk=None):
    detail_payroll = NeDetalleNominaElectronica.objects.select_related(
        'id_contrato__idempleado',
        'id_contrato__cargo',
    ).annotate(
        contract_id = F('id_contrato'),
        container_id = F('id_ne_datos_mensual'),
        detail_id = F('id_detalle_nomina_electronica'),
        state_send = F('estado'),
        employee_name=Concat(
            F('id_contrato__idempleado__pnombre'), Value(' '),
            F('id_contrato__idempleado__snombre'), Value(' '),
            F('id_contrato__idempleado__papellido'), Value(' '),
            F('id_contrato__idempleado__sapellido')
        ),
        employee_document=F('id_contrato__idempleado__docidentidad'), 
        employee_position = F('id_contrato__cargo__nombrecargo'),
        employee_salary = F('id_contrato__salario'),
        employee_entry_date = F('id_contrato__fechainiciocontrato'),
    ).get(id_detalle_nomina_electronica=pk)
    print(detail_payroll.container_id)
    detail_payroll_response = NeRespuestaDian.objects.filter(id_ne_detalle_nomina_electronica=pk)

    cune = None
    for response in detail_payroll_response:
        if response.codigo_respuesta == 'EXITOSO':
            response_data = json.loads(response.json_respuesta)
            cune = response_data.get("cune")
            break
            

    # Aquí asumimos que el campo con el JSON se llama `json_data`
    json_data = json.loads(detail_payroll.json_nomina)  # Convertir el JSON en diccionario
    print(json_data)
    context = {
        'detail_payroll': detail_payroll,
        'detail_payroll_response': detail_payroll_response,
        'json_data': json_data,
        'cune': cune
    }

    return render(request, 'payroll/electronic_payroll_detail_view.html', context)