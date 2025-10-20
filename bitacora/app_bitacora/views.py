from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, 'app_bitacora/index.html')

def register(request):
    imagen_estado = 'img/semillin_sonriendo_señalando.png'
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está en uso.")
            imagen_estado = 'img/semillin_confundido.png'
            return render(request, 'app_bitacora/register.html', {'imagen_estado': imagen_estado})

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('menu')

    return render(request, 'app_bitacora/register.html', {'imagen_estado': imagen_estado})

def login_view(request):
    imagen_estado = 'img/semillin_sonriendo_señalando.png'

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('menu')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
            imagen_estado = 'img/semillin_triste.png'

    return render(request, 'app_bitacora/login.html', {'imagen_estado': imagen_estado})

@login_required
def menu(request):
    return render(request, 'app_bitacora/menu.html')

def logout_view(request):
    logout(request)
    return redirect('index')
