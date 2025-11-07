from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('menu/', views.menu, name='menu'),
    path('logout/', views.logout_view, name='logout'),
    path('experimentos/', views.experimentos, name='experimentos'),
    path('experimentos/eliminar/<int:id>/', views.eliminar_experimento, name='eliminar_experimento'),
    path('registers/eliminar/<int:id>/', views.eliminar_register_planta, name='eliminar_register_planta'),
    path('experimentos/finalizar/<int:id>/', views.finalizar_experimento, name='finalizar_experimento'),
    path('plantas/', views.plantas, name='plantas'),
    path('register_planta/', views.register_planta, name='register_planta'),
    path('experimentos/opciones/<int:id>/', views.visualizacion_datos, name='opciones_experimento'),
]