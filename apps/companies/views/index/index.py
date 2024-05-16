from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.components.decorators import custom_login_required ,custom_permission
from django.contrib.auth.decorators import login_required


@login_required
@custom_permission('entrepreneur')
def index_companies(request):
    print(request.session)
    return render(request, './companies/index.html')
    





