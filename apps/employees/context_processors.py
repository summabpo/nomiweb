from django.shortcuts import render
from apps.companies.models import Contratos, Contratosemp

def busca_empleado_cp(request):
    idc = 3863
    mydatactx = Contratos.objects.filter(idcontrato=idc).values('idempleado')
    valuesctx = Contratosemp.objects.filter(idempleado__in=mydatactx).values('pnombre', 'snombre', 'papellido', 'sapellido', 'email', 'idempleado')
    return {
        "valuesctx": valuesctx,
        "idc": idc
    }