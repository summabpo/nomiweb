from django.http import HttpResponse
from django.shortcuts import render

def print_session(request):
    # Obtén todos los datos de la sesión
    session_data = request.session.items()
    
    # Crea una respuesta en formato de texto plano
    response_content = "Datos de la sesión:\n"
    for key, value in session_data:
        response_content += f"{key}: {value}\n"
    
    return HttpResponse(response_content, content_type="text/plain")
