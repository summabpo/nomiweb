import random
import string
import datetime
from .datacompanies import datos_cliente
from .dataemployees import datos_empleado
from apps.common.models import  Certificaciones, Nomina ,Contratosemp ,Contratos,Cargos
from django.db.models import Q,Sum
from django.utils import timezone
import pytz
from apps.components.humani import format_value



# Generador de codigo de  certificado 
def generar_codigo():
    caracteres = string.ascii_letters + string.digits 
    while True:
        codigo = ''.join(random.choice(caracteres) for _ in range(5))
        if not Certificaciones.objects.filter(codigoconfirmacion=codigo).exists():
            return codigo  


# Generador de meses anteriores 
def calculo_salario_promedio():
    mes_actual = datetime.datetime.now().month
    ano_actual = datetime.datetime.now().year

    # Diccionario de meses
    meses_dict = {
        1: "ENERO",
        2: "FEBRERO",
        3: "MARZO",
        4: "ABRIL",
        5: "MAYO",
        6: "JUNIO",
        7: "JULIO",
        8: "AGOSTO",
        9: "SEPTIEMBRE",
        10: "OCTUBRE",
        11: "NOVIEMBRE",
        12: "DICIEMBRE"
    }

    meses_anteriores = []
    for i in range(1, 4):
        mes_anterior = mes_actual - i
        ano_anterior = ano_actual
        if mes_anterior <= 0:
            mes_anterior += 12
            ano_anterior -= 1
        meses_anteriores.append((meses_dict[mes_anterior], ano_anterior))

    return meses_anteriores[0][0], meses_anteriores[1][0], meses_anteriores[2][0], meses_anteriores[0][1], meses_anteriores[1][1], meses_anteriores[2][1]



def workcertificategenerator(idc,destino ,modelo):
    zona_horaria = pytz.timezone('America/Bogota')
    nombre_mes_1, nombre_mes_2, nombre_mes_3, ano_1, ano_2, ano_3 = calculo_salario_promedio()
    contrato = Contratos.objects.get(idcontrato = idc )
    datae = datos_empleado(idc)
    
    datac = datos_cliente(contrato.id_empresa.idempresa)
    
    fecha_actual = timezone.now().astimezone(zona_horaria)
    salario = int(contrato.salario) 
    
    cargo = Cargos.objects.get(idcargo = contrato.cargo.idcargo)

    
    queryset_1 = Nomina.objects.filter(
        idconcepto__indicador__nombre="baseprestacionsocial",
        idnomina__mesacumular=nombre_mes_1,
        idnomina__anoacumular=ano_1,
        idcontrato=idc,
        valor__gt=0
    )

    queryset_2 = Nomina.objects.filter(
        idconcepto__indicador__nombre="baseprestacionsocial",
        idnomina__mesacumular=nombre_mes_2,
        idnomina__anoacumular=ano_2,
        idcontrato=idc,
        valor__gt=0
    )

    queryset_3 = Nomina.objects.filter(
        idconcepto__indicador__nombre="baseprestacionsocial",
        idnomina__mesacumular=nombre_mes_3,
        idnomina__anoacumular=ano_3,
        idcontrato=idc,
        valor__gt=0
    )

    queryset = queryset_1.union(queryset_2, queryset_3)


            
    
    if queryset.exists():
        salario_promedio = (queryset.aggregate(salario_promedio=Sum('valor'))['salario_promedio'])/3
    else:
        salario_promedio = 0

    if modelo == '2':
        salario_certificado = salario_promedio + salario
    else:
        salario_certificado=salario

    codigo_confirmacion = generar_codigo()
    tipo_certificado = modelo
    nombre_contrato = contrato.tipocontrato.tipocontrato 
    certificacion = Certificaciones(destino=destino,
                                    idcontrato=contrato, 
                                    salario= salario_certificado, 
                                    cargo = cargo , 
                                    tipocontrato=nombre_contrato, 
                                    codigoconfirmacion = codigo_confirmacion, 
                                    tipocertificacion = tipo_certificado,
                                    promediovariable = 0 ,
                                    )
    certificacion.save()
    certificacion.fecha = fecha_actual
    certificacion.save()
    
    
    
    context = {
            ## empresa 
            'empresa':datac['nombreempresa'],
            'rrhh':datac['contactorrhh'],
            'nit': datac['nit'],
            'direccion':datac['direccionempresa'],
            'ciudad':datac['ciudad'],
            'web':datac['website'],
            'telefono':datac['telefono'],
            'email ': datac['email'],
            'logo' : datac['logo'],
            'firma' : datac['firmacertificaciones'],
            'idempresa' : datac['idempresa'],
            'emailrrhh' : datac['emailrrhh'],
            'cargo_certificaciones':datac['cargocertificaciones'],
            
            ## empleado
            'nombre' : datae['nombre_completo'],
            'identificacion': datae['docidentidad'],
            'fecha':datae['fechainiciocontrato'],
            'fechafincontrato':datae['fechafincontrato'],
            'cargo':datae['cargo'],
            'sueldo': format_value(salario),
            'tipoc':datae['nombre_contrato'] , 
            
            # certificado 
            'destino':destino,
            'idcert':certificacion.idcert,
            'codigo_confirmacion':codigo_confirmacion,
            'fecha_certificacion':fecha_actual,
            'tipo':modelo,
        }
        
    return context 


#!  -----------------------------------------------------------------------------------



""" 
    idcert = models.AutoField(primary_key=True)
    destino = models.CharField(max_length=100, blank=True, null=True)
    idempleado = models.ForeignKey('Contratosemp', models.DO_NOTHING, db_column='idempleado')
    idcontrato = models.IntegerField(blank=True, null=True)
    fecha = models.DateField(blank=True, null=True)
    salario = models.IntegerField(blank=True, null=True)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    tipocontrato = models.CharField(max_length=30, blank=True, null=True)
    promediovariable = models.IntegerField(blank=True, null=True)
    codigoconfirmacion = models.CharField(max_length=8, blank=True, null=True)

"""

def workcertificatedownload(idcert):
    
    certificado = Certificaciones.objects.get(idcert = idcert)
    datae = datos_empleado(certificado.idcontrato.idcontrato)
    datac = datos_cliente(certificado.idcontrato.id_empresa.idempresa)
    
    context = {
            ## empresa 
            'empresa':datac['nombreempresa'],
            'rrhh':datac['contactorrhh'],
            'nit': datac['nit'],
            'direccion':datac['direccionempresa'],
            'ciudad':datac['ciudad'],
            'web':datac['website'],
            'telefono':datac['telefono'],
            'email ': datac['email'],
            'logo' : datac['logo'],
            'firma' : datac['firmacertificaciones'],
            'idempresa' : datac['idcliente'],
            'emailrrhh' : datac['emailcontab'],
            'cargo_certificaciones':datac['cargocertificaciones'],
            
            ## empleado
            'nombre' : datae['nombre_completo'],
            'identificacion': datae['docidentidad'],
            'fecha':datae['fechainiciocontrato'],
            'fechafincontrato':datae['fechafincontrato'],
            'cargo':datae['cargo'],
            'sueldo': "{:,.0f}".format(certificado.salario).replace(',', '.'),
            'tipoc':datae['nombre_contrato'] , 
            # certificado 
            'destino':certificado.destino ,
            'idcert':certificado.idcert,
            'codigo_confirmacion':certificado.codigoconfirmacion,
            'fecha_certificacion':certificado.fecha ,
            'tipo':str(certificado.tipocertificacion),
        }
    
    
    
    return context



