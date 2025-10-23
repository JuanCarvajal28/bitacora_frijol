from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('menu/', views.menu, name='menu'),
    path('logout/', views.logout_view, name='logout'),
    path('experimentos/', views.experimentos, name='experimentos'),
    path('experimentos/', views.experimentos, name='experimentos'),
    path('experimentos/eliminar/<int:id>/', views.eliminar_experimento, name='eliminar_experimento'),
    path('experimentos/finalizar/<int:id>/', views.finalizar_experimento, name='finalizar_experimento'),
]
