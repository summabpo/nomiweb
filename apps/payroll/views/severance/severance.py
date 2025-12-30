
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Tipodenomina , Conceptosdenomina ,Nomina, Crearnomina , Contratos , Anos, Liquidacion , Salariominimoanual , Nomina,Vacaciones
from apps.payroll.forms.BonusForm import BonusForm , BonusAddForm
from datetime import datetime, timedelta ,date
from dateutil.relativedelta import relativedelta

@login_required
@role_required('accountant')
def severance_annual_calculation(request):
    contratos_empleados = []
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    form = BonusForm()
    date_init_str = date_end_str = proy = ''
    
    
    if request.method == 'POST':
        form = BonusForm(request.POST)
        if form.is_valid():
            date_init_str = form.cleaned_data['init_Date']
            date_end_str = form.cleaned_data['end_date']
            
            date_init = datetime.strptime(date_init_str, '%d-%m-%Y').date()
            date_end = datetime.strptime(date_end_str, '%d-%m-%Y').date()
            año_actual = date_end.year

            proy = form.cleaned_data.get('estimated_bonus') or 0
            
            
            try:
                sm = Salariominimoanual.objects.get(ano=año_actual)
                salario_minimo = sm.salariominimo
                aux_transporte_val = sm.auxtransporte
            except Salariominimoanual.DoesNotExist:
                salario_minimo = 0
                aux_transporte_val = 0
                
            contratos_empleados = Contratos.objects.select_related('idempleado') \
                .filter(
                    estadocontrato=1,
                    tipocontrato__idtipocontrato__in=[1,2,3,4],
                    id_empresa_id=idempresa
                ) \
                .values(
                    'idempleado__docidentidad', 'idempleado__sapellido', 'idempleado__papellido',
                    'idempleado__pnombre', 'idempleado__snombre', 'idempleado__idempleado',
                    'idcontrato', 'fechainiciocontrato', 'salario', 'auxiliotransporte',
                    'tipocontrato', 'tiposalario','id_empresa'
                ).exclude(
                    tiposalario__idtiposalario=2
                )
            
            
            for contrato in contratos_empleados:
                for field in ['idempleado__pnombre', 'idempleado__snombre', 'idempleado__papellido', 'idempleado__sapellido']:
                    value = contrato.get(field, '')
                    if value is None or (isinstance(value, str) and value.strip().lower() == 'no data'):
                        contrato[field] = ''
                    else:
                        contrato[field] = value
                        
                fecha_inicio = contrato['fechainiciocontrato']
                fecha_fin = date_end
                validar = 0
                anio_actual = fecha_fin.year
                
                limite_cs = date(anio_actual, 12, 31)
                inicio_ano = date(anio_actual, 1, 1)
                
                if fecha_inicio <= inicio_ano:
                    fp_base = limite_cs if fecha_fin >= limite_cs else inicio_ano
                    fp = fp_base
                else:
                    if fecha_fin >= limite_cs and fecha_inicio > limite_cs:
                        fp_base = limite_cs
                        fp = fecha_inicio
                    elif fecha_fin >= limite_cs and fecha_inicio < limite_cs:
                        fp_base = limite_cs
                        fp = fp_base
                    elif fecha_fin < limite_cs and fecha_inicio < limite_cs:
                        fp_base = inicio_ano
                        fp = fecha_inicio
                    else:
                        fp_base = inicio_ano
                        fp = fecha_inicio
                        validar = 1

                # Calcular días prima
                if validar == 0:
                    fecha_fin_mas_uno = fecha_fin + timedelta(days=1)
                    diferencia = relativedelta(fecha_fin_mas_uno, fp)
                    anios, meses, dias = diferencia.years, diferencia.months, diferencia.days
                    dias_prima = anios * 360 + meses * 30 + dias
                    contrato['dias_prima'] = dias_prima + proy if dias_prima > 0 else 0
                else:
                    contrato['dias_prima'] = 0
                    
                contrato['cesantias'] =  cesantia_normal(contrato['idcontrato'] , contrato['dias_prima']) 
                
                contrato['trans'] = aux_transporte(contrato['idcontrato'], contrato['salario'], salario_minimo, aux_transporte_val)
                
                
            
            
            
    context = {
        'contratos_empleados': contratos_empleados,
        'form': form,
        'date_init_str':date_init_str,
        'date_end_str':date_end_str,
        'proy':proy,
        
    }
    
    return render(request, './payroll/severance_annual_calculation.html',context)

def cesantia_normal(idcontrato , dias ):
    cs = 0
    contrato = Contratos.objects.get(idcontrato=idcontrato)
    if contrato.tipocontrato.idtipocontrato == 5 or contrato.tiposalario.idtiposalario == 2 : 
        return 0
    else:
        cs = ( contrato.salario * dias ) / 360

    return cs



def aux_transporte(idcontrato , salario, minimo,aux):
    contrato = Contratos.objects.get(idcontrato=idcontrato)
    if contrato.tipocontrato.idtipocontrato == 5 or contrato.tiposalario.idtiposalario == 2 : 
        return 0
    return aux if salario < 2 * minimo else 0


