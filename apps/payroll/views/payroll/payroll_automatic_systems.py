Manuel Berdugo, [19/03/2025 2:12 p. m.]
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Crearnomina , Contratos ,Costos, Crearnomina ,EmpVacaciones, Salariominimoanual,Conceptosdenomina , Empresa , Vacaciones , Nomina , Contratos
from django.contrib import messages
from django.db import transaction, models
from datetime import datetime
from django.db.models import Sum

@login_required
@role_required('accountant')
def automatic_systems(request, type_payroll=0,idnomina=0):
    
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    titles = {
        0: 'Nómina Básica',
        1: 'Incapacidades',
        2: 'Aportes',
        3: 'Transporte',
        4: 'Reinicio de Nómina'
    }

    titulo = titles.get(type_payroll, 'Sistemas Automáticos')
    centros = Costos.objects.filter(id_empresa_id=idempresa)
    
    
    
    if request.method == 'POST':
        need_comment = request.POST.get('need_comment', False)  # Devuelve 'on' si está marcado, None si no
        no_cost_center = request.POST.get('no-cost-center', False)
        costo = request.POST.get('costos', False)
        # Convertirlo a True/False
        need_comment = need_comment == 'on'
        no_cost_center = no_cost_center == 'on'
                
        if need_comment:
            if type_payroll == 0:
                if procesar_nomina(idnomina, costo, idempresa):
                    messages.success(request, "Nómina procesada correctamente")
                    return redirect('payroll:payrollview', id=idnomina)
                else :
                    messages.error(request, "Error al procesar la nómina")
                    return redirect('payroll:payrollview', id=idnomina)
            else:
                messages.error(request, "Error #13 al procesar la nómina")
                return redirect('payroll:payrollview', id=idnomina)
        else:
            if type_payroll == 0:
                if procesar_nomina(idnomina, 0,idempresa) :
                    messages.success(request, "Nómina procesada correctamente")
                    return redirect('payroll:payrollview', id=idnomina)
                else :
                    messages.error(request, "Error al procesar la nómina")
                    return redirect('payroll:payrollview', id=idnomina)
            else:
                messages.error(request, "Error #13 al procesar la nómina")
                return redirect('payroll:payrollview', id=idnomina)
    
    return render(request, 'payroll/partials/payroll_automatic_systems.html', {'titulo': titulo, 'centros': centros, 'type_payroll': type_payroll , 'idnomina':idnomina})


# Lógica de consulta en Django ORM
def procesar_nomina(idn, parte_nomina,idempresa):
    if not parte_nomina:
        parte_nomina = 0

    contratos = Contratos.objects.filter(estadoliquidacion=3, id_empresa =  idempresa)
    if parte_nomina != 0:
        contratos = contratos.filter(idcosto = parte_nomina)

    try:
        nomina = Crearnomina.objects.get(idnomina=idn)
    except Crearnomina.DoesNotExist:
        return "Error de creación de nómina"

    for contrato in contratos:
        diasnomina = nomina.diasnomina

        if contrato.fechainiciocontrato > nomina.fechafinal:
            diasnomina = (nomina.fechafinal - contrato.fechainiciocontrato).days + 1

        if contrato.fechafincontrato and nomina.fechafinal <= contrato.fechafincontrato <= nomina.fechafinal:
            diasnomina -= (nomina.fechafinal - contrato.fechafincontrato).days
            
            
        dias_vacaciones = calcular_vacaciones(contrato, idn,nomina)
        dias_incapacidad = calculo_incapacidad(contrato, idn)

diasnomina -= dias_vacaciones 
        diasnomina -= dias_incapacidad 
        
        if contrato.tiposalario_id == 2:
            codigo_aux = '4'
        elif contrato.tipocontrato_id in [5, 6]:
            codigo_aux = '34'
        else:
            codigo_aux = '1'
        concepto = Conceptosdenomina.objects.get(codigo=codigo_aux, id_empresa_id = idempresa)
        if diasnomina > 0:
            if diasnomina > 30:
                diasnomina = 30
                
                
            valorsalario = (contrato.salario / 30) * diasnomina
            
            Nomina.objects.create(
                idconcepto = concepto ,#*
                cantidad=diasnomina ,#*
                valor=valorsalario , #*
                idcontrato_id=contrato.idcontrato ,
                idnomina_id = idn ,
            )
            
    return True


def calcular_vacaciones(contrato, idn ,nomina ):
    dias_vacaciones = 0
    vacaciones = EmpVacaciones.objects.filter(idcontrato=contrato ,estado = 2 ,tipovac='1' )
    
    for vac in vacaciones:
        data = Vacaciones.objects.filter(idcontrato=contrato, tipovac='1' ,idnomina = idn , idvacmaster = vac.id_sol_vac).first() 
        if data:
            dias_vacaciones = data.diasvac
        else:
            if vac.fechainicialvac <= nomina.fechafinal and vac.fechafinalvac >= nomina.fechainicial:
                inicio = max(vac.fechainicialvac, nomina.fechainicial)
                fin = min(vac.fechafinalvac, nomina.fechafinal)
                dias_vacaciones = (fin - inicio).days + 1

                
                Vacaciones.objects.create(
                    idcontrato= contrato  ,
                    diascalendario = vac.diascalendario,
                    diasvac = dias_vacaciones,
                    idnomina_id = idn,
                    cuentasabados = vac.cuentasabados,
                    tipovac = vac.tipovac,
                    idvacmaster = vac.id_sol_vac,
                    )        
    
    
    return dias_vacaciones

def calculo_incapacidad(contrato, idn ):   
    dias_incapacidad = 0
    
    dias_incapacidad_tempo = Nomina.objects.filter(
        idnomina=idn,
        idcontrato=contrato,
        idconcepto__codigo__in=[25, 26, 27, 28, 29]
    ).aggregate(total_dias_incapacidad=Sum('cantidad'))['total_dias_incapacidad']
    
    
    if dias_incapacidad_tempo:
        dias_incapacidad = dias_incapacidad_tempo
    
    return dias_incapacidad