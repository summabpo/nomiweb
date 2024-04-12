from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login , logout
from django.contrib import messages
from .forms import LoginForm


def Login(request):
    # if request.user.is_authenticated:
    #     return redirect_to_appropriate_page(request, request.user)
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('success_url')
            else:
                messages.error(request, 'Credenciales inválidas. Por favor, inténtalo de nuevo.')
    else:
        form = LoginForm()
    return render(request, './users/login.html', {'form': form})


def Logout(request):
    logout(request)
    return redirect('login:login')




