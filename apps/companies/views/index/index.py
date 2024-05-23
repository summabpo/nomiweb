from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.components.decorators import custom_login_required ,custom_permission
from django.contrib.auth.decorators import login_required
from apps.components.qrgenerate import generate_qr_code



@login_required
@custom_permission('entrepreneur')
def index_companies(request):
    data = "https://www.ejemplo.com"
    qr_code_html = generate_qr_code(data)
    
    return render(request, './companies/index.html',{'qr_code_html': qr_code_html})
    





