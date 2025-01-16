import datetime
from django.shortcuts import render, redirect, get_object_or_404
import json
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import F, Q, Case, When, Value, CharField, Sum
from django.db.models.functions import Concat
from django.core.serializers.json import DjangoJSONEncoder

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
                            idnomina__anoacumular=ano_id
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



        #generate register detalle_nomina_electronica
        #TODO

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
                    "Cantidad": item['cantidad_anotado'],
                    "Porcentaje": item['mulitplicador_concepto'],  # Example percentage, replace with actual value if needed
                    "Pago": item['valor_anotado']
                }

                if item['concepto_dian'] not in data["Devengados"]:
                    data["Devengados"][item['concepto_dian']] = {
                        "Cantidad": 0,
                        "Pago": 0,
                        "Detalles": []
                    }

                data["Devengados"][item['concepto_dian']]["Cantidad"] += item['cantidad_anotado']
                data["Devengados"][item['concepto_dian']]["Pago"] += item['valor_anotado']
                data["Devengados"][item['concepto_dian']]["Detalles"].append(array_sub)

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