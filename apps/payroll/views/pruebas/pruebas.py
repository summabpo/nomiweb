from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
from apps.common.models import Contratos
from django.shortcuts import get_object_or_404


# Datos de ejemplo
items = [
    {'name': 'Elemento 1'},
    {'name': 'Elemento 2'},
    {'name': 'Elemento 3'}
]

# Vista principal con el botón para abrir el modal
def index_item(request):
    return render(request, './payroll/prueba.html')

# Vista para el contenido del modal
@csrf_exempt
def item_modal(request):
    context = {'items': items}
    return render(request, './payroll/prueba_modal.html', context)

# Vista para agregar un ítem
@csrf_exempt
def add_item(request):
    if request.method == 'POST':
        item_name = request.POST.get('name')
        if item_name:
            items.append({'name': item_name})
    context = {'items': items}
    return render(request, './payroll/prueba_item_list.html', context)




def my_form(request):
    data = {
        "id":1121, 
    }
    return render(request, './payroll/prueba.html',{'data': data})


def get_multiplicador(request):
    data_id = request.GET.get('data_id')
    objeto = get_object_or_404(Contratos, idcontrato=data_id)
    print(objeto.salario)
    return JsonResponse({'multiplicador': objeto.salario/30})