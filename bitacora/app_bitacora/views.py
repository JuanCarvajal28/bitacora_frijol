from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from app_bitacora.models import Experimentos, Plantas, Etapas, Registros
from datetime import date
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import io, base64
from django.db.models import Avg
from django.utils import timezone


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

    return render(request, "app_bitacora/signup.html", {"imagen_estado": imagen_estado})


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
    logout(request)

    storage = messages.get_messages(request)
    for _ in storage:
        pass

    request.session.flush()

    response = redirect("index")
    response.delete_cookie("messages")
    return response


@login_required
def experimentos(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        descripcion = request.POST.get("descripcion")
        fecha_fin = request.POST.get("fecha_fin")

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
                fecha_fin=fecha_fin if fecha_fin else None,
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
def visualizacion_datos(request, id):
    experimento = get_object_or_404(
        Experimentos, id_experimento=id, id_usuario=request.user
    )

    registros = Registros.objects.filter(id_experimento=experimento).order_by("fecha_registro")

    if not registros.exists():
        return render(
            request,
            "app_bitacora/opcionesExp.html",
            {
                "experimento": experimento,
                "tabla": [],
                "grafica": None,
                "mensaje": "Aún no hay registros para este experimento 🌱",
            },
        )

    fechas = [r.fecha_registro for r in registros]
    alturas = [float(r.altura_cm) for r in registros]

    dias = np.array([(f - fechas[0]).days for f in fechas])
    alturas = np.array(alturas)

    n = len(dias)
    sumXY = np.sum(dias * alturas)
    sumXX = np.sum(dias**2)
    sumX = np.sum(dias)
    sumY = np.sum(alturas)

    a1 = (n * sumXY - sumX * sumY) / (n * sumXX - sumX**2)
    a0 = (sumY - a1 * sumX) / n

    y_estimado = a0 + a1 * dias
    r2 = 1 - (
        np.sum((alturas - y_estimado) ** 2) / np.sum((alturas - np.mean(alturas)) ** 2)
    )
    ecuacion = f"y = {a1:.4f}x + {a0:.4f}"

    plt.figure(figsize=(7, 5))
    plt.scatter(dias, alturas, color="green", label="Datos reales")
    plt.plot(dias, y_estimado, "r-", linewidth=2, label=f"Regresión: {ecuacion}")
    plt.title("Crecimiento de Planta de Frijol", fontsize=13)
    plt.xlabel("Días desde la primera medición")
    plt.ylabel("Altura (cm)")
    plt.grid(True, alpha=0.3)
    plt.legend()

    plt.xticks(range(int(dias.min()), int(dias.max()) + 1))

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    grafica_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()

    tabla = [
        {"fecha": r.fecha_registro, "altura": r.altura_cm}
        for r in registros
    ]

    contexto = {
        "experimento": experimento,
        "tabla": tabla,
        "grafica": grafica_base64,
        "ecuacion": ecuacion,
        "r2": round(r2, 4),
        "pendiente": round(a1, 4),
        "intercepto": round(a0, 4),
    }

    return render(request, "app_bitacora/visuaDatos.html", contexto)

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
    experimentos = Experimentos.objects.all()

    if request.method == "POST":
        id_experimento = request.POST.get("id_experimento")
        altura = request.POST.get("altura_cm")
        fecha = request.POST.get("fecha_registro")
        imagen = request.FILES.get("imagen")

        if not id_experimento or altura == "" or not fecha:
            messages.error(request, "Por favor completa todos los campos obligatorios.")
            return redirect("register_planta")

        nuevo_registro = Registros(
            id_experimento_id=id_experimento,
            altura_cm=altura,
            fecha_registro=fecha,
            imagen=imagen,
        )
        nuevo_registro.save()

        messages.success(request, "✅ Registro agregado exitosamente.")
        return redirect("register_planta")

    registros = Registros.objects.select_related("id_experimento").order_by("-fecha_registro")

    return render(
        request,
        "app_bitacora/register_planta.html",
        {"experimientos": experimentos, "registros": registros},
    )

def handler404(request, exception):
    return render(request, 'app_bitacora/404error.html', status=404)