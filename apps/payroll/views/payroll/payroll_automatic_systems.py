from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Crearnomina , Contratos, EditHistory , Conceptosfijos ,Costos,Salariominimoanual, Crearnomina ,EmpVacaciones,Prestamos ,Conceptosdenomina , Empresa , Vacaciones , Nomina , Contratos
from django.contrib import messages
from django.db import transaction, models
from datetime import datetime
from django.db.models import Sum

#prueba git
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
        
        ne = costo if need_comment else 0
        
        if type_payroll == 0:
            if procesar_nomina_basica(idnomina,ne, idempresa):
                messages.success(request, "Proceso Basico realizado correctamente")
                return redirect('payroll:payrollview', id=idnomina)
            else :
                messages.error(request, "Error al procesar la nómina")
                return redirect('payroll:payrollview', id=idnomina)
            
        
        elif  type_payroll == 1:
            if procesar_nomina_incapacidad(idnomina, ne , idempresa):
                messages.success(request, "Proceso de Incapacidades realizado correctamente")
                return redirect('payroll:payrollview', id=idnomina)
            else :
                messages.error(request, "Error al realizar procesar la nómina")
                return redirect('payroll:payrollview', id=idnomina)
        
        elif  type_payroll == 2:
            if procesar_nomina_aportes(idnomina, ne , idempresa):
                messages.success(request, "Proceso de Aportes realizado correctamente")
                return redirect('payroll:payrollview', id=idnomina)
            else :
                messages.error(request, "Error al realizar procesar la nómina")
                return redirect('payroll:payrollview', id=idnomina)
            
        elif  type_payroll == 3:
            if procesar_nomina_transporte(idnomina, ne , idempresa):
                messages.success(request, "Proceso de Transporte realizado correctamente")
                return redirect('payroll:payrollview', id=idnomina)
            else :
                messages.error(request, "Error al realizar procesar la nómina")
                return redirect('payroll:payrollview', id=idnomina)
        else:
            messages.error(request, "Error #13 al procesar la nómina")
            return redirect('payroll:payrollview', id=idnomina)
    
    return render(request, 'payroll/partials/payroll_automatic_systems.html', {'titulo': titulo, 'centros': centros, 'type_payroll': type_payroll , 'idnomina':idnomina})






def procesar_nomina_basica(idn, parte_nomina,idempresa):
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
            
            
        dias_vacaciones = calcular_vacaciones(contrato,nomina)
        dias_incapacidad = calculo_incapacidad(contrato, idn)

        diasnomina -= dias_vacaciones 
        diasnomina -= dias_incapacidad 
        
        
        calculo_prestamo(contrato, idn)
        
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
            
            aux_pass = Nomina.objects.filter(
                idconcepto=concepto,
                idcontrato=contrato,
                idnomina_id=idn
            ).first()
            
            if aux_pass:
                if not EditHistory.objects.filter(
                    id_empresa_id=idempresa,
                    modified_object_id=aux_pass.idregistronom,
                    modified_model='Nomina',
                ).exists():
                    aux_pass.cantidad = diasnomina
                    aux_pass.valor = valorsalario
                    aux_pass.save()  
                                
            else:
                Nomina.objects.create(
                    idconcepto = concepto ,#*
                    cantidad=diasnomina ,#*
                    valor=valorsalario , #*
                    idcontrato_id=contrato.idcontrato ,
                    idnomina_id = idn ,
                )   
    return True


def procesar_nomina_incapacidad(idn, parte_nomina,idempresa):
    if not parte_nomina:
        parte_nomina = 0
        


def procesar_nomina_aportes(idn, parte_nomina,idempresa):
    EPS = Conceptosfijos.objects.get(idfijo = 10)
    AFP = Conceptosfijos.objects.get(idfijo = 12)
    tope_ibc = Conceptosfijos.objects.get(idfijo = 4)
    factor_integral = Conceptosfijos.objects.get(idfijo = 3)
    
    ## pruebas de valores 
    fsp416 = Conceptosfijos.objects.get(idfijo = 14)
    fsp1617 = Conceptosfijos.objects.get(idfijo = 15)
    fsp1718 = Conceptosfijos.objects.get(idfijo = 16)
    fsp1819 = Conceptosfijos.objects.get(idfijo = 17)
    fsp1920 = Conceptosfijos.objects.get(idfijo = 18)
    fsp21 = Conceptosfijos.objects.get(idfijo = 19)
    
    sal_min = Salariominimoanual.objects.get(ano = datetime.now().year).salariominimo

    if not parte_nomina:
        parte_nomina = 0

    contratos = Contratos.objects.filter(estadoliquidacion=3, id_empresa =  idempresa)
    if parte_nomina != 0:
        contratos = contratos.filter(idcosto = parte_nomina)
    
    for contrato in contratos:
        
        salario_emp = contrato.salario
        tipo_salario = contrato.tiposalario

        
        # Obtener la suma de las deducciones de la eps 
        total_base_ss = Nomina.objects.filter(
            idcontrato=contrato,
            idnomina_id=idn,
            idconcepto__indicador__id=7
        ).exclude(
            idconcepto__codigo__in=[60, 70, 90] # Excluir conceptos cuyo código sea el de EPS
        ).aggregate(total=Sum('valor'))['total'] or 0  # Reemplaza 'monto' con el nombre correcto de la columna
                
        
        
        if total_base_ss > 0:
            
            concepto1 = Conceptosdenomina.objects.get(codigo = 60 , id_empresa_id = idempresa)
            concepto2 = Conceptosdenomina.objects.get(codigo = 70 , id_empresa_id = idempresa)
            concepto3 = Conceptosdenomina.objects.get(codigo = 90 , id_empresa_id = idempresa)
            
            base_max = sal_min * tope_ibc.valorfijo
        
            if tipo_salario == '2':
                total_base_ss *= (factor_integral / 100)
                
            base_ss = min(total_base_ss, base_max)
            
            
            if base_ss > (sal_min * 20):
                FSP = fsp21.valorfijo
            elif base_ss > (sal_min * 19):
                FSP = fsp1920.valorfijo
            elif base_ss > (sal_min * 18):
                FSP = fsp1819.valorfijo
            elif base_ss > (sal_min * 17):
                FSP = fsp1718.valorfijo
            elif base_ss > (sal_min * 16):
                FSP = fsp1617.valorfijo
            elif base_ss > (sal_min * 4):
                FSP = fsp416.valorfijo
            else:
                FSP = 0
            
            
            
            
            valoreps = (total_base_ss * EPS.valorfijo ) / 100
            valorafp = (total_base_ss * AFP.valorfijo ) / 100
            valorfsp = (total_base_ss * FSP ) / 100 if total_base_ss >= (sal_min * 4) else 0
            
            
            if contrato.pensionado == '2':
                valorafp = 0
                valorfsp = 0
            
            
            # Crear o actualizar el registro de la EPS
            aux_pass = Nomina.objects.filter(
                idconcepto=concepto1,
                idcontrato=contrato,
                idnomina_id=idn
            ).first()
            
            if aux_pass:
                if not EditHistory.objects.filter(
                    id_empresa_id=idempresa,
                    modified_object_id=aux_pass.idregistronom,
                    modified_model='Nomina',
                ).exists():
                    aux_pass.valor = -1*valoreps
                    aux_pass.save() 
                                
            else:
                Nomina.objects.create(
                        idconcepto = concepto1 ,#*
                        cantidad= 0 ,#*
                        valor=-1*valoreps , #*
                        idcontrato_id=contrato.idcontrato ,
                        idnomina_id = idn ,
                    )  
                
            
            
            
            aux_pass = Nomina.objects.filter(
                idconcepto=concepto2,
                idcontrato=contrato,
                idnomina_id=idn
            ).first()
            
            
            if aux_pass:
                if not EditHistory.objects.filter(
                    id_empresa_id=idempresa,
                    modified_object_id=aux_pass.idregistronom,
                    modified_model='Nomina',
                ).exists():
                    aux_pass.valor = -1*valorafp
                    aux_pass.save() 
                                
            else:
                Nomina.objects.create(
                        idconcepto = concepto2 ,#*
                        cantidad= 0 ,#*
                        valor=-1*valorafp , #*
                        idcontrato_id=contrato.idcontrato ,
                        idnomina_id = idn ,
                    ) 
            
            
            
            if valorfsp > 0:
                aux_pass = Nomina.objects.filter(
                    idconcepto=concepto3,
                    idcontrato=contrato,
                    idnomina_id=idn
                ).first()
                
                
                if aux_pass:
                    if not EditHistory.objects.filter(
                        id_empresa_id=idempresa,
                        modified_object_id=aux_pass.idregistronom,
                        modified_model='Nomina',
                    ).exists():
                        aux_pass.valor = -1*valorfsp
                        aux_pass.save() 
                                    
                else:
                    Nomina.objects.create(
                            idconcepto = concepto3 ,#*
                            cantidad= 0 ,#*
                            valor=-1*valorfsp , #*
                            idcontrato_id=contrato.idcontrato ,
                            idnomina_id = idn ,
                        ) 
                    
    return True



def procesar_nomina_transporte(idn, parte_nomina,idempresa):
    if not parte_nomina:
        parte_nomina = 0

    contratos = Contratos.objects.filter(estadoliquidacion=3, id_empresa =  idempresa)
    if parte_nomina != 0:
        contratos = contratos.filter(idcosto = parte_nomina)

    try:
        nomina = Crearnomina.objects.get(idnomina=idn)
    except Crearnomina.DoesNotExist:
        return "Error de creación de nómina"
    
    sal_min = Salariominimoanual.objects.get(ano = nomina.anoacumular.ano).salariominimo
    aux_tra = Salariominimoanual.objects.get(ano = nomina.anoacumular.ano).auxtransporte
    
    
    for contrato in contratos:
        diasnomina = nomina.diasnomina
        
        
        if contrato.fechainiciocontrato > nomina.fechafinal:
            diasnomina = (nomina.fechafinal - contrato.fechainiciocontrato).days + 1
        
        if contrato.fechafincontrato and nomina.fechafinal <= contrato.fechafincontrato <= nomina.fechafinal:
            diasnomina -= (nomina.fechafinal - contrato.fechafincontrato).days
            
    
        horas_basico_mes = Nomina.objects.filter(idconcepto__codigo = 1, idcontrato=contrato.idcontrato, 
                                                 idnomina__mesacumular = nomina.mesacumular , idnomina__anoacumular = nomina.anoacumular ,
                                                 estadonomina=2).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        
        horas_basico_quincena = Nomina.objects.filter(idconcepto=1, idcontrato=contrato.idcontrato, 
                                                       idnomina_id=idn).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        
        
        
        total_mes = horas_basico_mes + horas_basico_quincena
        
        
        if not contrato.auxiliotransporte :
            transporte = 0
            diasnomina = 0
        elif contrato.salario <= (sal_min * 2):
            # Obtener la suma de las deducciones de la eps 
            total_base_trans = Nomina.objects.filter(
                idcontrato=contrato,
                idnomina_id=idn,
                idconcepto__indicador__id=25  
            ).exclude(
                idconcepto__codigo=2
            ).distinct().aggregate(total=Sum('valor'))['total'] or 0# Reemplaza 'monto' con el nombre correcto de la columna
            
            if total_base_trans < (sal_min * 2):
                transporte = diasnomina * (aux_tra / 30)
            else:
                transporte = 0
                diasnomina = 0
        
        concepto = Conceptosdenomina.objects.get(codigo= 2 , id_empresa_id = idempresa)
        
        
        
        if diasnomina > 0 and transporte > 0 :
            
            if diasnomina > 30:
                diasnomina = 30
                
            
            aux_pass = Nomina.objects.filter(
                idconcepto=concepto,
                idcontrato=contrato,
                idnomina_id=idn
            ).first()
            
            
            if aux_pass:
                if not EditHistory.objects.filter(
                    id_empresa_id=idempresa,
                    modified_object_id=aux_pass.idregistronom,
                    modified_model='Nomina',
                ).exists():
                    aux_pass.cantidad = diasnomina
                    aux_pass.valor = transporte
                    aux_pass.save()                  
            else:
                
                Nomina.objects.create(
                    idconcepto = concepto ,#*
                    cantidad=diasnomina ,#*
                    valor=transporte , #*
                    idcontrato_id=contrato.idcontrato ,
                    idnomina_id = idn ,
                )  
        
    return True
        

def calcular_vacaciones(contrato,nomina ):
    dias_vacaciones = 0
    vacaciones = EmpVacaciones.objects.filter(idcontrato=contrato ,estado = 2 ,tipovac='1' )
    for vac in vacaciones:
        data = Vacaciones.objects.filter(idcontrato=contrato, tipovac='1', idvacmaster = vac.id_sol_vac).first() 
        if data:
            if data.fechainicialvac <= nomina.fechafinal and data.ultimodiavac >= nomina.fechainicial:
                inicio = max(data.fechainicialvac, nomina.fechainicial)
                fin = min(data.ultimodiavac, nomina.fechafinal)
                dias_vacaciones = (fin - inicio).days + 1
        else:
            dias_vacaciones = 0
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





def calculo_prestamo(contrato, idn):
    loans = Prestamos.objects.filter(idcontrato=contrato , estadoprestamo = True ).order_by('-idprestamo')
    conceptosdenomina = Conceptosdenomina.objects.get(codigo = 50 , id_empresa = contrato.id_empresa_id)
    
    
    
    for load in loans:
        nominactual = Nomina.objects.filter(idnomina=idn , idconcepto=conceptosdenomina,control=load.idprestamo).exists()
        # Obtener deducciones de nómina relacionadas al préstamo
        deducciones = Nomina.objects.filter(
            idconcepto=conceptosdenomina,  # Asegúrate que este es el id correcto para "deducción de préstamo"
            control=load.idprestamo
        ).order_by('-idnomina') 
        
        # Obtener la suma de las deducciones del préstamo
        suma_deducciones = Nomina.objects.filter(
            idconcepto=conceptosdenomina,
            control=load.idprestamo
        ).aggregate(total=Sum('valor'))['total'] or 0  # Reemplaza 'monto' con el nombre correcto de la columna

        
        if deducciones :
            if not nominactual : 
                
                if (load.valorprestamo + suma_deducciones ) > load.valorcuota :
                    valor = load.valorprestamo / load.cuotasprestamo
                else :
                    valor = load.valorprestamo + suma_deducciones
                
                Nomina.objects.create(
                    idconcepto = conceptosdenomina ,
                    cantidad = 1,
                    valor = -1*valor,
                    idcontrato = contrato,
                    idnomina_id = idn,
                    control = load.idprestamo
                )
                
        else:
            valor = load.valorprestamo / load.cuotasprestamo
            
            
            Nomina.objects.create(
                idconcepto = conceptosdenomina ,
                cantidad = 1,
                valor = -1*valor,
                idcontrato = contrato,
                idnomina_id = idn,
                control = load.idprestamo
            )
    
    
    
