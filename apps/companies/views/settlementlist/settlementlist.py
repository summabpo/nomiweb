from django.shortcuts import render
from apps.companies.models import Liquidacion


def settlementlist(request):
    liquidaciones = Liquidacion.objects.all()
    
    
    
    
    return render(request, 'companies/settlementlist.html',{
        'liquidaciones':liquidaciones,
    } )
