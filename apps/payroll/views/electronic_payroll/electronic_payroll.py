from django.shortcuts import render 
import json
from django.http import JsonResponse


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