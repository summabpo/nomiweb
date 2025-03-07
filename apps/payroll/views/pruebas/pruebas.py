from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render



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
    return render(request, './payroll/prueba.html')


def validate_number(request):
    number = request.GET.get('number')
    if not number.isdigit() or int(number) > 99:
        response = 'Número inválido'
    else:
        response = f'Número válido: {number}'
    return JsonResponse({'message': response})