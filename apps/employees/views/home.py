from django.shortcuts import render
from employees.context_global import datos_cliente, datos_empleado

# Create your views here.
from django.views.generic import TemplateView, ListView, View
from companies.models import Contratos, Contratosemp

class InicioView(TemplateView):
    """vista que carga la pagina de inicio"""
    template_name = 'home/inicio.html'

def busca_empleado(request):
    mydata = Contratos.objects.filter(idcontrato='2477').values('idempleado')
    values = Contratosemp.objects.filter(idempleado__in=mydata).values()
    return render(request, 'home/inicio.html', {'context': values})

class ListaNominas(ListView):
    
    template_name = 'home/inicio.html'
    context_object_name = 'contratos'
    model = Contratos
    ordering = 'idcontrato'
    
    def get_queryset(self):
        datose = datos_empleado()
        ide = datose['ide']
        queryset = Contratos.objects.filter(idempleado=ide)
        return queryset
 