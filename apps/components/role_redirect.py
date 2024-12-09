from django.shortcuts import redirect
from django.urls import NoReverseMatch

def redirect_by_role(user):
# Diccionario de roles y vistas asociadas
    role_views = {
        'admin': 'admin:admin',
        'accountant': 'payroll:index_payroll',
        'employee': 'employees:index_employees',
        'company': 'companies:index_companies',
    }

    # Obtener la vista correspondiente al rol del usuario
    url_name = role_views.get(user, 'login:error_page')
    
    try:
        # Intentar redirigir al usuario a la vista correspondiente
        return redirect(url_name)
    except NoReverseMatch:
        # Si la vista no existe, redirigir a la página de error
        return redirect('login:error_page')
    
    
    
def redirect_by_role2(user):
    role_views = {
        'administrator': 'admin:admin',
        'accountant': 'accountant_dashboard',
        'employees': 'employees:index_employees',
        'entrepreneur': 'companies:index_companies',
    }
    role = user
    return role_views.get(role, 'error_page')

