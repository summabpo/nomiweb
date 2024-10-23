from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from apps.components.qrgenerate import generate_qr_code



@login_required
@role_required('company')
def index_companies(request):
        
    return render(request, './companies/index.html')
    





