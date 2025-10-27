from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from app_bitacora.models import Experimentos, Plantas, Etapas, Registros
from datetime import date


def index(request):
    return render(request, "app_bitacora/index.html")


def signup(request):
    imagen_estado = "img/semillin_sonriendo_señalando.png"
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está en uso.")
            imagen_estado = "img/semillin_confundido.png"
            return render(
                request, "app_bitacora/signup.html", {"imagen_estado": imagen_estado}
            )

        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        login(request, user)
        return redirect("menu")

    return render(
        request, "app_bitacora/signup.html", {"imagen_estado": imagen_estado}
    )


def login_view(request):
    imagen_estado = "img/semillin_sonriendo_señalando.png"

    storage = messages.get_messages(request)
    for _ in storage:
        pass
    
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("menu")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
            imagen_estado = "img/semillin_triste.png"

    return render(request, "app_bitacora/login.html", {"imagen_estado": imagen_estado})


@login_required
def menu(request):
    return render(request, "app_bitacora/menu.html")


def logout_view(request):
    storage = messages.get_messages(request)
    for _ in storage:
        pass
    return redirect("index")


@login_required
def experimentos(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        descripcion = request.POST.get("descripcion")
        date = request.POST.get("fecha_fin")

        if not nombre:
            messages.error(request, "El nombre del experimento es obligatorio.")
            return redirect("experimentos")

        planta_frijol = Plantas.objects.filter(nombre_comun__iexact="Frijol").first()

        if planta_frijol:
            Experimentos.objects.create(
                id_usuario=request.user,
                id_planta=planta_frijol,
                nombre=nombre,
                descripcion=descripcion,
                fecha_inicio=date.today(),
                fecha_fin=fecha_fin,
            )
            messages.success(request, f"Experimento '{nombre}' creado exitosamente.")
        else:
            messages.error(request, "No existe la planta 'Frijol' en la base de datos.")
        return redirect("experimentos")

    lista_experimentos = Experimentos.objects.filter(id_usuario=request.user).order_by(
        "-id_experimento"
    )
    return render(
        request, "app_bitacora/experimentos.html", {"experimentos": lista_experimentos}
    )


@login_required
def eliminar_experimento(request, id):
    experimento = get_object_or_404(
        Experimentos, id_experimento=id, id_usuario=request.user
    )
    experimento.delete()
    return redirect("experimentos")


@login_required
def finalizar_experimento(request, id):
    experimento = get_object_or_404(
        Experimentos, id_experimento=id, id_usuario=request.user
    )

    if not experimento.fecha_fin:
        experimento.fecha_fin = date.today()
        experimento.save()
        messages.success(
            request, f"El experimento '{experimento.nombre}' fue finalizado."
        )
    else:
        messages.info(
            request, f"El experimento '{experimento.nombre}' ya estaba finalizado."
        )

    return redirect("experimentos")

@login_required
def opciones_experimento(request, id):
    experimento = get_object_or_404(Experimentos, id_experimento=id, id_usuario=request.user)
    return render(request, 'app_bitacora/opcionesExp.html', {'experimento': experimento})

@login_required
def plantas(request):
    if request.method == "POST":
        nombre_comun = request.POST.get("nombre_comun")
        nombre_cientifico = request.POST.get("nombre_cientifico")
        familia = request.POST.get("familia")
        region_origen = request.POST.get("region_origen")
        edad_planta = request.POST.get("edad_planta")
        descripcion = request.POST.get("descripcion")

        Plantas.objects.create(
            nombre_comun=nombre_comun,
            nombre_cientifico=nombre_cientifico,
            familia=familia,
            region_origen=region_origen,
            edad_planta=edad_planta,
            descripcion=descripcion,
        )
        return redirect("plantas")

    plantas = Plantas.objects.all()
    return render(request, "app_bitacora/planta.html", {"plantas": plantas})


@login_required
def register_planta(request):
    plantas = Plantas.objects.all()
    etapas = Etapas.objects.select_related('id_planta').all()

    if request.method == 'POST':
        id_planta = request.POST.get('id_planta')
        nombre_etapa = request.POST.get('nombre_etapa')
        orden = request.POST.get('orden')
        descripcion = request.POST.get('descripcion')

        Etapas.objects.create(
            id_planta_id=id_planta,
            nombre_etapa=nombre_etapa,
            orden=orden,
            descripcion=descripcion
        )
        # return redirect('etapas')

    return render(request, 'app_bitacora/register_planta.html', {'plantas': plantas, 'etapas': etapas})
    # return render(request, "app_bitacora/register_planta.html", {"register_planta": plantas})
