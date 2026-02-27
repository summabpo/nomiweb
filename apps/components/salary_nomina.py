from apps.common.models import Crearnomina , HistoricoNomina ,NominaComprobantes, NovSalarios , Empresa , Anos , Nomina , Contratos




def salary_nomina_update(contrato,fecha):
    salary = contrato.salario

    data = NovSalarios.objects.filter( idcontrato = contrato ).order_by('-idcambiosalario').first()
    nomina = Nomina.objects.filter(idnomina__fechapago__lt=data.fechanuevosalario , idnomina__tiponomina__idtiponomina__in=[1, 2] ,idconcepto__codigo = 1, idnomina__id_empresa = contrato.id_empresa).order_by('-idnomina').first()




    print('-------------------')
    print(salary)
    print(data)
    print(data.fechanuevosalario)
    print(nomina.valor)
    print(type(fecha))
    print('-------------------')


    return salary











