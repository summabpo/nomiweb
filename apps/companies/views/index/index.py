from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.models import Tipodocumento , Paises , Ciudades , Contratosemp , Contratos
from apps.companies.forms.EmployeeForm import EmployeeForm
from django.contrib import messages
from apps.login.middlewares import NombreDBSingleton




def index_companies(request):
    usuario_data = request.session.get('usuario', {})
    db = usuario_data.get('db', None)
    singleton = NombreDBSingleton()
    singleton.set_nombre_db(db)
    print(singleton.get_nombre_db())
    contactos = Contratosemp.objects.all()
    return render(request, './companies/index.html',{'comn':contactos})
    





